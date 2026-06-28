import time
import logging
from datetime import datetime
from PySide6.QtCore import QObject, Slot, QTimer
from core.enums import TypingState
from core.models import TypingSettings, TypingSession, TypingProgress, RecoveryState
from services.countdown_worker import CountdownWorker
from services.typing_worker import TypingWorker
from services.hotkey_service import HotkeyService
from utils.settings import SettingsManager
from utils.recovery import RecoveryManager
from utils.history import HistoryManager
from utils.constants import TEST_TYPING_TEXT

logger = logging.getLogger("TypeFlow")

class TypingController(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.view = main_window
        
        # Managers
        self.settings_mgr = SettingsManager()
        self.recovery_mgr = RecoveryManager()
        self.history_mgr = HistoryManager()
        
        # State
        self.state = TypingState.READY
        self.queue_texts = []
        
        # Workers
        self.countdown_worker = None
        self.typing_worker = None
        
        # Hotkey Service
        self.hotkey_svc = HotkeyService()
        
        # Checkpointing cache
        self.last_checkpoint_index = 0
        self.last_checkpoint_time = 0.0
        
        self.setup_connections()
        self.load_initial_state()

    def setup_connections(self) -> None:
        # Connect View Signals
        self.view.close_requested.connect(self.shutdown)
        
        panel = self.view.settings_panel
        panel.start_clicked.connect(self.start_typing)
        panel.stop_clicked.connect(self.cancel_typing)
        panel.test_clicked.connect(self.load_test_text)
        panel.paste_clicked.connect(self.paste_clipboard)
        panel.clear_clicked.connect(self.clear_editor)
        panel.theme_toggled.connect(self.change_theme)
        panel.settings_changed.connect(self.save_settings)
        
        # Queue Signals
        panel.add_to_queue.connect(self.add_text_to_queue)
        panel.clear_queue.connect(self.clear_queue_list)
        panel.remove_queue_item.connect(self.remove_queue_index)
        
        # History Selection
        panel.combo_history.activated.connect(self.load_history_item)

        # Connect Hotkey Service Signals
        self.hotkey_svc.start_pressed.connect(self.start_typing)
        self.hotkey_svc.pause_pressed.connect(self.pause_typing)
        self.hotkey_svc.resume_pressed.connect(self.resume_typing)
        self.hotkey_svc.stop_pressed.connect(self.cancel_typing)

    def load_initial_state(self) -> None:
        """Loads settings, updates theme, history, and checks for recovery state on launch."""
        # 1. Apply Settings
        self.view.settings_panel.apply_settings(self.settings_mgr.settings)
        self.view.apply_theme(self.settings_mgr.settings.theme)
        
        # Load and set geometry
        x, y, w, h = self.settings_mgr.get_window_geometry()
        if x != -1 and y != -1:
            self.view.setGeometry(x, y, w, h)
        else:
            self.view.resize(w, h)

        # 2. History
        self.refresh_history()

        # 3. Register Start Hotkey (F8)
        self.hotkey_svc.register_start_hotkey()

        # 4. Recovery Check
        QTimer.singleShot(500, self.check_recovery)

    def check_recovery(self) -> None:
        """Asks user to recover previous aborted session if found."""
        recovery = self.recovery_mgr.load_recovery()
        if recovery and recovery.text:
            logger.info("Recovery checkpoint detected.")
            if self.view.show_recovery_prompt(recovery):
                logger.info("Recovery accepted by user. Restoring state...")
                self.queue_texts = recovery.queue_texts
                self.view.settings_panel.update_queue_list(self.queue_texts)
                
                # Apply settings from recovery
                self.settings_mgr.settings = recovery.settings
                self.view.settings_panel.apply_settings(recovery.settings)
                
                # Restore text to editor and trigger typing
                self.view.editor.set_text(recovery.text)
                
                # Start immediately at the recovered index
                self.start_typing(start_index=recovery.current_index, elapsed=recovery.elapsed_seconds)
            else:
                logger.info("Recovery rejected by user. Clearing recovery state.")
                self.recovery_mgr.clear_recovery()

    def start_typing(self, start_index: int = 0, elapsed: int = 0) -> None:
        """Validates typing parameters and starts countdown."""
        if self.state in (TypingState.COUNTDOWN, TypingState.TYPING, TypingState.PAUSED):
            logger.warning("Typing run already in progress.")
            return

        # 1. Retrieve active text
        text = self.view.editor.get_text()
        
        # If queue has items and text editor is empty, load first item
        if not text and self.queue_texts:
            text = self.queue_texts[0]
            self.view.editor.set_text(text)
        
        if not text:
            self.view.show_error("Validation Error", "Text to type cannot be empty.")
            return

        # 2. Get Settings
        settings = self.view.settings_panel.get_settings()
        
        # Check validation
        if settings.get_char_delay() < 0:
            self.view.show_error("Validation Error", "Invalid typing speed delay.")
            return

        logger.info("Starting typing sequence...")
        self.state = TypingState.COUNTDOWN
        self.view.settings_panel.set_typing_active(True)
        self.view.editor.set_read_only(True)
        self.view.status_bar.set_status(TypingState.COUNTDOWN)

        # Set up recovery checkpoint caches
        self.last_checkpoint_index = start_index
        self.last_checkpoint_time = float(elapsed)

        # Save initial recovery file
        recovery_state = RecoveryState(
            text=text,
            current_index=start_index,
            elapsed_seconds=elapsed,
            settings=settings,
            queue_texts=self.queue_texts
        )
        self.recovery_mgr.save_recovery(recovery_state)

        # Register dynamic control hotkeys (F9, F10, ESC)
        self.hotkey_svc.register_control_hotkeys()

        # 3. Start countdown worker
        countdown_secs = settings.countdown_seconds
        self.countdown_worker = CountdownWorker(countdown_secs)
        self.countdown_worker.tick.connect(self.on_countdown_tick)
        self.countdown_worker.countdown_completed.connect(lambda: self.on_countdown_finished(text, start_index, settings, elapsed))
        self.countdown_worker.cancelled.connect(self.on_countdown_cancelled)
        self.countdown_worker.error.connect(self.on_worker_error)
        self.countdown_worker.finished.connect(self.countdown_worker.deleteLater)
        
        # Show focus overlay
        self.view.overlay.show_countdown(countdown_secs)
        self.countdown_worker.start()

    def cancel_typing(self) -> None:
        """Cancels either countdown or active typing."""
        logger.info("Emergency Stop triggered.")
        
        if self.state == TypingState.COUNTDOWN and self.countdown_worker:
            self.countdown_worker.cancel()
        elif self.state in (TypingState.TYPING, TypingState.PAUSED) and self.typing_worker:
            self.typing_worker.cancel()
        else:
            self.reset_ui(TypingState.CANCELLED)

    def pause_typing(self) -> None:
        """Pauses typing execution."""
        if self.state == TypingState.TYPING and self.typing_worker:
            self.typing_worker.pause()
            self.state = TypingState.PAUSED
            self.view.status_bar.set_status(TypingState.PAUSED)
            logger.info("Session paused.")

    def resume_typing(self) -> None:
        """Resumes typing execution."""
        if self.state == TypingState.PAUSED and self.typing_worker:
            self.typing_worker.resume()
            self.state = TypingState.TYPING
            self.view.status_bar.set_status(TypingState.TYPING)
            logger.info("Session resumed.")

    # Countdown Handlers
    def on_countdown_tick(self, seconds_remaining: int) -> None:
        self.view.overlay.set_tick(seconds_remaining)

    def on_countdown_finished(self, text: str, start_index: int, settings: TypingSettings, elapsed: int) -> None:
        self.view.overlay.hide()
        self.state = TypingState.TYPING
        self.view.status_bar.set_status(TypingState.TYPING)
        
        # Start typing worker
        self.typing_worker = TypingWorker(text, start_index, settings, elapsed)
        self.typing_worker.progress.connect(self.on_typing_progress)
        self.typing_worker.completed.connect(self.on_typing_completed)
        self.typing_worker.cancelled.connect(self.on_typing_cancelled)
        self.typing_worker.error.connect(self.on_worker_error)
        self.typing_worker.finished.connect(self.typing_worker.deleteLater)
        
        self.typing_worker.start()
        logger.info("Typing background thread started.")

    def on_countdown_cancelled(self) -> None:
        self.view.overlay.hide()
        self.recovery_mgr.clear_recovery()
        self.reset_ui(TypingState.CANCELLED)

    # Typing Handlers
    def on_typing_progress(self, progress: TypingProgress) -> None:
        self.view.progress_card.update_progress(progress)
        self.view.status_bar.set_status(
            TypingState.TYPING, progress.index, progress.total, progress.eta_seconds
        )
        
        # Checkpoint persistence: Save every 50 chars or 2 seconds
        if (progress.index - self.last_checkpoint_index >= 50 or 
            progress.elapsed_seconds - self.last_checkpoint_time >= 2.0):
            
            self.last_checkpoint_index = progress.index
            self.last_checkpoint_time = float(progress.elapsed_seconds)
            
            settings = self.view.settings_panel.get_settings()
            recovery_state = RecoveryState(
                text=self.view.editor.get_text(),
                current_index=progress.index,
                elapsed_seconds=progress.elapsed_seconds,
                settings=settings,
                queue_texts=self.queue_texts
            )
            self.recovery_mgr.save_recovery(recovery_state)
            logger.debug(f"Saved recovery checkpoint at index {progress.index}.")

    def on_typing_completed(self) -> None:
        logger.info("Typing sequence completed.")
        
        # Save typed text to history
        typed_text = self.view.editor.get_text()
        self.history_mgr.add_item(typed_text)
        self.refresh_history()
        
        # Clear recovery file
        self.recovery_mgr.clear_recovery()
        
        # Queue progression: If text was from queue, pop it
        if self.queue_texts and self.queue_texts[0] == typed_text:
            self.queue_texts.pop(0)
            self.view.settings_panel.update_queue_list(self.queue_texts)
            # Clear editor for next item
            self.view.editor.clear()
        
        self.reset_ui(TypingState.COMPLETED)

    def on_typing_cancelled(self) -> None:
        self.recovery_mgr.clear_recovery()
        self.reset_ui(TypingState.CANCELLED)

    def on_worker_error(self, msg: str) -> None:
        logger.error(f"Worker Thread Error: {msg}")
        self.view.show_error("Background Thread Error", f"An error occurred: {msg}")
        self.recovery_mgr.clear_recovery()
        self.reset_ui(TypingState.CANCELLED)

    # UI Reset Helpers
    def reset_ui(self, ending_state: TypingState) -> None:
        self.state = TypingState.READY
        self.view.settings_panel.set_typing_active(False)
        self.view.editor.set_read_only(False)
        self.view.status_bar.set_status(ending_state)
        self.view.progress_card.reset()
        
        # Unregister dynamic control hotkeys (F9, F10, ESC)
        self.hotkey_svc.unregister_control_hotkeys()
        
        # Cleanup workers
        self.countdown_worker = None
        self.typing_worker = None

    # Sidebar Commands
    def load_test_text(self) -> None:
        self.view.editor.set_text(TEST_TYPING_TEXT)
        logger.info("Test Typing text loaded.")

    def paste_clipboard(self) -> None:
        import pyperclip
        try:
            clipboard_text = pyperclip.paste()
            if clipboard_text:
                self.view.editor.set_text(clipboard_text)
                logger.info("Text pasted from clipboard.")
        except Exception as e:
            logger.error(f"Clipboard paste failed: {e}")

    def clear_editor(self) -> None:
        self.view.editor.clear()
        self.view.progress_card.reset()
        logger.info("Text editor cleared.")

    def change_theme(self, theme: str) -> None:
        # Update settings object and stylesheet
        self.settings_mgr.settings.theme = theme
        self.settings_mgr.save()
        self.view.apply_theme(theme)

    def save_settings(self, settings: TypingSettings) -> None:
        # Save geometry and options
        self.settings_mgr.settings = settings
        self.settings_mgr.save()

    # Queue Commands
    def add_text_to_queue(self) -> None:
        text = self.view.editor.get_text()
        if text:
            self.queue_texts.append(text)
            self.view.settings_panel.update_queue_list(self.queue_texts)
            self.view.editor.clear()
            logger.info("Added current text to queue.")
        else:
            self.view.show_error("Queue Error", "Cannot add empty text to queue.")

    def clear_queue_list(self) -> None:
        self.queue_texts = []
        self.view.settings_panel.update_queue_list(self.queue_texts)
        logger.info("Queue cleared.")

    def remove_queue_index(self, index: int) -> None:
        if 0 <= index < len(self.queue_texts):
            removed = self.queue_texts.pop(index)
            self.view.settings_panel.update_queue_list(self.queue_texts)
            logger.info(f"Removed item from queue at index {index}.")

    # History Commands
    def refresh_history(self) -> None:
        history = self.history_mgr.load_history()
        self.view.settings_panel.update_history_combobox(history)

    def load_history_item(self, index: int) -> None:
        history = self.history_mgr.load_history()
        if 0 <= index < len(history):
            self.view.editor.set_text(history[index])
            logger.info(f"Loaded history item at index {index}.")

    # Shutdown
    @Slot()
    def shutdown(self) -> None:
        """Gracefully and synchronously terminates running workers to avoid memory leaks."""
        logger.info("Controller shutdown hook initiated.")
        
        # Stop countdown if running
        if self.countdown_worker and self.countdown_worker.isRunning():
            self.countdown_worker.cancel()
            self.countdown_worker.wait()
            
        # Stop typing if running
        if self.typing_worker and self.typing_worker.isRunning():
            self.typing_worker.cancel()
            self.typing_worker.wait()

        # Clean up hotkey hooks
        self.hotkey_svc.cleanup()

        # Save window geometry
        geom = self.view.geometry()
        self.settings_mgr.set_window_geometry(geom.x(), geom.y(), geom.width(), geom.height())
        logger.info("Controller shutdown finished, settings saved.")

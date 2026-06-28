import logging
import keyboard
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger("TypeFlow")

class HotkeyService(QObject):
    # Signals to communicate hotkeys thread-safely to controller
    start_pressed = Signal()
    pause_pressed = Signal()
    resume_pressed = Signal()
    stop_pressed = Signal()

    def __init__(self):
        super().__init__()
        self._start_hook = None
        self._control_hooks = []
        self._is_active = False

    def register_start_hotkey(self) -> None:
        """Registers the F8 global hotkey to start typing."""
        if self._start_hook:
            return
        
        try:
            # Bind F8 globally
            self._start_hook = keyboard.add_hotkey("f8", self._on_start)
            logger.info("Global F8 (Start Typing) hotkey registered.")
        except Exception as e:
            logger.error(f"Failed to register F8 global hotkey: {e}")

    def register_control_hotkeys(self) -> None:
        """Registers F9, F10, and ESC dynamically when countdown/typing starts."""
        if self._control_hooks:
            return
        
        logger.info("Registering dynamic control hotkeys (F9, F10, ESC).")
        try:
            h_pause = keyboard.add_hotkey("f9", self._on_pause)
            h_resume = keyboard.add_hotkey("f10", self._on_resume)
            # Register ESC for emergency stop
            h_stop = keyboard.add_hotkey("esc", self._on_stop)
            
            self._control_hooks = [h_pause, h_resume, h_stop]
            self._is_active = True
        except Exception as e:
            logger.error(f"Failed to register control hotkeys: {e}")

    def unregister_control_hotkeys(self) -> None:
        """Cleans up the F9, F10, and ESC hotkeys to restore normal OS keyboard flow."""
        if not self._control_hooks:
            return
        
        logger.info("Unregistering dynamic control hotkeys.")
        try:
            for hook in self._control_hooks:
                keyboard.remove_hotkey(hook)
            self._control_hooks = []
            self._is_active = False
        except Exception as e:
            logger.error(f"Error removing control hotkeys: {e}")

    def cleanup(self) -> None:
        """Full cleanup on application shutdown."""
        self.unregister_control_hotkeys()
        if self._start_hook:
            try:
                keyboard.remove_hotkey(self._start_hook)
                self._start_hook = None
            except Exception as e:
                logger.error(f"Error removing start hotkey: {e}")
            logger.info("All global hotkeys cleared.")

    # Callbacks emitted thread-safely via Qt Signals
    def _on_start(self) -> None:
        logger.info("Hotkey pressed: F8")
        self.start_pressed.emit()

    def _on_pause(self) -> None:
        logger.info("Hotkey pressed: F9")
        self.pause_pressed.emit()

    def _on_resume(self) -> None:
        logger.info("Hotkey pressed: F10")
        self.resume_pressed.emit()

    def _on_stop(self) -> None:
        logger.info("Hotkey pressed: ESC")
        self.stop_pressed.emit()

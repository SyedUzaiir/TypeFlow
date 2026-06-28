import logging
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QMessageBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCloseEvent

from core.models import TypingSettings, TypingProgress, RecoveryState
from core.enums import TypingState
from ui.widgets.text_editor import TextEditor
from ui.widgets.progress_card import ProgressCard
from ui.widgets.status_bar import StatusBar
from ui.settings_panel import SettingsPanel
from ui.overlays.focus_overlay import FocusOverlay
from utils.constants import DARK_STYLESHEET, LIGHT_STYLESHEET

logger = logging.getLogger("TypeFlow")

class MainWindow(QMainWindow):
    # Signals for controller to bind to
    close_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TypeFlow - Typing Simulator")
        self.init_ui()

    def init_ui(self) -> None:
        # Central widget and layouts
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Left Column (Editor & Progress Card)
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)

        self.editor = TextEditor()
        self.progress_card = ProgressCard()
        
        left_layout.addWidget(self.editor, 3) # Editor takes 3x weight
        left_layout.addWidget(self.progress_card, 1) # Progress card takes 1x weight
        main_layout.addLayout(left_layout, 2) # Left side is 2x wider

        # Right Column (Settings Panel)
        self.settings_panel = SettingsPanel()
        main_layout.addWidget(self.settings_panel, 0) # Fixed size sidebar

        # Status Bar
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

        # Focus overlay (instantiated, centered when needed)
        self.overlay = FocusOverlay()

    def apply_theme(self, theme: str) -> None:
        """Dynamically applies the styling stylesheet based on theme string."""
        if theme == "dark":
            self.setStyleSheet(DARK_STYLESHEET)
            self.settings_panel.set_theme_label("dark")
            logger.info("Theme switched to Dark Mode")
        else:
            self.setStyleSheet(LIGHT_STYLESHEET)
            self.settings_panel.set_theme_label("light")
            logger.info("Theme switched to Light Mode")

    def show_recovery_prompt(self, state: RecoveryState) -> bool:
        """Prompts user if they want to restore an interrupted typing session."""
        text_preview = state.text[:40] + "..." if len(state.text) > 40 else state.text
        msg = (
            f"An interrupted typing session was found.\n\n"
            f"Text: \"{text_preview}\"\n"
            f"Progress: {state.current_index} characters typed.\n\n"
            f"Would you like to recover and resume this session?"
        )
        reply = QMessageBox.question(
            self, "Recover Typing Session?", msg,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        return reply == QMessageBox.Yes

    def show_error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Emits close requested signal so controller can clean up threads, then accepts event."""
        logger.info("Main Window close event triggered")
        self.close_requested.emit()
        self.overlay.close()
        event.accept()

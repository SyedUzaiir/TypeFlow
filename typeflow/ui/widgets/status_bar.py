from PySide6.QtWidgets import QStatusBar, QLabel, QHBoxLayout, QWidget
from PySide6.QtCore import Qt
from core.enums import TypingState

class StatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self) -> None:
        # Left Side Status Widget
        self.status_container = QWidget()
        layout = QHBoxLayout(self.status_container)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(8)

        # Status Light Indicator
        self.indicator = QLabel()
        self.indicator.setFixedSize(10, 10)
        self.update_indicator("#71717a")  # Default gray

        # Status Text Label
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setStyleSheet("font-weight: bold;")

        layout.addWidget(self.indicator)
        layout.addWidget(self.lbl_status)
        layout.addStretch()

        self.addWidget(self.status_container, 1)

        # Right Side Visual Details Widget
        self.lbl_details = QLabel("")
        self.lbl_details.setStyleSheet("font-family: monospace; font-size: 12px; margin-right: 15px;")
        self.addPermanentWidget(self.lbl_details, 0)

    def update_indicator(self, color_hex: str) -> None:
        self.indicator.setStyleSheet(
            f"background-color: {color_hex}; border-radius: 5px; border: 1px solid rgba(255,255,255,0.1);"
        )

    def set_status(self, state: TypingState, current: int = 0, total: int = 0, eta_s: int = 0) -> None:
        """Sets status texts, colors indicators and draws right side status block."""
        if state == TypingState.READY:
            self.lbl_status.setText("Ready")
            self.update_indicator("#3b82f6")  # Blue
            self.lbl_details.setText("")
        elif state == TypingState.COUNTDOWN:
            self.lbl_status.setText("Countdown...")
            self.update_indicator("#f59e0b")  # Amber/Orange
            self.lbl_details.setText("")
        elif state == TypingState.TYPING:
            self.lbl_status.setText("Typing...")
            self.update_indicator("#10b981")  # Emerald Green
            
            # Draw ASCII progress bar
            pct = int((current / total) * 100) if total > 0 else 0
            filled_len = pct // 10
            bar = "█" * filled_len + "░" * (10 - filled_len)
            
            m, s = divmod(eta_s, 60)
            eta_str = f"{m:02d}:{s:02d}"
            
            self.lbl_details.setText(
                f"Typing [{bar}] {current}/{total} ({pct}%)  ETA {eta_str}"
            )
        elif state == TypingState.PAUSED:
            self.lbl_status.setText("Paused")
            self.update_indicator("#8b5cf6")  # Purple
        elif state == TypingState.COMPLETED:
            self.lbl_status.setText("Completed")
            self.update_indicator("#10b981")  # Green
            self.lbl_details.setText("All items finished!")
        elif state == TypingState.CANCELLED:
            self.lbl_status.setText("Cancelled")
            self.update_indicator("#ef4444")  # Red
            self.lbl_details.setText("Typing stopped")

    def show_message_str(self, text: str, color_hex: str = "#71717a") -> None:
        """Helper to show generic message with indicator."""
        self.lbl_status.setText(text)
        self.update_indicator(color_hex)

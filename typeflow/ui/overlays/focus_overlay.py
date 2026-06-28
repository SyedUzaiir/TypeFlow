from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QScreen, QGuiApplication

class FocusOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set flags for frameless window that stays on top, is click-through, and doesn't get focus.
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.WindowTransparentForInput |
            Qt.ToolTip  # ToolTip is a lightweight window type that fits perfectly
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Container for the dialog box
        self.box = QWidget(self)
        # Give it a semi-transparent black background, rounded corners, and padding
        self.box.setStyleSheet("""
            QWidget {
                background-color: rgba(9, 9, 11, 0.85);
                border: 2px solid #6366f1;
                border-radius: 12px;
            }
            QLabel {
                background-color: transparent;
                border: none;
                font-family: 'Segoe UI', Roboto, sans-serif;
            }
        """)
        
        box_layout = QVBoxLayout(self.box)
        box_layout.setContentsMargins(30, 25, 30, 25)
        box_layout.setAlignment(Qt.AlignCenter)

        self.lbl_title = QLabel("Focus your destination window now!")
        self.lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        self.lbl_title.setAlignment(Qt.AlignCenter)

        self.lbl_countdown = QLabel("Starting in: 3")
        self.lbl_countdown.setStyleSheet("font-size: 40px; font-weight: bold; color: #6366f1; margin-top: 10px;")
        self.lbl_countdown.setAlignment(Qt.AlignCenter)

        self.lbl_esc = QLabel("Press ESC to abort immediately")
        self.lbl_esc.setStyleSheet("font-size: 12px; color: #71717a; margin-top: 8px;")
        self.lbl_esc.setAlignment(Qt.AlignCenter)

        box_layout.addWidget(self.lbl_title)
        box_layout.addWidget(self.lbl_countdown)
        box_layout.addWidget(self.lbl_esc)

        layout.addWidget(self.box)

    def show_countdown(self, seconds_remaining: int) -> None:
        """Displays the overlay and centers it on the active screen."""
        self.lbl_countdown.setText(str(seconds_remaining))
        
        # Determine current screen
        screen = QGuiApplication.primaryScreen()
        if screen:
            geom = screen.geometry()
            self.setGeometry(geom)
            
        self.show()

    def set_tick(self, seconds_remaining: int) -> None:
        self.lbl_countdown.setText(str(seconds_remaining))

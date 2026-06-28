from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, QProgressBar
from PySide6.QtCore import Qt
from core.models import TypingProgress

class ProgressCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("progressCard")
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(12)

        # 1. Preview Layout
        preview_container = QWidget()
        preview_layout = QHBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(8)

        self.lbl_prev = QLabel("...")
        self.lbl_prev.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lbl_prev.setStyleSheet("color: #71717a; font-family: monospace; font-size: 13px;")
        
        self.lbl_curr = QLabel("-")
        self.lbl_curr.setObjectName("charPreviewCurrent")
        self.lbl_curr.setAlignment(Qt.AlignCenter)
        self.lbl_curr.setMinimumWidth(35)
        self.lbl_curr.setMinimumHeight(35)
        
        self.lbl_next = QLabel("...")
        self.lbl_next.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.lbl_next.setStyleSheet("color: #71717a; font-family: monospace; font-size: 13px;")

        preview_layout.addWidget(self.lbl_prev, 4)
        preview_layout.addWidget(self.lbl_curr, 1)
        preview_layout.addWidget(self.lbl_next, 4)
        layout.addWidget(preview_container)

        # 2. Stats Grid
        stats_widget = QWidget()
        grid = QGridLayout(stats_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(8)

        # Typed
        lbl_typed_title = QLabel("Typed:")
        lbl_typed_title.setStyleSheet("color: #71717a; font-weight: 500;")
        self.lbl_typed = QLabel("0 / 0")
        self.lbl_typed.setStyleSheet("font-weight: bold;")
        
        # Speed
        lbl_speed_title = QLabel("Speed:")
        lbl_speed_title.setStyleSheet("color: #71717a; font-weight: 500;")
        self.lbl_speed = QLabel("0 CPM")
        self.lbl_speed.setStyleSheet("font-weight: bold;")

        # Elapsed
        lbl_elapsed_title = QLabel("Elapsed:")
        lbl_elapsed_title.setStyleSheet("color: #71717a; font-weight: 500;")
        self.lbl_elapsed = QLabel("00:00")
        self.lbl_elapsed.setStyleSheet("font-weight: bold;")

        # Remaining
        lbl_rem_title = QLabel("ETA:")
        lbl_rem_title.setStyleSheet("color: #71717a; font-weight: 500;")
        self.lbl_remaining = QLabel("00:00")
        self.lbl_remaining.setStyleSheet("font-weight: bold;")

        grid.addWidget(lbl_typed_title, 0, 0)
        grid.addWidget(self.lbl_typed, 0, 1)
        grid.addWidget(lbl_speed_title, 0, 2)
        grid.addWidget(self.lbl_speed, 0, 3)
        grid.addWidget(lbl_elapsed_title, 1, 0)
        grid.addWidget(self.lbl_elapsed, 1, 1)
        grid.addWidget(lbl_rem_title, 1, 2)
        grid.addWidget(self.lbl_remaining, 1, 3)

        layout.addWidget(stats_widget)

        # 3. Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

    def update_progress(self, progress: TypingProgress) -> None:
        """Updates the card visually with progress info."""
        # 1. Stats
        self.lbl_typed.setText(f"{progress.index} / {progress.total}")
        self.lbl_speed.setText(f"{progress.cpm} CPM")
        
        # Format time
        self.lbl_elapsed.setText(self.format_time(progress.elapsed_seconds))
        self.lbl_remaining.setText(self.format_time(progress.eta_seconds))

        # 2. Progress Bar
        pct = int((progress.index / progress.total) * 100) if progress.total > 0 else 0
        self.progress_bar.setValue(pct)

        # 3. Preview
        # Replace spaces with visual space representation so they are visible to the user
        curr_char = progress.current_char
        if curr_char == " ":
            curr_char = "␣"
        elif curr_char == "\n":
            curr_char = "↵"
        elif curr_char == "\t":
            curr_char = "⇥"

        self.lbl_curr.setText(curr_char or "-")
        self.lbl_prev.setText(progress.previous_chars[-15:])
        self.lbl_next.setText(progress.remaining_chars[:15])

    def format_time(self, seconds: int) -> str:
        if seconds < 0:
            return "00:00"
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    def reset(self) -> None:
        self.lbl_curr.setText("-")
        self.lbl_prev.setText("...")
        self.lbl_next.setText("...")
        self.lbl_typed.setText("0 / 0")
        self.lbl_speed.setText("0 CPM")
        self.lbl_elapsed.setText("00:00")
        self.lbl_remaining.setText("00:00")
        self.progress_bar.setValue(0)

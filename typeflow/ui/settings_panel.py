from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QSpinBox, QCheckBox, QPushButton, QListWidget, QFrame, QGroupBox
)
from PySide6.QtCore import Signal, Qt
from core.enums import TypingSpeed, Theme
from core.models import TypingSettings

class SettingsPanel(QFrame):
    # Signals for UI interactions
    start_clicked = Signal()
    stop_clicked = Signal()
    test_clicked = Signal()
    paste_clicked = Signal()
    clear_clicked = Signal()
    theme_toggled = Signal(str)  # "dark" or "light"
    settings_changed = Signal(object) # Emits TypingSettings
    
    # Queue Management Signals
    add_to_queue = Signal()
    clear_queue = Signal()
    remove_queue_item = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarFrame")
        self.setFixedWidth(320)
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Header Title
        title_layout = QHBoxLayout()
        self.lbl_title = QLabel("TypeFlow Panel")
        self.lbl_title.setObjectName("titleLabel")
        self.btn_theme = QPushButton("Dark Mode")
        self.btn_theme.setFixedWidth(100)
        self.btn_theme.clicked.connect(self.on_theme_toggle)
        title_layout.addWidget(self.lbl_title)
        title_layout.addWidget(self.btn_theme)
        layout.addLayout(title_layout)

        # History dropdown
        history_layout = QVBoxLayout()
        lbl_history = QLabel("Recent History:")
        lbl_history.setStyleSheet("font-weight: 500; color: #71717a;")
        self.combo_history = QComboBox()
        self.combo_history.setPlaceholderText("Select recent text...")
        history_layout.addWidget(lbl_history)
        history_layout.addWidget(self.combo_history)
        layout.addLayout(history_layout)

        # Typing Speed Selection Group
        speed_group = QGroupBox("Typing Speed")
        speed_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #27272a; border-radius: 6px; margin-top: 10px; padding-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
        speed_layout = QVBoxLayout(speed_group)
        speed_layout.setSpacing(8)
        
        self.combo_speed = QComboBox()
        self.combo_speed.addItems(["Slow", "Medium", "Fast", "Custom"])
        self.combo_speed.setCurrentText("Medium")
        self.combo_speed.currentTextChanged.connect(self.on_speed_changed)
        speed_layout.addWidget(self.combo_speed)

        custom_delay_layout = QHBoxLayout()
        self.lbl_custom_delay = QLabel("Delay (ms):")
        self.spin_delay = QSpinBox()
        self.spin_delay.setRange(1, 5000)
        self.spin_delay.setValue(50)
        self.spin_delay.setEnabled(False)
        self.spin_delay.valueChanged.connect(self.on_settings_dirty)
        custom_delay_layout.addWidget(self.lbl_custom_delay)
        custom_delay_layout.addWidget(self.spin_delay)
        speed_layout.addLayout(custom_delay_layout)
        layout.addWidget(speed_group)

        # Countdown Selector
        countdown_layout = QHBoxLayout()
        lbl_countdown = QLabel("Countdown Delay:")
        self.combo_countdown = QComboBox()
        self.combo_countdown.addItems(["3 seconds", "5 seconds", "10 seconds"])
        self.combo_countdown.setCurrentText("3 seconds")
        self.combo_countdown.currentIndexChanged.connect(self.on_settings_dirty)
        countdown_layout.addWidget(lbl_countdown)
        countdown_layout.addWidget(self.combo_countdown)
        layout.addLayout(countdown_layout)

        # Checkboxes Settings Group
        options_group = QGroupBox("Typing Options")
        options_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #27272a; border-radius: 6px; margin-top: 10px; padding-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(8)

        self.chk_enter = QCheckBox("Press Enter after typing")
        self.chk_preserve_breaks = QCheckBox("Preserve line breaks")
        self.chk_preserve_breaks.setChecked(True)
        self.chk_punc = QCheckBox("Type punctuation normally")
        self.chk_punc.setChecked(True)
        self.chk_randomize = QCheckBox("Randomize delay (natural)")

        # Bind checkbox changes
        for chk in [self.chk_enter, self.chk_preserve_breaks, self.chk_punc, self.chk_randomize]:
            chk.stateChanged.connect(self.on_settings_dirty)
            options_layout.addWidget(chk)
        
        layout.addWidget(options_group)

        # Queue Management Group
        queue_group = QGroupBox("Queue Mode")
        queue_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #27272a; border-radius: 6px; margin-top: 10px; padding-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
        queue_layout = QVBoxLayout(queue_group)
        queue_layout.setSpacing(6)

        self.list_queue = QListWidget()
        self.list_queue.setFixedHeight(80)
        queue_layout.addWidget(self.list_queue)

        queue_btn_layout = QHBoxLayout()
        self.btn_add_queue = QPushButton("+ Add Text")
        self.btn_add_queue.setStyleSheet("padding: 4px 8px; font-size: 11px;")
        self.btn_add_queue.clicked.connect(self.add_to_queue.emit)
        
        self.btn_del_queue = QPushButton("- Remove")
        self.btn_del_queue.setStyleSheet("padding: 4px 8px; font-size: 11px;")
        self.btn_del_queue.clicked.connect(self.on_remove_queue_item)
        
        self.btn_clear_queue = QPushButton("Clear All")
        self.btn_clear_queue.setStyleSheet("padding: 4px 8px; font-size: 11px;")
        self.btn_clear_queue.clicked.connect(self.clear_queue.emit)

        queue_btn_layout.addWidget(self.btn_add_queue)
        queue_btn_layout.addWidget(self.btn_del_queue)
        queue_btn_layout.addWidget(self.btn_clear_queue)
        queue_layout.addLayout(queue_btn_layout)
        layout.addWidget(queue_group)

        # Helper buttons
        help_btn_layout = QHBoxLayout()
        self.btn_paste = QPushButton("Paste Clipboard")
        self.btn_paste.clicked.connect(self.paste_clicked.emit)
        self.btn_clear = QPushButton("Clear")
        self.btn_clear.clicked.connect(self.clear_clicked.emit)
        help_btn_layout.addWidget(self.btn_paste)
        help_btn_layout.addWidget(self.btn_clear)
        layout.addLayout(help_btn_layout)

        # Action Buttons
        self.btn_start = QPushButton("Start Typing (F8)")
        self.btn_start.setObjectName("startBtn")
        self.btn_start.clicked.connect(self.start_clicked.emit)
        
        self.btn_stop = QPushButton("Stop Typing (ESC)")
        self.btn_stop.setObjectName("stopBtn")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_clicked.emit)

        self.btn_test = QPushButton("Test Typing Speed")
        self.btn_test.clicked.connect(self.test_clicked.emit)

        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.btn_test)

    def on_theme_toggle(self) -> None:
        current_theme = "dark" if self.btn_theme.text() == "Light Mode" else "light"
        self.set_theme_label(current_theme)
        self.theme_toggled.emit(current_theme)

    def set_theme_label(self, theme: str) -> None:
        if theme == "dark":
            self.btn_theme.setText("Light Mode")
        else:
            self.btn_theme.setText("Dark Mode")

    def on_speed_changed(self, text: str) -> None:
        self.spin_delay.setEnabled(text == "Custom")
        self.on_settings_dirty()

    def on_settings_dirty(self) -> None:
        """Collect current settings and emit SettingsChanged signal."""
        settings = self.get_settings()
        self.settings_changed.emit(settings)

    def on_remove_queue_item(self) -> None:
        selected = self.list_queue.currentRow()
        if selected >= 0:
            self.remove_queue_item.emit(selected)

    def get_settings(self) -> TypingSettings:
        countdown_sec = 3
        c_text = self.combo_countdown.currentText()
        if "5" in c_text:
            countdown_sec = 5
        elif "10" in c_text:
            countdown_sec = 10

        theme_val = "dark" if self.btn_theme.text() == "Light Mode" else "light"

        return TypingSettings(
            delay_speed=self.combo_speed.currentText(),
            custom_delay_ms=self.spin_delay.value(),
            countdown_seconds=countdown_sec,
            press_enter=self.chk_enter.isChecked(),
            preserve_breaks=self.chk_preserve_breaks.isChecked(),
            type_punctuation=self.chk_punc.isChecked(),
            randomize_delay=self.chk_randomize.isChecked(),
            theme=theme_val
        )

    def apply_settings(self, settings: TypingSettings) -> None:
        """Populates UI controls with the settings provided."""
        # Block signals to prevent dirty cycles
        self.blockSignals(True)
        
        self.combo_speed.setCurrentText(settings.delay_speed)
        self.spin_delay.setValue(settings.custom_delay_ms)
        self.spin_delay.setEnabled(settings.delay_speed == "Custom")
        
        if settings.countdown_seconds == 5:
            self.combo_countdown.setCurrentText("5 seconds")
        elif settings.countdown_seconds == 10:
            self.combo_countdown.setCurrentText("10 seconds")
        else:
            self.combo_countdown.setCurrentText("3 seconds")

        self.chk_enter.setChecked(settings.press_enter)
        self.chk_preserve_breaks.setChecked(settings.preserve_breaks)
        self.chk_punc.setChecked(settings.type_punctuation)
        self.chk_randomize.setChecked(settings.randomize_delay)
        
        self.set_theme_label(settings.theme)
        
        self.blockSignals(False)

    def update_queue_list(self, items: list[str]) -> None:
        self.list_queue.clear()
        for idx, text in enumerate(items):
            # Show a brief preview of text
            preview = text.strip().replace("\n", " ")[:25]
            if len(text) > 25:
                preview += "..."
            self.list_queue.addItem(f"{idx+1}. {preview}")

    def update_history_combobox(self, history: list[str]) -> None:
        self.combo_history.blockSignals(True)
        self.combo_history.clear()
        self.combo_history.addItems([h.replace("\n", " ")[:35] for h in history])
        self.combo_history.blockSignals(False)

    def set_typing_active(self, active: bool) -> None:
        """Disables controls while typing is active for protection."""
        self.combo_speed.setEnabled(not active)
        self.spin_delay.setEnabled(not active and self.combo_speed.currentText() == "Custom")
        self.combo_countdown.setEnabled(not active)
        self.chk_enter.setEnabled(not active)
        self.chk_preserve_breaks.setEnabled(not active)
        self.chk_punc.setEnabled(not active)
        self.chk_randomize.setEnabled(not active)
        self.btn_add_queue.setEnabled(not active)
        self.btn_del_queue.setEnabled(not active)
        self.btn_clear_queue.setEnabled(not active)
        self.btn_paste.setEnabled(not active)
        self.btn_clear.setEnabled(not active)
        self.btn_test.setEnabled(not active)
        self.combo_history.setEnabled(not active)

        self.btn_start.setEnabled(not active)
        self.btn_stop.setEnabled(active)

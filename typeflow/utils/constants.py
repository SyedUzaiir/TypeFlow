import os

# Application Info
APP_NAME = "TypeFlow"
CONFIG_VERSION = 1

# Speed Constants
DEFAULT_SPEEDS = {
    "Slow": 100,      # ms
    "Medium": 50,     # ms
    "Fast": 10,       # ms
}

# Test Typing Text
TEST_TYPING_TEXT = "The quick brown fox jumps over the lazy dog."

# Styling Sheets
DARK_STYLESHEET = """
QMainWindow {
    background-color: #121214;
}

QWidget {
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
    color: #e4e4e7;
}

/* Sidebar and Cards */
QFrame#sidebarFrame, QFrame#progressCard, QFrame#editorWrapper {
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 8px;
}

/* Text Editor */
QPlainTextEdit {
    background-color: #09090b;
    border: 1px solid #27272a;
    border-radius: 6px;
    padding: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 14px;
    color: #f4f4f5;
    selection-background-color: #4f46e5;
    selection-color: #ffffff;
}

QPlainTextEdit:focus {
    border: 1px solid #6366f1;
}

/* Input elements */
QComboBox, QSpinBox {
    background-color: #27272a;
    border: 1px solid #3f3f46;
    border-radius: 4px;
    padding: 5px 10px;
    color: #f4f4f5;
    min-height: 20px;
}

QComboBox:on, QSpinBox:focus {
    border: 1px solid #6366f1;
}

QComboBox::drop-down {
    border: none;
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
}

/* Buttons */
QPushButton {
    background-color: #27272a;
    border: 1px solid #3f3f46;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    color: #f4f4f5;
}

QPushButton:hover {
    background-color: #3f3f46;
    border-color: #52525b;
}

QPushButton:pressed {
    background-color: #18181b;
}

QPushButton#startBtn {
    background-color: #4f46e5;
    border: 1px solid #6366f1;
    color: #ffffff;
}

QPushButton#startBtn:hover {
    background-color: #4338ca;
}

QPushButton#startBtn:disabled {
    background-color: #1d1d35;
    border-color: #2e2e4f;
    color: #71717a;
}

QPushButton#stopBtn {
    background-color: #dc2626;
    border: 1px solid #ef4444;
    color: #ffffff;
}

QPushButton#stopBtn:hover {
    background-color: #b91c1c;
}

QPushButton#stopBtn:disabled {
    background-color: #3f1f1f;
    border-color: #5f2f2f;
    color: #71717a;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #3f3f46;
    border-radius: 4px;
    background-color: #18181b;
}

QCheckBox::indicator:unchecked:hover {
    border-color: #6366f1;
}

QCheckBox::indicator:checked {
    background-color: #4f46e5;
    border-color: #6366f1;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background-color: #18181b;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #3f3f46;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #52525b;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Labels */
QLabel {
    color: #d4d4d8;
}

QLabel#titleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #ffffff;
}

QLabel#charPreviewCurrent {
    font-size: 24px;
    font-weight: bold;
    color: #10b981;
    background-color: #064e3b;
    padding: 5px 12px;
    border-radius: 4px;
    border: 1px solid #059669;
}

/* Progress Bar */
QProgressBar {
    background-color: #27272a;
    border: 1px solid #3f3f46;
    border-radius: 4px;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #4f46e5;
    border-radius: 3px;
}

/* Status Bar */
QStatusBar {
    background-color: #09090b;
    border-top: 1px solid #27272a;
    min-height: 25px;
}

QStatusBar::item {
    border: none;
}

/* List Widget for Queue */
QListWidget {
    background-color: #09090b;
    border: 1px solid #27272a;
    border-radius: 6px;
    padding: 4px;
    color: #e4e4e7;
}

QListWidget::item {
    padding: 6px;
    border-bottom: 1px solid #18181b;
    border-radius: 4px;
}

QListWidget::item:selected {
    background-color: #4f46e5;
    color: #ffffff;
}

QListWidget::item:hover {
    background-color: #27272a;
}
"""

LIGHT_STYLESHEET = """
QMainWindow {
    background-color: #f4f4f5;
}

QWidget {
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
    color: #18181b;
}

/* Sidebar and Cards */
QFrame#sidebarFrame, QFrame#progressCard, QFrame#editorWrapper {
    background-color: #ffffff;
    border: 1px solid #e4e4e7;
    border-radius: 8px;
}

/* Text Editor */
QPlainTextEdit {
    background-color: #fafafa;
    border: 1px solid #e4e4e7;
    border-radius: 6px;
    padding: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 14px;
    color: #18181b;
    selection-background-color: #a5b4fc;
    selection-color: #1e1b4b;
}

QPlainTextEdit:focus {
    border: 1px solid #4f46e5;
}

/* Input elements */
QComboBox, QSpinBox {
    background-color: #ffffff;
    border: 1px solid #d4d4d8;
    border-radius: 4px;
    padding: 5px 10px;
    color: #18181b;
    min-height: 20px;
}

QComboBox:on, QSpinBox:focus {
    border: 1px solid #4f46e5;
}

QComboBox::drop-down {
    border: none;
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
}

/* Buttons */
QPushButton {
    background-color: #ffffff;
    border: 1px solid #d4d4d8;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    color: #18181b;
}

QPushButton:hover {
    background-color: #f4f4f5;
    border-color: #a1a1aa;
}

QPushButton:pressed {
    background-color: #e4e4e7;
}

QPushButton#startBtn {
    background-color: #4f46e5;
    border: 1px solid #4f46e5;
    color: #ffffff;
}

QPushButton#startBtn:hover {
    background-color: #4338ca;
}

QPushButton#startBtn:disabled {
    background-color: #e0e7ff;
    border-color: #c7d2fe;
    color: #9aa5b1;
}

QPushButton#stopBtn {
    background-color: #ef4444;
    border: 1px solid #ef4444;
    color: #ffffff;
}

QPushButton#stopBtn:hover {
    background-color: #dc2626;
}

QPushButton#stopBtn:disabled {
    background-color: #fee2e2;
    border-color: #fca5a5;
    color: #f87171;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #d4d4d8;
    border-radius: 4px;
    background-color: #ffffff;
}

QCheckBox::indicator:unchecked:hover {
    border-color: #4f46e5;
}

QCheckBox::indicator:checked {
    background-color: #4f46e5;
    border-color: #4f46e5;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background-color: #f4f4f5;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #d4d4d8;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #a1a1aa;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Labels */
QLabel {
    color: #4b5563;
}

QLabel#titleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #111827;
}

QLabel#charPreviewCurrent {
    font-size: 24px;
    font-weight: bold;
    color: #047857;
    background-color: #d1fae5;
    padding: 5px 12px;
    border-radius: 4px;
    border: 1px solid #34d399;
}

/* Progress Bar */
QProgressBar {
    background-color: #e4e4e7;
    border: 1px solid #d4d4d8;
    border-radius: 4px;
    text-align: center;
    color: #18181b;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #4f46e5;
    border-radius: 3px;
}

/* Status Bar */
QStatusBar {
    background-color: #ffffff;
    border-top: 1px solid #e4e4e7;
    min-height: 25px;
}

QStatusBar::item {
    border: none;
}

/* List Widget for Queue */
QListWidget {
    background-color: #ffffff;
    border: 1px solid #e4e4e7;
    border-radius: 6px;
    padding: 4px;
    color: #18181b;
}

QListWidget::item {
    padding: 6px;
    border-bottom: 1px solid #f4f4f5;
    border-radius: 4px;
}

QListWidget::item:selected {
    background-color: #4f46e5;
    color: #ffffff;
}

QListWidget::item:hover {
    background-color: #f4f4f5;
}
"""

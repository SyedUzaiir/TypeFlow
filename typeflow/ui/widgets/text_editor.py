from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Signal, Qt

class TextEditor(QWidget):
    text_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Main wrapper frame for borders
        self.wrapper = QFrame()
        self.wrapper.setObjectName("editorWrapper")
        wrapper_layout = QVBoxLayout(self.wrapper)
        wrapper_layout.setContentsMargins(1, 1, 1, 1)

        # Plain Text Edit
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Paste or type your text here...")
        self.editor.setFrameStyle(QFrame.NoFrame)
        self.editor.textChanged.connect(self.on_text_changed)
        wrapper_layout.addWidget(self.editor)
        layout.addWidget(self.wrapper)

        # Metrics Bar
        self.metrics_layout = QHBoxLayout()
        self.metrics_layout.setContentsMargins(5, 2, 5, 2)
        
        self.lbl_lines = QLabel("Lines: 0")
        self.lbl_chars = QLabel("Characters: 0")
        
        self.metrics_layout.addWidget(self.lbl_lines)
        self.metrics_layout.addSpacing(15)
        self.metrics_layout.addWidget(self.lbl_chars)
        self.metrics_layout.addStretch()
        
        layout.addLayout(self.metrics_layout)

    def on_text_changed(self) -> None:
        text = self.editor.toPlainText()
        char_count = len(text)
        # Count lines by split (ensure at least 1 if text not empty)
        line_count = len(text.splitlines()) if text else 0
        
        self.lbl_lines.setText(f"Lines: {line_count}")
        self.lbl_chars.setText(f"Characters: {char_count}")
        
        self.text_changed.emit(text)

    def get_text(self) -> str:
        return self.editor.toPlainText()

    def set_text(self, text: str) -> None:
        self.editor.setPlainText(text)
        self.on_text_changed()

    def clear(self) -> None:
        self.editor.clear()
        self.on_text_changed()

    def set_read_only(self, read_only: bool) -> None:
        self.editor.setReadOnly(read_only)

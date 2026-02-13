"""Keyboard shortcuts reference dialog (Ctrl+/)."""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QGridLayout
from PyQt6.QtCore import Qt

from config.settings import get_colors


SHORTCUTS = [
    ("Ctrl + /", "Show this dialog"),
    ("Ctrl + Q", "Quit application"),
    ("Tab", "Move to next control"),
    ("Shift + Tab", "Move to previous control"),
    ("Enter", "Submit / activate"),
    ("Escape", "Close dialog / cancel"),
]


class ShortcutsDialog(QDialog):
    """Reference dialog listing keyboard shortcuts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.setMinimumWidth(400)
        self.setAccessibleName("Keyboard Shortcuts Reference")
        c = get_colors()
        self.setStyleSheet(f"QDialog {{ background-color: {c['dark_card']}; }}")

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Keyboard Shortcuts")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {c['primary_text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setAccessibleName("Keyboard Shortcuts")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(8)
        for row, (key, desc) in enumerate(SHORTCUTS):
            k = QLabel(key)
            k.setStyleSheet(f"""
                background-color: {c['dark_input']}; color: {c['text']};
                padding: 4px 10px; border-radius: 4px; font-weight: bold;
            """)
            k.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(k, row, 0)

            d = QLabel(desc)
            d.setStyleSheet(f"color: {c['text']}; padding-left: 8px;")
            grid.addWidget(d, row, 1)

        layout.addLayout(grid)

        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close shortcuts dialog")
        close_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        close_btn.setFixedHeight(44)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

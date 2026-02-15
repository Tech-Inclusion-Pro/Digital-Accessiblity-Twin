"""Dialog for editing a profile item's text and priority."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit, QComboBox,
    QHBoxLayout, QPushButton,
)
from PyQt6.QtCore import Qt

from config.settings import get_colors

PRIORITY_CHOICES = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("non-negotiable", "Non-Negotiable"),
]


class EditItemDialog(QDialog):
    """Small dialog for editing an item's text and priority level.

    Use ``get_result()`` after ``exec()`` returns ``Accepted`` to retrieve
    the ``(text, priority)`` tuple.
    """

    def __init__(self, text: str = "", priority: str = "medium", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Item")
        self.setMinimumWidth(400)
        self._result = None
        self._build_ui(text, priority)

    def _build_ui(self, text: str, priority: str):
        c = get_colors()
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Text input
        text_label = QLabel("Item text:")
        text_label.setStyleSheet(f"font-size: 13px; color: {c['text']};")
        layout.addWidget(text_label)

        self._text_edit = QTextEdit()
        self._text_edit.setPlainText(text)
        self._text_edit.setAccessibleName("Item text")
        self._text_edit.setFixedHeight(90)
        layout.addWidget(self._text_edit)

        # Priority combo
        priority_label = QLabel("Priority:")
        priority_label.setStyleSheet(f"font-size: 13px; color: {c['text']};")
        layout.addWidget(priority_label)

        self._priority_combo = QComboBox()
        self._priority_combo.setAccessibleName("Priority level")
        for value, display in PRIORITY_CHOICES:
            self._priority_combo.addItem(display, value)
        # Select current priority
        for i, (value, _) in enumerate(PRIORITY_CHOICES):
            if value == priority:
                self._priority_combo.setCurrentIndex(i)
                break
        layout.addWidget(self._priority_combo)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setAccessibleName("Cancel editing")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setAccessibleName("Save changes")
        save_btn.setFixedHeight(40)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['primary']}; color: white;
                border: none; border-radius: 8px; padding: 0 20px;
                font-weight: bold;
            }}
        """)
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)

    def _on_save(self):
        text = self._text_edit.toPlainText().strip()
        if not text:
            return
        priority = self._priority_combo.currentData()
        self._result = (text, priority)
        self.accept()

    def get_result(self):
        """Return ``(text, priority)`` or ``None`` if cancelled."""
        return self._result

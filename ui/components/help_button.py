"""Persistent contextual help button."""

from PyQt6.QtWidgets import QPushButton, QMessageBox
from PyQt6.QtCore import Qt

from config.settings import get_colors


class HelpButton(QPushButton):
    """Floating '?' button for contextual help (stub — content in Phase 2)."""

    def __init__(self, context: str = "general", parent=None):
        super().__init__("?", parent)
        self._context = context
        c = get_colors()
        self.setFixedSize(44, 44)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName("Help")
        self.setAccessibleDescription(f"Open help for {context}")
        self.setToolTip("Help")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['dark_input']};
                color: {c['text']};
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 22px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {c['primary']};
            }}
        """)
        self.clicked.connect(self._show_help)

    def _show_help(self):
        QMessageBox.information(
            self.window(),
            "Help",
            f"Help content for '{self._context}' will be available in Phase 2.",
        )

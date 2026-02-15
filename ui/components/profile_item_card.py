"""Card widget for a single profile item (strength, history, goal, stakeholder)."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

from config.settings import get_colors

PRIORITY_STYLES = {
    "low": {"label": "Low", "bg": "#6c757d"},
    "medium": {"label": "Medium", "bg": "#2563eb"},
    "high": {"label": "High", "bg": "#ea580c"},
    "non-negotiable": {"label": "Non-Negotiable", "bg": "#dc2626"},
}


class ProfileItemCard(QWidget):
    """Card showing an item's text, priority badge, and Edit / Remove buttons."""

    edit_requested = pyqtSignal(int)
    remove_requested = pyqtSignal(int)

    def __init__(self, index: int, text: str, priority: str, parent=None):
        super().__init__(parent)
        self._index = index
        self._build_ui(text, priority)

    def _build_ui(self, text: str, priority: str):
        c = get_colors()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        # Priority badge
        ps = PRIORITY_STYLES.get(priority, PRIORITY_STYLES["medium"])
        badge = QLabel(ps["label"])
        badge.setStyleSheet(f"""
            font-size: 11px; color: white; background: {ps['bg']};
            border-radius: 8px; padding: 2px 10px; font-weight: bold;
        """)
        badge.setFixedHeight(22)
        badge.setAccessibleName(f"Priority: {ps['label']}")
        layout.addWidget(badge)

        # Item text
        text_label = QLabel(text)
        text_label.setStyleSheet(f"font-size: 13px; color: {c['text']};")
        text_label.setWordWrap(True)
        text_label.setAccessibleName(text)
        layout.addWidget(text_label, stretch=1)

        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setAccessibleName(f"Edit item: {text[:40]}")
        edit_btn.setMinimumHeight(44)
        edit_btn.setFixedWidth(60)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['secondary']}; color: white;
                border: none; border-radius: 6px; font-size: 12px;
            }}
            QPushButton:hover {{ background: {c['primary']}; }}
        """)
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self._index))
        layout.addWidget(edit_btn)

        # Remove button
        rm_btn = QPushButton("Remove")
        rm_btn.setAccessibleName(f"Remove item: {text[:40]}")
        rm_btn.setMinimumHeight(44)
        rm_btn.setFixedWidth(72)
        rm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rm_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        rm_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d; color: white;
                border: none; border-radius: 6px; font-size: 12px;
            }
            QPushButton:hover { background: #dc2626; }
        """)
        rm_btn.clicked.connect(lambda: self.remove_requested.emit(self._index))
        layout.addWidget(rm_btn)

        self.setStyleSheet(f"""
            ProfileItemCard {{
                background: {c['dark_card']};
                border: 1px solid {c['dark_border']};
                border-radius: 10px;
            }}
        """)
        self.setAccessibleName(f"{ps['label']} priority item: {text}")

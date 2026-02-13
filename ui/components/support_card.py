"""Card widget displaying a SupportEntry."""

import json

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

from config.settings import get_colors

CATEGORY_ICONS = {
    "technology": "\U0001F4BB",
    "physical": "\u267F",
    "sensory": "\U0001F441",
    "communication": "\U0001F4AC",
    "social": "\U0001F465",
    "academic": "\U0001F4DA",
    "behavioral": "\U0001F9E0",
    "other": "\u2699",
}


class SupportCard(QWidget):
    """Card showing a SupportEntry with category icon, description, status, tags."""

    def __init__(self, support_entry, parent=None):
        """
        Args:
            support_entry: SupportEntry ORM object
        """
        super().__init__(parent)
        self._entry = support_entry
        self._build_ui()

    def _build_ui(self):
        c = get_colors()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        # Header row: icon + category + status badge
        header = QHBoxLayout()
        cat = self._entry.category or "other"
        icon = CATEGORY_ICONS.get(cat.lower(), "\u2699")

        cat_label = QLabel(f"{icon} {cat.title()}")
        cat_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {c['text']};")
        header.addWidget(cat_label)

        header.addStretch()

        status = self._entry.status or "active"
        status_color = c["success"] if status == "active" else c["text_muted"]
        badge = QLabel(status.title())
        badge.setStyleSheet(f"""
            font-size: 11px; color: white; background: {status_color};
            border-radius: 8px; padding: 2px 8px;
        """)
        badge.setFixedHeight(20)
        header.addWidget(badge)
        layout.addLayout(header)

        # Description
        desc = QLabel(self._entry.description or "")
        desc.setStyleSheet(f"font-size: 13px; color: {c['text_muted']};")
        desc.setWordWrap(True)
        desc.setMaximumHeight(40)
        layout.addWidget(desc)

        # Tags row: UDL + POUR
        tags_row = QHBoxLayout()
        tags_row.setSpacing(4)

        udl = json.loads(self._entry.udl_mapping or "{}")
        pour = json.loads(self._entry.pour_mapping or "{}")

        for key in udl:
            tag = self._make_tag(key, c["primary"])
            tags_row.addWidget(tag)
        for key in pour:
            tag = self._make_tag(key, c["secondary"])
            tags_row.addWidget(tag)

        tags_row.addStretch()

        # Effectiveness
        if self._entry.effectiveness_rating is not None:
            rating = QLabel(f"\u2605 {self._entry.effectiveness_rating:.1f}")
            rating.setStyleSheet(f"font-size: 12px; color: {c['warning']};")
            tags_row.addWidget(rating)

        layout.addLayout(tags_row)

        self.setStyleSheet(f"""
            SupportCard {{
                background: {c['dark_card']};
                border: 1px solid {c['dark_border']};
                border-radius: 10px;
            }}
        """)
        self.setFixedHeight(120)
        self.setAccessibleName(
            f"{cat.title()} support: {self._entry.description or ''}"
        )

    @staticmethod
    def _make_tag(text: str, color: str) -> QLabel:
        tag = QLabel(text)
        tag.setStyleSheet(f"""
            font-size: 10px; color: white; background: {color};
            border-radius: 6px; padding: 1px 6px;
        """)
        tag.setFixedHeight(16)
        return tag

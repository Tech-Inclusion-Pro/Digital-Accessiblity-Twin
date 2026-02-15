"""Metric card widget for dashboard stats."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

from config.settings import get_colors


class StatCard(QWidget):
    """Compact metric card showing icon, value, and label."""

    def __init__(self, icon: str, value: str, label: str, parent=None):
        super().__init__(parent)
        self._icon = icon
        self._value = value
        self._label = label
        self._build_ui()

    def _build_ui(self):
        c = get_colors()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_lbl = QLabel(self._icon)
        icon_lbl.setStyleSheet(f"font-size: 28px; color: {c['primary_text']};")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setAccessibleName("")  # decorative icon, skip for screen readers
        layout.addWidget(icon_lbl)

        val_lbl = QLabel(self._value)
        val_lbl.setObjectName("stat_value")
        val_lbl.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {c['text']};")
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(val_lbl)

        label_lbl = QLabel(self._label)
        label_lbl.setStyleSheet(f"font-size: 12px; color: {c['text_muted']};")
        label_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_lbl.setWordWrap(True)
        layout.addWidget(label_lbl)

        self.setAccessibleName(f"{self._label}: {self._value}")

        self.setStyleSheet(f"""
            StatCard {{
                background: {c['dark_card']};
                border: 1px solid {c['dark_border']};
                border-radius: 12px;
            }}
        """)
        self.setMinimumWidth(140)
        self.setFixedHeight(120)

    def set_value(self, value: str):
        self._value = value
        val_lbl = self.findChild(QLabel, "stat_value")
        if val_lbl:
            val_lbl.setText(value)
        self.setAccessibleName(f"{self._label}: {value}")

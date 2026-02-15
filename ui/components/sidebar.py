"""Reusable sidebar navigation component."""

import os
import sys

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap

from config.settings import get_colors
from config.brand import ROLE_ACCENTS


def _get_asset_path(filename: str) -> str:
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, "assets", filename)


class Sidebar(QWidget):
    """Left sidebar with logo, nav buttons, and logout."""

    nav_clicked = pyqtSignal(str)  # emits item key
    logout_requested = pyqtSignal()
    settings_requested = pyqtSignal()

    def __init__(self, role: str, items: list[dict], parent=None):
        """
        Args:
            role: 'student' or 'teacher'
            items: list of dicts with keys: 'key', 'icon', 'label'
        """
        super().__init__(parent)
        self.role = role
        self.items = items
        self._buttons: dict[str, QPushButton] = {}
        self._active_key: str = items[0]["key"] if items else ""
        self.setFixedWidth(220)
        self._build_ui()

    def _build_ui(self):
        c = get_colors()
        accent = ROLE_ACCENTS.get(self.role, ROLE_ACCENTS["student"])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(4)

        # Logo row
        logo_row = QHBoxLayout()
        logo_row.setSpacing(8)

        logo_label = QLabel()
        logo_path = _get_asset_path("logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled = pixmap.scaled(
                32, 32,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_label.setPixmap(scaled)
        logo_label.setFixedSize(32, 32)
        logo_label.setAccessibleName("AccessTwin logo")
        logo_row.addWidget(logo_label)

        app_name = QLabel("AccessTwin")
        app_name.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {c['primary_text']};"
        )
        app_name.setAccessibleName("AccessTwin")
        logo_row.addWidget(app_name)
        logo_row.addStretch()
        layout.addLayout(logo_row)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {c['dark_border']};")
        layout.addWidget(sep)
        layout.addSpacing(8)

        # Nav buttons
        for item in self.items:
            btn = QPushButton(f"  {item['icon']}  {item['label']}")
            btn.setAccessibleName(item["label"])
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(44)
            btn.setProperty("nav_key", item["key"])
            btn.clicked.connect(lambda checked, k=item["key"]: self._on_nav(k))
            self._buttons[item["key"]] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # Settings button
        settings_btn = QPushButton("  \u229E  Settings")
        settings_btn.setAccessibleName("Settings")
        settings_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.setFixedHeight(44)
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none; border-radius: 8px;
                color: {c['text_muted']}; text-align: left; padding-left: 12px;
                font-size: 14px;
            }}
            QPushButton:hover {{ background: {c['dark_hover']}; color: {c['text']}; }}
        """)
        settings_btn.clicked.connect(self.settings_requested.emit)
        layout.addWidget(settings_btn)

        # Logout button
        logout_btn = QPushButton("  \u2190  Logout")
        logout_btn.setAccessibleName("Logout")
        logout_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setFixedHeight(44)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none; border-radius: 8px;
                color: {c['error']}; text-align: left; padding-left: 12px;
                font-size: 14px;
            }}
            QPushButton:hover {{ background: {c['dark_hover']}; }}
        """)
        logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout_btn)

        # Apply base sidebar style
        self.setStyleSheet(f"""
            Sidebar {{
                background: {c['dark_card']};
                border-right: 1px solid {c['dark_border']};
            }}
        """)

        self._update_button_styles()

    def _on_nav(self, key: str):
        if key == self._active_key:
            return
        self._active_key = key
        self._update_button_styles()
        self.nav_clicked.emit(key)

    def set_active(self, key: str):
        self._active_key = key
        self._update_button_styles()

    def _update_button_styles(self):
        c = get_colors()
        accent = ROLE_ACCENTS.get(self.role, ROLE_ACCENTS["student"])

        for key, btn in self._buttons.items():
            if key == self._active_key:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {c['dark_hover']};
                        border: none; border-left: 3px solid {accent['accent']};
                        border-radius: 0px 8px 8px 0px;
                        color: {c['text']}; text-align: left; padding-left: 12px;
                        font-size: 14px; font-weight: bold;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent; border: none; border-radius: 8px;
                        color: {c['text_muted']}; text-align: left; padding-left: 12px;
                        font-size: 14px;
                    }}
                    QPushButton:hover {{ background: {c['dark_hover']}; color: {c['text']}; }}
                """)

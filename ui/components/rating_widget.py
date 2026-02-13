"""1-5 clickable circle rating input."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal

from config.settings import get_colors


class RatingWidget(QWidget):
    """Clickable 1-5 circle rating input."""

    rating_changed = pyqtSignal(int)  # 1-5

    def __init__(self, label: str = "Rating:", parent=None):
        super().__init__(parent)
        self._rating = 0
        self._buttons: list[QPushButton] = []
        self._build_ui(label)

    def _build_ui(self, label: str):
        c = get_colors()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size: 14px; color: {c['text']};")
        layout.addWidget(lbl)

        for i in range(1, 6):
            btn = QPushButton(str(i))
            btn.setFixedSize(36, 36)
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setAccessibleName(f"Rate {i} out of 5")
            btn.clicked.connect(lambda checked, v=i: self._set_rating(v))
            self._buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()
        self._update_styles()
        self.setAccessibleName(f"{label} 0 out of 5")

    def _set_rating(self, value: int):
        self._rating = value
        self._update_styles()
        self.setAccessibleName(f"Rating: {value} out of 5")
        self.rating_changed.emit(value)

    def _update_styles(self):
        c = get_colors()
        for i, btn in enumerate(self._buttons):
            val = i + 1
            if val <= self._rating:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {c['primary']};
                        color: white; border: none; border-radius: 18px;
                        font-weight: bold; font-size: 14px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {c['dark_input']};
                        color: {c['text_muted']}; border: 1px solid {c['dark_border']};
                        border-radius: 18px; font-size: 14px;
                    }}
                    QPushButton:hover {{ background: {c['dark_hover']}; }}
                """)

    def get_rating(self) -> int:
        return self._rating

    def reset(self):
        self._rating = 0
        self._update_styles()

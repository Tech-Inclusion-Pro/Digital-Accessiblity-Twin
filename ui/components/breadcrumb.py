"""Navigation breadcrumb trail widget."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

from config.settings import get_colors


class Breadcrumb(QWidget):
    """Breadcrumb trail showing navigation path."""

    crumb_clicked = pyqtSignal(int)  # index of clicked crumb

    def __init__(self, parent=None):
        super().__init__(parent)
        self._crumbs: list[str] = []
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(4)
        self._layout.addStretch()
        self.setAccessibleName("Breadcrumb navigation")

    def set_crumbs(self, crumbs: list[str]):
        """Replace the breadcrumb trail."""
        self._crumbs = crumbs
        # Clear existing widgets (except trailing stretch)
        while self._layout.count() > 1:
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        c = get_colors()
        for i, text in enumerate(crumbs):
            if i > 0:
                sep = QLabel(">")
                sep.setStyleSheet(f"color: {c['text_muted']}; font-size: 12px;")
                self._layout.insertWidget(self._layout.count() - 1, sep)

            if i < len(crumbs) - 1:
                btn = QPushButton(text)
                btn.setAccessibleName(f"Navigate to {text}")
                btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent; border: none;
                        color: {c['primary_text']}; font-size: 12px;
                        text-decoration: underline; padding: 2px 4px;
                        min-height: 0; min-width: 0;
                    }}
                    QPushButton:hover {{ color: {c['text']}; }}
                """)
                idx = i
                btn.clicked.connect(lambda checked, x=idx: self.crumb_clicked.emit(x))
                self._layout.insertWidget(self._layout.count() - 1, btn)
            else:
                lbl = QLabel(text)
                lbl.setStyleSheet(f"color: {c['text']}; font-size: 12px; font-weight: bold;")
                self._layout.insertWidget(self._layout.count() - 1, lbl)

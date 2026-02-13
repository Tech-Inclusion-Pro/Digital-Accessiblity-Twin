"""Empty state placeholder widget."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

from config.settings import get_colors


class EmptyState(QWidget):
    """Placeholder shown when no data is available (icon + message + action)."""

    action_clicked = pyqtSignal()

    def __init__(self, icon_text: str = "", message: str = "",
                 action_label: str = "", parent=None):
        super().__init__(parent)
        c = get_colors()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        if icon_text:
            icon = QLabel(icon_text)
            icon.setStyleSheet(f"font-size: 48px; color: {c['text_muted']};")
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(icon)

        msg = QLabel(message)
        msg.setStyleSheet(f"font-size: 16px; color: {c['text_muted']};")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        msg.setAccessibleName(message)
        layout.addWidget(msg)

        if action_label:
            btn = QPushButton(action_label)
            btn.setAccessibleName(action_label)
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setFixedHeight(44)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 {c['primary']}, stop:1 {c['tertiary']});
                    color: white; border: none; border-radius: 8px;
                    padding: 8px 24px; font-weight: bold;
                }}
            """)
            btn.clicked.connect(self.action_clicked.emit)
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

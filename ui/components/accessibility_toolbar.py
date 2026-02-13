"""Quick-access accessibility toolbar — opens full settings panel."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt

from config.settings import get_colors
from ui.accessibility import AccessibilityManager


class AccessibilityToolbar(QWidget):
    """Compact toolbar with a single Settings button that opens all accessibility options."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.a11y = AccessibilityManager.instance()
        self.setAccessibleName("Accessibility toolbar")
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)
        layout.addStretch()

        self.settings_btn = QPushButton("Accessibility Settings")
        self.settings_btn.setAccessibleName("Open accessibility settings")
        self.settings_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.settings_btn.setMinimumHeight(36)
        self.settings_btn.setToolTip("Open accessibility settings (all options)")
        self.settings_btn.clicked.connect(self._open_full_settings)
        layout.addWidget(self.settings_btn)

    def _open_full_settings(self):
        from ui.components.accessibility_panel import AccessibilityPanel
        dlg = AccessibilityPanel(self.window())
        dlg.exec()

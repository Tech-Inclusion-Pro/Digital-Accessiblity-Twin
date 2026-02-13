"""Quick-access accessibility toolbar."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QComboBox
from PyQt6.QtCore import Qt

from config.settings import get_colors
from ui.accessibility import AccessibilityManager


class AccessibilityToolbar(QWidget):
    """Compact toolbar with font size +/-, theme toggle, color mode, and full settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.a11y = AccessibilityManager.instance()
        self.setAccessibleName("Accessibility quick toolbar")
        self._build_ui()

    def _build_ui(self):
        c = get_colors()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        # Font size decrease
        self.font_down = QPushButton("A-")
        self.font_down.setAccessibleName("Decrease font size")
        self.font_down.setAccessibleDescription("Make text smaller")
        self.font_down.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.font_down.setFixedSize(44, 36)
        self.font_down.setToolTip("Decrease font size")
        self.font_down.clicked.connect(self._decrease_font)
        layout.addWidget(self.font_down)

        # Font size increase
        self.font_up = QPushButton("A+")
        self.font_up.setAccessibleName("Increase font size")
        self.font_up.setAccessibleDescription("Make text larger")
        self.font_up.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.font_up.setFixedSize(44, 36)
        self.font_up.setToolTip("Increase font size")
        self.font_up.clicked.connect(self._increase_font)
        layout.addWidget(self.font_up)

        # High contrast toggle
        self.contrast_btn = QPushButton("HC")
        self.contrast_btn.setAccessibleName("Toggle high contrast")
        self.contrast_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.contrast_btn.setFixedSize(44, 36)
        self.contrast_btn.setCheckable(True)
        self.contrast_btn.setChecked(self.a11y.high_contrast)
        self.contrast_btn.setToolTip("Toggle high contrast mode")
        self.contrast_btn.clicked.connect(lambda checked: self.a11y.set_high_contrast(checked))
        layout.addWidget(self.contrast_btn)

        # Color blind mode dropdown
        self.cb_combo = QComboBox()
        self.cb_combo.setAccessibleName("Color blind mode")
        self.cb_combo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.cb_combo.setFixedHeight(36)
        for key, label in AccessibilityManager.COLOR_BLIND_LABELS.items():
            self.cb_combo.addItem(label, key)
        idx = self.cb_combo.findData(self.a11y.color_blind_mode)
        if idx >= 0:
            self.cb_combo.setCurrentIndex(idx)
        self.cb_combo.currentIndexChanged.connect(
            lambda: self.a11y.set_color_blind_mode(self.cb_combo.currentData())
        )
        layout.addWidget(self.cb_combo)

        # Full settings button
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setAccessibleName("Open full accessibility settings")
        self.settings_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.settings_btn.setFixedHeight(36)
        self.settings_btn.setToolTip("Open accessibility settings (all options)")
        self.settings_btn.clicked.connect(self._open_full_settings)
        layout.addWidget(self.settings_btn)

    _SCALE_ORDER = ["small", "medium", "large", "extra_large"]

    def _decrease_font(self):
        idx = self._SCALE_ORDER.index(self.a11y.font_scale) if self.a11y.font_scale in self._SCALE_ORDER else 1
        if idx > 0:
            self.a11y.set_font_scale(self._SCALE_ORDER[idx - 1])

    def _increase_font(self):
        idx = self._SCALE_ORDER.index(self.a11y.font_scale) if self.a11y.font_scale in self._SCALE_ORDER else 1
        if idx < len(self._SCALE_ORDER) - 1:
            self.a11y.set_font_scale(self._SCALE_ORDER[idx + 1])

    def _open_full_settings(self):
        from ui.components.accessibility_panel import AccessibilityPanel
        dlg = AccessibilityPanel(self.window())
        dlg.exec()

"""Full accessibility preferences dialog."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QPushButton, QGroupBox, QFormLayout,
)
from PyQt6.QtCore import Qt

from config.settings import get_colors
from ui.accessibility import AccessibilityManager


class AccessibilityPanel(QDialog):
    """Comprehensive accessibility settings dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.a11y = AccessibilityManager.instance()
        self.setWindowTitle("Accessibility Settings")
        self.setMinimumWidth(480)
        self.setAccessibleName("Accessibility Settings Dialog")
        self._build_ui()

    def _build_ui(self):
        c = get_colors()
        self.setStyleSheet(f"QDialog {{ background-color: {c['dark_card']}; }}")

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Accessibility Settings")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {c['primary_text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setAccessibleName("Accessibility Settings")
        layout.addWidget(title)

        # -- Font --
        font_group = QGroupBox("Text & Font")
        font_group.setAccessibleName("Text and Font settings")
        font_form = QFormLayout(font_group)

        self.font_combo = QComboBox()
        self.font_combo.setAccessibleName("Font size")
        self.font_combo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        for key in AccessibilityManager.FONT_SCALES:
            self.font_combo.addItem(key.replace("_", " ").title(), key)
        idx = self.font_combo.findData(self.a11y.font_scale)
        if idx >= 0:
            self.font_combo.setCurrentIndex(idx)
        font_form.addRow("Font Size:", self.font_combo)

        self.dyslexia_cb = QCheckBox("Use dyslexia-friendly font")
        self.dyslexia_cb.setAccessibleName("Dyslexia friendly font")
        self.dyslexia_cb.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.dyslexia_cb.setChecked(self.a11y.dyslexia_font)
        font_form.addRow(self.dyslexia_cb)

        layout.addWidget(font_group)

        # -- Colors --
        color_group = QGroupBox("Colors & Contrast")
        color_group.setAccessibleName("Colors and Contrast settings")
        color_form = QFormLayout(color_group)

        self.high_contrast_cb = QCheckBox("High contrast mode")
        self.high_contrast_cb.setAccessibleName("High contrast mode")
        self.high_contrast_cb.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.high_contrast_cb.setChecked(self.a11y.high_contrast)
        color_form.addRow(self.high_contrast_cb)

        self.cb_combo = QComboBox()
        self.cb_combo.setAccessibleName("Color blind mode")
        self.cb_combo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        for key, label in AccessibilityManager.COLOR_BLIND_LABELS.items():
            self.cb_combo.addItem(label, key)
        idx = self.cb_combo.findData(self.a11y.color_blind_mode)
        if idx >= 0:
            self.cb_combo.setCurrentIndex(idx)
        color_form.addRow("Color Blind Mode:", self.cb_combo)

        layout.addWidget(color_group)

        # -- Cursor & Reading --
        cursor_group = QGroupBox("Cursor & Reading Aids")
        cursor_group.setAccessibleName("Cursor and Reading Aids settings")
        cursor_form = QFormLayout(cursor_group)

        self.cursor_combo = QComboBox()
        self.cursor_combo.setAccessibleName("Cursor style")
        self.cursor_combo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        for key, label in AccessibilityManager.CUSTOM_CURSORS.items():
            self.cursor_combo.addItem(label, key)
        idx = self.cursor_combo.findData(self.a11y.custom_cursor)
        if idx >= 0:
            self.cursor_combo.setCurrentIndex(idx)
        cursor_form.addRow("Cursor Style:", self.cursor_combo)

        self.ruler_cb = QCheckBox("Reading ruler (highlight band)")
        self.ruler_cb.setAccessibleName("Reading ruler")
        self.ruler_cb.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.ruler_cb.setChecked(self.a11y.reading_ruler)
        cursor_form.addRow(self.ruler_cb)

        layout.addWidget(cursor_group)

        # -- Motion & Focus --
        motion_group = QGroupBox("Motion & Focus")
        motion_group.setAccessibleName("Motion and Focus settings")
        motion_form = QFormLayout(motion_group)

        self.reduced_motion_cb = QCheckBox("Reduce motion / animations")
        self.reduced_motion_cb.setAccessibleName("Reduce motion")
        self.reduced_motion_cb.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.reduced_motion_cb.setChecked(self.a11y.reduced_motion)
        motion_form.addRow(self.reduced_motion_cb)

        self.enhanced_focus_cb = QCheckBox("Enhanced focus indicators")
        self.enhanced_focus_cb.setAccessibleName("Enhanced focus indicators")
        self.enhanced_focus_cb.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.enhanced_focus_cb.setChecked(self.a11y.enhanced_focus)
        motion_form.addRow(self.enhanced_focus_cb)

        layout.addWidget(motion_group)

        # -- Buttons --
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        apply_btn = QPushButton("Apply")
        apply_btn.setAccessibleName("Apply accessibility settings")
        apply_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        apply_btn.setFixedHeight(44)
        apply_btn.clicked.connect(self._apply)
        apply_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {c['primary']}, stop:1 {c['tertiary']});
                color: white; border: none; border-radius: 8px;
                padding: 8px 24px; font-weight: bold;
            }}
        """)
        btn_layout.addWidget(apply_btn)

        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close accessibility settings")
        close_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        close_btn.setFixedHeight(44)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def _apply(self):
        self.a11y.set_font_scale(self.font_combo.currentData())
        self.a11y.set_dyslexia_font(self.dyslexia_cb.isChecked())
        self.a11y.set_high_contrast(self.high_contrast_cb.isChecked())
        self.a11y.set_color_blind_mode(self.cb_combo.currentData())
        self.a11y.set_custom_cursor(self.cursor_combo.currentData())
        self.a11y.set_reading_ruler(self.ruler_cb.isChecked())
        self.a11y.set_reduced_motion(self.reduced_motion_cb.isChecked())
        self.a11y.set_enhanced_focus(self.enhanced_focus_cb.isChecked())

"""Accessibility settings manager singleton."""

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QCursor, QPainter, QPainterPath, QPen, QPixmap

from config.settings import COLORS


class AccessibilityManager(QObject):
    """Singleton managing runtime accessibility preferences."""

    settings_changed = pyqtSignal()

    _instance = None

    FONT_SCALES = {
        "small": {"base": 14, "heading": 20, "subheading": 16},
        "medium": {"base": 16, "heading": 24, "subheading": 18},
        "large": {"base": 20, "heading": 30, "subheading": 22},
        "extra_large": {"base": 24, "heading": 36, "subheading": 28},
    }

    HIGH_CONTRAST_OVERRIDES = {
        "primary_text": "#f0a0d8",
        "error": "#ff9da7",
        "success": "#6fe882",
        "text_muted": "#d4d4d4",
    }

    COLOR_BLIND_MODES = {
        "none": {},
        "protanopia": {
            "primary": "#0072B2",
            "primary_text": "#56B4E9",
            "secondary": "#2b4095",
            "tertiary": "#3870b2",
            "success": "#009E73",
            "warning": "#E69F00",
            "error": "#D55E00",
            "dark_bg": "#0d1b2a",
            "dark_card": "#1b2838",
            "dark_border": "#1e3448",
            "dark_hover": "#1a3050",
            "dark_input": "#0e2d4a",
        },
        "deuteranopia": {
            "primary": "#0072B2",
            "primary_text": "#56B4E9",
            "secondary": "#2b4095",
            "tertiary": "#3870b2",
            "success": "#56B4E9",
            "warning": "#E69F00",
            "error": "#D55E00",
            "dark_bg": "#0d1b2a",
            "dark_card": "#1b2838",
            "dark_border": "#1e3448",
            "dark_hover": "#1a3050",
            "dark_input": "#0e2d4a",
        },
        "tritanopia": {
            "primary": "#CC79A7",
            "primary_text": "#d4a0c0",
            "secondary": "#8b3a50",
            "tertiary": "#a04068",
            "success": "#009E73",
            "warning": "#D55E00",
            "error": "#cc3333",
            "dark_bg": "#1a1520",
            "dark_card": "#261e2e",
            "dark_border": "#3a2840",
            "dark_hover": "#2e2238",
            "dark_input": "#321a3a",
        },
        "monochrome": {
            "primary": "#858585",
            "primary_text": "#b0b0b0",
            "secondary": "#5a5a5a",
            "tertiary": "#707070",
            "success": "#a0a0a0",
            "warning": "#d0d0d0",
            "error": "#c0c0c0",
            "dark_bg": "#1a1a1a",
            "dark_card": "#252525",
            "dark_border": "#333333",
            "dark_hover": "#2e2e2e",
            "dark_input": "#303030",
        },
    }

    COLOR_BLIND_LABELS = {
        "none": "None (Default)",
        "protanopia": "Protanopia (Red-blind)",
        "deuteranopia": "Deuteranopia (Green-blind)",
        "tritanopia": "Tritanopia (Blue-blind)",
        "monochrome": "Monochrome (Grayscale)",
    }

    CUSTOM_CURSORS = {
        "default": "System Default",
        "large_black": "Large Black Cursor",
        "large_white": "Large White Cursor",
        "large_crosshair": "Large Crosshair",
        "high_visibility": "High Visibility (Yellow/Black)",
        "pointer_trail": "Pointer with Trail",
    }

    @classmethod
    def instance(cls):
        return cls._instance

    @classmethod
    def create(cls, parent=None):
        if cls._instance is None:
            cls._instance = cls(parent)
        return cls._instance

    def __init__(self, parent=None):
        super().__init__(parent)
        self._font_scale = "medium"
        self._high_contrast = False
        self._reduced_motion = False
        self._enhanced_focus = False
        self._color_blind_mode = "none"
        self._dyslexia_font = False
        self._custom_cursor = "default"
        self._reading_ruler = False
        self._letter_spacing = 0  # extra px (WCAG 1.4.12)
        self._word_spacing = 0    # extra px
        self._line_height = 0     # extra px
        self._role_accent = None  # set on login

    # -- properties --

    @property
    def font_scale(self):
        return self._font_scale

    @property
    def high_contrast(self):
        return self._high_contrast

    @property
    def reduced_motion(self):
        return self._reduced_motion

    @property
    def enhanced_focus(self):
        return self._enhanced_focus

    @property
    def color_blind_mode(self):
        return self._color_blind_mode

    @property
    def dyslexia_font(self):
        return self._dyslexia_font

    @property
    def custom_cursor(self):
        return self._custom_cursor

    @property
    def reading_ruler(self):
        return self._reading_ruler

    @property
    def letter_spacing(self):
        return self._letter_spacing

    @property
    def word_spacing(self):
        return self._word_spacing

    @property
    def line_height(self):
        return self._line_height

    @property
    def role_accent(self):
        return self._role_accent

    # -- setters --

    def set_font_scale(self, scale: str):
        if scale in self.FONT_SCALES and scale != self._font_scale:
            self._font_scale = scale
            self.settings_changed.emit()

    def set_high_contrast(self, enabled: bool):
        if enabled != self._high_contrast:
            self._high_contrast = enabled
            self.settings_changed.emit()

    def set_reduced_motion(self, enabled: bool):
        if enabled != self._reduced_motion:
            self._reduced_motion = enabled
            self.settings_changed.emit()

    def set_enhanced_focus(self, enabled: bool):
        if enabled != self._enhanced_focus:
            self._enhanced_focus = enabled
            self.settings_changed.emit()

    def set_color_blind_mode(self, mode: str):
        if mode in self.COLOR_BLIND_MODES and mode != self._color_blind_mode:
            self._color_blind_mode = mode
            self.settings_changed.emit()

    def set_dyslexia_font(self, enabled: bool):
        if enabled != self._dyslexia_font:
            self._dyslexia_font = enabled
            self.settings_changed.emit()

    def set_custom_cursor(self, cursor: str):
        if cursor in self.CUSTOM_CURSORS and cursor != self._custom_cursor:
            self._custom_cursor = cursor
            self.settings_changed.emit()

    def set_reading_ruler(self, enabled: bool):
        if enabled != self._reading_ruler:
            self._reading_ruler = enabled
            self.settings_changed.emit()

    def set_letter_spacing(self, px: int):
        px = max(0, min(8, px))
        if px != self._letter_spacing:
            self._letter_spacing = px
            self.settings_changed.emit()

    def set_word_spacing(self, px: int):
        px = max(0, min(12, px))
        if px != self._word_spacing:
            self._word_spacing = px
            self.settings_changed.emit()

    def set_line_height(self, px: int):
        px = max(0, min(12, px))
        if px != self._line_height:
            self._line_height = px
            self.settings_changed.emit()

    def set_role_accent(self, role: str):
        from config.brand import ROLE_ACCENTS
        if role in ROLE_ACCENTS:
            self._role_accent = role
            self.settings_changed.emit()

    # -- derived --

    def get_effective_colors(self) -> dict:
        colors = dict(COLORS)
        cb_overrides = self.COLOR_BLIND_MODES.get(self._color_blind_mode, {})
        if cb_overrides:
            colors.update(cb_overrides)
        if self._high_contrast:
            colors.update(self.HIGH_CONTRAST_OVERRIDES)
        return colors

    def get_font_sizes(self) -> dict:
        return dict(self.FONT_SCALES.get(self._font_scale, self.FONT_SCALES["medium"]))

    def get_cursor(self):
        cursor_type = self._custom_cursor
        if cursor_type == "default":
            return None
        if cursor_type == "large_black":
            return self._make_arrow_cursor(32, QColor("black"), QColor("white"), 2)
        elif cursor_type == "large_white":
            return self._make_arrow_cursor(32, QColor("white"), QColor("black"), 2)
        elif cursor_type == "large_crosshair":
            return self._make_crosshair_cursor()
        elif cursor_type == "high_visibility":
            return self._make_arrow_cursor(40, QColor("yellow"), QColor("black"), 3)
        elif cursor_type == "pointer_trail":
            return self._make_arrow_cursor(32, QColor("black"), QColor("white"), 2)
        return None

    def _make_arrow_cursor(self, size, fill_color, stroke_color, stroke_width):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        scale = size / 32.0
        path = QPainterPath()
        path.moveTo(4 * scale, 4 * scale)
        path.lineTo(4 * scale, 28 * scale)
        path.lineTo(12 * scale, 20 * scale)
        path.lineTo(18 * scale, 28 * scale)
        path.lineTo(22 * scale, 26 * scale)
        path.lineTo(16 * scale, 18 * scale)
        path.lineTo(26 * scale, 18 * scale)
        path.closeSubpath()
        pen = QPen(stroke_color, stroke_width)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(QBrush(fill_color))
        painter.drawPath(path)
        painter.end()
        hotspot = int(4 * scale)
        return QCursor(pixmap, hotspot, hotspot)

    def _make_crosshair_cursor(self):
        size = 32
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("black"), 3))
        painter.drawLine(16, 0, 16, 32)
        painter.drawLine(0, 16, 32, 16)
        painter.setPen(QPen(QColor("red"), 1))
        painter.drawLine(16, 0, 16, 32)
        painter.drawLine(0, 16, 32, 16)
        painter.setPen(QPen(QColor("red"), 2))
        painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.drawEllipse(10, 10, 12, 12)
        painter.end()
        return QCursor(pixmap, 16, 16)

    # -- serialization --

    def to_dict(self) -> dict:
        return {
            "font_scale": self._font_scale,
            "high_contrast": self._high_contrast,
            "reduced_motion": self._reduced_motion,
            "enhanced_focus": self._enhanced_focus,
            "color_blind_mode": self._color_blind_mode,
            "dyslexia_font": self._dyslexia_font,
            "custom_cursor": self._custom_cursor,
            "reading_ruler": self._reading_ruler,
            "letter_spacing": self._letter_spacing,
            "word_spacing": self._word_spacing,
            "line_height": self._line_height,
        }

    def load_from_dict(self, data: dict):
        changed = False

        for key, attr, valid in [
            ("font_scale", "_font_scale", self.FONT_SCALES),
            ("color_blind_mode", "_color_blind_mode", self.COLOR_BLIND_MODES),
            ("custom_cursor", "_custom_cursor", self.CUSTOM_CURSORS),
        ]:
            val = data.get(key)
            if val and val in valid and val != getattr(self, attr):
                setattr(self, attr, val)
                changed = True

        for key, attr in [
            ("high_contrast", "_high_contrast"),
            ("reduced_motion", "_reduced_motion"),
            ("enhanced_focus", "_enhanced_focus"),
            ("dyslexia_font", "_dyslexia_font"),
            ("reading_ruler", "_reading_ruler"),
        ]:
            val = data.get(key, False)
            if val != getattr(self, attr):
                setattr(self, attr, val)
                changed = True

        for key, attr in [
            ("letter_spacing", "_letter_spacing"),
            ("word_spacing", "_word_spacing"),
            ("line_height", "_line_height"),
        ]:
            val = data.get(key, 0)
            if isinstance(val, int) and val != getattr(self, attr):
                setattr(self, attr, max(0, val))
                changed = True

        if changed:
            self.settings_changed.emit()

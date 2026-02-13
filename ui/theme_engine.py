"""Stylesheet generation with role-aware accent colors."""

from config.settings import get_colors, APP_SETTINGS
from config.brand import ROLE_ACCENTS, SPACING


def get_main_stylesheet(colors: dict = None, fonts: dict = None,
                        enhanced_focus: bool = False,
                        dyslexia_font: bool = False,
                        custom_cursor: str = "default") -> str:
    """Generate the full application QSS."""
    c = colors or get_colors()
    f = fonts or {"base": 16, "heading": 24, "subheading": 18}
    family = "OpenDyslexic, Arial" if dyslexia_font else "Arial"
    focus_width = APP_SETTINGS["focus_outline_width"]
    touch = APP_SETTINGS["touch_target_min"]

    focus_extra = ""
    if enhanced_focus:
        focus_extra = f"""
        *:focus {{
            outline: {focus_width}px solid {c['primary']};
            outline-offset: 2px;
        }}
        """

    return f"""
    * {{
        font-family: {family};
        font-size: {f['base']}px;
    }}

    QMainWindow, QWidget {{
        background-color: {c['dark_bg']};
        color: {c['text']};
    }}

    QPushButton {{
        min-height: {touch}px;
        min-width: {touch}px;
        border-radius: {SPACING['button_radius']}px;
        padding: 8px 16px;
        font-weight: bold;
    }}

    QPushButton:focus {{
        outline: {focus_width}px solid {c['primary']};
        outline-offset: 2px;
    }}

    QLineEdit, QComboBox, QTextEdit {{
        min-height: {touch}px;
        background-color: {c['dark_input']};
        color: {c['text']};
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: {SPACING['input_radius']}px;
        padding: 4px 14px;
    }}

    QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
        border: 2px solid {c['primary']};
    }}

    QScrollBar:vertical {{
        background-color: {c['dark_bg']};
        width: 10px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {c['dark_input']};
        border-radius: 5px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {c['primary']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QLabel {{
        color: {c['text']};
    }}

    QCheckBox {{
        color: {c['text']};
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
    }}
    QCheckBox::indicator:unchecked {{
        background-color: {c['dark_input']};
        border: 2px solid rgba(255, 255, 255, 0.15);
    }}
    QCheckBox::indicator:checked {{
        background-color: {c['primary']};
        border: 2px solid {c['primary']};
    }}

    QToolTip {{
        background-color: {c['dark_card']};
        color: {c['text']};
        border: 1px solid {c['dark_border']};
        padding: 6px;
        border-radius: 4px;
    }}

    {focus_extra}
    """


def get_role_stylesheet(role: str) -> str:
    """Return additional QSS accent overrides for a role."""
    accent = ROLE_ACCENTS.get(role)
    if not accent:
        return ""
    return f"""
    QPushButton#primaryAction {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {accent['gradient_start']}, stop:1 {accent['gradient_end']});
        color: white;
    }}
    QPushButton#primaryAction:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {accent['accent_light']}, stop:1 {accent['gradient_end']});
    }}
    """

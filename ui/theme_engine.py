"""Stylesheet generation with role-aware accent colors."""

from config.settings import get_colors, APP_SETTINGS
from config.brand import ROLE_ACCENTS, SPACING


def get_main_stylesheet(colors: dict = None, fonts: dict = None,
                        enhanced_focus: bool = False,
                        dyslexia_font: bool = False,
                        custom_cursor: str = "default",
                        reduced_motion: bool = False,
                        letter_spacing: int = 0,
                        word_spacing: int = 0,
                        line_height: int = 0) -> str:
    """Generate the full application QSS."""
    c = colors or get_colors()
    f = fonts or {"base": 16, "heading": 24, "subheading": 18}
    family = "OpenDyslexic, Arial" if dyslexia_font else "Arial"
    focus_width = APP_SETTINGS["focus_outline_width"]
    touch = APP_SETTINGS["touch_target_min"]

    # WCAG 1.4.12 — text spacing overrides
    spacing_css = ""
    if letter_spacing > 0:
        spacing_css += f"letter-spacing: {letter_spacing}px; "
    if word_spacing > 0:
        spacing_css += f"word-spacing: {word_spacing}px; "
    if line_height > 0:
        spacing_css += f"line-height: {100 + line_height * 10}%; "

    # WCAG 2.4.7 — focus indicators always visible; enhanced mode makes them thicker
    if enhanced_focus:
        focus_extra = f"""
        *:focus {{
            outline: {focus_width + 1}px solid {c['primary']};
            outline-offset: 2px;
        }}
        """
    else:
        focus_extra = f"""
        *:focus {{
            outline: 2px solid {c['primary']};
            outline-offset: 1px;
        }}
        """

    return f"""
    * {{
        font-family: {family};
        font-size: {f['base']}px;
        {spacing_css}
    }}

    QMainWindow, QWidget {{
        background-color: {c['dark_bg']};
        color: {c['text']};
    }}

    QLabel {{
        background: transparent;
        color: {c['text']};
    }}

    QPushButton {{
        min-height: {touch}px;
        min-width: {touch}px;
        border-radius: {SPACING['button_radius']}px;
        padding: 8px 16px;
        font-weight: bold;
        background-color: {c['dark_card']};
        color: {c['text']};
        border: 1px solid {c['dark_border']};
    }}

    QPushButton:hover {{
        background-color: {c['dark_hover']};
    }}

    QPushButton:focus {{
        outline: {focus_width}px solid {c['primary']};
        outline-offset: 2px;
    }}

    QLineEdit, QComboBox, QTextEdit {{
        min-height: {touch}px;
        background-color: {c['dark_input']};
        color: {c['text']};
        border: 1px solid rgba(255, 255, 255, 0.35);
        border-radius: {SPACING['input_radius']}px;
        padding: 4px 14px;
    }}

    QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
        border: 2px solid {c['primary']};
    }}

    QFrame {{
        background: transparent;
        border: none;
    }}

    QScrollArea {{
        background: transparent;
        border: none;
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

    QCheckBox {{
        background: transparent;
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
        border: 2px solid rgba(255, 255, 255, 0.35);
    }}
    QCheckBox::indicator:checked {{
        background-color: {c['primary']};
        border: 2px solid {c['primary']};
    }}

    QGroupBox {{
        background-color: {c['dark_card']};
        color: {c['text']};
        border: 1px solid {c['dark_border']};
        border-radius: 8px;
        padding: 12px;
        margin-top: 12px;
    }}
    QGroupBox::title {{
        color: {c['primary_text']};
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 4px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {c['dark_card']};
        color: {c['text']};
        selection-background-color: {c['primary']};
        selection-color: white;
        border: 1px solid {c['dark_border']};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 28px;
    }}

    QToolTip {{
        background-color: {c['dark_card']};
        color: {c['text']};
        border: 1px solid {c['dark_border']};
        padding: 6px;
        border-radius: 4px;
    }}

    QDialog {{
        background-color: {c['dark_card']};
        color: {c['text']};
    }}

    {focus_extra}

    {"" if not reduced_motion else '''
    * {
        transition: none !important;
        animation: none !important;
    }
    '''}
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

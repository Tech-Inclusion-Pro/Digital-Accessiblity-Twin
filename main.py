#!/usr/bin/env python3
"""
AccessTwin — Digital Accessibility Twin Manager
A PyQt6 desktop app for Tech Inclusion Pro that creates
"Digital Accessibility Twins" for students with accommodations.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QLocale
from PyQt6.QtGui import QPalette, QColor

from config.settings import COLORS, APP_SETTINGS


def setup_palette(app: QApplication):
    """Set up the color palette from current accessibility settings."""
    from config.settings import get_colors
    colors = get_colors()

    palette = QPalette()

    palette.setColor(QPalette.ColorRole.Window, QColor(colors["dark_bg"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(colors["text"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(colors["dark_input"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors["dark_card"]))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors["dark_card"]))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors["text"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(colors["text"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(colors["primary"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors["text"]))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(colors["text"]))
    palette.setColor(QPalette.ColorRole.Link, QColor(colors["primary"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(colors["primary"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors["text"]))

    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(colors["text_muted"]))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(colors["text_muted"]))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(colors["text_muted"]))

    app.setPalette(palette)


def main():
    """Main entry point."""
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    # WCAG 3.1.1 — declare the application language
    QLocale.setDefault(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))

    app.setApplicationName(APP_SETTINGS["app_name"])
    app.setApplicationVersion(APP_SETTINGS["version"])
    app.setOrganizationName("Tech Inclusion Pro")

    # Load pre-login accessibility preferences
    from ui.accessibility import AccessibilityManager
    a11y = AccessibilityManager.create()

    from ui.accessibility_prefs import load_prefs
    saved = load_prefs()
    if saved:
        a11y.load_from_dict(saved)

    setup_palette(app)

    font = app.font()
    font.setFamily("Arial")
    font.setPointSize(APP_SETTINGS["min_font_size"])
    app.setFont(font)

    from ui.navigation import MainWindow
    window = MainWindow()
    window.show()
    window.raise_()
    window.activateWindow()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

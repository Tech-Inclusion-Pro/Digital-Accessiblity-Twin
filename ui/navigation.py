"""Main application window — navigation controller."""

from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence

from config.settings import APP_SETTINGS
from models.database import DatabaseManager
from models.auth import AuthManager
from ai.backend_manager import BackendManager
from ui.accessibility import AccessibilityManager
from ui.accessibility_prefs import save_prefs
from ui.theme_engine import get_main_stylesheet, get_role_stylesheet
from ui.cursor_trail import CursorTrailOverlay
from ui.reading_ruler import ReadingRulerOverlay
from ui.focus_manager import FocusManager


class MainWindow(QMainWindow):
    """Main application window with screen navigation."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_SETTINGS["app_name"])
        self.setMinimumSize(900, 700)

        # Core managers
        self.db_manager = DatabaseManager()
        self.auth_manager = AuthManager(self.db_manager)
        self.backend_manager = BackendManager()
        self.backend_manager.load_config()
        self.a11y = AccessibilityManager.instance() or AccessibilityManager.create()

        # Screen stack
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Overlays (created lazily)
        self._cursor_trail: CursorTrailOverlay | None = None
        self._reading_ruler: ReadingRulerOverlay | None = None

        # Build screens
        from ui.screens.login_screen import LoginScreen
        self.login_screen = LoginScreen(self.auth_manager, self.a11y)
        self.login_screen.login_successful.connect(self._on_login)
        self.stack.addWidget(self.login_screen)  # index 0

        # Real dashboards
        from ui.screens.student.dashboard import StudentDashboard
        from ui.screens.teacher.dashboard import TeacherDashboard

        self.student_dashboard = StudentDashboard(self.db_manager, self.auth_manager, self.backend_manager)
        self.student_dashboard.logout_requested.connect(self._on_logout)
        self.stack.addWidget(self.student_dashboard)  # index 1

        self.teacher_dashboard = TeacherDashboard(self.db_manager, self.auth_manager, self.backend_manager)
        self.teacher_dashboard.logout_requested.connect(self._on_logout)
        self.stack.addWidget(self.teacher_dashboard)  # index 2

        # Apply theme
        self._apply_theme()
        self.a11y.settings_changed.connect(self._on_a11y_changed)

        # Global shortcuts
        QShortcut(QKeySequence("Ctrl+/"), self).activated.connect(self._show_shortcuts_dialog)
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.close)

    # -- screen transitions --

    def _on_login(self):
        """Route to role-specific dashboard after login."""
        user = self.auth_manager.get_current_user()
        if user.role == "student":
            self.a11y.set_role_accent("student")
            self.student_dashboard.refresh_data()
            self.stack.setCurrentIndex(1)
            FocusManager.set_focus_after_transition(self.student_dashboard)
        else:
            self.a11y.set_role_accent("teacher")
            self.teacher_dashboard.refresh_data()
            self.stack.setCurrentIndex(2)
            FocusManager.set_focus_after_transition(self.teacher_dashboard)

    def _on_logout(self):
        """Handle logout from either dashboard."""
        self.auth_manager.logout()
        self.a11y.set_role_accent(None)
        self._apply_theme()
        self.stack.setCurrentIndex(0)
        FocusManager.set_focus_after_transition(self.login_screen)

    # -- theme / a11y --

    def _apply_theme(self):
        colors = self.a11y.get_effective_colors()
        fonts = self.a11y.get_font_sizes()
        qss = get_main_stylesheet(
            colors=colors,
            fonts=fonts,
            enhanced_focus=self.a11y.enhanced_focus,
            dyslexia_font=self.a11y.dyslexia_font,
            custom_cursor=self.a11y.custom_cursor,
            reduced_motion=self.a11y.reduced_motion,
            letter_spacing=self.a11y.letter_spacing,
            word_spacing=self.a11y.word_spacing,
            line_height=self.a11y.line_height,
        )
        if self.a11y.role_accent:
            qss += get_role_stylesheet(self.a11y.role_accent)
        self.setStyleSheet(qss)

        # Custom cursor
        cursor = self.a11y.get_cursor()
        if cursor:
            QApplication.setOverrideCursor(cursor)
        else:
            QApplication.restoreOverrideCursor()

        # Cursor trail
        if self.a11y.custom_cursor == "pointer_trail":
            self._start_cursor_trail(cursor)
        elif self._cursor_trail:
            self._cursor_trail.stop()

        # Reading ruler
        if self.a11y.reading_ruler:
            self._start_reading_ruler()
        elif self._reading_ruler:
            self._reading_ruler.stop()

    def _start_cursor_trail(self, cursor):
        if cursor is None:
            return
        pixmap = cursor.pixmap()
        if pixmap.isNull():
            return
        if self._cursor_trail is None:
            self._cursor_trail = CursorTrailOverlay(
                pixmap, cursor.hotSpot().x(), cursor.hotSpot().y(), self
            )
        self._cursor_trail.start()

    def _start_reading_ruler(self):
        if self._reading_ruler is None:
            self._reading_ruler = ReadingRulerOverlay(self)
        self._reading_ruler.start()

    def _on_a11y_changed(self):
        self._apply_theme()
        save_prefs(self.a11y.to_dict())
        # Re-apply palette
        from main import setup_palette
        setup_palette(QApplication.instance())

    def _show_shortcuts_dialog(self):
        from ui.components.shortcuts_dialog import ShortcutsDialog
        dlg = ShortcutsDialog(self)
        dlg.exec()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._cursor_trail and self._cursor_trail.isVisible():
            self._cursor_trail.setGeometry(self.rect())
        if self._reading_ruler and self._reading_ruler.isVisible():
            self._reading_ruler.setGeometry(self.rect())

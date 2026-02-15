"""Teacher dashboard — sidebar + stacked sub-pages."""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget,
)
from PyQt6.QtCore import pyqtSignal

from ui.components.sidebar import Sidebar
from ui.components.breadcrumb import Breadcrumb
from ui.screens.teacher.home_page import TeacherHomePage
from ui.screens.teacher.students_page import TeacherStudentsPage
from ui.screens.teacher.evaluate_page import TeacherEvaluatePage
from ui.screens.teacher.log_impl_page import TeacherLogImplPage
from ui.screens.teacher.tracking_page import TeacherTrackingPage
from ui.screens.teacher.insights_page import TeacherInsightsPage

NAV_ITEMS = [
    {"key": "home", "icon": "\u2302", "label": "Home"},
    {"key": "students", "icon": "\u25C7", "label": "Students"},
    {"key": "evaluate", "icon": "\u25B3", "label": "Evaluate"},
    {"key": "log", "icon": "\u270E", "label": "Log Implementation"},
    {"key": "tracking", "icon": "\u2630", "label": "Tracking"},
    {"key": "insights", "icon": "\u2606", "label": "AI Insights"},
    {"key": "ai_settings", "icon": "\u2261", "label": "AI Settings"},
]

PAGE_MAP = {
    "home": 0,
    "students": 1,
    "evaluate": 2,
    "log": 3,
    "tracking": 4,
    "insights": 5,
    "ai_settings": 6,
}

BREADCRUMB_MAP = {
    "home": ["Teacher", "Home"],
    "students": ["Teacher", "Students"],
    "evaluate": ["Teacher", "Evaluate"],
    "log": ["Teacher", "Log Implementation"],
    "tracking": ["Teacher", "Tracking"],
    "insights": ["Teacher", "AI Insights"],
    "ai_settings": ["Teacher", "AI Settings"],
}


class TeacherDashboard(QWidget):
    """Main teacher dashboard container: sidebar (left) + content (right)."""

    logout_requested = pyqtSignal()

    def __init__(self, db_manager, auth_manager, backend_manager=None, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.auth = auth_manager
        self.backend_manager = backend_manager
        self._build_ui()

    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Sidebar
        self._sidebar = Sidebar("teacher", NAV_ITEMS)
        self._sidebar.nav_clicked.connect(self._navigate)
        self._sidebar.logout_requested.connect(self.logout_requested.emit)
        self._sidebar.settings_requested.connect(self._open_settings)
        outer.addWidget(self._sidebar)

        # Right content area
        right = QVBoxLayout()
        right.setContentsMargins(0, 8, 0, 0)
        right.setSpacing(0)

        self._breadcrumb = Breadcrumb()
        self._breadcrumb.crumb_clicked.connect(self._on_crumb)
        right.addWidget(self._breadcrumb)

        self._stack = QStackedWidget()

        self._home_page = TeacherHomePage(self.db, self.auth, self.backend_manager)
        self._home_page.navigate_to.connect(self._navigate)
        self._stack.addWidget(self._home_page)

        self._students_page = TeacherStudentsPage(self.db, self.auth, self.backend_manager)
        self._stack.addWidget(self._students_page)

        self._evaluate_page = TeacherEvaluatePage(self.db, self.auth)
        self._stack.addWidget(self._evaluate_page)

        self._log_page = TeacherLogImplPage(self.db, self.auth)
        self._stack.addWidget(self._log_page)

        self._tracking_page = TeacherTrackingPage(self.db, self.auth)
        self._stack.addWidget(self._tracking_page)

        self._insights_page = TeacherInsightsPage(self.db, self.auth, self.backend_manager)
        self._stack.addWidget(self._insights_page)

        from ui.screens.ai_settings_page import AISettingsPage
        self._ai_settings_page = AISettingsPage(self.backend_manager)
        self._stack.addWidget(self._ai_settings_page)

        right.addWidget(self._stack, stretch=1)
        outer.addLayout(right, stretch=1)

        # Default
        self._breadcrumb.set_crumbs(BREADCRUMB_MAP["home"])

    def _navigate(self, key: str):
        idx = PAGE_MAP.get(key)
        if idx is not None:
            self._stack.setCurrentIndex(idx)
            self._sidebar.set_active(key)
            self._breadcrumb.set_crumbs(BREADCRUMB_MAP.get(key, ["Teacher"]))
            self._refresh_current_page(idx)

    def _on_crumb(self, index: int):
        if index == 0:
            self._navigate("home")

    def _open_settings(self):
        from ui.components.accessibility_panel import AccessibilityPanel
        dlg = AccessibilityPanel(self)
        dlg.exec()

    def refresh_data(self):
        """Called on login — refresh all sub-pages."""
        self._navigate("home")
        self._home_page.refresh_data()

    def _refresh_current_page(self, idx: int):
        pages = [
            self._home_page,
            self._students_page,
            self._evaluate_page,
            self._log_page,
            self._tracking_page,
            self._insights_page,
            self._ai_settings_page,
        ]
        if 0 <= idx < len(pages):
            pages[idx].refresh_data()

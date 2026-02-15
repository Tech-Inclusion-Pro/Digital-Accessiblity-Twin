"""Student home page — welcome, stats, active supports grid."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal

from config.settings import get_colors
from config.brand import ROLE_ACCENTS
from models.student_profile import StudentProfile
from models.support import SupportEntry
from ui.components.stat_card import StatCard
from ui.components.support_card import SupportCard
from ui.components.empty_state import EmptyState


class StudentHomePage(QWidget):
    """Student dashboard home: welcome, stats, supports grid, quick actions."""

    navigate_to = pyqtSignal(str)  # emits page key

    def __init__(self, db_manager, auth_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.auth = auth_manager
        self._build_ui()

    def _build_ui(self):
        c = get_colors()
        accent = ROLE_ACCENTS["student"]

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(24, 20, 24, 20)
        self._layout.setSpacing(16)

        # Welcome header
        self._welcome = QLabel("Welcome!")
        self._welcome.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {c['text']};"
        )
        self._welcome.setAccessibleName("Welcome")
        self._layout.addWidget(self._welcome)

        # Stats row
        self._stats_row = QHBoxLayout()
        self._stats_row.setSpacing(12)

        self._stat_active = StatCard("\u25B3", "0", "Active Supports")
        self._stat_udl = StatCard("\u25CE", "0%", "UDL Coverage")
        self._stat_eff = StatCard("\u2606", "N/A", "Avg Effectiveness")

        self._stats_row.addWidget(self._stat_active)
        self._stats_row.addWidget(self._stat_udl)
        self._stats_row.addWidget(self._stat_eff)
        self._stats_row.addStretch()
        self._layout.addLayout(self._stats_row)

        # Supports section header
        section_hdr = QLabel("Active Supports")
        section_hdr.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {c['text']};"
        )
        self._layout.addWidget(section_hdr)

        # Scroll area for supports grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._grid_container = QWidget()
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setSpacing(12)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self._grid_container)
        self._layout.addWidget(scroll, stretch=1)

        # Empty state (hidden by default)
        self._empty = EmptyState(
            icon_text="\u2630",
            message="No profile yet. Create your accessibility profile to get started.",
            action_label="Create Profile",
        )
        self._empty.action_clicked.connect(lambda: self.navigate_to.emit("profile"))
        self._empty.setVisible(False)
        self._layout.addWidget(self._empty)

        # Quick actions
        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)

        for label, key in [
            ("Log Experience", "log"),
            ("View Profile", "profile"),
            ("Export Twin", "export"),
        ]:
            btn = QPushButton(label)
            btn.setAccessibleName(label)
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {c['dark_input']}; color: {c['text']};
                    border: 1px solid {c['dark_border']}; border-radius: 8px;
                    padding: 6px 16px; font-size: 13px;
                }}
                QPushButton:hover {{ background: {c['dark_hover']}; }}
            """)
            btn.clicked.connect(lambda checked, k=key: self.navigate_to.emit(k))
            actions_row.addWidget(btn)

        actions_row.addStretch()
        self._layout.addLayout(actions_row)

    def refresh_data(self):
        c = get_colors()
        user = self.auth.get_current_user()
        if not user:
            return

        self._welcome.setText(f"Welcome, {user.display_name or user.username}!")

        session = self.db.get_session()
        try:
            profile = session.query(StudentProfile).filter(
                StudentProfile.user_id == user.id
            ).first()

            # Clear grid
            while self._grid_layout.count():
                item = self._grid_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            if not profile:
                self._empty.setVisible(True)
                self._stat_active.set_value("0")
                self._stat_udl.set_value("0%")
                self._stat_eff.set_value("N/A")
                return

            self._empty.setVisible(False)

            supports = session.query(SupportEntry).filter(
                SupportEntry.profile_id == profile.id,
                SupportEntry.status == "active",
            ).all()

            self._stat_active.set_value(str(len(supports)))

            # UDL coverage: count supports with non-empty udl_mapping
            udl_count = sum(
                1 for s in supports
                if s.udl_mapping and s.udl_mapping != "{}"
            )
            pct = int(udl_count / len(supports) * 100) if supports else 0
            self._stat_udl.set_value(f"{pct}%")

            # Avg effectiveness
            rated = [s.effectiveness_rating for s in supports if s.effectiveness_rating]
            if rated:
                avg = sum(rated) / len(rated)
                self._stat_eff.set_value(f"{avg:.1f}")
            else:
                self._stat_eff.set_value("N/A")

            # Populate grid (2 columns)
            for i, s in enumerate(supports):
                card = SupportCard(s)
                self._grid_layout.addWidget(card, i // 2, i % 2)

        finally:
            session.close()

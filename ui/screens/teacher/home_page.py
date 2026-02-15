"""Teacher home page — welcome, stats, recent students, quick actions."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal

from config.settings import get_colors
from config.brand import ROLE_ACCENTS
from models.student_profile import StudentProfile
from models.document import Document
from models.support import SupportEntry
from models.tracking import TrackingLog
from models.evaluation import TwinEvaluation
from ui.components.stat_card import StatCard
from ui.components.empty_state import EmptyState


class TeacherHomePage(QWidget):
    """Teacher dashboard home: welcome, stats, student grid, quick actions."""

    navigate_to = pyqtSignal(str)

    def __init__(self, db_manager, auth_manager, backend_manager=None, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.auth = auth_manager
        self.backend_manager = backend_manager
        self._build_ui()

    def _build_ui(self):
        c = get_colors()

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(24, 20, 24, 20)
        self._layout.setSpacing(16)

        # Welcome
        self._welcome = QLabel("Welcome!")
        self._welcome.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {c['text']};"
        )
        self._welcome.setAccessibleName("Welcome")
        self._layout.addWidget(self._welcome)

        # Stats row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        self._stat_students = StatCard("\u25C7", "0", "Imported Twins")
        self._stat_docs = StatCard("\u25A1", "0", "Docs Evaluated")
        self._stat_logs = StatCard("\u270E", "0", "Supports Logged")

        stats_row.addWidget(self._stat_students)
        stats_row.addWidget(self._stat_docs)
        stats_row.addWidget(self._stat_logs)
        stats_row.addStretch()
        self._layout.addLayout(stats_row)

        # Recent students
        section_hdr = QLabel("Recent Students")
        section_hdr.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {c['text']};")
        self._layout.addWidget(section_hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self._grid_container = QWidget()
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setSpacing(12)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self._grid_container)
        self._layout.addWidget(scroll, stretch=1)

        # Empty state
        self._empty = EmptyState(
            icon_text="\u25C7",
            message="No students yet. Import a student twin to get started.",
            action_label="Import Student",
        )
        self._empty.action_clicked.connect(lambda: self.navigate_to.emit("students"))
        self._empty.setVisible(False)
        self._layout.addWidget(self._empty)

        # Quick actions
        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)

        for label, key in [
            ("Import Student", "students"),
            ("Evaluate Document", "evaluate"),
            ("Log Implementation", "log"),
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

        # Configure AI quick action
        ai_btn = QPushButton("Configure AI")
        ai_btn.setAccessibleName("Configure AI backend")
        ai_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        ai_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ai_btn.setFixedHeight(40)
        ai_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['dark_input']}; color: {c['text']};
                border: 1px solid {c['dark_border']}; border-radius: 8px;
                padding: 6px 16px; font-size: 13px;
            }}
            QPushButton:hover {{ background: {c['dark_hover']}; }}
        """)
        ai_btn.clicked.connect(self._open_ai_setup)
        actions_row.addWidget(ai_btn)

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
            # Get student profiles the teacher has access to
            # via Documents with purpose_description="twin_import"
            import_docs = session.query(Document).filter(
                Document.teacher_user_id == user.id,
                Document.purpose_description == "twin_import",
            ).all()

            # Get profile IDs from twin evaluations linked to import docs
            profile_ids = set()
            for doc in import_docs:
                evals = session.query(TwinEvaluation).filter(
                    TwinEvaluation.document_id == doc.id
                ).all()
                for ev in evals:
                    profile_ids.add(ev.student_profile_id)

            profiles = []
            if profile_ids:
                profiles = session.query(StudentProfile).filter(
                    StudentProfile.id.in_(profile_ids)
                ).all()

            self._stat_students.set_value(str(len(profiles)))

            # Docs evaluated
            all_docs = session.query(Document).filter(
                Document.teacher_user_id == user.id,
            ).count()
            self._stat_docs.set_value(str(all_docs))

            # Tracking logs by teacher
            log_count = session.query(TrackingLog).filter(
                TrackingLog.logged_by_role == "teacher",
            ).count()
            self._stat_logs.set_value(str(log_count))

            # Clear grid
            while self._grid_layout.count():
                item = self._grid_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            if not profiles:
                self._empty.setVisible(True)
                return

            self._empty.setVisible(False)

            for i, p in enumerate(profiles[:6]):
                card = self._make_student_card(p, session, c)
                self._grid_layout.addWidget(card, i // 3, i % 3)

        finally:
            session.close()

    def _make_student_card(self, profile, session, c) -> QWidget:
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background: {c['dark_card']};
                border: 1px solid {c['dark_border']};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        name = QLabel(profile.name)
        name.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {c['text']};")
        layout.addWidget(name)

        support_count = session.query(SupportEntry).filter(
            SupportEntry.profile_id == profile.id,
            SupportEntry.status == "active",
        ).count()

        info = QLabel(f"{support_count} active supports")
        info.setStyleSheet(f"font-size: 12px; color: {c['text_muted']};")
        layout.addWidget(info)

        card.setFixedHeight(80)
        card.setAccessibleName(f"Student: {profile.name}")
        return card

    def _open_ai_setup(self):
        if self.backend_manager is None:
            return
        from ui.screens.setup_wizard import SetupWizard
        dlg = SetupWizard(self.backend_manager, self)
        dlg.exec()

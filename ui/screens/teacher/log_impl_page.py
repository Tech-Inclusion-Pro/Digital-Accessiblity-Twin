"""Teacher log implementation page — log support implementation for students."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QMessageBox, QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt

from config.settings import get_colors
from models.student_profile import StudentProfile
from models.support import SupportEntry
from models.document import Document
from models.tracking import TrackingLog
from models.evaluation import TwinEvaluation
from ui.components.empty_state import EmptyState
from ui.components.mic_button import MicButton


class TeacherLogImplPage(QWidget):
    """Log implementation: select student, support, add notes, submit."""

    def __init__(self, db_manager, auth_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.auth = auth_manager
        self._profiles: list = []
        self._build_ui()

    def _build_ui(self):
        c = get_colors()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        header = QLabel("Log Implementation")
        header.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {c['text']};")
        header.setAccessibleName("Log Implementation")
        layout.addWidget(header)

        desc = QLabel(
            "Record how you implemented a support for a student and note the outcome."
        )
        desc.setStyleSheet(f"font-size: 14px; color: {c['text_muted']};")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Empty state
        self._empty = EmptyState(
            icon_text="\u270E",
            message="No students available. Import student twins first.",
        )
        self._empty.setVisible(False)
        layout.addWidget(self._empty)

        # Form
        self._form = QWidget()
        form_layout = QVBoxLayout(self._form)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        # Select student
        form_layout.addWidget(QLabel("Student:"))
        self._student_combo = QComboBox()
        self._student_combo.setAccessibleName("Select a student")
        self._student_combo.setFixedHeight(44)
        self._student_combo.currentIndexChanged.connect(self._on_student_changed)
        form_layout.addWidget(self._student_combo)

        # Select support
        form_layout.addWidget(QLabel("Support:"))
        self._support_combo = QComboBox()
        self._support_combo.setAccessibleName("Select a support")
        self._support_combo.setFixedHeight(44)
        form_layout.addWidget(self._support_combo)

        # Implementation notes
        form_layout.addWidget(QLabel("Implementation Notes:"))
        self._impl_notes = QTextEdit()
        self._impl_notes.setPlaceholderText("How did you implement this support?")
        self._impl_notes.setAccessibleName("Implementation notes")
        self._impl_notes.setMaximumHeight(80)
        impl_row = QHBoxLayout()
        impl_row.addWidget(self._impl_notes, stretch=1)
        impl_row.addWidget(MicButton(target=self._impl_notes), alignment=Qt.AlignmentFlag.AlignTop)
        form_layout.addLayout(impl_row)

        # Outcome notes
        form_layout.addWidget(QLabel("Outcome Notes:"))
        self._outcome_notes = QTextEdit()
        self._outcome_notes.setPlaceholderText("What was the observed outcome?")
        self._outcome_notes.setAccessibleName("Outcome notes")
        self._outcome_notes.setMaximumHeight(80)
        outcome_row = QHBoxLayout()
        outcome_row.addWidget(self._outcome_notes, stretch=1)
        outcome_row.addWidget(MicButton(target=self._outcome_notes), alignment=Qt.AlignmentFlag.AlignTop)
        form_layout.addLayout(outcome_row)

        # Submit
        submit_btn = QPushButton("Submit Log")
        submit_btn.setAccessibleName("Submit implementation log")
        submit_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.setFixedHeight(44)
        submit_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {c['primary']}, stop:1 {c['secondary']});
                color: white; border: none; border-radius: 8px;
                padding: 8px 24px; font-weight: bold;
            }}
        """)
        submit_btn.clicked.connect(self._submit)
        form_layout.addWidget(submit_btn)

        layout.addWidget(self._form)

        # Recent logs
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {c['dark_border']};")
        layout.addWidget(sep)

        recent_hdr = QLabel("Recent Logs")
        recent_hdr.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {c['text']};")
        layout.addWidget(recent_hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self._logs_container = QWidget()
        self._logs_layout = QVBoxLayout(self._logs_container)
        self._logs_layout.setSpacing(8)
        self._logs_layout.setContentsMargins(0, 0, 0, 0)
        self._logs_layout.addStretch()
        scroll.setWidget(self._logs_container)
        layout.addWidget(scroll, stretch=1)

    def _on_student_changed(self):
        self._support_combo.clear()
        profile_id = self._student_combo.currentData()
        if not profile_id:
            return

        session = self.db.get_session()
        try:
            supports = session.query(SupportEntry).filter(
                SupportEntry.profile_id == profile_id,
                SupportEntry.status == "active",
            ).all()
            for s in supports:
                sub = s.subcategory or "General"
                self._support_combo.addItem(
                    f"{s.category.title()} - {sub.title()}", s.id
                )
        finally:
            session.close()

    def _submit(self):
        profile_id = self._student_combo.currentData()
        support_id = self._support_combo.currentData()
        impl = self._impl_notes.toPlainText().strip()
        outcome = self._outcome_notes.toPlainText().strip()

        if not profile_id:
            QMessageBox.warning(self, "Missing", "Please select a student.")
            return

        session = self.db.get_session()
        try:
            log = TrackingLog(
                profile_id=profile_id,
                logged_by_role="teacher",
                support_id=support_id,
                implementation_notes=impl if impl else None,
                outcome_notes=outcome if outcome else None,
            )
            session.add(log)
            session.commit()
        finally:
            session.close()

        self._impl_notes.clear()
        self._outcome_notes.clear()
        QMessageBox.information(self, "Success", "Implementation log submitted!")
        self.refresh_data()

    def refresh_data(self):
        user = self.auth.get_current_user()
        if not user:
            return

        session = self.db.get_session()
        try:
            # Get accessible profiles
            import_docs = session.query(Document).filter(
                Document.teacher_user_id == user.id,
                Document.purpose_description == "twin_import",
            ).all()

            profile_ids = set()
            for doc in import_docs:
                evals = session.query(TwinEvaluation).filter(
                    TwinEvaluation.document_id == doc.id
                ).all()
                for ev in evals:
                    profile_ids.add(ev.student_profile_id)

            self._profiles = []
            if profile_ids:
                self._profiles = session.query(StudentProfile).filter(
                    StudentProfile.id.in_(profile_ids)
                ).all()

            if not self._profiles:
                self._empty.setVisible(True)
                self._form.setVisible(False)
                return

            self._empty.setVisible(False)
            self._form.setVisible(True)

            # Populate student combo
            self._student_combo.clear()
            for p in self._profiles:
                self._student_combo.addItem(p.name, p.id)

            # Refresh recent logs
            self._refresh_logs(session)
        finally:
            session.close()

    def _refresh_logs(self, session):
        c = get_colors()

        while self._logs_layout.count() > 1:
            item = self._logs_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        logs = session.query(TrackingLog).filter(
            TrackingLog.logged_by_role == "teacher",
        ).order_by(TrackingLog.created_at.desc()).limit(10).all()

        for log in logs:
            card = QWidget()
            card.setStyleSheet(f"""
                QWidget {{
                    background: {c['dark_card']};
                    border: 1px solid {c['dark_border']};
                    border-radius: 8px;
                }}
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 8, 10, 8)
            card_layout.setSpacing(4)

            # Student name
            profile = session.query(StudentProfile).get(log.profile_id) if log.profile_id else None
            profile_name = profile.name if profile else "Unknown"

            support = session.query(SupportEntry).get(log.support_id) if log.support_id else None
            sup_text = f"{support.category.title()} - {(support.subcategory or 'General').title()}" if support else "General"

            hdr = QLabel(f"{profile_name} — {sup_text}")
            hdr.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {c['text']};")
            card_layout.addWidget(hdr)

            if log.implementation_notes:
                notes = QLabel(log.implementation_notes[:80])
                notes.setStyleSheet(f"font-size: 12px; color: {c['text_muted']};")
                notes.setWordWrap(True)
                card_layout.addWidget(notes)

            if log.outcome_notes:
                outcome = QLabel(log.outcome_notes[:80])
                outcome.setStyleSheet(f"font-size: 12px; color: {c['warning']};")
                card_layout.addWidget(outcome)

            date_str = log.created_at.strftime("%b %d, %Y %H:%M") if log.created_at else ""
            date_lbl = QLabel(date_str)
            date_lbl.setStyleSheet(f"font-size: 11px; color: {c['text_muted']};")
            card_layout.addWidget(date_lbl)

            self._logs_layout.insertWidget(self._logs_layout.count() - 1, card)

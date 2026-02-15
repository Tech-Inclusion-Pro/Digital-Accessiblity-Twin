"""Student log experience page — rate support effectiveness."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QScrollArea, QFrame, QMessageBox,
)
from PyQt6.QtCore import Qt

from config.settings import get_colors
from models.student_profile import StudentProfile
from models.support import SupportEntry
from models.tracking import TrackingLog
from ui.components.rating_widget import RatingWidget
from ui.components.empty_state import EmptyState


class StudentLogExperiencePage(QWidget):
    """Log experience: select support, rate, add notes, submit."""

    def __init__(self, db_manager, auth_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.auth = auth_manager
        self._profile = None
        self._build_ui()

    def _build_ui(self):
        c = get_colors()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        header = QLabel("Log Experience")
        header.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {c['text']};")
        header.setAccessibleName("Log Experience")
        layout.addWidget(header)

        desc = QLabel("Rate how well a support is working and add notes about your experience.")
        desc.setStyleSheet(f"font-size: 14px; color: {c['text_muted']};")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Empty state
        self._empty = EmptyState(
            icon_text="\u270E",
            message="No supports to rate. Add supports in your profile first.",
        )
        self._empty.setVisible(False)
        layout.addWidget(self._empty)

        # Form container
        self._form = QWidget()
        form_layout = QVBoxLayout(self._form)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        # Select support
        form_layout.addWidget(QLabel("Select Support:"))
        self._support_combo = QComboBox()
        self._support_combo.setAccessibleName("Select a support to rate")
        self._support_combo.setFixedHeight(44)
        form_layout.addWidget(self._support_combo)

        # Rating
        self._rating = RatingWidget("Effectiveness Rating:")
        form_layout.addWidget(self._rating)

        # Notes
        form_layout.addWidget(QLabel("Notes:"))
        self._notes = QTextEdit()
        self._notes.setPlaceholderText("How is this support working for you?")
        self._notes.setAccessibleName("Experience notes")
        self._notes.setMaximumHeight(100)
        form_layout.addWidget(self._notes)

        # Submit
        submit_btn = QPushButton("Submit Log")
        submit_btn.setAccessibleName("Submit experience log")
        submit_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.setFixedHeight(44)
        submit_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {c['primary']}, stop:1 {c['tertiary']});
                color: white; border: none; border-radius: 8px;
                padding: 8px 24px; font-weight: bold;
            }}
        """)
        submit_btn.clicked.connect(self._submit)
        form_layout.addWidget(submit_btn)

        layout.addWidget(self._form)

        # Recent logs section
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

    def _submit(self):
        if not self._profile:
            return
        if self._support_combo.count() == 0:
            return

        support_id = self._support_combo.currentData()
        rating = self._rating.get_rating()
        notes = self._notes.toPlainText().strip()

        if rating == 0:
            QMessageBox.warning(self, "Missing Rating", "Please select a rating (1-5).")
            return

        session = self.db.get_session()
        try:
            # Create tracking log
            log = TrackingLog(
                profile_id=self._profile.id,
                logged_by_role="student",
                support_id=support_id,
                implementation_notes=notes if notes else None,
                outcome_notes=f"Effectiveness rated: {rating}/5",
            )
            session.add(log)

            # Update support effectiveness (running average)
            support = session.query(SupportEntry).get(support_id)
            if support:
                if support.effectiveness_rating is not None:
                    support.effectiveness_rating = (
                        support.effectiveness_rating + rating
                    ) / 2
                else:
                    support.effectiveness_rating = float(rating)

            session.commit()
        finally:
            session.close()

        # Reset form
        self._rating.reset()
        self._notes.clear()
        QMessageBox.information(self, "Success", "Experience logged successfully!")
        self.refresh_data()

    def refresh_data(self):
        user = self.auth.get_current_user()
        if not user:
            return

        session = self.db.get_session()
        try:
            self._profile = session.query(StudentProfile).filter(
                StudentProfile.user_id == user.id
            ).first()

            if not self._profile:
                self._empty.setVisible(True)
                self._form.setVisible(False)
                return

            supports = session.query(SupportEntry).filter(
                SupportEntry.profile_id == self._profile.id,
                SupportEntry.status == "active",
            ).all()

            if not supports:
                self._empty.setVisible(True)
                self._form.setVisible(False)
                return

            self._empty.setVisible(False)
            self._form.setVisible(True)

            # Populate support combo
            self._support_combo.clear()
            for s in supports:
                self._support_combo.addItem(
                    f"{s.category.title()}: {s.description[:50]}", s.id
                )

            # Refresh recent logs
            self._refresh_logs(session)
        finally:
            session.close()

    def _refresh_logs(self, session):
        c = get_colors()

        # Clear existing log entries (keep the stretch)
        while self._logs_layout.count() > 1:
            item = self._logs_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._profile:
            return

        logs = session.query(TrackingLog).filter(
            TrackingLog.profile_id == self._profile.id,
            TrackingLog.logged_by_role == "student",
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

            # Support info
            support = session.query(SupportEntry).get(log.support_id) if log.support_id else None
            sup_text = f"{support.category.title()}: {support.description[:40]}" if support else "General"
            sup_lbl = QLabel(sup_text)
            sup_lbl.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {c['text']};")
            card_layout.addWidget(sup_lbl)

            if log.implementation_notes:
                notes_lbl = QLabel(log.implementation_notes[:80])
                notes_lbl.setStyleSheet(f"font-size: 12px; color: {c['text_muted']};")
                notes_lbl.setWordWrap(True)
                card_layout.addWidget(notes_lbl)

            if log.outcome_notes:
                outcome_lbl = QLabel(log.outcome_notes)
                outcome_lbl.setStyleSheet(f"font-size: 12px; color: {c['warning']};")
                card_layout.addWidget(outcome_lbl)

            date_str = log.created_at.strftime("%b %d, %Y %H:%M") if log.created_at else ""
            date_lbl = QLabel(date_str)
            date_lbl.setStyleSheet(f"font-size: 11px; color: {c['text_muted']};")
            card_layout.addWidget(date_lbl)

            self._logs_layout.insertWidget(self._logs_layout.count() - 1, card)

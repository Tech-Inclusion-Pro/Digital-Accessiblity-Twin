"""Student tracking page — recent activity list + placeholders."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt

from config.settings import get_colors
from models.student_profile import StudentProfile
from models.support import SupportEntry
from models.tracking import TrackingLog
from ui.components.empty_state import EmptyState


class StudentTrackingPage(QWidget):
    """Tracking: recent activity list + future timeline/chart placeholders."""

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

        header = QLabel("Tracking & Progress")
        header.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {c['text']};")
        header.setAccessibleName("Tracking and Progress")
        layout.addWidget(header)

        # Recent activity
        activity_hdr = QLabel("Recent Activity")
        activity_hdr.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {c['text']};")
        layout.addWidget(activity_hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self._activity_container = QWidget()
        self._activity_layout = QVBoxLayout(self._activity_container)
        self._activity_layout.setSpacing(8)
        self._activity_layout.setContentsMargins(0, 0, 0, 0)
        self._activity_layout.addStretch()
        scroll.setWidget(self._activity_container)
        layout.addWidget(scroll, stretch=1)

        # Future placeholders
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {c['dark_border']};")
        layout.addWidget(sep)

        timeline_placeholder = EmptyState(
            icon_text="\U0001F4CA",
            message="Timeline view and progress charts coming soon.",
        )
        layout.addWidget(timeline_placeholder)

    def refresh_data(self):
        user = self.auth.get_current_user()
        if not user:
            return

        c = get_colors()

        session = self.db.get_session()
        try:
            self._profile = session.query(StudentProfile).filter(
                StudentProfile.user_id == user.id
            ).first()

            # Clear existing
            while self._activity_layout.count() > 1:
                item = self._activity_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            if not self._profile:
                return

            logs = session.query(TrackingLog).filter(
                TrackingLog.profile_id == self._profile.id,
            ).order_by(TrackingLog.created_at.desc()).limit(20).all()

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

                # Role badge + support
                role_text = log.logged_by_role.title() if log.logged_by_role else ""
                support = session.query(SupportEntry).get(log.support_id) if log.support_id else None
                sup_text = f"{support.category.title()}: {support.description[:40]}" if support else "General"

                hdr = QLabel(f"[{role_text}] {sup_text}")
                hdr.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {c['text']};")
                card_layout.addWidget(hdr)

                if log.implementation_notes:
                    notes = QLabel(log.implementation_notes[:100])
                    notes.setStyleSheet(f"font-size: 12px; color: {c['text_muted']};")
                    notes.setWordWrap(True)
                    card_layout.addWidget(notes)

                if log.outcome_notes:
                    outcome = QLabel(log.outcome_notes[:100])
                    outcome.setStyleSheet(f"font-size: 12px; color: {c['warning']};")
                    card_layout.addWidget(outcome)

                date_str = log.created_at.strftime("%b %d, %Y %H:%M") if log.created_at else ""
                date_lbl = QLabel(date_str)
                date_lbl.setStyleSheet(f"font-size: 11px; color: {c['text_muted']};")
                card_layout.addWidget(date_lbl)

                self._activity_layout.insertWidget(self._activity_layout.count() - 1, card)
        finally:
            session.close()

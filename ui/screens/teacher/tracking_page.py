"""Teacher tracking page — recent activity list + charts & analytics."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt

from config.settings import get_colors
from models.student_profile import StudentProfile
from models.support import SupportEntry
from models.tracking import TrackingLog
from ui.components.empty_state import EmptyState
from ui.components.chart_utils import build_chart_card, group_logs_by_week
from ui.components.timeline_chart import TimelineChart
from ui.components.horizontal_bar_chart import HorizontalBarChart


class TeacherTrackingPage(QWidget):
    """Tracking: recent teacher activity + charts & analytics."""

    def __init__(self, db_manager, auth_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.auth = auth_manager
        self._build_ui()

    def _build_ui(self):
        c = get_colors()
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        header = QLabel("Tracking & Progress")
        header.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {c['text']};")
        header.setAccessibleName("Tracking and Progress")
        layout.addWidget(header)

        # --- Recent activity ---
        activity_hdr = QLabel("Recent Activity")
        activity_hdr.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {c['text']};")
        layout.addWidget(activity_hdr)

        self._activity_container = QWidget()
        self._activity_layout = QVBoxLayout(self._activity_container)
        self._activity_layout.setSpacing(8)
        self._activity_layout.setContentsMargins(0, 0, 0, 0)
        self._activity_layout.addStretch()
        layout.addWidget(self._activity_container)

        # --- Charts & Analytics section ---
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {c['dark_border']};")
        layout.addWidget(sep)

        charts_hdr = QLabel("Charts & Analytics")
        charts_hdr.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {c['text']};")
        layout.addWidget(charts_hdr)

        # Implementation Timeline
        self._timeline_chart = TimelineChart()
        self._timeline_scroll = QScrollArea()
        self._timeline_scroll.setWidgetResizable(False)
        self._timeline_scroll.setWidget(self._timeline_chart)
        self._timeline_scroll.setFixedHeight(168)
        self._timeline_scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )
        self._timeline_card = build_chart_card(
            "Implementation Timeline", self._timeline_scroll
        )
        self._timeline_empty = EmptyState(
            icon_text="\u2630", message="No implementation activity logged yet."
        )
        layout.addWidget(self._timeline_card)
        layout.addWidget(self._timeline_empty)
        self._timeline_empty.hide()

        # Activity by Student
        self._student_bar = HorizontalBarChart()
        self._student_card = build_chart_card(
            "Activity by Student", self._student_bar
        )
        self._student_empty = EmptyState(
            icon_text="\u25C7",
            message="No student activity data available yet.",
        )
        layout.addWidget(self._student_card)
        layout.addWidget(self._student_empty)
        self._student_empty.hide()

        # Implementation Frequency
        self._freq_bar = HorizontalBarChart()
        self._freq_card = build_chart_card(
            "Implementation Frequency", self._freq_bar
        )
        self._freq_empty = EmptyState(
            icon_text="\u25CB",
            message="No weekly frequency data available yet.",
        )
        layout.addWidget(self._freq_card)
        layout.addWidget(self._freq_empty)
        self._freq_empty.hide()

        layout.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll)

    def refresh_data(self):
        user = self.auth.get_current_user()
        if not user:
            return

        c = get_colors()

        session = self.db.get_session()
        try:
            # Clear existing activity cards
            while self._activity_layout.count() > 1:
                item = self._activity_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Get all teacher logs (up to 50 for charts)
            logs = session.query(TrackingLog).filter(
                TrackingLog.logged_by_role == "teacher",
            ).order_by(TrackingLog.created_at.desc()).limit(50).all()

            # Build activity cards (show most recent 20)
            for log in logs[:20]:
                card = self._make_activity_card(log, session, c)
                self._activity_layout.insertWidget(
                    self._activity_layout.count() - 1, card
                )

            # --- Feed charts ---
            if not logs:
                self._show_empty_charts()
                return

            # Batch-load profiles and supports
            profile_ids = {l.profile_id for l in logs if l.profile_id}
            profiles_map = {}
            if profile_ids:
                profiles = session.query(StudentProfile).filter(
                    StudentProfile.id.in_(profile_ids)
                ).all()
                profiles_map = {p.id: p for p in profiles}

            support_ids = {l.support_id for l in logs if l.support_id}
            supports_map = {}
            if support_ids:
                entries = session.query(SupportEntry).filter(
                    SupportEntry.id.in_(support_ids)
                ).all()
                supports_map = {s.id: s for s in entries}

            # Implementation Timeline
            timeline_data = []
            for log in reversed(logs):
                profile = profiles_map.get(log.profile_id)
                sup = supports_map.get(log.support_id)
                label = profile.name if profile else "Unknown"
                cat = sup.category.title() if sup else "General"
                date = log.created_at.strftime("%b %d") if log.created_at else ""
                timeline_data.append({
                    "date": date,
                    "label": label,
                    "sublabel": cat,
                })
            self._timeline_chart.set_data(timeline_data)
            self._timeline_card.setVisible(bool(timeline_data))
            self._timeline_empty.setVisible(not timeline_data)

            # Activity by Student
            from collections import defaultdict
            student_counts: dict[str, int] = defaultdict(int)
            for log in logs:
                profile = profiles_map.get(log.profile_id)
                name = profile.name if profile else "Unknown"
                student_counts[name] += 1
            student_data = sorted(
                [{"label": k, "value": v} for k, v in student_counts.items()],
                key=lambda d: d["value"],
                reverse=True,
            )
            self._student_bar.set_data(student_data)
            self._student_card.setVisible(bool(student_data))
            self._student_empty.setVisible(not student_data)

            # Implementation Frequency (by week)
            freq_data = group_logs_by_week(logs)
            self._freq_bar.set_data(freq_data)
            self._freq_card.setVisible(bool(freq_data))
            self._freq_empty.setVisible(not freq_data)

        finally:
            session.close()

    def _show_empty_charts(self):
        self._timeline_card.hide()
        self._timeline_empty.show()
        self._student_card.hide()
        self._student_empty.show()
        self._freq_card.hide()
        self._freq_empty.show()

    @staticmethod
    def _make_activity_card(log, session, c):
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background: {c['dark_card']};
                border: 1px solid {c['dark_border']};
                border-radius: 8px;
            }}
        """)
        from PyQt6.QtWidgets import QVBoxLayout
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 8, 10, 8)
        card_layout.setSpacing(4)

        profile = session.query(StudentProfile).get(
            log.profile_id
        ) if log.profile_id else None
        profile_name = profile.name if profile else "Unknown"
        support = session.query(SupportEntry).get(
            log.support_id
        ) if log.support_id else None
        sup_text = (
            f"{support.category.title()} - "
            f"{(support.subcategory or 'General').title()}"
            if support else "General"
        )

        hdr = QLabel(f"{profile_name} \u2014 {sup_text}")
        hdr.setStyleSheet(
            f"font-size: 13px; font-weight: bold; color: {c['text']};"
        )
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

        date_str = (
            log.created_at.strftime("%b %d, %Y %H:%M") if log.created_at else ""
        )
        date_lbl = QLabel(date_str)
        date_lbl.setStyleSheet(f"font-size: 11px; color: {c['text_muted']};")
        card_layout.addWidget(date_lbl)

        return card

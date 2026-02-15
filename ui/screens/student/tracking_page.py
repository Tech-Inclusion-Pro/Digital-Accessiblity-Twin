"""Student tracking page — recent activity list + charts & progress."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt

from config.settings import get_colors
from models.student_profile import StudentProfile
from models.support import SupportEntry
from models.tracking import TrackingLog
from ui.components.empty_state import EmptyState
from ui.components.chart_utils import (
    build_chart_card, parse_effectiveness_rating,
    group_logs_by_category,
)
from ui.components.timeline_chart import TimelineChart
from ui.components.line_chart import LineChart
from ui.components.horizontal_bar_chart import HorizontalBarChart


class StudentTrackingPage(QWidget):
    """Tracking: recent activity list + timeline/chart visualizations."""

    def __init__(self, db_manager, auth_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.auth = auth_manager
        self._profile = None
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

        # --- Charts & Progress section ---
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {c['dark_border']};")
        layout.addWidget(sep)

        charts_hdr = QLabel("Charts & Progress")
        charts_hdr.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {c['text']};")
        layout.addWidget(charts_hdr)

        # Activity Timeline
        self._timeline_chart = TimelineChart()
        self._timeline_scroll = QScrollArea()
        self._timeline_scroll.setWidgetResizable(False)
        self._timeline_scroll.setWidget(self._timeline_chart)
        self._timeline_scroll.setFixedHeight(168)
        self._timeline_scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )
        self._timeline_card = build_chart_card("Activity Timeline", self._timeline_scroll)
        self._timeline_empty = EmptyState(
            icon_text="\u2630", message="No activity logged yet."
        )
        layout.addWidget(self._timeline_card)
        layout.addWidget(self._timeline_empty)
        self._timeline_empty.hide()

        # Effectiveness Over Time
        self._line_chart = LineChart()
        self._line_card = build_chart_card("Effectiveness Over Time", self._line_chart)
        self._line_empty = EmptyState(
            icon_text="\u2605",
            message="No effectiveness ratings recorded yet.",
        )
        layout.addWidget(self._line_card)
        layout.addWidget(self._line_empty)
        self._line_empty.hide()

        # Support Category Breakdown
        self._bar_chart = HorizontalBarChart()
        self._bar_card = build_chart_card(
            "Support Category Breakdown", self._bar_chart
        )
        self._bar_empty = EmptyState(
            icon_text="\u25A1",
            message="No support category data available yet.",
        )
        layout.addWidget(self._bar_card)
        layout.addWidget(self._bar_empty)
        self._bar_empty.hide()

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
            self._profile = session.query(StudentProfile).filter(
                StudentProfile.user_id == user.id
            ).first()

            # Clear existing activity cards
            while self._activity_layout.count() > 1:
                item = self._activity_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            if not self._profile:
                self._show_empty_charts()
                return

            logs = session.query(TrackingLog).filter(
                TrackingLog.profile_id == self._profile.id,
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

            # Batch-load all referenced supports
            support_ids = {l.support_id for l in logs if l.support_id}
            supports_map = {}
            if support_ids:
                entries = session.query(SupportEntry).filter(
                    SupportEntry.id.in_(support_ids)
                ).all()
                supports_map = {s.id: s for s in entries}

            # Timeline
            timeline_data = []
            for log in reversed(logs):
                sup = supports_map.get(log.support_id)
                label = sup.category.title() if sup else "General"
                date = log.created_at.strftime("%b %d") if log.created_at else ""
                timeline_data.append({
                    "date": date,
                    "label": label,
                    "sublabel": "",
                })
            self._timeline_chart.set_data(timeline_data)
            self._timeline_card.setVisible(bool(timeline_data))
            self._timeline_empty.setVisible(not timeline_data)

            # Effectiveness line chart
            eff_data = []
            for log in reversed(logs):
                rating = parse_effectiveness_rating(log.outcome_notes)
                if rating is not None:
                    date = log.created_at.strftime("%b %d") if log.created_at else ""
                    eff_data.append({"date": date, "value": rating})
            self._line_chart.set_data(eff_data)
            self._line_card.setVisible(bool(eff_data))
            self._line_empty.setVisible(not eff_data)

            # Category bar chart
            cat_data = group_logs_by_category(logs, supports_map)
            self._bar_chart.set_data(cat_data)
            self._bar_card.setVisible(bool(cat_data))
            self._bar_empty.setVisible(not cat_data)

        finally:
            session.close()

    def _show_empty_charts(self):
        self._timeline_card.hide()
        self._timeline_empty.show()
        self._line_card.hide()
        self._line_empty.show()
        self._bar_card.hide()
        self._bar_empty.show()

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

        role_text = log.logged_by_role.title() if log.logged_by_role else ""
        support = session.query(SupportEntry).get(
            log.support_id
        ) if log.support_id else None
        sup_text = (
            f"{support.category.title()}: {support.description[:40]}"
            if support else "General"
        )

        hdr = QLabel(f"[{role_text}] {sup_text}")
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

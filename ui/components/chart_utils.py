"""Shared helpers for chart components."""

import re
from collections import defaultdict
from datetime import timedelta

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

from config.settings import get_colors

# 8-color palette drawn from the brand theme.
CHART_PALETTE = [
    "#6f2fa6",  # primary purple
    "#a23b84",  # tertiary pink
    "#3a2b95",  # secondary blue
    "#28a745",  # success green
    "#ffc107",  # warning yellow
    "#b065d6",  # light purple
    "#0f3460",  # dark input blue
    "#ff4d5e",  # error red
]


def parse_effectiveness_rating(outcome_notes: str) -> float | None:
    """Extract 'Effectiveness rated: X/5' from outcome notes, return float or None."""
    if not outcome_notes:
        return None
    m = re.search(r"[Ee]ffectiveness\s+rated:\s*(\d+(?:\.\d+)?)\s*/\s*5", outcome_notes)
    if m:
        return float(m.group(1))
    return None


def group_logs_by_week(logs) -> list[dict]:
    """Group logs by ISO week, return [{"label": "Jan 6", "value": count}, ...]."""
    if not logs:
        return []
    buckets: dict[str, int] = defaultdict(int)
    week_starts: dict[str, object] = {}
    for log in logs:
        dt = log.created_at
        if not dt:
            continue
        # Monday of the ISO week
        monday = dt - timedelta(days=dt.weekday())
        key = monday.strftime("%Y-%m-%d")
        buckets[key] += 1
        if key not in week_starts:
            week_starts[key] = monday
    result = []
    for key in sorted(buckets):
        label = week_starts[key].strftime("%b %d")
        result.append({"label": label, "value": buckets[key]})
    return result


def group_logs_by_category(logs, supports_map: dict) -> list[dict]:
    """Group logs by support category, return [{"label": "Sensory", "value": 3}, ...].

    supports_map maps support_id → SupportEntry (or object with .category).
    """
    if not logs:
        return []
    counts: dict[str, int] = defaultdict(int)
    for log in logs:
        support = supports_map.get(log.support_id)
        cat = support.category.title() if support and support.category else "General"
        counts[cat] += 1
    result = sorted(
        [{"label": k, "value": v} for k, v in counts.items()],
        key=lambda d: d["value"],
        reverse=True,
    )
    return result


def build_chart_card(title: str, chart_widget: QWidget) -> QWidget:
    """Wrap a chart widget in a styled dark card with a title label."""
    c = get_colors()
    card = QWidget()
    card.setStyleSheet(f"""
        QWidget {{
            background: {c['dark_card']};
            border: 1px solid {c['dark_border']};
            border-radius: 12px;
        }}
    """)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(16, 12, 16, 12)
    layout.setSpacing(8)

    lbl = QLabel(title)
    lbl.setStyleSheet(
        f"font-size: 14px; font-weight: bold; color: {c['text']}; "
        "border: none; background: transparent;"
    )
    lbl.setAccessibleName(title)
    layout.addWidget(lbl)

    chart_widget.setStyleSheet(
        chart_widget.styleSheet() + " border: none; background: transparent;"
    )
    layout.addWidget(chart_widget)

    return card

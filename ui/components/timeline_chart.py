"""Horizontal timeline chart widget drawn with QPainter."""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen

from config.settings import get_colors
from ui.components.chart_utils import CHART_PALETTE

MAX_ENTRIES = 15


class TimelineChart(QWidget):
    """Horizontal timeline — colored dots on a line, labels above, dates below."""

    DOT_RADIUS = 6
    FIXED_HEIGHT = 160
    ENTRY_WIDTH = 100

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: list[dict] = []
        self.setFixedHeight(self.FIXED_HEIGHT)
        self.setAccessibleName("Activity timeline")
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)

    def set_data(self, data: list[dict]):
        """Set data as [{"date": str, "label": str, "sublabel": str}, ...].

        Most recent entries last.  Capped to MAX_ENTRIES.
        """
        self._data = (data or [])[-MAX_ENTRIES:]
        total_w = max(self.ENTRY_WIDTH * len(self._data) + 40, 200)
        self.setMinimumWidth(total_w)
        self._update_accessible_description()
        self.update()

    def _update_accessible_description(self):
        if not self._data:
            self.setAccessibleDescription("No timeline entries.")
            return
        parts = [f"{d.get('date', '?')}: {d.get('label', '')}" for d in self._data[-6:]]
        desc = f"Timeline with {len(self._data)} entries. Recent: " + "; ".join(parts)
        self.setAccessibleDescription(desc)

    def paintEvent(self, event):
        if not self._data:
            return
        c = get_colors()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        n = len(self._data)
        h = self.height()
        mid_y = h * 0.55

        # Compute x positions
        pad_l = 20
        pad_r = 20
        avail = max(self.width() - pad_l - pad_r, 100)
        spacing = avail / max(n - 1, 1) if n > 1 else 0
        xs = [pad_l + i * spacing for i in range(n)]

        # Horizontal line
        line_pen = QPen(QColor(c["dark_border"]), 2)
        painter.setPen(line_pen)
        painter.drawLine(QPointF(xs[0], mid_y), QPointF(xs[-1], mid_y))

        label_font = QFont()
        label_font.setPixelSize(11)
        date_font = QFont()
        date_font.setPixelSize(10)

        for i, item in enumerate(self._data):
            cx = xs[i]
            color = QColor(CHART_PALETTE[i % len(CHART_PALETTE)])

            # Dot
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawEllipse(QPointF(cx, mid_y), self.DOT_RADIUS, self.DOT_RADIUS)

            # Label above
            painter.setPen(QPen(QColor(c["text"])))
            painter.setFont(label_font)
            label_rect = QRectF(cx - 45, mid_y - 50, 90, 36)
            painter.drawText(
                label_rect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
                item.get("label", "")[:18],
            )

            # Sublabel (date) below
            painter.setPen(QPen(QColor(c["text_muted"])))
            painter.setFont(date_font)
            date_rect = QRectF(cx - 45, mid_y + 12, 90, 30)
            painter.drawText(
                date_rect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                item.get("date", ""),
            )
            # Extra sublabel line
            sublabel = item.get("sublabel", "")
            if sublabel:
                sub_rect = QRectF(cx - 45, mid_y + 26, 90, 30)
                painter.drawText(
                    sub_rect,
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                    sublabel[:18],
                )

        # Focus indicator
        if self.hasFocus():
            focus_pen = QPen(QColor(c["primary"]), 2, Qt.PenStyle.DashLine)
            painter.setPen(focus_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(
                QRectF(1, 1, self.width() - 2, h - 2), 4, 4
            )

        painter.end()

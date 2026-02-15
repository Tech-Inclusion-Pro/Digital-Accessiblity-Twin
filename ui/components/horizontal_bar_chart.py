"""Horizontal bar chart widget drawn with QPainter."""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen

from config.settings import get_colors
from ui.components.chart_utils import CHART_PALETTE


class HorizontalBarChart(QWidget):
    """Horizontal bar chart — labels on left, rounded bars, value on right."""

    BAR_HEIGHT = 20
    ROW_SPACING = 8
    LABEL_WIDTH = 100
    VALUE_WIDTH = 36
    PADDING_TOP = 4
    PADDING_BOTTOM = 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: list[dict] = []
        self.setAccessibleName("Horizontal bar chart")
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)

    def set_data(self, data: list[dict]):
        """Set data as [{"label": str, "value": int/float}, ...]."""
        self._data = data or []
        row_h = self.BAR_HEIGHT + self.ROW_SPACING
        total = self.PADDING_TOP + row_h * max(len(self._data), 1) + self.PADDING_BOTTOM
        self.setFixedHeight(total)
        self._update_accessible_description()
        self.update()

    def _update_accessible_description(self):
        """Build a text summary of the chart data for screen readers."""
        if not self._data:
            self.setAccessibleDescription("No data available.")
            return
        parts = [f"{d['label']}: {d['value']}" for d in self._data]
        self.setAccessibleDescription("Bar chart data: " + "; ".join(parts))

    def paintEvent(self, event):
        if not self._data:
            return
        c = get_colors()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        max_val = max(d["value"] for d in self._data) or 1
        w = self.width()
        bar_area = w - self.LABEL_WIDTH - self.VALUE_WIDTH - 8

        font = QFont()
        font.setPixelSize(12)
        painter.setFont(font)

        y = self.PADDING_TOP
        for i, item in enumerate(self._data):
            color = QColor(CHART_PALETTE[i % len(CHART_PALETTE)])

            # Label
            painter.setPen(QPen(QColor(c["text_muted"])))
            label_rect = QRectF(0, y, self.LABEL_WIDTH - 4, self.BAR_HEIGHT)
            painter.drawText(
                label_rect,
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                item["label"][:14],
            )

            # Bar
            bar_w = max(4, (item["value"] / max_val) * bar_area)
            bar_rect = QRectF(self.LABEL_WIDTH, y + 2, bar_w, self.BAR_HEIGHT - 4)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawRoundedRect(bar_rect, 4, 4)

            # Value
            painter.setPen(QPen(QColor(c["text"])))
            val_rect = QRectF(
                self.LABEL_WIDTH + bar_area + 4, y, self.VALUE_WIDTH, self.BAR_HEIGHT,
            )
            painter.drawText(
                val_rect,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                str(item["value"]),
            )

            y += self.BAR_HEIGHT + self.ROW_SPACING

        # Focus indicator
        if self.hasFocus():
            focus_pen = QPen(QColor(c["primary"]), 2, Qt.PenStyle.DashLine)
            painter.setPen(focus_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(QRectF(1, 1, w - 2, self.height() - 2), 4, 4)

        painter.end()

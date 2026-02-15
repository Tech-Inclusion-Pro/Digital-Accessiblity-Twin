"""Line chart widget drawn with QPainter (effectiveness trends)."""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QPainterPath, QLinearGradient

from config.settings import get_colors
from ui.components.chart_utils import CHART_PALETTE


class LineChart(QWidget):
    """Line chart — Y-axis 1-5, grid lines, connected dots with filled area."""

    FIXED_HEIGHT = 200
    PAD_LEFT = 30
    PAD_RIGHT = 16
    PAD_TOP = 16
    PAD_BOTTOM = 28

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: list[dict] = []
        self.setFixedHeight(self.FIXED_HEIGHT)
        self.setAccessibleName("Effectiveness trend line chart")
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)

    def set_data(self, data: list[dict]):
        """Set data as [{"date": str, "value": float (1-5)}, ...]."""
        self._data = data or []
        self._update_accessible_description()
        self.update()

    def _update_accessible_description(self):
        if not self._data:
            self.setAccessibleDescription("No data available.")
            return
        vals = [d["value"] for d in self._data]
        avg = sum(vals) / len(vals)
        parts = [f"{d.get('date', '?')}: {d['value']:.1f}" for d in self._data[-6:]]
        desc = f"Effectiveness trend with {len(self._data)} data points. Average: {avg:.1f}/5. Recent: " + "; ".join(parts)
        self.setAccessibleDescription(desc)

    def paintEvent(self, event):
        if not self._data:
            return
        c = get_colors()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        plot_x = self.PAD_LEFT
        plot_y = self.PAD_TOP
        plot_w = w - self.PAD_LEFT - self.PAD_RIGHT
        plot_h = h - self.PAD_TOP - self.PAD_BOTTOM

        if plot_w < 10 or plot_h < 10:
            painter.end()
            return

        grid_pen = QPen(QColor(c["dark_border"]), 1, Qt.PenStyle.DotLine)
        label_font = QFont()
        label_font.setPixelSize(10)
        painter.setFont(label_font)

        # Y-axis grid lines and labels (1 through 5)
        for val in range(1, 6):
            y = plot_y + plot_h - ((val - 1) / 4) * plot_h
            painter.setPen(grid_pen)
            painter.drawLine(QPointF(plot_x, y), QPointF(plot_x + plot_w, y))
            painter.setPen(QPen(QColor(c["text_muted"])))
            painter.drawText(QRectF(0, y - 8, self.PAD_LEFT - 4, 16),
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                             str(val))

        # Map data to screen points
        n = len(self._data)
        points: list[QPointF] = []
        for i, item in enumerate(self._data):
            x = plot_x + (i / max(n - 1, 1)) * plot_w if n > 1 else plot_x + plot_w / 2
            val = max(1.0, min(5.0, item["value"]))
            y = plot_y + plot_h - ((val - 1) / 4) * plot_h
            points.append(QPointF(x, y))

        line_color = QColor(CHART_PALETTE[0])

        # Filled area under curve
        if len(points) >= 2:
            fill_path = QPainterPath()
            fill_path.moveTo(QPointF(points[0].x(), plot_y + plot_h))
            for p in points:
                fill_path.lineTo(p)
            fill_path.lineTo(QPointF(points[-1].x(), plot_y + plot_h))
            fill_path.closeSubpath()

            gradient = QLinearGradient(0, plot_y, 0, plot_y + plot_h)
            fill = QColor(line_color)
            fill.setAlpha(60)
            gradient.setColorAt(0, fill)
            fill_bottom = QColor(line_color)
            fill_bottom.setAlpha(10)
            gradient.setColorAt(1, fill_bottom)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(gradient)
            painter.drawPath(fill_path)

        # Line
        line_pen = QPen(line_color, 2)
        painter.setPen(line_pen)
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i + 1])

        # Dots
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(line_color)
        for p in points:
            painter.drawEllipse(p, 4, 4)

        # Date labels along x-axis
        painter.setPen(QPen(QColor(c["text_muted"])))
        painter.setFont(label_font)
        # Show at most 6 labels to avoid overlap
        step = max(1, n // 6)
        for i in range(0, n, step):
            x = points[i].x()
            rect = QRectF(x - 30, plot_y + plot_h + 4, 60, 20)
            painter.drawText(rect,
                             Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                             self._data[i].get("date", ""))

        # Focus indicator
        if self.hasFocus():
            focus_pen = QPen(QColor(c["primary"]), 2, Qt.PenStyle.DashLine)
            painter.setPen(focus_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(QRectF(1, 1, w - 2, h - 2), 4, 4)

        painter.end()

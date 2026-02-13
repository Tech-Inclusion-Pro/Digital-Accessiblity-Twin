"""Cursor trail overlay widget (extracted from IDW main_window pattern)."""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor, QPainter


class CursorTrailOverlay(QWidget):
    """Transparent overlay that paints fading cursor images at recent positions."""

    TRAIL_LENGTH = 8
    UPDATE_MS = 20
    MIN_DISTANCE_SQ = 36

    def __init__(self, cursor_pixmap, hot_x, hot_y, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._pixmap = cursor_pixmap
        self._hot_x = hot_x
        self._hot_y = hot_y
        self._points = []
        self._last_global = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def start(self):
        self.setGeometry(self.parentWidget().rect())
        self.raise_()
        self.show()
        self._timer.start(self.UPDATE_MS)

    def stop(self):
        self._timer.stop()
        self._points.clear()
        self.hide()

    def _tick(self):
        gpos = QCursor.pos()
        if self._last_global is not None:
            dx = gpos.x() - self._last_global.x()
            dy = gpos.y() - self._last_global.y()
            if dx * dx + dy * dy < self.MIN_DISTANCE_SQ:
                return
        self._last_global = gpos
        self._points.append(self.mapFromGlobal(gpos))
        if len(self._points) > self.TRAIL_LENGTH:
            self._points.pop(0)
        self.update()

    def paintEvent(self, event):
        if len(self._points) < 2:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        n = len(self._points) - 1
        for i in range(n):
            frac = (i + 1) / (n + 1)
            painter.setOpacity(frac * 0.35)
            scale = 0.4 + frac * 0.6
            w = int(self._pixmap.width() * scale)
            h = int(self._pixmap.height() * scale)
            x = self._points[i].x() - int(self._hot_x * scale)
            y = self._points[i].y() - int(self._hot_y * scale)
            painter.drawPixmap(x, y, w, h, self._pixmap)
        painter.end()

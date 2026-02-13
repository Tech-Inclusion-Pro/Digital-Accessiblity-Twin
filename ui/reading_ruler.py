"""Reading ruler overlay — horizontal highlight band that follows cursor Y."""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QCursor, QPainter


class ReadingRulerOverlay(QWidget):
    """Semi-transparent horizontal band that tracks the cursor's Y position."""

    BAND_HEIGHT = 40
    UPDATE_MS = 30

    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._y = 0
        self._band_color = QColor(255, 255, 100, 40)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def start(self):
        self.setGeometry(self.parentWidget().rect())
        self.raise_()
        self.show()
        self._timer.start(self.UPDATE_MS)

    def stop(self):
        self._timer.stop()
        self.hide()

    def _tick(self):
        gpos = QCursor.pos()
        local = self.mapFromGlobal(gpos)
        new_y = local.y()
        if new_y != self._y:
            self._y = new_y
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        top = self._y - self.BAND_HEIGHT // 2
        painter.fillRect(0, top, self.width(), self.BAND_HEIGHT, self._band_color)
        # Thin border lines
        border = QColor(255, 255, 100, 80)
        painter.setPen(border)
        painter.drawLine(0, top, self.width(), top)
        painter.drawLine(0, top + self.BAND_HEIGHT, self.width(), top + self.BAND_HEIGHT)
        painter.end()

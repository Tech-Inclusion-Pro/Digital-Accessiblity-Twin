"""Focus management for keyboard navigation and screen reader announcements."""

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer


class FocusManager:
    """Utility for keyboard navigation, tab trapping in modals, and screen reader hints."""

    @staticmethod
    def set_focus_after_transition(widget: QWidget, delay_ms: int = 100):
        """Set focus to widget after a short delay (post screen transition)."""
        QTimer.singleShot(delay_ms, lambda: widget.setFocus(Qt.FocusReason.OtherFocusReason))

    @staticmethod
    def announce(text: str):
        """Announce text to screen readers via accessible description on the active window."""
        window = QApplication.activeWindow()
        if window:
            window.setAccessibleDescription(text)

    @staticmethod
    def setup_tab_trapping(dialog: QWidget, focusable_widgets: list):
        """Install an event filter to trap Tab/Shift+Tab within a dialog."""
        _filter = _TabTrapFilter(focusable_widgets, dialog)
        dialog.installEventFilter(_filter)
        return _filter


class _TabTrapFilter:
    """Event filter that wraps focus within a list of widgets."""

    def __init__(self, widgets: list, parent):
        from PyQt6.QtCore import QObject
        # We store as plain list; parent keeps a reference to prevent GC
        self._widgets = [w for w in widgets if w is not None]
        self._parent = parent
        self._qobj = _TabTrapQObject(self._widgets, parent)

    def eventFilter(self, obj, event):
        return self._qobj.eventFilter(obj, event)


from PyQt6.QtCore import QObject, QEvent


class _TabTrapQObject(QObject):
    def __init__(self, widgets, parent):
        super().__init__(parent)
        self._widgets = widgets

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Tab:
                current = QApplication.focusWidget()
                if current in self._widgets:
                    idx = self._widgets.index(current)
                    if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                        next_idx = (idx - 1) % len(self._widgets)
                    else:
                        next_idx = (idx + 1) % len(self._widgets)
                    self._widgets[next_idx].setFocus(Qt.FocusReason.TabFocusReason)
                    return True
        return False

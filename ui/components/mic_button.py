"""Reusable microphone button for speech-to-text input."""

from PyQt6.QtWidgets import QPushButton, QLineEdit, QTextEdit, QMessageBox
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor

from config.settings import get_colors
from stt.engine import is_available, STTEngine
from stt.stt_settings_store import load_stt_settings


class MicButton(QPushButton):
    """Microphone button that records speech and appends text to a target widget.

    Constructor: ``MicButton(target=some_qlineedit_or_qtextedit)``

    Flow: click to record → click to stop → transcribe → append text
    """

    def __init__(self, target, parent=None):
        super().__init__(parent)
        self._target = target
        self._state = "idle"  # idle | recording | transcribing
        self._record_worker = None
        self._transcribe_worker = None
        self._pulse_timer = QTimer(self)
        self._pulse_timer.setInterval(500)
        self._pulse_on = False
        self._pulse_timer.timeout.connect(self._pulse_tick)

        self.setFixedSize(44, 44)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName("Microphone — speech to text")
        self.setAccessibleDescription("Click to start or stop voice recording")
        self.setToolTip("Speech to text")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_idle_style()
        self.clicked.connect(self._on_click)

    # ---------------------------------------------------------------- styles

    def _apply_idle_style(self):
        c = get_colors()
        self.setText("")
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['dark_input']};
                color: {c['text']};
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 22px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {c['primary']};
            }}
        """)

    def _apply_recording_style(self, bright=True):
        color = "#e53935" if bright else "#b71c1c"
        self.setText("\u23F9")  # stop icon
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 18px;
            }}
        """)

    def _apply_transcribing_style(self):
        c = get_colors()
        self.setText("")
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {c.get('warning', '#FFA726')};
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 18px;
            }}
        """)

    # ---------------------------------------------------------------- paint

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._state == "idle":
            self._paint_mic_icon()
        elif self._state == "transcribing":
            self._paint_hourglass_icon()

    def _paint_mic_icon(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(255, 255, 255), 1.8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        cx = self.width() / 2
        cy = self.height() / 2

        # Microphone body (rounded capsule)
        body_w, body_h = 10, 16
        body_rect = QRectF(cx - body_w / 2, cy - body_h / 2 - 3,
                           body_w, body_h)
        painter.drawRoundedRect(body_rect, body_w / 2, body_w / 2)

        # Arc / cradle below the body
        arc_w, arc_h = 18, 20
        arc_rect = QRectF(cx - arc_w / 2, cy - arc_h / 2 - 3,
                          arc_w, arc_h)
        painter.drawArc(arc_rect, -10 * 16, -160 * 16)

        # Vertical stem from arc bottom to stand
        stem_top = cy - 3 + arc_h / 2
        stem_bottom = stem_top + 5
        painter.drawLine(int(cx), int(stem_top), int(cx), int(stem_bottom))

        # Stand base
        base_w = 8
        painter.drawLine(int(cx - base_w / 2), int(stem_bottom),
                         int(cx + base_w / 2), int(stem_bottom))

        painter.end()

    def _paint_hourglass_icon(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(255, 255, 255), 1.8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        cx = self.width() / 2
        cy = self.height() / 2
        half_w = 7
        half_h = 10

        # Top horizontal line
        painter.drawLine(int(cx - half_w), int(cy - half_h),
                         int(cx + half_w), int(cy - half_h))
        # Top triangle sides pinch to center
        painter.drawLine(int(cx - half_w), int(cy - half_h),
                         int(cx), int(cy))
        painter.drawLine(int(cx + half_w), int(cy - half_h),
                         int(cx), int(cy))
        # Bottom triangle sides expand from center
        painter.drawLine(int(cx), int(cy),
                         int(cx - half_w), int(cy + half_h))
        painter.drawLine(int(cx), int(cy),
                         int(cx + half_w), int(cy + half_h))
        # Bottom horizontal line
        painter.drawLine(int(cx - half_w), int(cy + half_h),
                         int(cx + half_w), int(cy + half_h))

        painter.end()

    # ---------------------------------------------------------------- pulse

    def _pulse_tick(self):
        self._pulse_on = not self._pulse_on
        self._apply_recording_style(bright=self._pulse_on)

    # ---------------------------------------------------------------- click

    def _on_click(self):
        if self._state == "idle":
            self._start_recording()
        elif self._state == "recording":
            self._stop_recording()

    def _start_recording(self):
        if not is_available():
            QMessageBox.warning(
                self.window(), "Missing Package",
                "The 'faster-whisper' package is not installed.\n"
                "Install it with: pip install faster-whisper"
            )
            return

        # Check if model is cached; if not, show download dialog
        settings = load_stt_settings()
        engine = STTEngine()
        if not engine.is_model_cached(settings["model_size"]):
            from ui.components.model_download_dialog import ModelDownloadDialog
            dlg = ModelDownloadDialog(self.window())
            dlg.start()
            if dlg.exec() != ModelDownloadDialog.DialogCode.Accepted:
                return
        else:
            try:
                engine.load_model()
            except Exception as e:
                QMessageBox.critical(
                    self.window(), "Model Error",
                    f"Failed to load speech model: {e}"
                )
                return

        from stt.workers import AudioRecordWorker
        self._state = "recording"
        self._apply_recording_style()
        self._pulse_timer.start()
        self.setAccessibleName("Stop recording")

        self._record_worker = AudioRecordWorker(self)
        self._record_worker.finished_signal.connect(self._on_audio_ready)
        self._record_worker.error_signal.connect(self._on_record_error)
        self._record_worker.start()

    def _stop_recording(self):
        self._pulse_timer.stop()
        if self._record_worker:
            self._record_worker.stop_recording()

    # ---------------------------------------------------------------- callbacks

    def _on_audio_ready(self, audio_array):
        self._state = "transcribing"
        self._apply_transcribing_style()
        self.setAccessibleName("Transcribing speech...")
        self.setEnabled(False)

        from stt.workers import TranscribeWorker
        self._transcribe_worker = TranscribeWorker(audio_array, self)
        self._transcribe_worker.transcription_ready.connect(self._on_text_ready)
        self._transcribe_worker.error_signal.connect(self._on_transcribe_error)
        self._transcribe_worker.finished_signal.connect(self._on_transcribe_done)
        self._transcribe_worker.start()

    def _on_text_ready(self, text: str):
        if not text.strip():
            QMessageBox.information(
                self.window(), "Speech to Text",
                "No speech was detected in the recording."
            )
            return
        self._append_text(text)

    def _on_transcribe_done(self):
        self._state = "idle"
        self._apply_idle_style()
        self.setEnabled(True)
        self.setAccessibleName("Microphone — speech to text")

    def _on_record_error(self, msg: str):
        self._state = "idle"
        self._pulse_timer.stop()
        self._apply_idle_style()
        self.setAccessibleName("Microphone — speech to text")
        QMessageBox.warning(self.window(), "Recording Error", msg)

    def _on_transcribe_error(self, msg: str):
        QMessageBox.warning(self.window(), "Transcription Error", msg)

    # ---------------------------------------------------------------- helpers

    def _append_text(self, text: str):
        """Insert transcribed text at the current cursor position.

        A space is added before the text if the character immediately
        before the cursor is not already a space (or the field is empty).
        This lets users freely mix typing and dictation.
        """
        if isinstance(self._target, QLineEdit):
            pos = self._target.cursorPosition()
            current = self._target.text()
            before = current[:pos]
            separator = " " if before and not before.endswith(" ") else ""
            new_text = before + separator + text + current[pos:]
            self._target.setText(new_text)
            self._target.setCursorPosition(pos + len(separator) + len(text))
        elif isinstance(self._target, QTextEdit):
            cursor = self._target.textCursor()
            before = self._target.toPlainText()[:cursor.position()]
            separator = " " if before and not before.endswith(" ") else ""
            cursor.insertText(separator + text)
            self._target.setTextCursor(cursor)

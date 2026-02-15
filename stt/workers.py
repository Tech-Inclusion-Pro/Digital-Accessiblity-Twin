"""QThread workers for STT recording, transcription, and model download."""

import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

from stt.engine import STTEngine


class AudioRecordWorker(QThread):
    """Records from the microphone via sounddevice at 16kHz mono.

    Call ``stop_recording()`` to end capture. Emits the audio as a numpy array.
    """

    finished_signal = pyqtSignal(np.ndarray)
    error_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False

    def stop_recording(self):
        self._running = False

    def run(self):
        try:
            import sounddevice as sd
        except ImportError:
            self.error_signal.emit(
                "The 'sounddevice' package is not installed.\n"
                "Install it with: pip install sounddevice"
            )
            return

        sample_rate = 16000
        channels = 1
        chunks: list[np.ndarray] = []
        self._running = True

        try:
            with sd.InputStream(samplerate=sample_rate, channels=channels,
                                dtype="float32") as stream:
                while self._running:
                    data, _ = stream.read(int(sample_rate * 0.1))  # 100ms chunks
                    chunks.append(data.copy())
        except Exception as e:
            self.error_signal.emit(f"Microphone error: {e}")
            return

        if not chunks:
            self.error_signal.emit("No audio was recorded.")
            return

        audio = np.concatenate(chunks, axis=0).flatten()
        self.finished_signal.emit(audio)


class TranscribeWorker(QThread):
    """Runs STTEngine.transcribe() on an audio array in a background thread."""

    transcription_ready = pyqtSignal(str)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, audio_array: np.ndarray, parent=None):
        super().__init__(parent)
        self._audio = audio_array

    def run(self):
        try:
            engine = STTEngine()
            text = engine.transcribe(self._audio)
            self.transcription_ready.emit(text)
        except Exception as e:
            self.error_signal.emit(f"Transcription error: {e}")
        finally:
            self.finished_signal.emit()


class ModelDownloadWorker(QThread):
    """Calls STTEngine.load_model() to trigger model download/load."""

    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        try:
            engine = STTEngine()
            engine.load_model()
        except Exception as e:
            self.error_signal.emit(f"Model download failed: {e}")
        finally:
            self.finished_signal.emit()


class LiveDictationWorker(QThread):
    """Records audio via blocking reads and transcribes periodically.

    Uses the same proven blocking-read approach as AudioRecordWorker,
    with periodic transcription of all accumulated audio for live updates.
    """

    partial_text = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    SAMPLE_RATE = 16000
    # Transcribe every N chunks. Each chunk is 100ms, so 30 = every 3 seconds.
    TRANSCRIBE_EVERY = 30
    # Minimum chunks before first transcription (2 seconds).
    MIN_CHUNKS = 20

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False

    def stop_recording(self):
        self._running = False

    def run(self):
        try:
            import sounddevice as sd
        except ImportError:
            self.error_signal.emit(
                "The 'sounddevice' package is not installed.\n"
                "Install it with: pip install sounddevice"
            )
            return

        self._running = True
        chunks: list[np.ndarray] = []
        engine = STTEngine()
        chunk_counter = 0

        try:
            with sd.InputStream(samplerate=self.SAMPLE_RATE, channels=1,
                                dtype="float32") as stream:
                while self._running:
                    data, _ = stream.read(int(self.SAMPLE_RATE * 0.1))
                    chunks.append(data.copy())
                    chunk_counter += 1

                    if (chunk_counter % self.TRANSCRIBE_EVERY == 0
                            and len(chunks) >= self.MIN_CHUNKS):
                        audio = np.concatenate(chunks, axis=0).flatten()
                        try:
                            text = engine.transcribe(audio)
                            if text.strip():
                                self.partial_text.emit(text.strip())
                        except Exception:
                            pass
        except Exception as e:
            self.error_signal.emit(f"Microphone error: {e}")
            self.finished_signal.emit()
            return

        # Final transcription with all captured audio.
        if chunks:
            audio = np.concatenate(chunks, axis=0).flatten()
            try:
                text = engine.transcribe(audio)
                if text.strip():
                    self.partial_text.emit(text.strip())
            except Exception as e:
                self.error_signal.emit(f"Transcription error: {e}")

        self.finished_signal.emit()

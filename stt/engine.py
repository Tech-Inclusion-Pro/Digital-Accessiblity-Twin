"""STT Engine — thread-safe singleton managing the faster-whisper model."""

import threading
from pathlib import Path

import numpy as np

from stt.stt_settings_store import load_stt_settings

_DOWNLOAD_ROOT = Path.home() / ".accesstwin" / "whisper_models"


def is_available() -> bool:
    """Check if faster-whisper is installed."""
    try:
        import faster_whisper  # noqa: F401
        return True
    except ImportError:
        return False


class STTEngine:
    """Thread-safe singleton for faster-whisper model lifecycle."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._model = None
                cls._instance._loaded_size = None
            return cls._instance

    @staticmethod
    def is_model_cached(model_size: str) -> bool:
        """Check if model files exist locally."""
        model_dir = _DOWNLOAD_ROOT / f"models--Systran--faster-whisper-{model_size}"
        return model_dir.exists() and any(model_dir.rglob("model.bin"))

    def load_model(self):
        """Load or reload the whisper model based on current settings."""
        from faster_whisper import WhisperModel

        settings = load_stt_settings()
        size = settings["model_size"]
        device = settings["device"]
        compute_type = settings["compute_type"]

        with self._lock:
            if self._model is not None and self._loaded_size == size:
                return
            _DOWNLOAD_ROOT.mkdir(parents=True, exist_ok=True)
            self._model = WhisperModel(
                size,
                device=device,
                compute_type=compute_type,
                download_root=str(_DOWNLOAD_ROOT),
            )
            self._loaded_size = size

    def transcribe(self, audio_array) -> str:
        """Run transcription on a numpy audio array (16kHz mono float32).

        Returns the transcribed text string.
        """
        with self._lock:
            if self._model is None:
                raise RuntimeError("Model not loaded. Call load_model() first.")
            model = self._model

        # The MacBook Pro mic can produce values outside [-1, 1] when
        # recording at 16kHz (native rate is 48kHz).  Whisper expects
        # audio in [-1, 1], so we must normalise first.
        peak = float(np.max(np.abs(audio_array)))
        if peak > 1.0:
            audio_array = (audio_array / peak).astype(np.float32)

        settings = load_stt_settings()
        segments, _ = model.transcribe(
            audio_array,
            language=settings["language"],
            beam_size=5,
            condition_on_previous_text=False,
        )
        return " ".join(seg.text.strip() for seg in segments).strip()

    def unload(self):
        """Release the model from memory."""
        with self._lock:
            self._model = None
            self._loaded_size = None

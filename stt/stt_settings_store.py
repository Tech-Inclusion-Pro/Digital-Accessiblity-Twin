"""STT settings persistence — save/load to ~/.accesstwin/stt_settings.json."""

import json
from pathlib import Path

_SETTINGS_DIR = Path.home() / ".accesstwin"
_SETTINGS_FILE = _SETTINGS_DIR / "stt_settings.json"

_DEFAULTS = {
    "model_size": "small",
    "language": "en",
    "compute_type": "int8",
    "device": "cpu",
}


def load_stt_settings() -> dict:
    try:
        if _SETTINGS_FILE.exists():
            data = json.loads(_SETTINGS_FILE.read_text())
            result = {**_DEFAULTS, **data}
            # Migrate: "base" model is too small for reliable dictation.
            if result.get("model_size") == "base":
                result["model_size"] = "small"
            return result
    except Exception:
        pass
    return dict(_DEFAULTS)


def save_stt_settings(data: dict):
    try:
        _SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        _SETTINGS_FILE.write_text(json.dumps(data, indent=2))
    except Exception:
        pass


def clear_stt_settings():
    try:
        if _SETTINGS_FILE.exists():
            _SETTINGS_FILE.unlink()
    except Exception:
        pass

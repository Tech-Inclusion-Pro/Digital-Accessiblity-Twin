"""AI settings persistence — save/load to ~/.accesstwin/ai_settings.json."""

import json
from pathlib import Path

_SETTINGS_DIR = Path.home() / ".accesstwin"
_SETTINGS_FILE = _SETTINGS_DIR / "ai_settings.json"


def load_ai_settings() -> dict | None:
    try:
        if _SETTINGS_FILE.exists():
            return json.loads(_SETTINGS_FILE.read_text())
    except Exception:
        pass
    return None


def save_ai_settings(data: dict):
    try:
        _SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        _SETTINGS_FILE.write_text(json.dumps(data, indent=2))
    except Exception:
        pass


def clear_ai_settings():
    try:
        if _SETTINGS_FILE.exists():
            _SETTINGS_FILE.unlink()
    except Exception:
        pass

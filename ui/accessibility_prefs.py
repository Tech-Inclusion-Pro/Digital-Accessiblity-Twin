"""Device-level accessibility preferences persistence."""

import json
from pathlib import Path

_PREFS_DIR = Path.home() / ".accesstwin"
_PREFS_FILE = _PREFS_DIR / "accessibility_prefs.json"


def load_prefs() -> dict | None:
    try:
        if _PREFS_FILE.exists():
            return json.loads(_PREFS_FILE.read_text())
    except Exception:
        pass
    return None


def save_prefs(data: dict):
    try:
        _PREFS_DIR.mkdir(parents=True, exist_ok=True)
        _PREFS_FILE.write_text(json.dumps(data, indent=2))
    except Exception:
        pass

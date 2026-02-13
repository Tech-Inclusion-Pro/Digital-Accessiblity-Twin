"""Accessibility infrastructure tests."""

import json
import pytest
from pathlib import Path


class TestColorBlindEngine:
    def test_contrast_ratio_white_on_dark(self):
        from ui.color_blind_engine import validate_contrast
        ratio = validate_contrast("#ffffff", "#1a1a2e")
        assert ratio > 4.5  # WCAG AA

    def test_contrast_ratio_same_color(self):
        from ui.color_blind_engine import validate_contrast
        ratio = validate_contrast("#ffffff", "#ffffff")
        assert ratio == pytest.approx(1.0)

    def test_passes_aa(self):
        from ui.color_blind_engine import passes_aa
        assert passes_aa("#ffffff", "#1a1a2e")
        assert not passes_aa("#888888", "#999999")

    def test_passes_aaa(self):
        from ui.color_blind_engine import passes_aaa
        assert passes_aaa("#ffffff", "#000000")

    def test_wong_palette(self):
        from ui.color_blind_engine import get_safe_palette
        palette = get_safe_palette()
        assert "orange" in palette
        assert "sky_blue" in palette
        assert len(palette) == 8


class TestAccessibilityPrefs:
    def test_save_and_load(self, tmp_path, monkeypatch):
        import ui.accessibility_prefs as prefs
        monkeypatch.setattr(prefs, "_PREFS_DIR", tmp_path)
        monkeypatch.setattr(prefs, "_PREFS_FILE", tmp_path / "test_prefs.json")

        prefs.save_prefs({"font_scale": "large", "high_contrast": True})
        loaded = prefs.load_prefs()
        assert loaded is not None
        assert loaded["font_scale"] == "large"
        assert loaded["high_contrast"] is True

    def test_load_missing(self, tmp_path, monkeypatch):
        import ui.accessibility_prefs as prefs
        monkeypatch.setattr(prefs, "_PREFS_FILE", tmp_path / "missing.json")
        assert prefs.load_prefs() is None


class TestAccessibilityManager:
    def test_singleton(self):
        from ui.accessibility import AccessibilityManager
        # Reset for test
        AccessibilityManager._instance = None
        a = AccessibilityManager.create()
        b = AccessibilityManager.instance()
        assert a is b
        AccessibilityManager._instance = None  # cleanup

    def test_color_blind_overrides(self):
        from ui.accessibility import AccessibilityManager
        AccessibilityManager._instance = None
        mgr = AccessibilityManager.create()

        mgr._color_blind_mode = "protanopia"
        colors = mgr.get_effective_colors()
        assert colors["primary"] == "#0072B2"

        AccessibilityManager._instance = None

    def test_serialization_roundtrip(self):
        from ui.accessibility import AccessibilityManager
        AccessibilityManager._instance = None
        mgr = AccessibilityManager.create()

        mgr._font_scale = "large"
        mgr._high_contrast = True
        mgr._reading_ruler = True

        data = mgr.to_dict()
        assert data["font_scale"] == "large"
        assert data["high_contrast"] is True
        assert data["reading_ruler"] is True

        # Load into fresh instance
        AccessibilityManager._instance = None
        mgr2 = AccessibilityManager.create()
        mgr2.load_from_dict(data)
        assert mgr2.font_scale == "large"
        assert mgr2.high_contrast is True
        assert mgr2.reading_ruler is True

        AccessibilityManager._instance = None

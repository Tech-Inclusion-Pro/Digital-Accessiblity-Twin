"""Application settings and color scheme."""

COLORS = {
    "primary": "#6f2fa6",
    "primary_text": "#b065d6",
    "secondary": "#3a2b95",
    "tertiary": "#a23b84",
    "dark_bg": "#1a1a2e",
    "dark_card": "#16213e",
    "dark_border": "#1c2a4a",
    "dark_hover": "#1a2d50",
    "dark_input": "#0f3460",
    "text": "#ffffff",
    "text_muted": "#b8b8b8",
    "success": "#28a745",
    "warning": "#ffc107",
    "error": "#ff4d5e",
}


def get_colors():
    """Get effective colors, using AccessibilityManager overrides if available."""
    try:
        from ui.accessibility import AccessibilityManager
        manager = AccessibilityManager.instance()
        if manager:
            return manager.get_effective_colors()
    except Exception:
        pass
    return COLORS


APP_SETTINGS = {
    "app_name": "AccessTwin",
    "version": "1.0.0",
    "min_font_size": 16,
    "touch_target_min": 44,
    "focus_outline_width": 3,
}

"""Persistent contextual help button with detailed 3-part guidance."""

from PyQt6.QtWidgets import (
    QPushButton, QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget,
)
from PyQt6.QtCore import Qt

from config.settings import get_colors, APP_SETTINGS

# ---------------------------------------------------------------------------
# Contextual help content — keyed by context name.
# Each entry follows the 3-part format:
#   1) What is the issue / what is this feature
#   2) How to fix or use it
#   3) Step-by-step instructions
# ---------------------------------------------------------------------------

_HELP_CONTENT: dict[str, dict] = {
    "general": {
        "title": "Getting Help in AccessTwin",
        "body": (
            "1) What is this?\n"
            "   AccessTwin is your accessibility digital twin \u2014 it helps you "
            "document, track, and share accessibility needs and supports.\n\n"
            "2) How to get started:\n"
            "   Use the sidebar on the left to navigate between features. "
            "Click the \"? Tutorial\" button in the sidebar for a complete "
            "step-by-step walkthrough.\n\n"
            "3) Quick steps:\n"
            "   \u2022 Set up your profile first (My Profile).\n"
            "   \u2022 Configure AI (AI Settings) to enable insights.\n"
            "   \u2022 Log experiences or implementations regularly.\n"
            "   \u2022 View your progress in the Tracking page.\n"
            "   \u2022 Press Ctrl+/ to see keyboard shortcuts."
        ),
    },
    "profile": {
        "title": "My Profile \u2014 Help",
        "body": (
            "1) What is the issue?\n"
            "   Your profile is empty or incomplete. AccessTwin needs profile "
            "data (Strengths, Supports, History, Goals) to generate meaningful "
            "insights and track progress.\n\n"
            "2) How to fix it:\n"
            "   Add items to each profile section using the \"+\" button.\n\n"
            "3) Step-by-step instructions:\n"
            "   \u2022 Click \"My Profile\" in the sidebar.\n"
            "   \u2022 Find the section you want (e.g., Strengths).\n"
            "   \u2022 Click the \"+\" button next to the section header.\n"
            "   \u2022 Type a description in the text field.\n"
            "   \u2022 Select a priority: High, Medium, or Low.\n"
            "   \u2022 Click Save.\n"
            "   \u2022 Repeat for each section.\n\n"
            "   Tip: Start with Strengths to frame your profile positively."
        ),
    },
    "ai_settings": {
        "title": "AI Settings \u2014 Help",
        "body": (
            "1) What is the issue?\n"
            "   AccessTwin needs an AI model to power the Insights, Evaluate, "
            "and Coach features. Without a configured and running AI server, "
            "these features will not work.\n\n"
            "2) How to fix it:\n"
            "   Install a local AI provider (recommended) or configure a "
            "cloud provider. The \"? Tutorial\" button in the sidebar has a "
            "full walkthrough, or click the guide button below for "
            "platform-specific setup instructions.\n\n"
            "3) Step-by-step instructions:\n"
            "   Local AI (recommended \u2014 data stays on device):\n"
            "   \u2022 Install Ollama from https://ollama.com/download\n"
            "     Mac: brew install ollama  or download .dmg\n"
            "     Windows: Download and run OllamaSetup.exe\n"
            "     Linux: curl -fsSL https://ollama.com/install.sh | sh\n"
            "   \u2022 Start the server: ollama serve\n"
            "   \u2022 Download a model: ollama pull gemma3:4b\n"
            "   \u2022 In AccessTwin, set Provider to Ollama.\n"
            "   \u2022 Set Server URL to: http://localhost:11434\n"
            "   \u2022 Set Model to: gemma3:4b\n"
            "   \u2022 Click \"Test Connection\" to verify.\n"
            "   \u2022 Click \"Save Configuration\".\n\n"
            "   Cloud AI (requires institutional consent):\n"
            "   \u2022 Get an API key from OpenAI or Anthropic.\n"
            "   \u2022 Set Provider Type to Cloud.\n"
            "   \u2022 Enter your API key.\n"
            "   \u2022 Check both consent checkboxes.\n"
            "   \u2022 Click \"Test Connection\", then \"Save Configuration\".\n\n"
            "   If the test fails:\n"
            "   \u2022 \"Connection refused\" \u2014 the server is not running.\n"
            "   \u2022 \"Model not found\" \u2014 you need to download the model.\n"
            "   \u2022 \"Invalid API key\" \u2014 re-copy the key from your provider."
        ),
    },
    "log_experience": {
        "title": "Log Experience \u2014 Help",
        "body": (
            "1) What is the issue?\n"
            "   You need to record how an accessibility support worked in "
            "practice so you can track patterns over time.\n\n"
            "2) How to fix it:\n"
            "   Fill in the log form with details about what happened.\n\n"
            "3) Step-by-step instructions:\n"
            "   \u2022 Select a support/accommodation from the dropdown.\n"
            "     (If empty, add supports in My Profile first.)\n"
            "   \u2022 Write Implementation Notes: what was done, where, how.\n"
            "   \u2022 Write Outcome Notes: how effective it was.\n"
            "   \u2022 To track effectiveness, include this exact phrase:\n"
            "     \"Effectiveness rated: 4/5\" (use any number 1\u20135).\n"
            "   \u2022 Click \"Save Log\".\n"
            "   \u2022 Use the microphone button for voice dictation.\n\n"
            "   Tip: The more detail you include, the better AI insights "
            "will be."
        ),
    },
    "tracking": {
        "title": "Tracking & Progress \u2014 Help",
        "body": (
            "1) What is the issue?\n"
            "   The charts appear empty because there is not enough logged "
            "data to visualize.\n\n"
            "2) How to fix it:\n"
            "   Log more experiences or implementations. Charts populate "
            "automatically as data accumulates.\n\n"
            "3) Step-by-step instructions:\n"
            "   \u2022 Go to \"Log Experience\" (student) or \"Log Implementation\" "
            "(teacher) and create entries.\n"
            "   \u2022 Include \"Effectiveness rated: X/5\" in outcome notes "
            "to populate the effectiveness line chart.\n"
            "   \u2022 Return to the Tracking page \u2014 charts will refresh.\n"
            "   \u2022 The Activity Timeline scrolls horizontally for many entries.\n"
            "   \u2022 The bar charts show category and frequency breakdowns.\n\n"
            "   Tip: Log at least 3\u20135 entries to see meaningful trends."
        ),
    },
    "insights": {
        "title": "AI Insights \u2014 Help",
        "body": (
            "1) What is the issue?\n"
            "   The AI chat is not responding, or you\u2019re not sure how to "
            "use it.\n\n"
            "2) How to fix it:\n"
            "   Make sure AI is configured (AI Settings page) and the server "
            "is running.\n\n"
            "3) Step-by-step instructions:\n"
            "   \u2022 First, go to AI Settings and verify the connection works.\n"
            "   \u2022 If the test fails, see the AI Settings help for "
            "troubleshooting.\n"
            "   \u2022 Return to the Insights page.\n"
            "   \u2022 Type a question in the chat box, for example:\n"
            "     \"What patterns do you see in my support usage?\"\n"
            "   \u2022 Press Enter or click Send.\n"
            "   \u2022 Wait for the AI response (may take a few seconds).\n"
            "   \u2022 Click \"How was this decided?\" to see what data was "
            "shared with the AI.\n\n"
            "   Note: AI suggestions are not professional advice. Always "
            "discuss changes with your support team."
        ),
    },
    "export": {
        "title": "Export \u2014 Help",
        "body": (
            "1) What is the issue?\n"
            "   You want to create a portable file of your accessibility "
            "profile or implementation report.\n\n"
            "2) How to fix it:\n"
            "   Use the Export page to generate and save a file.\n\n"
            "3) Step-by-step instructions:\n"
            "   \u2022 Click \"Export Twin\" (student) or \"Export Report\" "
            "(teacher) in the sidebar.\n"
            "   \u2022 Review the data preview.\n"
            "   \u2022 Choose your export format.\n"
            "   \u2022 Click \"Export\" to save the file.\n"
            "   \u2022 Share the file with teachers, schools, or support staff.\n\n"
            "   Tip: Export before school transitions so your supports "
            "carry forward."
        ),
    },
    "evaluate": {
        "title": "Evaluate \u2014 Help",
        "body": (
            "1) What is the issue?\n"
            "   You want to check how well a document meets a student\u2019s "
            "accessibility needs.\n\n"
            "2) How to fix it:\n"
            "   Upload a document and run the AI evaluation.\n\n"
            "3) Step-by-step instructions:\n"
            "   \u2022 Click \"Evaluate\" in the sidebar.\n"
            "   \u2022 Select a student from the dropdown.\n"
            "   \u2022 Upload or select a document.\n"
            "   \u2022 Click \"Evaluate\".\n"
            "   \u2022 Review the AI\u2019s gap analysis and suggestions.\n"
            "   \u2022 Each suggestion has a confidence score.\n"
            "   \u2022 Click \"How was this decided?\" for full transparency.\n\n"
            "   Note: AI evaluation is a starting point. Use your "
            "professional judgement."
        ),
    },
    "students": {
        "title": "Students \u2014 Help",
        "body": (
            "1) What is the issue?\n"
            "   The student list is empty or you need to view a "
            "student\u2019s profile.\n\n"
            "2) How to fix it:\n"
            "   Students appear here after they create accounts and build "
            "their profiles.\n\n"
            "3) Step-by-step instructions:\n"
            "   \u2022 Click \"Students\" in the sidebar.\n"
            "   \u2022 You will see a list of student profiles.\n"
            "   \u2022 Click a student\u2019s name to view their full profile.\n"
            "   \u2022 Use the AI Coach button for privacy-preserving AI "
            "advice about supporting that student.\n\n"
            "   If the list is empty, students need to create accounts "
            "and set up their profiles first."
        ),
    },
    "stt_download": {
        "title": "Speech-to-Text Model \u2014 Help",
        "body": (
            "1) What is the issue?\n"
            "   The speech-to-text (voice dictation) feature requires a "
            "model to be downloaded the first time you use it. The download "
            "failed or is taking a long time.\n\n"
            "2) How to fix it:\n"
            "   Check your internet connection and try again. The model "
            "only needs to download once.\n\n"
            "3) Step-by-step instructions:\n"
            "   \u2022 Make sure you have a stable internet connection.\n"
            "   \u2022 Click the microphone button again to retry.\n"
            "   \u2022 The default model (tiny, ~75 MB) should download in "
            "under a minute on most connections.\n"
            "   \u2022 If it keeps failing:\n"
            "     Mac: Open Terminal, run: pip3 install openai-whisper\n"
            "     Windows: Open Command Prompt, run: pip install openai-whisper\n"
            "     Linux: Open terminal, run: pip3 install openai-whisper\n"
            "   \u2022 Once downloaded, the model is cached locally and "
            "works offline."
        ),
    },
}


class HelpButton(QPushButton):
    """Floating '?' button for contextual help with detailed guidance."""

    def __init__(self, context: str = "general", parent=None):
        super().__init__("?", parent)
        self._context = context
        c = get_colors()
        self.setFixedSize(44, 44)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName("Help")
        self.setAccessibleDescription(f"Open help for {context}")
        self.setToolTip("Help")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['dark_input']};
                color: {c['text']};
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 22px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {c['primary']};
            }}
        """)
        self.clicked.connect(self._show_help)

    def _show_help(self):
        content = _HELP_CONTENT.get(self._context, _HELP_CONTENT["general"])
        dlg = _HelpDialog(content["title"], content["body"], self._context, self.window())
        dlg.exec()


class _HelpDialog(QDialog):
    """Styled help dialog showing detailed contextual guidance."""

    def __init__(self, title: str, body: str, context: str, parent=None):
        super().__init__(parent)
        self._context = context
        self.setWindowTitle(title)
        self.setMinimumWidth(520)
        self.setMinimumHeight(420)
        self.setAccessibleName(title)
        self._build_ui(title, body)

    def _build_ui(self, title: str, body: str):
        c = get_colors()
        self.setStyleSheet(f"QDialog {{ background-color: {c['dark_bg']}; }}")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        # Title
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {c['text']};"
        )
        title_lbl.setAccessibleName(title)
        root.addWidget(title_lbl)

        # Scrollable body
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        body_card = QWidget()
        body_card.setStyleSheet(
            f"QWidget {{ background: {c['dark_card']}; "
            f"border: 1px solid {c['dark_border']}; border-radius: 12px; }}"
        )
        card_layout = QVBoxLayout(body_card)
        card_layout.setContentsMargins(20, 16, 20, 16)

        body_lbl = QLabel(body)
        body_lbl.setWordWrap(True)
        body_lbl.setStyleSheet(
            f"font-size: 13px; color: {c['text']}; line-height: 1.5; border: none;"
        )
        body_lbl.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        card_layout.addWidget(body_lbl)

        container_layout.addWidget(body_card)
        container_layout.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll, stretch=1)

        # Bottom buttons
        btn_row = QVBoxLayout()
        btn_row.setSpacing(8)

        # Show "Open AI Setup Guide" button for AI-related contexts
        if self._context in ("ai_settings", "insights", "evaluate"):
            guide_btn = QPushButton("Open Full AI Setup Guide")
            guide_btn.setAccessibleName("Open AI setup guide with platform instructions")
            guide_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            guide_btn.setFixedHeight(APP_SETTINGS["touch_target_min"])
            guide_btn.setStyleSheet(
                f"QPushButton {{ "
                f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                f"stop:0 {c['primary']}, stop:1 {c['tertiary']}); "
                f"color: white; border: none; border-radius: 8px; "
                f"padding: 8px 24px; font-weight: bold; font-size: 13px; }}"
            )
            guide_btn.clicked.connect(self._open_ai_guide)
            btn_row.addWidget(guide_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close help dialog")
        close_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setFixedHeight(APP_SETTINGS["touch_target_min"])
        close_btn.setFixedWidth(120)
        close_btn.setStyleSheet(
            f"QPushButton {{ background: {c['dark_input']}; color: {c['text']}; "
            f"border: 1px solid {c['dark_border']}; border-radius: 8px; "
            f"font-size: 13px; }}"
            f"QPushButton:hover {{ background: {c['dark_hover']}; }}"
        )
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        root.addLayout(btn_row)

    def _open_ai_guide(self):
        from ui.components.ai_setup_guide_dialog import AISetupGuideDialog
        guide = AISetupGuideDialog(self)
        guide.exec()

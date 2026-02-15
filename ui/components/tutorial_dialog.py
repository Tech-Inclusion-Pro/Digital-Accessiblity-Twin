"""Step-by-step tutorial dialog for AccessTwin."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget,
)
from PyQt6.QtCore import Qt

from config.settings import get_colors, APP_SETTINGS

# ---------------------------------------------------------------------------
# Tutorial step definitions — each is a dict with:
#   icon, title, body  (body is a multi-line string with step-by-step detail)
# ---------------------------------------------------------------------------

_STUDENT_STEPS = [
    {
        "icon": "\u2302",
        "title": "Welcome to AccessTwin",
        "body": (
            "AccessTwin is your personal accessibility digital twin. "
            "It helps you document, track, and share your accessibility "
            "needs and experiences.\n\n"
            "This tutorial will walk you through every feature, step by step.\n\n"
            "Use the Next and Previous buttons below to move through "
            "the tutorial at your own pace."
        ),
    },
    {
        "icon": "\u25CB",
        "title": "Step 1 \u2014 Set Up Your Profile",
        "body": (
            "Your profile is the foundation of your digital twin.\n\n"
            "How to set up your profile:\n"
            "1. Click \"My Profile\" in the left sidebar.\n"
            "2. You will see sections for Strengths, Supports, History, "
            "Hopes & Goals, and Stakeholders.\n"
            "3. Click the \"+\" button next to any section to add an item.\n"
            "4. Type a description and select a priority (High, Medium, Low).\n"
            "5. Click Save to keep your entry.\n"
            "6. You can edit any item later by clicking on it.\n\n"
            "Tip: Start with your Strengths \u2014 they help frame your "
            "accommodations positively."
        ),
    },
    {
        "icon": "\u2261",
        "title": "Step 2 \u2014 Configure AI Settings",
        "body": (
            "AccessTwin uses AI to generate insights from your data. "
            "You need to connect an AI model before using Insights.\n\n"
            "How to configure AI:\n"
            "1. Click \"AI Settings\" in the left sidebar.\n"
            "2. Choose \"Local\" (recommended \u2014 data stays on your device) "
            "or \"Cloud\" (requires consent).\n"
            "3. For Local AI, you need to install a provider first. "
            "Click the \"?\" help button on the AI Settings page for "
            "detailed installation instructions for your operating system "
            "(Mac, Windows, or Linux).\n"
            "4. Set the Server URL (default: http://localhost:11434).\n"
            "5. Set the Model name (default: gemma3:4b).\n"
            "6. Click \"Test Connection\" to verify it works.\n"
            "7. Click \"Save Configuration\" to keep your settings.\n\n"
            "If the test fails, click the \"?\" help button for "
            "step-by-step troubleshooting for your platform."
        ),
    },
    {
        "icon": "\u270E",
        "title": "Step 3 \u2014 Log an Experience",
        "body": (
            "Logging experiences creates a record of how your supports "
            "work in practice.\n\n"
            "How to log an experience:\n"
            "1. Click \"Log Experience\" in the left sidebar.\n"
            "2. Select a support/accommodation from the dropdown list.\n"
            "   (If the list is empty, add supports in My Profile first.)\n"
            "3. Write your Implementation Notes \u2014 describe what happened, "
            "where, and how the support was used.\n"
            "4. Write your Outcome Notes \u2014 describe how effective it was.\n"
            "   To record a rating, include the phrase:\n"
            "   \"Effectiveness rated: 4/5\" (use any number 1\u20135).\n"
            "5. Click \"Save Log\" to record the experience.\n\n"
            "Tip: You can use the microphone button (\U0001F3A4) to dictate "
            "notes using speech-to-text. The first time you use it, "
            "a small model will download automatically."
        ),
    },
    {
        "icon": "\u2630",
        "title": "Step 4 \u2014 View Your Tracking & Progress",
        "body": (
            "The Tracking page shows your activity history and visual charts.\n\n"
            "How to use Tracking:\n"
            "1. Click \"Tracking\" in the left sidebar.\n"
            "2. The top section shows your Recent Activity \u2014 a list of "
            "all logged experiences with dates and notes.\n"
            "3. Scroll down to see the Charts & Progress section:\n"
            "   \u2022 Activity Timeline \u2014 a visual timeline of your logged "
            "experiences. Scroll horizontally to see older entries.\n"
            "   \u2022 Effectiveness Over Time \u2014 a line chart showing your "
            "ratings across all supports (only appears if you\u2019ve "
            "included \"Effectiveness rated: X/5\" in outcome notes).\n"
            "   \u2022 Support Category Breakdown \u2014 a bar chart showing how "
            "many times each support category has been logged.\n\n"
            "Tip: Log experiences regularly to build meaningful trend data."
        ),
    },
    {
        "icon": "\u2606",
        "title": "Step 5 \u2014 Get AI Insights",
        "body": (
            "The Insights page lets you have a conversation with AI "
            "about your accessibility data.\n\n"
            "How to use AI Insights:\n"
            "1. Click \"My Insights\" in the left sidebar.\n"
            "2. Make sure AI is configured (see Step 2).\n"
            "3. Type a question in the chat box at the bottom, for example:\n"
            "   \u2022 \"What patterns do you see in my support usage?\"\n"
            "   \u2022 \"Which accommodations seem most effective?\"\n"
            "   \u2022 \"What should I share with my teacher?\"\n"
            "4. Press Enter or click Send.\n"
            "5. The AI will respond based on your profile and logged data.\n"
            "6. You can click \"How was this decided?\" to see exactly "
            "what data was shared with the AI and what rules it follows.\n\n"
            "Important: AI suggestions are not professional advice. "
            "Always discuss changes with your teachers or support team."
        ),
    },
    {
        "icon": "\u25A1",
        "title": "Step 6 \u2014 Export Your Digital Twin",
        "body": (
            "Exporting creates a portable summary of your accessibility "
            "profile that you can share.\n\n"
            "How to export:\n"
            "1. Click \"Export Twin\" in the left sidebar.\n"
            "2. Review the preview of your profile data.\n"
            "3. Choose your export format.\n"
            "4. Click \"Export\" to save the file.\n"
            "5. Share the file with teachers, schools, or support staff "
            "as needed.\n\n"
            "Tip: Export before transitioning to a new school or program "
            "so your supports carry over."
        ),
    },
    {
        "icon": "\u229E",
        "title": "Step 7 \u2014 Accessibility Settings",
        "body": (
            "AccessTwin has extensive accessibility settings you can "
            "customize at any time.\n\n"
            "How to open accessibility settings:\n"
            "1. Click the \"\u229E Settings\" button at the bottom of the "
            "left sidebar.\n"
            "2. The Accessibility Settings dialog will open with these options:\n"
            "   \u2022 Font Size \u2014 choose from several size scales.\n"
            "   \u2022 Dyslexia-Friendly Font \u2014 switches to a font "
            "designed for readability.\n"
            "   \u2022 High Contrast Mode \u2014 increases color contrast.\n"
            "   \u2022 Color Blind Mode \u2014 choose from Protanopia, "
            "Deuteranopia, Tritanopia, and more.\n"
            "   \u2022 Cursor Style \u2014 choose a larger or trailing cursor.\n"
            "   \u2022 Reading Ruler \u2014 shows a highlight band that "
            "follows your mouse to help track lines.\n"
            "   \u2022 Reduce Motion \u2014 disables animations.\n"
            "   \u2022 Enhanced Focus \u2014 makes focus outlines bolder.\n"
            "3. Click \"Apply\" to save your changes.\n\n"
            "These settings are also available on the login screen "
            "before you sign in."
        ),
    },
    {
        "icon": "\u2328",
        "title": "Step 8 \u2014 Keyboard Shortcuts",
        "body": (
            "AccessTwin supports keyboard navigation throughout the app.\n\n"
            "Shortcuts you can use:\n"
            "   \u2022 Ctrl + /  \u2014  Show the keyboard shortcuts reference.\n"
            "   \u2022 Ctrl + Q  \u2014  Quit the application.\n"
            "   \u2022 Tab  \u2014  Move to the next control.\n"
            "   \u2022 Shift + Tab  \u2014  Move to the previous control.\n"
            "   \u2022 Enter  \u2014  Submit or activate a button.\n"
            "   \u2022 Escape  \u2014  Close a dialog or cancel.\n\n"
            "Every button and control has an accessible name for screen readers."
        ),
    },
]

_TEACHER_STEPS = [
    {
        "icon": "\u2302",
        "title": "Welcome to AccessTwin",
        "body": (
            "AccessTwin helps you manage, track, and evaluate accessibility "
            "supports for your students.\n\n"
            "This tutorial will walk you through every feature, step by step.\n\n"
            "Use the Next and Previous buttons below to move through "
            "the tutorial at your own pace."
        ),
    },
    {
        "icon": "\u2261",
        "title": "Step 1 \u2014 Configure AI Settings",
        "body": (
            "Before using AI-powered features (Insights, Evaluate, Coach), "
            "you need to connect an AI model.\n\n"
            "How to configure AI:\n"
            "1. Click \"AI Settings\" in the left sidebar.\n"
            "2. Choose \"Local\" (recommended \u2014 data stays on your device) "
            "or \"Cloud\" (requires institutional consent).\n"
            "3. For Local AI, you must install a provider on your computer. "
            "Click the \"?\" help button on the AI Settings page for "
            "detailed installation instructions for Mac, Windows, and Linux.\n"
            "4. Set the Server URL (default: http://localhost:11434).\n"
            "5. Set the Model name (default: gemma3:4b).\n"
            "6. Click \"Test Connection\" to verify it works.\n"
            "7. Click \"Save Configuration\" to keep your settings.\n\n"
            "Cloud AI requires checking both consent boxes:\n"
            "   \u2022 Institutional approval for cloud AI usage.\n"
            "   \u2022 Understanding that data is transmitted to a third party.\n\n"
            "If the test fails, click the \"?\" help button for "
            "platform-specific troubleshooting."
        ),
    },
    {
        "icon": "\u25C7",
        "title": "Step 2 \u2014 Manage Students",
        "body": (
            "The Students page lets you view and manage student profiles.\n\n"
            "How to use the Students page:\n"
            "1. Click \"Students\" in the left sidebar.\n"
            "2. You will see a list of student profiles linked to your "
            "account.\n"
            "3. Click on a student\u2019s name to view their full profile, "
            "including Strengths, Supports, History, and Goals.\n"
            "4. You can use the AI Coach (button in the top-right) to get "
            "privacy-preserving AI advice about supporting this student.\n\n"
            "Note: Student data is aggregated and anonymized when sent to "
            "the AI. You can click \"How was this decided?\" to see exactly "
            "what information was shared."
        ),
    },
    {
        "icon": "\u25B3",
        "title": "Step 3 \u2014 Evaluate Accommodations",
        "body": (
            "The Evaluate page helps you assess how well a document or "
            "lesson plan meets a student\u2019s accessibility needs.\n\n"
            "How to evaluate:\n"
            "1. Click \"Evaluate\" in the left sidebar.\n"
            "2. Select a student from the dropdown.\n"
            "3. Upload or select a document to evaluate.\n"
            "4. Click \"Evaluate\" to run the AI analysis.\n"
            "5. Review the results: the AI will identify gaps between "
            "the student\u2019s needs and what the document provides.\n"
            "6. Each suggestion includes a confidence score and reasoning.\n"
            "7. Click \"How was this decided?\" for full transparency.\n\n"
            "Tip: Use evaluation results as a starting point, not a final "
            "answer. Your professional judgement is essential."
        ),
    },
    {
        "icon": "\u270E",
        "title": "Step 4 \u2014 Log an Implementation",
        "body": (
            "Logging implementations creates a record of how you\u2019ve "
            "applied supports in your classroom.\n\n"
            "How to log an implementation:\n"
            "1. Click \"Log Implementation\" in the left sidebar.\n"
            "2. Select the student this log is about.\n"
            "3. Select the support/accommodation you implemented.\n"
            "4. Write your Implementation Notes \u2014 describe what you did, "
            "in what context, and any adaptations you made.\n"
            "5. Write your Outcome Notes \u2014 describe the result.\n"
            "   To record a rating, include the phrase:\n"
            "   \"Effectiveness rated: 4/5\" (use any number 1\u20135).\n"
            "6. Click \"Save Log\" to record the implementation.\n\n"
            "Tip: Use the microphone button (\U0001F3A4) for voice dictation."
        ),
    },
    {
        "icon": "\u2630",
        "title": "Step 5 \u2014 View Tracking & Analytics",
        "body": (
            "The Tracking page shows implementation history and analytics.\n\n"
            "How to use Tracking:\n"
            "1. Click \"Tracking\" in the left sidebar.\n"
            "2. The top section shows Recent Activity \u2014 your most "
            "recent implementation logs.\n"
            "3. Scroll down to see Charts & Analytics:\n"
            "   \u2022 Implementation Timeline \u2014 a visual timeline showing "
            "each implementation with student name and category.\n"
            "   \u2022 Activity by Student \u2014 a bar chart showing how many "
            "implementations you\u2019ve logged per student.\n"
            "   \u2022 Implementation Frequency \u2014 a bar chart showing "
            "weekly implementation counts over time.\n\n"
            "Tip: These charts update automatically as you log more data."
        ),
    },
    {
        "icon": "\u2606",
        "title": "Step 6 \u2014 Get AI Insights",
        "body": (
            "The AI Insights page lets you consult the AI about "
            "patterns across all your students.\n\n"
            "How to use AI Insights:\n"
            "1. Click \"AI Insights\" in the left sidebar.\n"
            "2. Make sure AI is configured (see Step 1).\n"
            "3. Type a question, for example:\n"
            "   \u2022 \"Which students need the most support this week?\"\n"
            "   \u2022 \"What accommodation patterns are most effective?\"\n"
            "   \u2022 \"How can I improve my approach to sensory supports?\"\n"
            "4. Press Enter or click Send.\n"
            "5. Click \"How was this decided?\" to see what data was shared.\n\n"
            "Important: AI suggestions are based on pattern matching. "
            "Always apply your professional judgement."
        ),
    },
    {
        "icon": "\u25A1",
        "title": "Step 7 \u2014 Export Reports",
        "body": (
            "Exporting creates a portable report of your implementation "
            "data and student support summaries.\n\n"
            "How to export:\n"
            "1. Click \"Export Report\" in the left sidebar.\n"
            "2. Select which student(s) to include.\n"
            "3. Review the preview.\n"
            "4. Choose your export format.\n"
            "5. Click \"Export\" to save the file.\n\n"
            "Tip: Export reports for IEP meetings, parent conferences, "
            "or school transitions."
        ),
    },
    {
        "icon": "\u229E",
        "title": "Step 8 \u2014 Accessibility Settings",
        "body": (
            "AccessTwin includes extensive accessibility customization.\n\n"
            "How to open accessibility settings:\n"
            "1. Click the \"\u229E Settings\" button at the bottom of the "
            "left sidebar.\n"
            "2. Available options:\n"
            "   \u2022 Font Size \u2014 choose from several size scales.\n"
            "   \u2022 Dyslexia-Friendly Font \u2014 switches to a font "
            "designed for readability.\n"
            "   \u2022 High Contrast Mode \u2014 increases color contrast.\n"
            "   \u2022 Color Blind Mode \u2014 Protanopia, Deuteranopia, "
            "Tritanopia, and more.\n"
            "   \u2022 Cursor Style \u2014 larger or trailing cursor.\n"
            "   \u2022 Reading Ruler \u2014 highlight band following mouse.\n"
            "   \u2022 Reduce Motion \u2014 disables animations.\n"
            "   \u2022 Enhanced Focus \u2014 bolder focus outlines.\n"
            "3. Click \"Apply\" to save.\n\n"
            "These settings are also available before login."
        ),
    },
    {
        "icon": "\u2328",
        "title": "Step 9 \u2014 Keyboard Shortcuts",
        "body": (
            "AccessTwin supports full keyboard navigation.\n\n"
            "Shortcuts:\n"
            "   \u2022 Ctrl + /  \u2014  Show the keyboard shortcuts reference.\n"
            "   \u2022 Ctrl + Q  \u2014  Quit the application.\n"
            "   \u2022 Tab  \u2014  Move to the next control.\n"
            "   \u2022 Shift + Tab  \u2014  Move to the previous control.\n"
            "   \u2022 Enter  \u2014  Submit or activate a button.\n"
            "   \u2022 Escape  \u2014  Close a dialog or cancel.\n\n"
            "Every button and control has an accessible name for screen readers."
        ),
    },
]


class TutorialDialog(QDialog):
    """Step-by-step tutorial walkthrough, role-aware (student or teacher)."""

    def __init__(self, role: str = "student", parent=None):
        super().__init__(parent)
        self._role = role
        self._steps = _STUDENT_STEPS if role == "student" else _TEACHER_STEPS
        self._current = 0
        self.setWindowTitle("AccessTwin Tutorial")
        self.setMinimumWidth(560)
        self.setMinimumHeight(520)
        self.setAccessibleName("AccessTwin Tutorial")
        self._build_ui()
        self._show_step(0)

    def _build_ui(self):
        c = get_colors()
        self.setStyleSheet(f"QDialog {{ background-color: {c['dark_bg']}; }}")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        # Step indicator row
        self._indicator_layout = QHBoxLayout()
        self._indicator_layout.setSpacing(6)
        self._indicator_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._dots: list[QLabel] = []
        for i in range(len(self._steps)):
            dot = QLabel("\u25CF")
            dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dot.setFixedSize(18, 18)
            dot.setAccessibleName(f"Step {i + 1}")
            self._dots.append(dot)
            self._indicator_layout.addWidget(dot)
        root.addLayout(self._indicator_layout)

        # Step counter
        self._counter = QLabel()
        self._counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._counter.setStyleSheet(
            f"font-size: 12px; color: {c['text_muted']};"
        )
        root.addWidget(self._counter)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )

        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(12)

        # Icon
        self._icon_label = QLabel()
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setStyleSheet(
            f"font-size: 48px; color: {c['primary_text']};"
        )
        self._content_layout.addWidget(self._icon_label)

        # Title
        self._title_label = QLabel()
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_label.setWordWrap(True)
        self._title_label.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {c['text']};"
        )
        self._content_layout.addWidget(self._title_label)

        # Body card
        body_card = QWidget()
        body_card.setStyleSheet(
            f"QWidget {{ background: {c['dark_card']}; "
            f"border: 1px solid {c['dark_border']}; border-radius: 12px; }}"
        )
        body_inner = QVBoxLayout(body_card)
        body_inner.setContentsMargins(20, 16, 20, 16)

        self._body_label = QLabel()
        self._body_label.setWordWrap(True)
        self._body_label.setStyleSheet(
            f"font-size: 13px; color: {c['text']}; line-height: 1.5; border: none;"
        )
        self._body_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        body_inner.addWidget(self._body_label)

        self._content_layout.addWidget(body_card)
        self._content_layout.addStretch()

        scroll.setWidget(self._content_widget)
        root.addWidget(scroll, stretch=1)

        # Navigation buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self._prev_btn = QPushButton("\u2190  Previous")
        self._prev_btn.setAccessibleName("Previous step")
        self._prev_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._prev_btn.setFixedHeight(APP_SETTINGS["touch_target_min"])
        self._prev_btn.setStyleSheet(
            f"QPushButton {{ background: {c['dark_input']}; color: {c['text']}; "
            f"border: 1px solid {c['dark_border']}; border-radius: 8px; "
            f"padding: 6px 20px; font-size: 13px; }}"
            f"QPushButton:hover {{ background: {c['dark_hover']}; }}"
        )
        self._prev_btn.clicked.connect(self._go_prev)
        btn_row.addWidget(self._prev_btn)

        btn_row.addStretch()

        self._next_btn = QPushButton("Next  \u2192")
        self._next_btn.setAccessibleName("Next step")
        self._next_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._next_btn.setFixedHeight(APP_SETTINGS["touch_target_min"])
        self._next_btn.setStyleSheet(
            f"QPushButton {{ "
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {c['primary']}, stop:1 {c['tertiary']}); "
            f"color: white; border: none; border-radius: 8px; "
            f"padding: 6px 24px; font-weight: bold; font-size: 13px; }}"
        )
        self._next_btn.clicked.connect(self._go_next)
        btn_row.addWidget(self._next_btn)

        root.addLayout(btn_row)

    def _show_step(self, index: int):
        c = get_colors()
        self._current = index
        step = self._steps[index]

        self._icon_label.setText(step["icon"])
        self._title_label.setText(step["title"])
        self._title_label.setAccessibleName(step["title"])
        self._body_label.setText(step["body"])

        # Counter
        self._counter.setText(
            f"Step {index + 1} of {len(self._steps)}"
        )

        # Dot indicators
        for i, dot in enumerate(self._dots):
            if i == index:
                dot.setStyleSheet(f"font-size: 12px; color: {c['primary_text']};")
            elif i < index:
                dot.setStyleSheet(f"font-size: 12px; color: {c['success']};")
            else:
                dot.setStyleSheet(f"font-size: 12px; color: {c['dark_border']};")

        # Button states
        self._prev_btn.setEnabled(index > 0)
        is_last = index == len(self._steps) - 1
        self._next_btn.setText("Finish" if is_last else "Next  \u2192")
        self._next_btn.setAccessibleName("Finish tutorial" if is_last else "Next step")

    def _go_prev(self):
        if self._current > 0:
            self._show_step(self._current - 1)

    def _go_next(self):
        if self._current < len(self._steps) - 1:
            self._show_step(self._current + 1)
        else:
            self.accept()

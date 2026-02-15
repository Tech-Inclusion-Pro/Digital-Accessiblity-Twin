"""Coach chat dialog — privacy-preserving AI consultation for teachers."""

import asyncio
from functools import partial

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QLineEdit, QSizePolicy, QFrame,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from config.settings import get_colors, APP_SETTINGS
from ai.backend_manager import BackendManager
from ai.privacy_aggregator import PrivacyAggregator
from ai.prompts.coach_prompt import build_coach_prompt

# Category → pill colour (muted palette that works on dark backgrounds)
_CATEGORY_COLORS = {
    "sensory": "#2e7d82",
    "motor": "#6d4c8d",
    "cognitive": "#4a6fa5",
    "communication": "#7b6b3a",
    "technology": "#3a7b5c",
    "executive function": "#8b5e3c",
    "environmental": "#5c6b3a",
}

_SUGGESTED_QUESTIONS = [
    "What should I consider for a reading activity?",
    "Would a timed test work for this student?",
    "What strengths can I build on?",
    "How can I make group work more inclusive?",
    "What UDL checkpoints apply here?",
]


class _StreamWorker(QThread):
    """Runs the async AI generation in a background thread."""

    chunk_received = pyqtSignal(str)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, backend_manager, user_message, system_prompt,
                 conversation_history, parent=None):
        super().__init__(parent)
        self.bm = backend_manager
        self.user_message = user_message
        self.system_prompt = system_prompt
        self.conversation_history = list(conversation_history)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._stream())
        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            loop.close()
            self.finished_signal.emit()

    async def _stream(self):
        async for chunk in self.bm.generate_response(
            self.user_message,
            system_prompt=self.system_prompt,
            conversation_history=self.conversation_history,
        ):
            self.chunk_received.emit(chunk)


class CoachDialog(QDialog):
    """Privacy-preserving AI coach consultation dialog."""

    def __init__(self, profile, supports, tracking_logs,
                 backend_manager: BackendManager, parent=None):
        super().__init__(parent)
        self.profile = profile
        self.supports = supports
        self.backend_manager = backend_manager
        self._worker = None
        self._conversation_history: list = []
        self._current_assistant_label = None

        # Run privacy aggregation
        self._aggregated = PrivacyAggregator.aggregate(
            profile, supports, tracking_logs
        )
        self._teacher_safe = self._aggregated["teacher_safe"]
        self._system_prompt = build_coach_prompt(
            self._aggregated["ai_only"]["full_context_for_ai"]
        )

        self.setWindowTitle(
            f"Accessibility Coach — {self._teacher_safe['first_name']}"
        )
        self.setMinimumSize(620, 560)
        self.setAccessibleName(
            f"Accessibility Coach for {self._teacher_safe['first_name']}"
        )

        self._build_ui()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        c = get_colors()
        self.setStyleSheet(f"QDialog {{ background-color: {c['dark_bg']}; }}")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(10)

        # -- Header: first name + category badges --
        header_row = QHBoxLayout()
        header_row.setSpacing(8)

        name_lbl = QLabel(self._teacher_safe["first_name"])
        name_lbl.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {c['text']};"
        )
        name_lbl.setAccessibleName(
            f"Student first name: {self._teacher_safe['first_name']}"
        )
        header_row.addWidget(name_lbl)

        for cat in self._teacher_safe["support_categories"]:
            pill = QLabel(cat.title())
            bg = _CATEGORY_COLORS.get(cat, "#555555")
            pill.setStyleSheet(
                f"background: {bg}; color: white; border-radius: 10px; "
                f"padding: 3px 10px; font-size: 11px; font-weight: bold;"
            )
            pill.setAccessibleName(f"Support category: {cat}")
            header_row.addWidget(pill)

        header_row.addStretch()
        root.addLayout(header_row)

        # -- Collapsible theme summary panel --
        self._summary_visible = True
        toggle_btn = QPushButton("Hide Summary")
        toggle_btn.setAccessibleName("Toggle theme summary panel")
        toggle_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        toggle_btn.setFixedHeight(28)
        toggle_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {c['text_muted']}; "
            f"border: none; font-size: 12px; text-decoration: underline; }}"
        )
        self._toggle_btn = toggle_btn
        root.addWidget(toggle_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        self._summary_panel = self._build_summary_panel(c)
        root.addWidget(self._summary_panel)
        toggle_btn.clicked.connect(self._toggle_summary)

        # -- Chat area --
        chat_scroll = QScrollArea()
        chat_scroll.setWidgetResizable(True)
        chat_scroll.setStyleSheet(
            f"QScrollArea {{ border: 1px solid {c['dark_border']}; "
            f"border-radius: 8px; background: {c['dark_card']}; }}"
        )
        chat_scroll.setAccessibleName("Chat conversation area")
        self._chat_scroll = chat_scroll

        self._chat_container = QWidget()
        self._chat_layout = QVBoxLayout(self._chat_container)
        self._chat_layout.setContentsMargins(8, 8, 8, 8)
        self._chat_layout.setSpacing(8)
        self._chat_layout.addStretch()
        chat_scroll.setWidget(self._chat_container)
        root.addWidget(chat_scroll, stretch=1)

        # -- No-backend message --
        self._no_backend_widget = self._build_no_backend_widget(c)
        self._no_backend_widget.setVisible(self.backend_manager._client is None)
        root.addWidget(self._no_backend_widget)

        # -- Suggested questions --
        suggestions_row = QHBoxLayout()
        suggestions_row.setSpacing(6)
        for q in _SUGGESTED_QUESTIONS:
            pill = QPushButton(q)
            pill.setAccessibleName(f"Suggested question: {q}")
            pill.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            pill.setCursor(Qt.CursorShape.PointingHandCursor)
            pill.setFixedHeight(APP_SETTINGS["touch_target_min"])
            pill.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            pill.setStyleSheet(
                f"QPushButton {{ background: {c['dark_input']}; color: {c['text']}; "
                f"border: 1px solid {c['dark_border']}; border-radius: 14px; "
                f"padding: 4px 12px; font-size: 11px; }}"
                f"QPushButton:hover {{ background: {c['dark_hover']}; }}"
            )
            pill.clicked.connect(partial(self._on_suggestion, q))
            suggestions_row.addWidget(pill)
        suggestions_row.addStretch()

        suggest_scroll = QScrollArea()
        suggest_scroll.setWidgetResizable(True)
        suggest_scroll.setFixedHeight(APP_SETTINGS["touch_target_min"] + 8)
        suggest_scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )
        suggest_widget = QWidget()
        suggest_widget.setLayout(suggestions_row)
        suggest_scroll.setWidget(suggest_widget)
        root.addWidget(suggest_scroll)

        # -- Input area --
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Ask the coach a question...")
        self._input.setAccessibleName("Message input")
        self._input.setFixedHeight(APP_SETTINGS["touch_target_min"])
        self._input.setStyleSheet(
            f"QLineEdit {{ background: {c['dark_input']}; color: {c['text']}; "
            f"border: 1px solid {c['dark_border']}; border-radius: 8px; "
            f"padding: 0 12px; font-size: 14px; }}"
        )
        self._input.returnPressed.connect(self._send_message)
        input_row.addWidget(self._input, stretch=1)

        self._send_btn = QPushButton("Send")
        self._send_btn.setAccessibleName("Send message")
        self._send_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._send_btn.setFixedHeight(APP_SETTINGS["touch_target_min"])
        self._send_btn.setFixedWidth(80)
        self._send_btn.setStyleSheet(
            f"QPushButton {{ background: {c['primary']}; color: white; "
            f"border: none; border-radius: 8px; font-weight: bold; font-size: 14px; }}"
            f"QPushButton:disabled {{ background: {c['dark_border']}; color: {c['text_muted']}; }}"
        )
        self._send_btn.clicked.connect(self._send_message)
        input_row.addWidget(self._send_btn)

        root.addLayout(input_row)

        # -- Footer: Configure AI link + status --
        footer_row = QHBoxLayout()
        footer_row.setSpacing(12)

        configure_link = QPushButton("Configure AI")
        configure_link.setAccessibleName("Configure AI backend")
        configure_link.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        configure_link.setCursor(Qt.CursorShape.PointingHandCursor)
        configure_link.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {c['primary_text']}; "
            f"border: none; font-size: 12px; text-decoration: underline; }}"
        )
        configure_link.clicked.connect(self._open_setup_wizard)
        footer_row.addWidget(configure_link)

        self._status_label = QLabel()
        self._status_label.setStyleSheet(
            f"font-size: 11px; color: {c['text_muted']};"
        )
        self._update_status_label()
        footer_row.addWidget(self._status_label)
        footer_row.addStretch()

        root.addLayout(footer_row)

    # -- sub-builders --

    def _build_summary_panel(self, c) -> QWidget:
        panel = QWidget()
        panel.setStyleSheet(
            f"QWidget {{ background: {c['dark_card']}; "
            f"border: 1px solid {c['dark_border']}; border-radius: 8px; }}"
        )
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Strength themes
        if self._teacher_safe["strength_themes"]:
            lbl = QLabel("Strength Themes")
            lbl.setStyleSheet(
                f"font-size: 12px; font-weight: bold; color: {c['text']}; border: none;"
            )
            layout.addWidget(lbl)
            themes_text = ", ".join(self._teacher_safe["strength_themes"])
            t = QLabel(themes_text)
            t.setWordWrap(True)
            t.setStyleSheet(f"font-size: 12px; color: {c['text_muted']}; border: none;")
            t.setAccessibleName(f"Strength themes: {themes_text}")
            layout.addWidget(t)

        # Support categories with counts
        if self._teacher_safe["support_category_counts"]:
            lbl = QLabel("Support Areas")
            lbl.setStyleSheet(
                f"font-size: 12px; font-weight: bold; color: {c['text']}; border: none;"
            )
            layout.addWidget(lbl)
            parts = [
                f"{cat.title()} ({count})"
                for cat, count in self._teacher_safe["support_category_counts"].items()
            ]
            cats_text = ", ".join(parts)
            t = QLabel(cats_text)
            t.setWordWrap(True)
            t.setStyleSheet(f"font-size: 12px; color: {c['text_muted']}; border: none;")
            t.setAccessibleName(f"Support areas: {cats_text}")
            layout.addWidget(t)

        # Goal themes
        if self._teacher_safe["goal_themes"]:
            lbl = QLabel("Goal Themes")
            lbl.setStyleSheet(
                f"font-size: 12px; font-weight: bold; color: {c['text']}; border: none;"
            )
            layout.addWidget(lbl)
            goals_text = ", ".join(self._teacher_safe["goal_themes"])
            t = QLabel(goals_text)
            t.setWordWrap(True)
            t.setStyleSheet(f"font-size: 12px; color: {c['text_muted']}; border: none;")
            t.setAccessibleName(f"Goal themes: {goals_text}")
            layout.addWidget(t)

        # UDL / POUR badges
        badge_row = QHBoxLayout()
        badge_row.setSpacing(4)
        if self._teacher_safe["udl_principles"]:
            for principle in self._teacher_safe["udl_principles"][:8]:
                badge = QLabel(principle)
                badge.setStyleSheet(
                    f"background: {c['secondary']}; color: white; "
                    f"border-radius: 8px; padding: 2px 8px; font-size: 10px;"
                )
                badge.setAccessibleName(f"UDL principle: {principle}")
                badge_row.addWidget(badge)
        if self._teacher_safe["pour_principles"]:
            for principle in self._teacher_safe["pour_principles"][:4]:
                badge = QLabel(principle)
                badge.setStyleSheet(
                    f"background: {c['tertiary']}; color: white; "
                    f"border-radius: 8px; padding: 2px 8px; font-size: 10px;"
                )
                badge.setAccessibleName(f"POUR principle: {principle}")
                badge_row.addWidget(badge)
        badge_row.addStretch()
        layout.addLayout(badge_row)

        # Effectiveness summary
        if self._teacher_safe["effectiveness_summary"]:
            lbl = QLabel("Effectiveness")
            lbl.setStyleSheet(
                f"font-size: 12px; font-weight: bold; color: {c['text']}; border: none;"
            )
            layout.addWidget(lbl)
            for cat, avg in self._teacher_safe["effectiveness_summary"].items():
                bar_row = QHBoxLayout()
                bar_row.setSpacing(6)
                cat_lbl = QLabel(f"{cat.title()}")
                cat_lbl.setFixedWidth(120)
                cat_lbl.setStyleSheet(
                    f"font-size: 11px; color: {c['text_muted']}; border: none;"
                )
                bar_row.addWidget(cat_lbl)

                # Simple bar
                bar_bg = QWidget()
                bar_bg.setFixedHeight(10)
                bar_bg.setStyleSheet(
                    f"background: {c['dark_input']}; border-radius: 5px; border: none;"
                )
                bar_fill = QWidget(bar_bg)
                fill_pct = min(avg / 5.0, 1.0)
                bar_fill.setFixedHeight(10)
                bar_fill.setFixedWidth(int(fill_pct * 150))
                bar_fill.setStyleSheet(
                    f"background: {c['success']}; border-radius: 5px; border: none;"
                )
                bar_bg.setFixedWidth(150)
                bar_row.addWidget(bar_bg)

                rating_lbl = QLabel(f"{avg}/5")
                rating_lbl.setStyleSheet(
                    f"font-size: 11px; color: {c['text_muted']}; border: none;"
                )
                bar_row.addWidget(rating_lbl)
                bar_row.addStretch()
                layout.addLayout(bar_row)

        panel.setAccessibleName("Theme summary panel")
        return panel

    def _build_no_backend_widget(self, c) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)

        lbl = QLabel("No AI backend configured.")
        lbl.setStyleSheet(f"font-size: 13px; color: {c['warning']};")
        layout.addWidget(lbl)

        setup_btn = QPushButton("Set Up Now")
        setup_btn.setAccessibleName("Set up AI backend")
        setup_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        setup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        setup_btn.setFixedHeight(32)
        setup_btn.setStyleSheet(
            f"QPushButton {{ background: {c['primary']}; color: white; "
            f"border: none; border-radius: 6px; padding: 0 14px; font-size: 12px; }}"
        )
        setup_btn.clicked.connect(self._open_setup_wizard)
        layout.addWidget(setup_btn)
        layout.addStretch()
        return widget

    # -- actions --

    def _toggle_summary(self):
        self._summary_visible = not self._summary_visible
        self._summary_panel.setVisible(self._summary_visible)
        self._toggle_btn.setText(
            "Hide Summary" if self._summary_visible else "Show Summary"
        )

    def _on_suggestion(self, question: str):
        self._input.setText(question)
        self._send_message()

    def _send_message(self):
        text = self._input.text().strip()
        if not text:
            return
        if self.backend_manager._client is None:
            self._add_system_bubble("Please configure an AI backend first.")
            return

        self._input.clear()
        self._add_user_bubble(text)
        self._set_input_enabled(False)

        # Start streaming
        self._current_assistant_label = self._add_assistant_bubble("")
        self._worker = _StreamWorker(
            self.backend_manager, text,
            self._system_prompt, self._conversation_history,
        )
        self._worker.chunk_received.connect(self._on_chunk)
        self._worker.finished_signal.connect(self._on_stream_done)
        self._worker.error_signal.connect(self._on_stream_error)
        self._worker.start()

    def _on_chunk(self, chunk: str):
        if self._current_assistant_label:
            current = self._current_assistant_label.text()
            self._current_assistant_label.setText(current + chunk)
            # Scroll to bottom
            QTimer.singleShot(10, self._scroll_to_bottom)

    def _on_stream_error(self, error_msg: str):
        self._add_system_bubble(f"Error: {error_msg}")
        self._set_input_enabled(True)

    # -- chat bubble helpers --

    def _add_user_bubble(self, text: str):
        c = get_colors()
        # Store in conversation history
        self._conversation_history.append({"role": "user", "content": text})

        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setStyleSheet(
            f"background: {c['primary']}; color: white; border-radius: 12px; "
            f"padding: 8px 14px; font-size: 13px;"
        )
        bubble.setAccessibleName(f"You said: {text}")
        bubble.setMinimumHeight(APP_SETTINGS["touch_target_min"])

        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(bubble)

        container = QWidget()
        container.setLayout(row)
        self._chat_layout.insertWidget(self._chat_layout.count() - 1, container)
        QTimer.singleShot(10, self._scroll_to_bottom)

    def _add_assistant_bubble(self, text: str) -> QLabel:
        c = get_colors()
        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setStyleSheet(
            f"background: {c['dark_input']}; color: {c['text']}; "
            f"border-radius: 12px; padding: 8px 14px; font-size: 13px;"
        )
        bubble.setAccessibleName("Coach is responding")
        bubble.setMinimumHeight(APP_SETTINGS["touch_target_min"])
        bubble.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )

        role_lbl = QLabel("Coach")
        role_lbl.setStyleSheet(
            f"font-size: 10px; color: {c['text_muted']}; margin-bottom: 2px;"
        )
        role_lbl.setAccessibleName("Coach message")

        col = QVBoxLayout()
        col.setSpacing(2)
        col.addWidget(role_lbl)
        col.addWidget(bubble)

        row = QHBoxLayout()
        row.addLayout(col)
        row.addStretch()

        container = QWidget()
        container.setLayout(row)
        self._chat_layout.insertWidget(self._chat_layout.count() - 1, container)
        return bubble

    def _add_system_bubble(self, text: str):
        c = get_colors()
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(
            f"color: {c['warning']}; font-size: 12px; font-style: italic; "
            f"padding: 6px;"
        )
        lbl.setAccessibleName(f"System message: {text}")
        self._chat_layout.insertWidget(self._chat_layout.count() - 1, lbl)
        QTimer.singleShot(10, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        vbar = self._chat_scroll.verticalScrollBar()
        vbar.setValue(vbar.maximum())

    def _set_input_enabled(self, enabled: bool):
        self._input.setEnabled(enabled)
        self._send_btn.setEnabled(enabled)

    def _update_status_label(self):
        if self.backend_manager._client is None:
            self._status_label.setText("Status: No backend")
        else:
            provider = self.backend_manager.provider
            model = self.backend_manager.model
            self._status_label.setText(f"Status: {provider} / {model}")

    def _open_setup_wizard(self):
        from ui.screens.setup_wizard import SetupWizard
        dlg = SetupWizard(self.backend_manager, self)
        dlg.exec()
        # Refresh status after wizard closes
        self._update_status_label()
        self._no_backend_widget.setVisible(
            self.backend_manager._client is None
        )

    def _on_stream_done(self):
        """Called when streaming finishes — save assistant response to history."""
        if self._current_assistant_label:
            full_response = self._current_assistant_label.text()
            self._conversation_history.append(
                {"role": "assistant", "content": full_response}
            )
            self._current_assistant_label.setAccessibleName(
                f"Coach response: {full_response[:200]}"
            )
        self._current_assistant_label = None
        self._set_input_enabled(True)
        self._input.setFocus()

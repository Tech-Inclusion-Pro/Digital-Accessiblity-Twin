"""Student My Insights page — AI analyses the student's own support effectiveness."""

import asyncio
import json
from datetime import datetime, timezone

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QComboBox, QFrame, QLineEdit,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer

from config.settings import get_colors, APP_SETTINGS
from models.student_profile import StudentProfile
from models.support import SupportEntry
from models.tracking import TrackingLog
from ai.prompts.student_insights_prompt import build_student_insights_prompt
from ui.components.empty_state import EmptyState
from ui.components.mic_button import MicButton
from models.insight_log import InsightLog


class _StudentInsightsStreamWorker(QThread):
    """Runs the async AI generation in a background thread."""

    chunk_received = pyqtSignal(str)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, backend_manager, system_prompt, parent=None):
        super().__init__(parent)
        self.bm = backend_manager
        self.system_prompt = system_prompt

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
            "Please analyse my support data and produce the insights report.",
            system_prompt=self.system_prompt,
            conversation_history=[],
        ):
            self.chunk_received.emit(chunk)


class _InsightChatStreamWorker(QThread):
    """Runs the async AI chat in a background thread."""

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


def _parse_json_field(raw):
    """Safely parse a JSON string or return the dict/list as-is."""
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {}
    return raw if raw else {}


class StudentInsightsPage(QWidget):
    """My Insights page — AI analyses the student's own support effectiveness."""

    def __init__(self, db_manager, auth_manager, backend_manager=None, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.auth = auth_manager
        self.backend_manager = backend_manager
        self._worker = None
        self._chat_worker = None
        self._profile = None
        self._insight_history = []  # [(id, content, created_at)]
        self._current_insight_id = None
        self._chat_history = []  # [{role, content}, ...]
        self._current_chat_label = None
        self._build_ui()

    def _build_ui(self):
        c = get_colors()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Header
        header = QLabel("My Insights")
        header.setStyleSheet(
            f"font-size: 22px; font-weight: bold; color: {c['text']};"
        )
        header.setAccessibleName("My Insights")
        layout.addWidget(header)

        # Description
        desc = QLabel(
            "See how your supports are working for you. This page analyses "
            "your support ratings and tracking notes to find what's working "
            "well, what might need attention, and topics to discuss with "
            "your teacher."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size: 13px; color: {c['text_muted']};")
        desc.setAccessibleName("My Insights description")
        layout.addWidget(desc)

        # Action row
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self._generate_btn = QPushButton("Generate Insights")
        self._generate_btn.setAccessibleName("Generate my insights")
        self._generate_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._generate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._generate_btn.setFixedHeight(APP_SETTINGS["touch_target_min"])
        self._generate_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['primary']}; color: white;
                border: none; border-radius: 8px; padding: 0 20px;
                font-weight: bold; font-size: 13px;
            }}
            QPushButton:disabled {{
                background: {c['dark_border']}; color: {c['text_muted']};
            }}
        """)
        self._generate_btn.clicked.connect(self._generate_insights)
        action_row.addWidget(self._generate_btn)

        self._transparency_btn = QPushButton("How was this decided?")
        self._transparency_btn.setAccessibleName("Show AI transparency information")
        self._transparency_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._transparency_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._transparency_btn.setFixedHeight(APP_SETTINGS["touch_target_min"])
        self._transparency_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {c['text_muted']}; "
            f"border: none; font-size: 12px; text-decoration: underline; }}"
        )
        self._transparency_btn.clicked.connect(self._show_transparency)
        action_row.addWidget(self._transparency_btn)

        action_row.addStretch()
        layout.addLayout(action_row)

        # Info label
        self._info_label = QLabel("")
        self._info_label.setStyleSheet(
            f"font-size: 12px; color: {c['text_muted']};"
        )
        layout.addWidget(self._info_label)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {c['dark_border']};")
        layout.addWidget(sep)

        # Saved Insights history row
        history_row = QHBoxLayout()
        history_row.setSpacing(10)

        history_label = QLabel("Saved Insights:")
        history_label.setStyleSheet(f"font-size: 13px; color: {c['text']};")
        history_row.addWidget(history_label)

        self._history_combo = QComboBox()
        self._history_combo.setAccessibleName("Browse saved insights")
        self._history_combo.setFixedHeight(APP_SETTINGS["touch_target_min"])
        self._history_combo.setMinimumWidth(300)
        self._history_combo.setStyleSheet(f"""
            QComboBox {{
                background: {c['dark_input']}; color: {c['text']};
                border: 1px solid {c['dark_border']}; border-radius: 8px;
                padding: 0 12px; font-size: 13px;
            }}
        """)
        self._history_combo.setPlaceholderText("No saved insights yet")
        self._history_combo.currentIndexChanged.connect(self._on_history_changed)
        history_row.addWidget(self._history_combo)

        history_row.addStretch()
        layout.addLayout(history_row)

        # Empty state
        self._empty = EmptyState(
            icon_text="\u2606",
            message="No supports found. Add supports in your profile first.",
            action_label="Go to Profile",
        )
        self._empty.setVisible(False)
        layout.addWidget(self._empty)

        # Scrollable output area
        self._output_scroll = QScrollArea()
        self._output_scroll.setWidgetResizable(True)
        self._output_scroll.setStyleSheet(
            f"QScrollArea {{ border: 1px solid {c['dark_border']}; "
            f"border-radius: 8px; background: {c['dark_card']}; }}"
        )
        self._output_scroll.setAccessibleName("Insights output area")

        self._output_label = QLabel("")
        self._output_label.setWordWrap(True)
        self._output_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._output_label.setStyleSheet(
            f"font-size: 13px; color: {c['text']}; padding: 16px;"
        )
        self._output_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        self._output_scroll.setWidget(self._output_label)
        layout.addWidget(self._output_scroll, stretch=1)

        # ---- Chat with Insight section ----
        chat_sep = QFrame()
        chat_sep.setFrameShape(QFrame.Shape.HLine)
        chat_sep.setStyleSheet(f"color: {c['dark_border']};")
        layout.addWidget(chat_sep)

        chat_header = QLabel("Chat with this Insight")
        chat_header.setStyleSheet(
            f"font-size: 15px; font-weight: bold; color: {c['text']};"
        )
        chat_header.setAccessibleName("Chat with this insight")
        layout.addWidget(chat_header)

        # Chat messages area
        self._chat_scroll = QScrollArea()
        self._chat_scroll.setWidgetResizable(True)
        self._chat_scroll.setStyleSheet(
            f"QScrollArea {{ border: 1px solid {c['dark_border']}; "
            f"border-radius: 8px; background: {c['dark_card']}; }}"
        )
        self._chat_scroll.setAccessibleName("Insight chat conversation area")

        self._chat_container = QWidget()
        self._chat_layout = QVBoxLayout(self._chat_container)
        self._chat_layout.setContentsMargins(8, 8, 8, 8)
        self._chat_layout.setSpacing(8)
        self._chat_layout.addStretch()
        self._chat_scroll.setWidget(self._chat_container)
        layout.addWidget(self._chat_scroll, stretch=1)

        # Chat input row
        chat_input_row = QHBoxLayout()
        chat_input_row.setSpacing(8)

        self._chat_input = QLineEdit()
        self._chat_input.setPlaceholderText(
            "Generate or select an insight to start chatting..."
        )
        self._chat_input.setAccessibleName("Chat message input")
        self._chat_input.setFixedHeight(APP_SETTINGS["touch_target_min"])
        self._chat_input.setEnabled(False)
        self._chat_input.setStyleSheet(
            f"QLineEdit {{ background: {c['dark_input']}; color: {c['text']}; "
            f"border: 1px solid {c['dark_border']}; border-radius: 8px; "
            f"padding: 0 12px; font-size: 14px; }}"
        )
        self._chat_input.returnPressed.connect(self._send_chat_message)
        chat_input_row.addWidget(self._chat_input, stretch=1)

        chat_input_row.addWidget(MicButton(target=self._chat_input))

        self._chat_send_btn = QPushButton("Send")
        self._chat_send_btn.setAccessibleName("Send chat message")
        self._chat_send_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._chat_send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._chat_send_btn.setFixedHeight(APP_SETTINGS["touch_target_min"])
        self._chat_send_btn.setFixedWidth(80)
        self._chat_send_btn.setEnabled(False)
        self._chat_send_btn.setStyleSheet(
            f"QPushButton {{ background: {c['primary']}; color: white; "
            f"border: none; border-radius: 8px; font-weight: bold; font-size: 14px; }}"
            f"QPushButton:disabled {{ background: {c['dark_border']}; color: {c['text_muted']}; }}"
        )
        self._chat_send_btn.clicked.connect(self._send_chat_message)
        chat_input_row.addWidget(self._chat_send_btn)

        layout.addLayout(chat_input_row)

    # ------------------------------------------------------------------ data

    def _build_support_data_string(self, profile, supports, tracking_logs) -> str:
        """Format student support data for the AI prompt."""
        lines = []
        first_name = profile.name.split()[0] if profile.name else "Student"
        lines.append(f"Student first name: {first_name}")
        lines.append("")

        # Active supports
        active = [s for s in supports if s.status == "active"]
        lines.append(f"Active supports: {len(active)}")
        lines.append("")

        if active:
            lines.append("-- Support Entries --")
            for s in active:
                rating = f" (effectiveness: {s.effectiveness_rating}/5)" if s.effectiveness_rating else " (no rating yet)"
                lines.append(f"  [{s.category}/{s.subcategory or 'general'}] {s.description}{rating}")
                udl = _parse_json_field(s.udl_mapping)
                if udl:
                    lines.append(f"    UDL: {json.dumps(udl)}")
                pour = _parse_json_field(s.pour_mapping)
                if pour:
                    lines.append(f"    POUR: {json.dumps(pour)}")
            lines.append("")

        # Tracking logs
        if tracking_logs:
            lines.append(f"-- Tracking Logs ({len(tracking_logs)} entries) --")
            for log in tracking_logs:
                ts = log.created_at.strftime("%Y-%m-%d %H:%M") if log.created_at else "unknown"
                impl = log.implementation_notes or ""
                outcome = log.outcome_notes or ""
                support_info = ""
                if log.support_id:
                    # Find matching support
                    match = next((s for s in supports if s.id == log.support_id), None)
                    if match:
                        support_info = f" [{match.category}: {match.description[:50]}]"
                lines.append(f"  {ts}{support_info}")
                if impl:
                    lines.append(f"    Implementation: {impl[:300]}")
                if outcome:
                    lines.append(f"    Outcome: {outcome[:300]}")
            lines.append("")

        # Summary stats
        rated = [s for s in active if s.effectiveness_rating is not None]
        if rated:
            avg = sum(s.effectiveness_rating for s in rated) / len(rated)
            lines.append(f"Overall average effectiveness: {avg:.1f}/5")
            high = [s for s in rated if s.effectiveness_rating >= 3.5]
            low = [s for s in rated if s.effectiveness_rating < 3.0]
            lines.append(f"Supports rated 3.5+: {len(high)}")
            lines.append(f"Supports rated below 3.0: {len(low)}")

        return "\n".join(lines)

    # --------------------------------------------------------- insight generation

    def _generate_insights(self):
        # Check AI backend
        if not self.backend_manager or self.backend_manager._client is None:
            self._output_label.setText(
                "No AI backend configured. Please set up an AI provider in "
                "AI Settings before generating insights."
            )
            return

        if not self._profile:
            self._output_label.setText(
                "No student profile found. Please create your profile first."
            )
            return

        self._generate_btn.setEnabled(False)
        self._output_label.setText("Generating insights...")
        self._clear_chat()
        self._current_insight_id = None
        self._set_chat_enabled(False)

        session = self.db.get_session()
        try:
            profile = session.query(StudentProfile).get(self._profile.id)
            if not profile:
                self._output_label.setText("Student profile not found.")
                self._generate_btn.setEnabled(True)
                return

            supports = session.query(SupportEntry).filter(
                SupportEntry.profile_id == profile.id
            ).all()

            tracking_logs = session.query(TrackingLog).filter(
                TrackingLog.profile_id == profile.id,
            ).order_by(TrackingLog.created_at.desc()).all()

            if not supports:
                self._output_label.setText(
                    "No supports found. Add supports in your profile first, "
                    "then come back here for insights."
                )
                self._generate_btn.setEnabled(True)
                return

            support_data = self._build_support_data_string(
                profile, supports, tracking_logs
            )
        finally:
            session.close()

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        system_prompt = build_student_insights_prompt(support_data, now)

        # Start streaming
        self._output_label.setText("")
        self._worker = _StudentInsightsStreamWorker(
            self.backend_manager, system_prompt
        )
        self._worker.chunk_received.connect(self._on_chunk)
        self._worker.finished_signal.connect(self._on_stream_done)
        self._worker.error_signal.connect(self._on_stream_error)
        self._worker.start()

    def _on_chunk(self, chunk: str):
        current = self._output_label.text()
        self._output_label.setText(current + chunk)
        QTimer.singleShot(10, self._scroll_to_bottom)

    def _on_stream_done(self):
        self._generate_btn.setEnabled(True)
        self._save_insight()

    def _on_stream_error(self, error_msg: str):
        self._output_label.setText(f"Error generating insights: {error_msg}")
        self._generate_btn.setEnabled(True)

    def _scroll_to_bottom(self):
        vbar = self._output_scroll.verticalScrollBar()
        vbar.setValue(vbar.maximum())

    # --------------------------------------------------------- insight persistence

    def _save_insight(self):
        """Save the generated insight to the database."""
        content = self._output_label.text().strip()
        if not content or content.startswith("Error") or not self._profile:
            return

        user = self.auth.get_current_user()
        if not user:
            return

        session = self.db.get_session()
        try:
            log = InsightLog(
                profile_id=self._profile.id,
                user_id=user.id,
                role="student",
                content=content,
            )
            session.add(log)
            session.commit()
            self._current_insight_id = log.id
        finally:
            session.close()

        self._set_chat_enabled(True)
        self._refresh_history()

    def _refresh_history(self):
        """Reload the history combo with past insights."""
        user = self.auth.get_current_user()
        if not user or not self._profile:
            return

        session = self.db.get_session()
        try:
            logs = (
                session.query(InsightLog)
                .filter(
                    InsightLog.profile_id == self._profile.id,
                    InsightLog.user_id == user.id,
                    InsightLog.role == "student",
                )
                .order_by(InsightLog.created_at.desc())
                .all()
            )
            self._insight_history = [
                (log.id, log.content, log.created_at) for log in logs
            ]
        finally:
            session.close()

        self._history_combo.blockSignals(True)
        self._history_combo.clear()
        for _, _, created_at in self._insight_history:
            ts = created_at.strftime("%b %d, %Y at %I:%M %p") if created_at else "Unknown"
            self._history_combo.addItem(ts)
        self._history_combo.blockSignals(False)

        # Select the most recent entry if available
        if self._insight_history:
            self._history_combo.setCurrentIndex(0)

    def _on_history_changed(self, index: int):
        """Load a past insight and its chat when selected from the history combo."""
        if 0 <= index < len(self._insight_history):
            insight_id, content, _ = self._insight_history[index]
            self._output_label.setText(content)
            self._load_chat_history(insight_id)

    # --------------------------------------------------------- chat with insight

    def _set_chat_enabled(self, enabled: bool):
        """Enable or disable the chat input area."""
        self._chat_input.setEnabled(enabled)
        self._chat_send_btn.setEnabled(enabled)
        if enabled:
            self._chat_input.setPlaceholderText(
                "Ask a question about this insight..."
            )
        else:
            self._chat_input.setPlaceholderText(
                "Generate or select an insight to start chatting..."
            )

    def _clear_chat(self):
        """Remove all chat bubbles from the chat area."""
        while self._chat_layout.count() > 1:  # keep the trailing stretch
            item = self._chat_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._chat_history = []
        self._current_chat_label = None

    def _load_chat_history(self, insight_id: int):
        """Load and display chat history for a saved insight."""
        self._clear_chat()
        self._current_insight_id = insight_id

        session = self.db.get_session()
        try:
            log = session.query(InsightLog).get(insight_id)
            if log:
                self._chat_history = list(log.conversation)
        finally:
            session.close()

        for msg in self._chat_history:
            if msg.get("role") == "user":
                self._add_user_bubble(msg["content"])
            elif msg.get("role") == "assistant":
                self._add_assistant_bubble(msg["content"])

        self._set_chat_enabled(True)

    def _build_chat_system_prompt(self) -> str:
        """Build the system prompt for chatting about the current insight."""
        insight_text = self._output_label.text()
        return (
            "You are a supportive accessibility insights assistant helping a student "
            "understand their AI-generated insight report about their support effectiveness. "
            "Answer their questions about this report helpfully and concisely.\n\n"
            "Guidelines:\n"
            "- Be warm, encouraging, and strengths-based\n"
            "- Help the student understand what the insights mean for them\n"
            "- Suggest ways they can advocate for themselves based on the insights\n"
            "- Keep responses concise and clear\n"
            "- Never reveal diagnoses or sensitive information\n"
            "- Use the student's first name if they mention it\n\n"
            f"=== INSIGHT REPORT ===\n{insight_text}\n=== END REPORT ==="
        )

    def _send_chat_message(self):
        """Send a user message to the insight chat."""
        text = self._chat_input.text().strip()
        if not text or not self._current_insight_id:
            return
        if not self.backend_manager or self.backend_manager._client is None:
            self._add_system_bubble("Please configure an AI backend first.")
            return

        self._chat_input.clear()
        self._chat_history.append({"role": "user", "content": text})
        self._add_user_bubble(text)
        self._chat_input.setEnabled(False)
        self._chat_send_btn.setEnabled(False)

        # Start streaming the assistant reply
        self._current_chat_label = self._add_assistant_bubble("")
        self._chat_worker = _InsightChatStreamWorker(
            self.backend_manager, text,
            self._build_chat_system_prompt(), self._chat_history[:-1],
        )
        self._chat_worker.chunk_received.connect(self._on_chat_chunk)
        self._chat_worker.finished_signal.connect(self._on_chat_done)
        self._chat_worker.error_signal.connect(self._on_chat_error)
        self._chat_worker.start()

    def _on_chat_chunk(self, chunk: str):
        if self._current_chat_label:
            current = self._current_chat_label.text()
            self._current_chat_label.setText(current + chunk)
            QTimer.singleShot(10, self._scroll_chat_to_bottom)

    def _on_chat_done(self):
        if self._current_chat_label:
            full_response = self._current_chat_label.text()
            self._chat_history.append(
                {"role": "assistant", "content": full_response}
            )
            self._current_chat_label.setAccessibleName(
                f"Insight assistant response: {full_response[:200]}"
            )
        self._current_chat_label = None
        self._chat_input.setEnabled(True)
        self._chat_send_btn.setEnabled(True)
        self._chat_input.setFocus()
        self._save_chat()

    def _on_chat_error(self, error_msg: str):
        self._add_system_bubble(f"Error: {error_msg}")
        self._chat_input.setEnabled(True)
        self._chat_send_btn.setEnabled(True)

    def _save_chat(self):
        """Persist chat history to the current InsightLog."""
        if not self._current_insight_id or not self._chat_history:
            return
        session = self.db.get_session()
        try:
            log = session.query(InsightLog).get(self._current_insight_id)
            if log:
                log.conversation = self._chat_history
                session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

    # ---- chat bubble helpers ----

    def _add_user_bubble(self, text: str):
        c = get_colors()
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
        QTimer.singleShot(10, self._scroll_chat_to_bottom)

    def _add_assistant_bubble(self, text: str) -> QLabel:
        c = get_colors()
        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setStyleSheet(
            f"background: {c['dark_input']}; color: {c['text']}; "
            f"border-radius: 12px; padding: 8px 14px; font-size: 13px;"
        )
        bubble.setAccessibleName("Insight assistant response")
        bubble.setMinimumHeight(APP_SETTINGS["touch_target_min"])
        bubble.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )

        role_lbl = QLabel("Insight Assistant")
        role_lbl.setStyleSheet(
            f"font-size: 10px; color: {c['text_muted']}; margin-bottom: 2px;"
        )

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
        QTimer.singleShot(10, self._scroll_chat_to_bottom)

    def _scroll_chat_to_bottom(self):
        vbar = self._chat_scroll.verticalScrollBar()
        vbar.setValue(vbar.maximum())

    # --------------------------------------------------------- transparency

    def _show_transparency(self):
        from ui.components.transparency_dialog import TransparencyDialog, TransparencyInfo

        info = TransparencyInfo(
            feature_name="My Insights",
            provider_type=self.backend_manager.provider_type if self.backend_manager else "",
            provider=self.backend_manager.provider if self.backend_manager else "",
            model=self.backend_manager.model if self.backend_manager else "",
            principles=[
                "Presume Competence — you are capable and know yourself best.",
                "Strengths-Based — always lead with what is working well.",
                "Nothing About Us Without Us — your voice and preferences are central.",
                "Self-Advocacy — insights are designed to help you speak up for yourself.",
                "Privacy First — only your first name is used; no diagnoses are revealed.",
            ],
            privacy_rules=[
                "Only your first name is used — never your full name.",
                "No diagnoses or medical labels are mentioned.",
                "No stakeholder or family member names are revealed.",
                "Support descriptions are summarised, not quoted verbatim.",
                "Data stays on this device (or your configured AI provider).",
            ],
            data_summary=self._build_transparency_data_summary(),
            warnings=[
                "AI analysis is based on the data you have entered — more data "
                "means better insights.",
                "AI may misinterpret patterns or make incorrect suggestions.",
                "These insights are a starting point for conversation, not a "
                "professional assessment.",
                "Always trust your own experience over AI-generated analysis.",
            ],
        )

        dlg = TransparencyDialog(info, self)
        dlg.exec()

    def _build_transparency_data_summary(self) -> dict:
        """Build a summary of what data is provided to the AI."""
        summary = {}
        if self._profile:
            first_name = self._profile.name.split()[0] if self._profile.name else "Student"
            summary["Student"] = f"{first_name} (first name only)"

        info_text = self._info_label.text()
        if info_text:
            summary["Data"] = info_text
        return summary

    # --------------------------------------------------------- refresh

    def refresh_data(self):
        """Load profile and update support/log counts."""
        user = self.auth.get_current_user()
        if not user:
            return

        session = self.db.get_session()
        try:
            profile = session.query(StudentProfile).filter(
                StudentProfile.user_id == user.id
            ).first()

            if not profile:
                self._profile = None
                self._info_label.setText("")
                self._empty.setVisible(True)
                self._output_scroll.setVisible(False)
                return

            self._profile = profile

            support_count = session.query(SupportEntry).filter(
                SupportEntry.profile_id == profile.id
            ).count()

            log_count = session.query(TrackingLog).filter(
                TrackingLog.profile_id == profile.id
            ).count()
        finally:
            session.close()

        if support_count == 0:
            self._info_label.setText("")
            self._empty.setVisible(True)
            self._output_scroll.setVisible(False)
        else:
            self._info_label.setText(
                f"{support_count} support(s) and {log_count} tracking log(s) found."
            )
            self._empty.setVisible(False)
            self._output_scroll.setVisible(True)

        self._refresh_history()

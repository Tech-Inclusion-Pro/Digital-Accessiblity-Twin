"""Teacher AI Insights page — analyses past consultations for a selected student."""

import asyncio

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QComboBox, QFrame,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer

from config.settings import get_colors, APP_SETTINGS
from models.student_profile import StudentProfile
from models.document import Document
from models.evaluation import TwinEvaluation
from models.support import SupportEntry
from models.tracking import TrackingLog
from models.consultation_log import ConsultationLog
from ai.privacy_aggregator import PrivacyAggregator
from ai.prompts.insights_prompt import build_insights_prompt
from ui.components.empty_state import EmptyState


class _InsightsStreamWorker(QThread):
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
            "Please analyse the consultation history and produce the insights report.",
            system_prompt=self.system_prompt,
            conversation_history=[],
        ):
            self.chunk_received.emit(chunk)


class TeacherInsightsPage(QWidget):
    """AI Insights page — analyses past consultations through POUR/UDL lenses."""

    def __init__(self, db_manager, auth_manager, backend_manager=None, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.auth = auth_manager
        self.backend_manager = backend_manager
        self._worker = None
        self._student_data: list = []  # [(profile_id, name, consult_count)]
        self._build_ui()

    def _build_ui(self):
        c = get_colors()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Header
        header = QLabel("AI Insights")
        header.setStyleSheet(
            f"font-size: 22px; font-weight: bold; color: {c['text']};"
        )
        header.setAccessibleName("AI Insights")
        layout.addWidget(header)

        # Description
        desc = QLabel(
            "Analyse past coach consultations to identify question patterns, "
            "student needs through POUR and UDL lenses, and receive concrete "
            "preparation recommendations."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size: 13px; color: {c['text_muted']};")
        desc.setAccessibleName("AI Insights description")
        layout.addWidget(desc)

        # Student selector row
        selector_row = QHBoxLayout()
        selector_row.setSpacing(10)

        selector_label = QLabel("Student:")
        selector_label.setStyleSheet(
            f"font-size: 14px; color: {c['text']};"
        )
        selector_row.addWidget(selector_label)

        self._combo = QComboBox()
        self._combo.setAccessibleName("Select student for insights")
        self._combo.setFixedHeight(APP_SETTINGS["touch_target_min"])
        self._combo.setMinimumWidth(250)
        self._combo.setStyleSheet(f"""
            QComboBox {{
                background: {c['dark_input']}; color: {c['text']};
                border: 1px solid {c['dark_border']}; border-radius: 8px;
                padding: 0 12px; font-size: 13px;
            }}
        """)
        self._combo.currentIndexChanged.connect(self._on_student_changed)
        selector_row.addWidget(self._combo)

        self._generate_btn = QPushButton("Generate Insights")
        self._generate_btn.setAccessibleName("Generate AI insights for selected student")
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
        selector_row.addWidget(self._generate_btn)

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
        selector_row.addWidget(self._transparency_btn)

        selector_row.addStretch()
        layout.addLayout(selector_row)

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

        # Empty state (no consultations)
        self._empty = EmptyState(
            icon_text="\u2606",
            message="No past consultations found for this student.",
            action_label="Go to Students",
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

    def _on_student_changed(self, index: int):
        """Update the info label when student selection changes."""
        if 0 <= index < len(self._student_data):
            _, name, count = self._student_data[index]
            if count > 0:
                self._info_label.setText(
                    f"{count} consultation(s) found for {name}."
                )
                self._empty.setVisible(False)
                self._output_scroll.setVisible(True)
            else:
                self._info_label.setText("")
                self._empty.setVisible(True)
                self._output_scroll.setVisible(False)
        else:
            self._info_label.setText("")

    def _generate_insights(self):
        index = self._combo.currentIndex()
        if index < 0 or index >= len(self._student_data):
            return

        profile_id, name, count = self._student_data[index]

        # Check AI backend
        if not self.backend_manager or self.backend_manager._client is None:
            self._output_label.setText(
                "No AI backend configured. Please set up an AI provider in "
                "AI Settings before generating insights."
            )
            return

        if count == 0:
            self._output_label.setText(
                f"No past consultations for {name}. Use the Coach feature on "
                f"the Students page first, then come back here for insights."
            )
            return

        self._generate_btn.setEnabled(False)
        self._output_label.setText("Generating insights...")

        # Load consultation logs and student context
        session = self.db.get_session()
        try:
            profile = session.query(StudentProfile).get(profile_id)
            if not profile:
                self._output_label.setText("Student profile not found.")
                self._generate_btn.setEnabled(True)
                return

            supports = session.query(SupportEntry).filter(
                SupportEntry.profile_id == profile_id
            ).all()

            tracking_logs = session.query(TrackingLog).filter(
                TrackingLog.profile_id == profile_id,
            ).order_by(TrackingLog.created_at.desc()).limit(20).all()

            logs = (
                session.query(ConsultationLog)
                .filter(ConsultationLog.profile_id == profile_id)
                .order_by(ConsultationLog.created_at.asc())
                .all()
            )

            # Build student context via privacy aggregator
            aggregated = PrivacyAggregator.aggregate(profile, supports, tracking_logs)
            student_context = aggregated["ai_only"]["full_context_for_ai"]

            # Format consultation history
            history_lines = []
            for i, log in enumerate(logs, 1):
                ts = log.created_at.strftime("%Y-%m-%d %H:%M") if log.created_at else "unknown"
                history_lines.append(f"--- Consultation {i} ({ts}) ---")
                for msg in log.conversation:
                    role = "Teacher" if msg.get("role") == "user" else "Coach"
                    content = msg.get("content", "")
                    history_lines.append(f"  {role}: {content}")
                history_lines.append(f"  ({log.message_count} messages total)")
                history_lines.append("")

            consultation_history = "\n".join(history_lines)
        finally:
            session.close()

        system_prompt = build_insights_prompt(student_context, consultation_history)

        # Start streaming
        self._output_label.setText("")
        self._worker = _InsightsStreamWorker(
            self.backend_manager, system_prompt
        )
        self._worker.chunk_received.connect(self._on_chunk)
        self._worker.finished_signal.connect(self._on_stream_done)
        self._worker.error_signal.connect(self._on_stream_error)
        self._worker.start()

    def _show_transparency(self):
        """Show the AI transparency dialog."""
        from ui.components.transparency_dialog import TransparencyDialog, TransparencyInfo

        data_summary = {}
        index = self._combo.currentIndex()
        if 0 <= index < len(self._student_data):
            _, name, count = self._student_data[index]
            first_name = name.split()[0] if name else "Student"
            data_summary["Student"] = f"{first_name} (first name only)"
            data_summary["Consultations"] = str(count)

        info = TransparencyInfo(
            feature_name="AI Insights",
            provider_type=self.backend_manager.provider_type if self.backend_manager else "",
            provider=self.backend_manager.provider if self.backend_manager else "",
            model=self.backend_manager.model if self.backend_manager else "",
            principles=[
                "Nothing About Us Without Us — the student's own voice and "
                "preferences are paramount.",
                "Presume Competence — assume the student can learn and succeed.",
                "Design for the Margins — solutions that work for students at "
                "the margins work for everyone.",
                "Intersectionality — disability interacts with other identities.",
                "Collective Access — access benefits the whole community.",
            ],
            privacy_rules=[
                "Never reveals specific diagnoses or medical information.",
                "Never mentions stakeholder names or family members.",
                "Never quotes specific history events or personal anecdotes.",
                "Uses broad support themes only, not specific tool names.",
                "Uses the student's first name only.",
                "Summarises confidential details in broad strokes only.",
            ],
            data_summary=data_summary,
            warnings=[
                "Insights quality depends on the volume of consultation data — "
                "more consultations yield richer analysis.",
                "AI may misidentify patterns or produce inaccurate observations.",
                "The analysis reflects consultation content, not direct "
                "knowledge of the student.",
                "Always verify recommendations with the student and their "
                "support team.",
            ],
        )

        dlg = TransparencyDialog(info, self)
        dlg.exec()

    def _on_chunk(self, chunk: str):
        current = self._output_label.text()
        self._output_label.setText(current + chunk)
        QTimer.singleShot(10, self._scroll_to_bottom)

    def _on_stream_done(self):
        self._generate_btn.setEnabled(True)

    def _on_stream_error(self, error_msg: str):
        c = get_colors()
        self._output_label.setText(f"Error generating insights: {error_msg}")
        self._generate_btn.setEnabled(True)

    def _scroll_to_bottom(self):
        vbar = self._output_scroll.verticalScrollBar()
        vbar.setValue(vbar.maximum())

    def refresh_data(self):
        """Reload teacher's students and their consultation counts."""
        user = self.auth.get_current_user()
        if not user:
            return

        session = self.db.get_session()
        try:
            # Same pattern as home_page: Documents -> TwinEvaluations -> StudentProfiles
            import_docs = session.query(Document).filter(
                Document.teacher_user_id == user.id,
                Document.purpose_description == "twin_import",
            ).all()

            profile_ids = set()
            for doc in import_docs:
                evals = session.query(TwinEvaluation).filter(
                    TwinEvaluation.document_id == doc.id
                ).all()
                for ev in evals:
                    profile_ids.add(ev.student_profile_id)

            self._student_data = []
            if profile_ids:
                profiles = session.query(StudentProfile).filter(
                    StudentProfile.id.in_(profile_ids)
                ).all()
                for p in profiles:
                    count = session.query(ConsultationLog).filter(
                        ConsultationLog.profile_id == p.id,
                    ).count()
                    self._student_data.append((p.id, p.name, count))
        finally:
            session.close()

        # Populate combo
        self._combo.blockSignals(True)
        self._combo.clear()
        for pid, name, count in self._student_data:
            self._combo.addItem(f"{name} ({count} consultations)")
        self._combo.blockSignals(False)

        # Trigger change to update info label
        if self._student_data:
            self._on_student_changed(0)
        else:
            self._info_label.setText("")
            self._empty.setVisible(True)
            self._output_scroll.setVisible(False)

"""Review-gate dialog for the de-identified Share Overview export.

The student is the final authority: they see exactly what the teacher will
receive, can edit it, optionally run a local-AI privacy check, and must
explicitly confirm before the file is saved.
"""

import asyncio
from collections import Counter

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QFileDialog, QMessageBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from config.settings import get_colors, APP_SETTINGS
from utils.share_overview import build_overview_markdown
from utils.deidentify import generate_alias

_PRIVACY_CHECK_SYSTEM = (
    "You are a privacy reviewer helping a student share a de-identified "
    "document with a teacher. List any remaining details that could identify "
    "a specific person: names of people, schools, places, contact "
    "information, or unique identifying details. Quote each one briefly. "
    "If there are none, respond with exactly: No identifying information found."
)


class _PrivacyCheckWorker(QThread):
    """Run the overview draft through the local AI backend."""

    finished_text = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, backend_manager, markdown, parent=None):
        super().__init__(parent)
        self.bm = backend_manager
        self.markdown = markdown

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._ask())
        except Exception as e:
            self.failed.emit(str(e))
        finally:
            loop.close()

    async def _ask(self):
        chunks = []
        async for chunk in self.bm.generate_response(
            f"Review this document for identifying information:\n\n{self.markdown}",
            system_prompt=_PRIVACY_CHECK_SYSTEM,
        ):
            chunks.append(chunk)
        self.finished_text.emit("".join(chunks).strip())


class ShareOverviewDialog(QDialog):
    """Build, review, and save a de-identified overview Markdown file."""

    def __init__(self, profile, supports, tracking_logs,
                 backend_manager=None, db_manager=None, user_id=None,
                 parent=None):
        super().__init__(parent)
        self._profile = profile
        self._supports = supports
        self._logs = tracking_logs
        self.bm = backend_manager
        self.db = db_manager
        self._user_id = user_id
        self._worker = None

        self.setWindowTitle("Share Overview — Review Before Sharing")
        self.setMinimumSize(720, 640)
        self._build_ui()
        self._rebuild_draft()

    def _build_ui(self):
        c = get_colors()
        self.setStyleSheet(f"QDialog {{ background: {c['dark_bg']}; }}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        header = QLabel("Review Your Shared Overview")
        header.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {c['text']};"
        )
        header.setAccessibleName("Review your shared overview")
        layout.addWidget(header)

        intro = QLabel(
            "This is everything the teacher will see — nothing else leaves "
            "your device. Your name, history, stakeholders, and AI chats are "
            "not included. Edit the text below if anything still feels too "
            "personal."
        )
        intro.setStyleSheet(f"font-size: 13px; color: {c['text_muted']};")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        # Alias row
        alias_row = QHBoxLayout()
        alias_lbl = QLabel("Shared as:")
        alias_lbl.setStyleSheet(f"font-size: 13px; color: {c['text']};")
        alias_row.addWidget(alias_lbl)

        self._alias_edit = QLineEdit(generate_alias())
        self._alias_edit.setAccessibleName("Alias shown to the teacher")
        self._alias_edit.setFixedHeight(36)
        self._alias_edit.setMaximumWidth(220)
        self._alias_edit.setStyleSheet(f"""
            QLineEdit {{
                background: {c['dark_input']}; color: {c['text']};
                border: 1px solid {c['dark_border']}; border-radius: 6px;
                padding: 0 10px; font-size: 13px;
            }}
        """)
        alias_lbl.setBuddy(self._alias_edit)
        alias_row.addWidget(self._alias_edit)

        rebuild_btn = QPushButton("Rebuild Draft")
        rebuild_btn.setAccessibleName(
            "Rebuild draft with new alias, discarding manual edits"
        )
        rebuild_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        rebuild_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rebuild_btn.setFixedHeight(36)
        rebuild_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['dark_input']}; color: {c['text']};
                border: 1px solid {c['dark_border']}; border-radius: 6px;
                padding: 0 14px; font-size: 12px;
            }}
            QPushButton:hover {{ background: {c['dark_hover']}; }}
        """)
        rebuild_btn.clicked.connect(self._confirm_rebuild)
        alias_row.addWidget(rebuild_btn)
        alias_row.addStretch()
        layout.addLayout(alias_row)

        # Redaction summary
        self._redaction_lbl = QLabel("")
        self._redaction_lbl.setStyleSheet(
            f"font-size: 12px; color: {c['success']};"
        )
        self._redaction_lbl.setWordWrap(True)
        self._redaction_lbl.setAccessibleName("Summary of removed personal details")
        layout.addWidget(self._redaction_lbl)

        # Editable draft
        self._editor = QTextEdit()
        self._editor.setAccessibleName(
            "Overview draft, editable. This exact text will be shared."
        )
        self._editor.setStyleSheet(f"""
            QTextEdit {{
                background: {c['dark_card']}; color: {c['text']};
                border: 1px solid {c['dark_border']}; border-radius: 8px;
                font-family: monospace; font-size: 13px; padding: 8px;
            }}
        """)
        layout.addWidget(self._editor, stretch=1)

        # AI privacy check row
        check_row = QHBoxLayout()
        self._check_btn = QPushButton("Run AI Privacy Check")
        self._check_btn.setAccessibleName(
            "Run local AI privacy check on the draft"
        )
        self._check_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._check_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._check_btn.setFixedHeight(APP_SETTINGS["touch_target_min"])
        self._check_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['secondary']}; color: white;
                border: none; border-radius: 8px;
                padding: 0 20px; font-weight: bold; font-size: 13px;
            }}
            QPushButton:disabled {{ background: {c['dark_border']}; }}
        """)
        self._check_btn.clicked.connect(self._run_privacy_check)
        check_row.addWidget(self._check_btn)
        check_row.addStretch()
        layout.addLayout(check_row)

        local_ok = (
            self.bm is not None
            and self.bm.is_configured
            and self.bm.provider_type == "local"
        )
        if not local_ok:
            self._check_btn.setEnabled(False)
            self._check_btn.setToolTip(
                "Available when a local AI backend (e.g. Ollama) is configured. "
                "Cloud AI is never used for privacy checks."
            )

        self._check_result = QLabel("")
        self._check_result.setWordWrap(True)
        self._check_result.setStyleSheet(
            f"font-size: 12px; color: {c['warning']};"
        )
        self._check_result.setAccessibleName("AI privacy check results")
        layout.addWidget(self._check_result)

        # Bottom buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setAccessibleName("Cancel sharing")
        cancel_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        cancel_btn.setFixedHeight(APP_SETTINGS["touch_target_min"])
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['dark_input']}; color: {c['text']};
                border: 1px solid {c['dark_border']}; border-radius: 8px;
                padding: 0 20px; font-size: 13px;
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("Save && Share…")
        save_btn.setAccessibleName("Confirm and save overview file")
        save_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setFixedHeight(APP_SETTINGS["touch_target_min"])
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['primary']}; color: white;
                border: none; border-radius: 8px;
                padding: 0 24px; font-weight: bold; font-size: 13px;
            }}
        """)
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    # ------------------------------------------------------------------ draft

    def _rebuild_draft(self):
        alias = self._alias_edit.text().strip() or "Student"
        markdown, redactions = build_overview_markdown(
            self._profile, self._supports, self._logs, alias=alias
        )
        self._editor.setPlainText(markdown)

        if redactions:
            counts = Counter(label for label, _ in redactions)
            summary = ", ".join(f"{n}× {label}" for label, n in counts.items())
            self._redaction_lbl.setText(
                f"Automatically removed: {summary}. Please read the draft to "
                "catch anything the rules missed."
            )
        else:
            self._redaction_lbl.setText(
                "No personal details were detected by the automatic rules — "
                "please still read the draft carefully."
            )

    def _confirm_rebuild(self):
        reply = QMessageBox.question(
            self, "Rebuild Draft?",
            "Rebuilding regenerates the draft from your twin data and "
            "discards any manual edits. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._rebuild_draft()
            self._check_result.setText("")

    # ------------------------------------------------------------- AI check

    def _run_privacy_check(self):
        self._check_btn.setEnabled(False)
        self._check_btn.setText("Checking…")
        self._check_result.setText("")

        self._worker = _PrivacyCheckWorker(
            self.bm, self._editor.toPlainText(), parent=self
        )
        self._worker.finished_text.connect(self._on_check_done)
        self._worker.failed.connect(self._on_check_failed)
        self._worker.start()

    def _on_check_done(self, text: str):
        c = get_colors()
        self._check_btn.setEnabled(True)
        self._check_btn.setText("Run AI Privacy Check")
        if "no identifying information found" in text.lower():
            self._check_result.setStyleSheet(
                f"font-size: 12px; color: {c['success']};"
            )
            self._check_result.setText("AI check: no identifying information found.")
        else:
            self._check_result.setStyleSheet(
                f"font-size: 12px; color: {c['warning']};"
            )
            self._check_result.setText(
                f"AI check flagged possible identifying details — please "
                f"review and edit:\n{text}"
            )

    def _on_check_failed(self, err: str):
        c = get_colors()
        self._check_btn.setEnabled(True)
        self._check_btn.setText("Run AI Privacy Check")
        self._check_result.setStyleSheet(
            f"font-size: 12px; color: {c['error']};"
        )
        self._check_result.setText(f"AI check failed: {err}")

    # ----------------------------------------------------------------- save

    def _save(self):
        alias = self._alias_edit.text().strip() or "Student"
        reply = QMessageBox.question(
            self, "Share This Overview?",
            "The file will contain exactly the text shown in the draft — "
            "this is everything the teacher will see.\n\nSave it now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        default_name = f"{alias.replace(' ', '_')}_overview.md"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Overview", default_name, "Markdown Files (*.md)"
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._editor.toPlainText())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {e}")
            return

        self._audit("overview_exported", f"alias={alias}")
        QMessageBox.information(
            self, "Overview Saved",
            f"Your de-identified overview was saved to:\n{path}\n\n"
            "Share it only with teachers you trust.",
        )
        self.accept()

    def _audit(self, action: str, detail: str):
        if not self.db:
            return
        try:
            from models.audit import AuditLog
            session = self.db.get_session()
            try:
                session.add(AuditLog(
                    user_id=self._user_id, action=action, detail=detail
                ))
                session.commit()
            finally:
                session.close()
        except Exception:
            pass

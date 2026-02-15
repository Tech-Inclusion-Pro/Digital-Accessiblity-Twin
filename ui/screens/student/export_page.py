"""Student export page — JSON export (functional) + PDF export (stub)."""

import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFileDialog, QMessageBox,
)
from PyQt6.QtCore import Qt

from config.settings import get_colors
from models.student_profile import StudentProfile
from models.support import SupportEntry
from models.tracking import TrackingLog
from ui.components.empty_state import EmptyState


class StudentExportPage(QWidget):
    """Export accessibility twin as JSON or PDF."""

    def __init__(self, db_manager, auth_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.auth = auth_manager
        self._profile = None
        self._build_ui()

    def _build_ui(self):
        c = get_colors()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        header = QLabel("Export Accessibility Twin")
        header.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {c['text']};")
        header.setAccessibleName("Export Accessibility Twin")
        layout.addWidget(header)

        desc = QLabel(
            "Export your accessibility twin data as a JSON file for sharing "
            "with teachers or other tools."
        )
        desc.setStyleSheet(f"font-size: 14px; color: {c['text_muted']};")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Empty state
        self._empty = EmptyState(
            icon_text="\u25A1",
            message="No profile to export. Create your profile first.",
        )
        self._empty.setVisible(False)
        layout.addWidget(self._empty)

        # Export content
        self._content = QWidget()
        content_layout = QVBoxLayout(self._content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)

        # Preview
        preview_lbl = QLabel("Preview:")
        preview_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {c['text']};")
        content_layout.addWidget(preview_lbl)

        self._preview = QTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setAccessibleName("Export data preview")
        self._preview.setStyleSheet(f"""
            QTextEdit {{
                background: {c['dark_card']}; color: {c['text']};
                border: 1px solid {c['dark_border']}; border-radius: 8px;
                font-family: monospace; font-size: 12px;
                padding: 8px;
            }}
        """)
        content_layout.addWidget(self._preview, stretch=1)

        # Export buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        json_btn = QPushButton("Export as JSON")
        json_btn.setAccessibleName("Export as JSON file")
        json_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        json_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        json_btn.setFixedHeight(44)
        json_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {c['primary']}, stop:1 {c['tertiary']});
                color: white; border: none; border-radius: 8px;
                padding: 8px 24px; font-weight: bold;
            }}
        """)
        json_btn.clicked.connect(self._export_json)
        btn_row.addWidget(json_btn)

        pdf_btn = QPushButton("Export as PDF (Coming Soon)")
        pdf_btn.setAccessibleName("Export as PDF coming soon")
        pdf_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        pdf_btn.setFixedHeight(44)
        pdf_btn.setEnabled(False)
        btn_row.addWidget(pdf_btn)

        btn_row.addStretch()
        content_layout.addLayout(btn_row)

        layout.addWidget(self._content)

    def _build_twin_dict(self) -> dict | None:
        if not self._profile:
            return None

        session = self.db.get_session()
        try:
            supports = session.query(SupportEntry).filter(
                SupportEntry.profile_id == self._profile.id
            ).all()

            logs = session.query(TrackingLog).filter(
                TrackingLog.profile_id == self._profile.id
            ).order_by(TrackingLog.created_at.desc()).all()

            twin = {
                "version": "1.0",
                "profile": {
                    "name": self._profile.name,
                    "strengths": self._profile.strengths,
                    "supports_summary": self._profile.supports,
                    "history": self._profile.history,
                    "hopes": self._profile.hopes,
                    "stakeholders": self._profile.stakeholders,
                },
                "support_entries": [
                    {
                        "id": s.id,
                        "category": s.category,
                        "subcategory": s.subcategory,
                        "description": s.description,
                        "udl_mapping": json.loads(s.udl_mapping or "{}"),
                        "pour_mapping": json.loads(s.pour_mapping or "{}"),
                        "status": s.status,
                        "effectiveness_rating": s.effectiveness_rating,
                    }
                    for s in supports
                ],
                "tracking_logs": [
                    {
                        "id": lg.id,
                        "logged_by_role": lg.logged_by_role,
                        "support_id": lg.support_id,
                        "implementation_notes": lg.implementation_notes,
                        "outcome_notes": lg.outcome_notes,
                        "created_at": lg.created_at.isoformat() if lg.created_at else None,
                    }
                    for lg in logs
                ],
            }
            return twin
        finally:
            session.close()

    def _export_json(self):
        twin = self._build_twin_dict()
        if not twin:
            QMessageBox.warning(self, "No Data", "No profile data to export.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Accessibility Twin",
            f"{self._profile.name.replace(' ', '_')}_twin.json",
            "JSON Files (*.json)",
        )
        if not path:
            return

        try:
            with open(path, "w") as f:
                json.dump(twin, f, indent=2)
            QMessageBox.information(
                self, "Exported", f"Twin data saved to:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {e}")

    def refresh_data(self):
        user = self.auth.get_current_user()
        if not user:
            return

        session = self.db.get_session()
        try:
            self._profile = session.query(StudentProfile).filter(
                StudentProfile.user_id == user.id
            ).first()
        finally:
            session.close()

        if not self._profile:
            self._empty.setVisible(True)
            self._content.setVisible(False)
            return

        self._empty.setVisible(False)
        self._content.setVisible(True)

        twin = self._build_twin_dict()
        if twin:
            self._preview.setPlainText(json.dumps(twin, indent=2))

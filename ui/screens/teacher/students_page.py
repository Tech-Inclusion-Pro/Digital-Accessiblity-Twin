"""Teacher students page — list imported student twins, import JSON, consult coach."""

import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout, QLineEdit, QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import Qt

from config.settings import get_colors
from models.student_profile import StudentProfile
from models.support import SupportEntry
from models.document import Document
from models.tracking import TrackingLog
from models.evaluation import TwinEvaluation
from ui.components.empty_state import EmptyState


class TeacherStudentsPage(QWidget):
    """List/grid of imported student twins + import + search + consult coach."""

    def __init__(self, db_manager, auth_manager, backend_manager=None, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.auth = auth_manager
        self.backend_manager = backend_manager
        self._profiles: list = []
        self._build_ui()

    def _build_ui(self):
        c = get_colors()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        header = QLabel("Students")
        header.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {c['text']};")
        header.setAccessibleName("Students")
        layout.addWidget(header)

        # Toolbar: search + import button
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search students...")
        self._search.setAccessibleName("Search students")
        self._search.setFixedHeight(40)
        self._search.textChanged.connect(self._filter_grid)
        toolbar.addWidget(self._search, stretch=1)

        import_btn = QPushButton("Import Twin (JSON)")
        import_btn.setAccessibleName("Import student twin from JSON file")
        import_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        import_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        import_btn.setFixedHeight(40)
        import_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['primary']}; color: white;
                border: none; border-radius: 8px; padding: 0 20px;
                font-weight: bold;
            }}
        """)
        import_btn.clicked.connect(self._import_twin)
        toolbar.addWidget(import_btn)

        layout.addLayout(toolbar)

        # Empty state
        self._empty = EmptyState(
            icon_text="\u25C7",
            message="No student twins imported yet.",
            action_label="Import Twin",
        )
        self._empty.action_clicked.connect(self._import_twin)
        self._empty.setVisible(False)
        layout.addWidget(self._empty)

        # Students grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self._grid_container = QWidget()
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setSpacing(12)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self._grid_container)
        layout.addWidget(scroll, stretch=1)

    def _import_twin(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Student Twin", "", "JSON Files (*.json)"
        )
        if not path:
            return

        try:
            with open(path, "r") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to read file: {e}")
            return

        user = self.auth.get_current_user()
        if not user:
            return

        profile_data = data.get("profile", {})
        name = profile_data.get("name", "Unnamed Student")

        session = self.db.get_session()
        try:
            # Create a StudentProfile for the imported twin
            profile = StudentProfile(
                user_id=user.id,  # teacher's user_id as owner for imported profiles
                name=name,
                strengths_json=json.dumps(profile_data.get("strengths", [])),
                supports_json=json.dumps(profile_data.get("supports_summary", [])),
                history_json=json.dumps(profile_data.get("history", [])),
                hopes_json=json.dumps(profile_data.get("hopes", [])),
                stakeholders_json=json.dumps(profile_data.get("stakeholders", [])),
            )
            session.add(profile)
            session.flush()

            # Create SupportEntry records
            for se in data.get("support_entries", []):
                entry = SupportEntry(
                    profile_id=profile.id,
                    category=se.get("category", "other"),
                    subcategory=se.get("subcategory"),
                    description=se.get("description", ""),
                    udl_mapping=json.dumps(se.get("udl_mapping", {})),
                    pour_mapping=json.dumps(se.get("pour_mapping", {})),
                    status=se.get("status", "active"),
                    effectiveness_rating=se.get("effectiveness_rating"),
                )
                session.add(entry)

            # Create a Document record for the import
            file_blob = json.dumps(data).encode("utf-8")
            doc = Document(
                teacher_user_id=user.id,
                filename=path.split("/")[-1],
                file_type="json",
                file_blob=file_blob,
                purpose_description="twin_import",
            )
            session.add(doc)
            session.flush()

            # Link via TwinEvaluation
            twin_eval = TwinEvaluation(
                document_id=doc.id,
                student_profile_id=profile.id,
            )
            session.add(twin_eval)
            session.commit()

            QMessageBox.information(
                self, "Imported",
                f"Successfully imported twin for: {name}"
            )
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Import Error", f"Failed to import: {e}")
        finally:
            session.close()

        self.refresh_data()

    def _filter_grid(self):
        query = self._search.text().strip().lower()
        self._populate_grid(query)

    def _populate_grid(self, search: str = ""):
        c = get_colors()

        # Clear grid
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        filtered = [
            p for p in self._profiles
            if not search or search in p.name.lower()
        ]

        if not filtered:
            self._empty.setVisible(True)
            return
        self._empty.setVisible(False)

        for i, p in enumerate(filtered):
            card = self._make_card(p, c)
            self._grid_layout.addWidget(card, i // 3, i % 3)

    def _make_card(self, profile, c) -> QWidget:
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background: {c['dark_card']};
                border: 1px solid {c['dark_border']};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        name = QLabel(profile.name)
        name.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {c['text']};")
        layout.addWidget(name)

        # Quick info — show support area count (privacy-safe)
        session = self.db.get_session()
        try:
            category_count = len(set(
                s.category for s in session.query(SupportEntry).filter(
                    SupportEntry.profile_id == profile.id,
                    SupportEntry.status == "active",
                ).all()
            ))
        finally:
            session.close()
        info = QLabel(f"{category_count} support areas")
        info.setStyleSheet(f"font-size: 12px; color: {c['text_muted']};")
        layout.addWidget(info)

        coach_btn = QPushButton("Consult Coach")
        coach_btn.setAccessibleName(f"Consult accessibility coach for {profile.name}")
        coach_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        coach_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        coach_btn.setFixedHeight(32)
        coach_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['dark_input']}; color: {c['text']};
                border: 1px solid {c['dark_border']}; border-radius: 6px;
                font-size: 12px;
            }}
            QPushButton:hover {{ background: {c['dark_hover']}; }}
        """)
        coach_btn.clicked.connect(lambda checked, pid=profile.id: self._view_profile(pid))
        layout.addWidget(coach_btn)

        card.setFixedHeight(110)
        card.setAccessibleName(f"Student: {profile.name}")
        return card

    def _view_profile(self, profile_id: int):
        session = self.db.get_session()
        try:
            profile = session.query(StudentProfile).get(profile_id)
            if not profile:
                return

            supports = session.query(SupportEntry).filter(
                SupportEntry.profile_id == profile_id
            ).all()

            tracking_logs = session.query(TrackingLog).filter(
                TrackingLog.profile_id == profile_id,
            ).order_by(TrackingLog.created_at.desc()).limit(20).all()

            from ui.screens.teacher.coach_dialog import CoachDialog
            dlg = CoachDialog(
                profile, supports, tracking_logs,
                self.backend_manager, self,
            )
            dlg.exec()
        finally:
            session.close()

    def refresh_data(self):
        user = self.auth.get_current_user()
        if not user:
            return

        session = self.db.get_session()
        try:
            # Get profiles linked to this teacher via twin_import documents
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

            if profile_ids:
                self._profiles = session.query(StudentProfile).filter(
                    StudentProfile.id.in_(profile_ids)
                ).all()
            else:
                self._profiles = []
        finally:
            session.close()

        self._populate_grid(self._search.text().strip().lower())

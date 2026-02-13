"""Teacher evaluate page — upload documents and link to student profiles."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QTextEdit, QListWidget, QListWidgetItem,
    QMessageBox, QScrollArea,
)
from PyQt6.QtCore import Qt

from config.settings import get_colors
from models.student_profile import StudentProfile
from models.document import Document
from models.evaluation import TwinEvaluation
from ui.components.empty_state import EmptyState


class TeacherEvaluatePage(QWidget):
    """Upload document, select students, create evaluation records."""

    def __init__(self, db_manager, auth_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.auth = auth_manager
        self._profiles: list = []
        self._selected_file: str | None = None
        self._file_data: bytes | None = None
        self._build_ui()

    def _build_ui(self):
        c = get_colors()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        header = QLabel("Evaluate Document")
        header.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {c['text']};")
        header.setAccessibleName("Evaluate Document")
        layout.addWidget(header)

        desc = QLabel(
            "Upload a document (IEP, lesson plan, etc.) and link it to student "
            "profiles for evaluation."
        )
        desc.setStyleSheet(f"font-size: 14px; color: {c['text_muted']};")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # File upload section
        file_section = QHBoxLayout()
        file_section.setSpacing(10)

        upload_btn = QPushButton("Choose File")
        upload_btn.setAccessibleName("Choose a document file to upload")
        upload_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        upload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        upload_btn.setFixedHeight(44)
        upload_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['dark_input']}; color: {c['text']};
                border: 1px solid {c['dark_border']}; border-radius: 8px;
                padding: 0 20px;
            }}
            QPushButton:hover {{ background: {c['dark_hover']}; }}
        """)
        upload_btn.clicked.connect(self._choose_file)
        file_section.addWidget(upload_btn)

        self._file_label = QLabel("No file selected")
        self._file_label.setStyleSheet(f"font-size: 13px; color: {c['text_muted']};")
        file_section.addWidget(self._file_label, stretch=1)
        layout.addLayout(file_section)

        # Purpose description
        layout.addWidget(QLabel("Purpose / Description:"))
        self._purpose = QTextEdit()
        self._purpose.setPlaceholderText("Describe the purpose of this document evaluation...")
        self._purpose.setAccessibleName("Document purpose description")
        self._purpose.setMaximumHeight(80)
        layout.addWidget(self._purpose)

        # Student selection
        layout.addWidget(QLabel("Select Students:"))

        self._student_list = QListWidget()
        self._student_list.setAccessibleName("Select students to link to this document")
        self._student_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self._student_list.setMaximumHeight(150)
        layout.addWidget(self._student_list)

        # Submit
        submit_btn = QPushButton("Upload & Create Evaluation")
        submit_btn.setAccessibleName("Upload document and create evaluation")
        submit_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.setFixedHeight(44)
        submit_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {c['primary']}, stop:1 {c['secondary']});
                color: white; border: none; border-radius: 8px;
                padding: 8px 24px; font-weight: bold;
            }}
        """)
        submit_btn.clicked.connect(self._submit)
        layout.addWidget(submit_btn)

        # AI analysis placeholder
        self._ai_placeholder = EmptyState(
            icon_text="\U0001F916",
            message="AI-powered document analysis coming soon. Documents will be stored for future analysis.",
        )
        layout.addWidget(self._ai_placeholder)

        layout.addStretch()

    def _choose_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Document", "",
            "All Supported (*.pdf *.docx *.txt *.doc *.rtf);;All Files (*)",
        )
        if not path:
            return

        try:
            with open(path, "rb") as f:
                self._file_data = f.read()
            self._selected_file = path
            filename = path.split("/")[-1]
            self._file_label.setText(filename)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read file: {e}")

    def _submit(self):
        user = self.auth.get_current_user()
        if not user:
            return

        if not self._selected_file or not self._file_data:
            QMessageBox.warning(self, "No File", "Please select a file to upload.")
            return

        selected_items = self._student_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Students", "Please select at least one student.")
            return

        purpose = self._purpose.toPlainText().strip()
        filename = self._selected_file.split("/")[-1]
        file_ext = filename.rsplit(".", 1)[-1] if "." in filename else ""

        session = self.db.get_session()
        try:
            doc = Document(
                teacher_user_id=user.id,
                filename=filename,
                file_type=file_ext,
                file_blob=self._file_data,
                purpose_description=purpose if purpose else None,
            )
            session.add(doc)
            session.flush()

            for item in selected_items:
                profile_id = item.data(Qt.ItemDataRole.UserRole)
                if profile_id:
                    twin_eval = TwinEvaluation(
                        document_id=doc.id,
                        student_profile_id=profile_id,
                    )
                    session.add(twin_eval)

            session.commit()

            QMessageBox.information(
                self, "Success",
                f"Document '{filename}' uploaded and linked to "
                f"{len(selected_items)} student(s)."
            )
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Upload failed: {e}")
        finally:
            session.close()

        # Reset form
        self._selected_file = None
        self._file_data = None
        self._file_label.setText("No file selected")
        self._purpose.clear()
        self._student_list.clearSelection()

    def refresh_data(self):
        user = self.auth.get_current_user()
        if not user:
            return

        session = self.db.get_session()
        try:
            # Get accessible student profiles
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

            self._profiles = []
            if profile_ids:
                self._profiles = session.query(StudentProfile).filter(
                    StudentProfile.id.in_(profile_ids)
                ).all()
        finally:
            session.close()

        # Populate student list
        self._student_list.clear()
        for p in self._profiles:
            item = QListWidgetItem(p.name)
            item.setData(Qt.ItemDataRole.UserRole, p.id)
            self._student_list.addItem(item)

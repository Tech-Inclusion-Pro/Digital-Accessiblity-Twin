"""First-time setup wizard stub with functional AI setup page."""

import asyncio

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QCheckBox, QGroupBox, QFormLayout,
    QStackedWidget, QWidget,
)
from PyQt6.QtCore import Qt

from config.settings import get_colors
from ai.backend_manager import BackendManager


class SetupWizard(QDialog):
    """First-time setup wizard. Phase 1 provides a functional AI config page."""

    def __init__(self, backend_manager: BackendManager, parent=None):
        super().__init__(parent)
        self.bm = backend_manager
        self.setWindowTitle("AccessTwin Setup")
        self.setMinimumSize(520, 540)
        self.setAccessibleName("Setup Wizard")
        c = get_colors()
        self.setStyleSheet(f"QDialog {{ background-color: {c['dark_card']}; }}")
        self._build()

    def _build(self):
        c = get_colors()
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("AI Backend Configuration")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {c['primary_text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setAccessibleName("AI Backend Configuration")
        layout.addWidget(title)

        # Provider type
        type_group = QGroupBox("Provider Type")
        type_group.setAccessibleName("Provider type selection")
        type_form = QFormLayout(type_group)

        self.type_combo = QComboBox()
        self.type_combo.addItem("Local (Privacy-first)", "local")
        self.type_combo.addItem("Cloud (Requires consent)", "cloud")
        self.type_combo.setAccessibleName("Select local or cloud provider")
        self.type_combo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.type_combo.setFixedHeight(44)
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        type_form.addRow("Type:", self.type_combo)

        layout.addWidget(type_group)

        # Provider stack
        self.provider_stack = QStackedWidget()

        # Local config
        local_widget = QWidget()
        local_layout = QFormLayout(local_widget)

        self.local_provider = QComboBox()
        self.local_provider.addItem("Ollama", "ollama")
        self.local_provider.addItem("LM Studio", "lmstudio")
        self.local_provider.addItem("GPT4All", "gpt4all")
        self.local_provider.setAccessibleName("Select local provider")
        self.local_provider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.local_provider.setFixedHeight(44)
        local_layout.addRow("Provider:", self.local_provider)

        self.local_url = QLineEdit("http://localhost:11434")
        self.local_url.setAccessibleName("Server URL")
        self.local_url.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.local_url.setFixedHeight(44)
        local_layout.addRow("Server URL:", self.local_url)

        self.local_model = QLineEdit("gemma3:4b")
        self.local_model.setAccessibleName("Model name")
        self.local_model.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.local_model.setFixedHeight(44)
        local_layout.addRow("Model:", self.local_model)

        self.provider_stack.addWidget(local_widget)

        # Cloud config
        cloud_widget = QWidget()
        cloud_layout = QVBoxLayout(cloud_widget)

        cloud_form = QFormLayout()

        self.cloud_provider = QComboBox()
        self.cloud_provider.addItem("OpenAI", "openai")
        self.cloud_provider.addItem("Anthropic", "anthropic")
        self.cloud_provider.setAccessibleName("Select cloud provider")
        self.cloud_provider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.cloud_provider.setFixedHeight(44)
        cloud_form.addRow("Provider:", self.cloud_provider)

        self.cloud_key = QLineEdit()
        self.cloud_key.setPlaceholderText("API key")
        self.cloud_key.setAccessibleName("API key")
        self.cloud_key.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.cloud_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.cloud_key.setFixedHeight(44)
        cloud_form.addRow("API Key:", self.cloud_key)

        self.cloud_model = QLineEdit("gpt-4o")
        self.cloud_model.setAccessibleName("Cloud model name")
        self.cloud_model.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.cloud_model.setFixedHeight(44)
        cloud_form.addRow("Model:", self.cloud_model)

        cloud_layout.addLayout(cloud_form)

        # Dual consent
        consent_group = QGroupBox("Cloud Data Consent (both required)")
        consent_group.setAccessibleName("Cloud data consent checkboxes")
        cl = QVBoxLayout(consent_group)

        self.consent_institutional = QCheckBox(
            "I confirm my institution approves cloud AI usage for student data"
        )
        self.consent_institutional.setAccessibleName("Institutional approval confirmation")
        self.consent_institutional.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        cl.addWidget(self.consent_institutional)

        self.consent_data = QCheckBox(
            "I understand that data will be transmitted to a third-party AI service"
        )
        self.consent_data.setAccessibleName("Data transmission understanding")
        self.consent_data.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        cl.addWidget(self.consent_data)

        cloud_layout.addWidget(consent_group)

        self.provider_stack.addWidget(cloud_widget)
        layout.addWidget(self.provider_stack)

        # Test + status
        test_row = QHBoxLayout()
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.setAccessibleName("Test AI connection")
        self.test_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.test_btn.setFixedHeight(44)
        self.test_btn.clicked.connect(self._on_test)
        test_row.addWidget(self.test_btn)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setAccessibleName("Connection status")
        test_row.addWidget(self.status_label, 1)
        layout.addLayout(test_row)

        # Save / Cancel
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        save_btn = QPushButton("Save Configuration")
        save_btn.setAccessibleName("Save AI configuration")
        save_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        save_btn.setFixedHeight(44)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {c['primary']}, stop:1 {c['tertiary']});
                color: white; border: none; border-radius: 8px;
                padding: 8px 24px; font-weight: bold;
            }}
        """)
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setAccessibleName("Cancel setup")
        cancel_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        cancel_btn.setFixedHeight(44)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        layout.addLayout(btn_row)

    def _on_type_changed(self):
        self.provider_stack.setCurrentIndex(self.type_combo.currentIndex())

    def _on_test(self):
        self._apply_to_manager()
        self.status_label.setText("Testing...")
        self.status_label.setStyleSheet(f"color: {get_colors()['text_muted']};")

        loop = asyncio.new_event_loop()
        try:
            ok, msg = loop.run_until_complete(self.bm.test_connection())
        finally:
            loop.close()

        c = get_colors()
        if ok:
            self.status_label.setText(f"Connected: {msg}")
            self.status_label.setStyleSheet(f"color: {c['success']};")
        else:
            self.status_label.setText(f"Failed: {msg}")
            self.status_label.setStyleSheet(f"color: {c['error']};")

    def _on_save(self):
        if self.type_combo.currentData() == "cloud":
            if not self.consent_institutional.isChecked() or not self.consent_data.isChecked():
                self.status_label.setText("Both consent checkboxes must be checked for cloud usage.")
                self.status_label.setStyleSheet(f"color: {get_colors()['error']};")
                return
            self.bm.cloud_consent_institutional = True
            self.bm.cloud_consent_data = True

        self._apply_to_manager()
        self.accept()

    def _apply_to_manager(self):
        ptype = self.type_combo.currentData()
        if ptype == "local":
            self.bm.configure(
                "local",
                self.local_provider.currentData(),
                model=self.local_model.text().strip(),
                base_url=self.local_url.text().strip(),
            )
        else:
            self.bm.configure(
                "cloud",
                self.cloud_provider.currentData(),
                model=self.cloud_model.text().strip(),
                api_key=self.cloud_key.text().strip(),
            )

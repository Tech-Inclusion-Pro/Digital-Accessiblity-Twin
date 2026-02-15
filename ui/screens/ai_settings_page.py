"""AI Settings page — user-configurable local/cloud AI provider settings."""

import asyncio

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QCheckBox, QFormLayout,
    QStackedWidget, QScrollArea, QMessageBox,
)
from PyQt6.QtCore import Qt

from config.settings import get_colors, APP_SETTINGS
from ai.backend_manager import BackendManager


class AISettingsPage(QWidget):
    """Full-page AI provider settings with local/cloud selection and privacy warnings."""

    def __init__(self, backend_manager: BackendManager, parent=None):
        super().__init__(parent)
        self.backend_manager = backend_manager
        self._build_ui()

    def _build_ui(self):
        c = get_colors()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Page header
        title = QLabel("AI Provider Settings")
        title.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {c['text']};"
        )
        title.setAccessibleName("AI Provider Settings")
        layout.addWidget(title)

        # Current status banner
        self._status_banner = QLabel()
        self._status_banner.setAccessibleName("Current AI status")
        self._status_banner.setFixedHeight(APP_SETTINGS["touch_target_min"])
        self._status_banner.setStyleSheet(
            f"background: {c['dark_card']}; color: {c['text']}; "
            f"border: 1px solid {c['dark_border']}; border-radius: 8px; "
            f"padding: 8px 16px; font-size: 14px;"
        )
        layout.addWidget(self._status_banner)

        # Privacy recommendation — local banner (always visible)
        self._local_banner = QLabel(
            "Recommended: Local AI — all data stays on your device"
        )
        self._local_banner.setAccessibleName(
            "Recommendation: Local AI keeps all data on your device"
        )
        self._local_banner.setWordWrap(True)
        self._local_banner.setFixedHeight(APP_SETTINGS["touch_target_min"])
        self._local_banner.setStyleSheet(
            f"background: {c['success']}; color: white; border-radius: 8px; "
            f"padding: 8px 16px; font-size: 14px; font-weight: bold;"
        )
        layout.addWidget(self._local_banner)

        # Cloud privacy warning (shown only when cloud selected)
        self._cloud_warning = QLabel(
            "PRIVACY WARNING: Cloud AI sends student accessibility data to external "
            "servers operated by third parties (e.g., OpenAI, Anthropic). This data may "
            "include sensitive information about student disabilities and accommodations. "
            "Only use cloud AI if your institution has explicitly approved this. "
            "Local AI is strongly recommended for privacy and compliance."
        )
        self._cloud_warning.setAccessibleName("Privacy warning for cloud AI usage")
        self._cloud_warning.setWordWrap(True)
        self._cloud_warning.setStyleSheet(
            f"background: {c['error']}; color: white; border-radius: 8px; "
            f"padding: 12px 16px; font-size: 13px; font-weight: bold;"
        )
        self._cloud_warning.setVisible(False)
        layout.addWidget(self._cloud_warning)

        # Provider type selection
        type_row = QHBoxLayout()
        type_label = QLabel("Provider Type:")
        type_label.setStyleSheet(f"font-size: 14px; color: {c['text']};")
        type_row.addWidget(type_label)

        self._type_combo = QComboBox()
        self._type_combo.addItem("Local (Privacy-first)", "local")
        self._type_combo.addItem("Cloud (Requires consent)", "cloud")
        self._type_combo.setAccessibleName("Select local or cloud provider")
        self._type_combo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._type_combo.setFixedHeight(APP_SETTINGS["touch_target_min"])
        self._type_combo.currentIndexChanged.connect(self._on_type_changed)
        type_row.addWidget(self._type_combo, stretch=1)
        layout.addLayout(type_row)

        # Provider config stack
        self._provider_stack = QStackedWidget()

        # --- Local panel ---
        local_widget = QWidget()
        local_widget.setStyleSheet(
            f"QWidget {{ background: {c['dark_card']}; "
            f"border: 1px solid {c['dark_border']}; border-radius: 8px; }}"
        )
        local_layout = QFormLayout(local_widget)
        local_layout.setContentsMargins(16, 12, 16, 12)
        local_layout.setSpacing(10)

        self._local_provider = QComboBox()
        self._local_provider.addItem("Ollama", "ollama")
        self._local_provider.addItem("LM Studio", "lmstudio")
        self._local_provider.addItem("GPT4All", "gpt4all")
        self._local_provider.setAccessibleName("Select local provider")
        self._local_provider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._local_provider.setFixedHeight(APP_SETTINGS["touch_target_min"])
        local_layout.addRow("Provider:", self._local_provider)

        self._local_url = QLineEdit("http://localhost:11434")
        self._local_url.setAccessibleName("Server URL")
        self._local_url.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._local_url.setFixedHeight(APP_SETTINGS["touch_target_min"])
        local_layout.addRow("Server URL:", self._local_url)

        self._local_model = QLineEdit("gemma3:4b")
        self._local_model.setAccessibleName("Model name")
        self._local_model.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._local_model.setFixedHeight(APP_SETTINGS["touch_target_min"])
        local_layout.addRow("Model:", self._local_model)

        self._provider_stack.addWidget(local_widget)

        # --- Cloud panel ---
        cloud_widget = QWidget()
        cloud_widget.setStyleSheet(
            f"QWidget {{ background: {c['dark_card']}; "
            f"border: 1px solid {c['dark_border']}; border-radius: 8px; }}"
        )
        cloud_layout = QVBoxLayout(cloud_widget)
        cloud_layout.setContentsMargins(16, 12, 16, 12)
        cloud_layout.setSpacing(10)

        cloud_form = QFormLayout()
        cloud_form.setSpacing(10)

        self._cloud_provider = QComboBox()
        self._cloud_provider.addItem("OpenAI", "openai")
        self._cloud_provider.addItem("Anthropic", "anthropic")
        self._cloud_provider.setAccessibleName("Select cloud provider")
        self._cloud_provider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._cloud_provider.setFixedHeight(APP_SETTINGS["touch_target_min"])
        cloud_form.addRow("Provider:", self._cloud_provider)

        self._cloud_key = QLineEdit()
        self._cloud_key.setPlaceholderText("API key")
        self._cloud_key.setAccessibleName("API key")
        self._cloud_key.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._cloud_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._cloud_key.setFixedHeight(APP_SETTINGS["touch_target_min"])
        cloud_form.addRow("API Key:", self._cloud_key)

        self._cloud_model = QLineEdit("gpt-4o")
        self._cloud_model.setAccessibleName("Cloud model name")
        self._cloud_model.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._cloud_model.setFixedHeight(APP_SETTINGS["touch_target_min"])
        cloud_form.addRow("Model:", self._cloud_model)

        cloud_layout.addLayout(cloud_form)

        # Dual consent checkboxes
        consent_label = QLabel("Cloud Data Consent (both required)")
        consent_label.setStyleSheet(
            f"font-size: 13px; font-weight: bold; color: {c['text']}; border: none;"
        )
        cloud_layout.addWidget(consent_label)

        self._consent_institutional = QCheckBox(
            "I confirm my institution approves cloud AI usage for student data"
        )
        self._consent_institutional.setAccessibleName("Institutional approval confirmation")
        self._consent_institutional.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._consent_institutional.setStyleSheet(f"color: {c['text']}; border: none;")
        cloud_layout.addWidget(self._consent_institutional)

        self._consent_data = QCheckBox(
            "I understand that data will be transmitted to a third-party AI service"
        )
        self._consent_data.setAccessibleName("Data transmission understanding")
        self._consent_data.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._consent_data.setStyleSheet(f"color: {c['text']}; border: none;")
        cloud_layout.addWidget(self._consent_data)

        self._provider_stack.addWidget(cloud_widget)
        layout.addWidget(self._provider_stack)

        # Test connection row
        test_row = QHBoxLayout()
        test_row.setSpacing(10)

        self._test_btn = QPushButton("Test Connection")
        self._test_btn.setAccessibleName("Test AI connection")
        self._test_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._test_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._test_btn.setFixedHeight(APP_SETTINGS["touch_target_min"])
        self._test_btn.setStyleSheet(
            f"QPushButton {{ background: {c['dark_input']}; color: {c['text']}; "
            f"border: 1px solid {c['dark_border']}; border-radius: 8px; "
            f"padding: 6px 20px; font-size: 13px; }}"
            f"QPushButton:hover {{ background: {c['dark_hover']}; }}"
        )
        self._test_btn.clicked.connect(self._on_test)
        test_row.addWidget(self._test_btn)

        self._test_status = QLabel("")
        self._test_status.setWordWrap(True)
        self._test_status.setAccessibleName("Connection test status")
        self._test_status.setStyleSheet(f"font-size: 13px; color: {c['text_muted']};")
        test_row.addWidget(self._test_status, stretch=1)

        layout.addLayout(test_row)

        # Action buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        save_btn = QPushButton("Save Configuration")
        save_btn.setAccessibleName("Save AI configuration")
        save_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setFixedHeight(APP_SETTINGS["touch_target_min"])
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {c['primary']}, stop:1 {c['tertiary']});
                color: white; border: none; border-radius: 8px;
                padding: 8px 24px; font-weight: bold; font-size: 14px;
            }}
        """)
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn)

        clear_btn = QPushButton("Clear Configuration")
        clear_btn.setAccessibleName("Clear AI configuration and reset to defaults")
        clear_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setFixedHeight(APP_SETTINGS["touch_target_min"])
        clear_btn.setStyleSheet(
            f"QPushButton {{ background: {c['dark_input']}; color: {c['text']}; "
            f"border: 1px solid {c['dark_border']}; border-radius: 8px; "
            f"padding: 6px 20px; font-size: 13px; }}"
            f"QPushButton:hover {{ background: {c['dark_hover']}; }}"
        )
        clear_btn.clicked.connect(self._on_clear)
        btn_row.addWidget(clear_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        layout.addStretch()

        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        # Populate from current state
        self._populate_from_manager()
        self._update_status_banner()

    # -- populate fields from backend_manager --

    def _populate_from_manager(self):
        bm = self.backend_manager
        # Provider type
        idx = 0 if bm.provider_type == "local" else 1
        self._type_combo.setCurrentIndex(idx)
        self._on_type_changed()

        # Local fields
        local_providers = {"ollama": 0, "lmstudio": 1, "gpt4all": 2}
        self._local_provider.setCurrentIndex(local_providers.get(bm.provider, 0))
        self._local_url.setText(bm.base_url or "http://localhost:11434")
        self._local_model.setText(bm.model or "gemma3:4b")

        # Cloud fields
        cloud_providers = {"openai": 0, "anthropic": 1}
        self._cloud_provider.setCurrentIndex(cloud_providers.get(bm.provider, 0))
        self._cloud_key.setText(bm.api_key or "")
        self._cloud_model.setText(bm.model or "gpt-4o")

        # Consent
        self._consent_institutional.setChecked(bm.cloud_consent_institutional)
        self._consent_data.setChecked(bm.cloud_consent_data)

    def _update_status_banner(self):
        bm = self.backend_manager
        if bm.is_configured:
            self._status_banner.setText(
                f"Current: {bm.provider} / {bm.model} ({bm.provider_type})"
            )
        else:
            self._status_banner.setText("Status: Not configured")

    # -- event handlers --

    def _on_type_changed(self):
        idx = self._type_combo.currentIndex()
        self._provider_stack.setCurrentIndex(idx)
        is_cloud = self._type_combo.currentData() == "cloud"
        self._cloud_warning.setVisible(is_cloud)

    def _on_test(self):
        self._apply_to_manager()
        self._test_status.setText("Testing...")
        c = get_colors()
        self._test_status.setStyleSheet(f"font-size: 13px; color: {c['text_muted']};")

        loop = asyncio.new_event_loop()
        try:
            ok, msg = loop.run_until_complete(self.backend_manager.test_connection())
        finally:
            loop.close()

        if ok:
            self._test_status.setText(f"Connected: {msg}")
            self._test_status.setStyleSheet(f"font-size: 13px; color: {c['success']};")
        else:
            self._test_status.setText(f"Failed: {msg}")
            self._test_status.setStyleSheet(f"font-size: 13px; color: {c['error']};")

    def _on_save(self):
        c = get_colors()
        if self._type_combo.currentData() == "cloud":
            if not self._consent_institutional.isChecked() or not self._consent_data.isChecked():
                self._test_status.setText(
                    "Both consent checkboxes must be checked for cloud usage."
                )
                self._test_status.setStyleSheet(f"font-size: 13px; color: {c['error']};")
                return
            self.backend_manager.cloud_consent_institutional = True
            self.backend_manager.cloud_consent_data = True

        self._apply_to_manager()
        self.backend_manager.save_config()
        self._update_status_banner()
        self._test_status.setText("Configuration saved.")
        self._test_status.setStyleSheet(f"font-size: 13px; color: {c['success']};")

    def _on_clear(self):
        reply = QMessageBox.question(
            self, "Confirm Clear",
            "Are you sure you want to clear all AI configuration?\n\n"
            "This will reset provider settings and remove any saved API keys.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        from ai.ai_settings_store import clear_ai_settings
        clear_ai_settings()

        # Reset manager to defaults
        self.backend_manager.provider_type = "local"
        self.backend_manager.provider = "ollama"
        self.backend_manager.model = "gemma3:4b"
        self.backend_manager.api_key = None
        self.backend_manager.base_url = "http://localhost:11434"
        self.backend_manager.cloud_consent_institutional = False
        self.backend_manager.cloud_consent_data = False
        self.backend_manager._client = None

        self._populate_from_manager()
        self._update_status_banner()

        c = get_colors()
        self._test_status.setText("Configuration cleared.")
        self._test_status.setStyleSheet(f"font-size: 13px; color: {c['text_muted']};")

    def _apply_to_manager(self):
        ptype = self._type_combo.currentData()
        if ptype == "local":
            self.backend_manager.configure(
                "local",
                self._local_provider.currentData(),
                model=self._local_model.text().strip(),
                base_url=self._local_url.text().strip(),
            )
        else:
            self.backend_manager.configure(
                "cloud",
                self._cloud_provider.currentData(),
                model=self._cloud_model.text().strip(),
                api_key=self._cloud_key.text().strip(),
            )

    def refresh_data(self):
        """Refresh fields from current backend_manager state."""
        self._populate_from_manager()
        self._update_status_banner()

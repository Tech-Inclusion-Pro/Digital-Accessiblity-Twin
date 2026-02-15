"""Detailed AI model setup guide with platform-specific instructions."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea, QWidget,
    QTabWidget,
)
from PyQt6.QtCore import Qt

from config.settings import get_colors, APP_SETTINGS


# ---------------------------------------------------------------------------
# Platform-specific instructions
# ---------------------------------------------------------------------------

_MAC_OLLAMA = """\
Issue:
  AccessTwin needs a local AI model to generate insights, but no AI \
server is running on your computer.

How to fix it:
  Install Ollama (a free, open-source local AI server) and download a \
model. All data stays on your device.

Step-by-step instructions (Mac):

  1. Install Ollama using one of these methods:
     a) Homebrew (if you have it):
        Open Terminal (Cmd + Space, type "Terminal", press Enter).
        Run:  brew install ollama
     b) Direct download:
        Open Safari and go to  https://ollama.com/download
        Click "Download for macOS".
        Open the downloaded .dmg file and drag Ollama to Applications.

  2. Start the Ollama server:
     Open Terminal and run:  ollama serve
     Leave this Terminal window open while using AccessTwin.
     (Ollama may also auto-start after installation.)

  3. Download a model:
     Open a NEW Terminal window (Cmd + N) and run:
        ollama pull gemma3:4b
     This downloads ~3 GB. Wait for it to finish.

  4. Verify it works:
     In Terminal, run:  ollama list
     You should see "gemma3:4b" in the list.

  5. Configure AccessTwin:
     Go to AI Settings in AccessTwin.
     Set Provider to "Ollama".
     Set Server URL to:  http://localhost:11434
     Set Model to:  gemma3:4b
     Click "Test Connection" \u2014 it should say "Connected".
     Click "Save Configuration".

Troubleshooting:
  \u2022 "Connection refused" \u2014 Ollama is not running. Open Terminal \
and run: ollama serve
  \u2022 "Model not found" \u2014 You haven\u2019t downloaded the model yet. \
Run: ollama pull gemma3:4b
  \u2022 Slow performance \u2014 Try a smaller model: ollama pull gemma3:1b
  \u2022 Mac with Apple Silicon (M1/M2/M3/M4) \u2014 Ollama runs natively \
and uses the GPU automatically. No extra setup needed."""

_WINDOWS_OLLAMA = """\
Issue:
  AccessTwin needs a local AI model to generate insights, but no AI \
server is running on your computer.

How to fix it:
  Install Ollama (a free, open-source local AI server) and download a \
model. All data stays on your device.

Step-by-step instructions (Windows):

  1. Download Ollama:
     Open your web browser and go to  https://ollama.com/download
     Click "Download for Windows".
     Run the downloaded installer (OllamaSetup.exe).
     Follow the installation prompts (click Next, then Install).

  2. Ollama starts automatically:
     After installation, Ollama runs as a background service.
     You should see the Ollama icon in your system tray \
(bottom-right corner of the taskbar).

  3. Download a model:
     Open Command Prompt (press Windows key, type "cmd", press Enter).
     Run:  ollama pull gemma3:4b
     This downloads ~3 GB. Wait for it to finish.

  4. Verify it works:
     In Command Prompt, run:  ollama list
     You should see "gemma3:4b" in the list.

  5. Configure AccessTwin:
     Go to AI Settings in AccessTwin.
     Set Provider to "Ollama".
     Set Server URL to:  http://localhost:11434
     Set Model to:  gemma3:4b
     Click "Test Connection" \u2014 it should say "Connected".
     Click "Save Configuration".

Troubleshooting:
  \u2022 "Connection refused" \u2014 Ollama is not running. Look for the \
Ollama icon in your system tray. If it\u2019s not there, search for \
"Ollama" in the Start menu and open it.
  \u2022 "Model not found" \u2014 Open Command Prompt and run: \
ollama pull gemma3:4b
  \u2022 Slow performance \u2014 Try a smaller model: ollama pull gemma3:1b
  \u2022 If you have an NVIDIA GPU, Ollama will use it automatically. \
Make sure your NVIDIA drivers are up to date."""

_LINUX_OLLAMA = """\
Issue:
  AccessTwin needs a local AI model to generate insights, but no AI \
server is running on your computer.

How to fix it:
  Install Ollama (a free, open-source local AI server) and download a \
model. All data stays on your device.

Step-by-step instructions (Linux):

  1. Install Ollama:
     Open a terminal and run:
        curl -fsSL https://ollama.com/install.sh | sh
     This installs Ollama and sets it up as a systemd service.

  2. Start the Ollama server:
     If it didn\u2019t auto-start, run:
        sudo systemctl start ollama
     Or run it manually:
        ollama serve

  3. Download a model:
     Open a terminal and run:
        ollama pull gemma3:4b
     This downloads ~3 GB. Wait for it to finish.

  4. Verify it works:
     Run:  ollama list
     You should see "gemma3:4b" in the list.

  5. Enable auto-start (optional):
     Run:  sudo systemctl enable ollama
     This makes Ollama start automatically on boot.

  6. Configure AccessTwin:
     Go to AI Settings in AccessTwin.
     Set Provider to "Ollama".
     Set Server URL to:  http://localhost:11434
     Set Model to:  gemma3:4b
     Click "Test Connection" \u2014 it should say "Connected".
     Click "Save Configuration".

Troubleshooting:
  \u2022 "Connection refused" \u2014 Ollama is not running. Run: ollama serve
  \u2022 "Model not found" \u2014 Run: ollama pull gemma3:4b
  \u2022 Slow performance \u2014 Try a smaller model: ollama pull gemma3:1b
  \u2022 Permission denied \u2014 Run: sudo systemctl start ollama
  \u2022 NVIDIA GPU \u2014 Install NVIDIA Container Toolkit for GPU acceleration. \
See: https://docs.nvidia.com/datacenter/cloud-native/"""

_LM_STUDIO = """\
Issue:
  AccessTwin needs a local AI model, and you prefer a graphical \
application instead of the command line.

How to fix it:
  Install LM Studio, a desktop app for running local AI models.

Step-by-step instructions (Mac / Windows / Linux):

  1. Download LM Studio:
     Go to  https://lmstudio.ai
     Click the download button for your operating system.

  2. Install:
     Mac: Open the .dmg and drag LM Studio to Applications.
     Windows: Run the installer and follow the prompts.
     Linux: Download the .AppImage, make it executable \
(chmod +x LM-Studio*.AppImage), and run it.

  3. Download a model inside LM Studio:
     Open LM Studio.
     Click the Search/Download tab (magnifying glass icon).
     Search for "gemma" or any model you prefer.
     Click Download next to the model.

  4. Start the local server:
     Click the "Local Server" tab (the computer icon) in LM Studio.
     Select your downloaded model from the dropdown.
     Click "Start Server".
     The server URL will be shown (usually http://localhost:1234).

  5. Configure AccessTwin:
     Go to AI Settings in AccessTwin.
     Set Provider to "LM Studio".
     Set Server URL to:  http://localhost:1234/v1
     Set Model to the model name shown in LM Studio.
     Click "Test Connection" \u2014 it should say "Connected".
     Click "Save Configuration".

Troubleshooting:
  \u2022 "Connection refused" \u2014 The LM Studio server is not running. \
Open LM Studio, go to Local Server, and click Start Server.
  \u2022 "Model not found" \u2014 Make sure you selected a model in the \
Local Server tab before starting.
  \u2022 Slow performance \u2014 Choose a smaller model (look for ones \
under 4 GB)."""

_CLOUD_SETUP = """\
Issue:
  You want to use a cloud AI provider instead of running AI locally.

How to fix it:
  Sign up for an API key from OpenAI or Anthropic, then configure \
AccessTwin to use it.

IMPORTANT PRIVACY WARNING:
  Cloud AI sends student accessibility data to external servers. \
Only use this option if your institution has explicitly approved it.

Step-by-step instructions:

  For OpenAI:
  1. Go to  https://platform.openai.com/signup
  2. Create an account and verify your email.
  3. Go to  https://platform.openai.com/api-keys
  4. Click "Create new secret key" and copy the key.
  5. In AccessTwin AI Settings:
     Set Provider Type to "Cloud".
     Set Provider to "OpenAI".
     Paste your API key.
     Set Model to: gpt-4o (or gpt-3.5-turbo for lower cost).
     Check BOTH consent boxes.
     Click "Test Connection", then "Save Configuration".

  For Anthropic:
  1. Go to  https://console.anthropic.com
  2. Create an account and verify your email.
  3. Go to API Keys in your console settings.
  4. Create a new key and copy it.
  5. In AccessTwin AI Settings:
     Set Provider Type to "Cloud".
     Set Provider to "Anthropic".
     Paste your API key.
     Set Model to: claude-sonnet-4-5-20250929 (or another available model).
     Check BOTH consent boxes.
     Click "Test Connection", then "Save Configuration".

Troubleshooting:
  \u2022 "Invalid API key" \u2014 Double-check that you copied the full key. \
API keys are long strings starting with "sk-".
  \u2022 "Rate limited" \u2014 You may need to add a payment method to your \
provider account.
  \u2022 "Consent required" \u2014 You must check both consent checkboxes \
in AccessTwin before saving cloud configuration."""


class AISetupGuideDialog(QDialog):
    """Detailed AI setup guide with tabbed platform-specific instructions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Model Setup Guide")
        self.setMinimumWidth(600)
        self.setMinimumHeight(560)
        self.setAccessibleName("AI Model Setup Guide")
        self._build_ui()

    def _build_ui(self):
        c = get_colors()
        self.setStyleSheet(f"QDialog {{ background-color: {c['dark_bg']}; }}")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        # Title
        title = QLabel("AI Model Setup Guide")
        title.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {c['text']};"
        )
        title.setAccessibleName("AI Model Setup Guide")
        root.addWidget(title)

        subtitle = QLabel(
            "Choose your operating system below for step-by-step instructions."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(f"font-size: 13px; color: {c['text_muted']};")
        root.addWidget(subtitle)

        # Tabbed instructions
        tabs = QTabWidget()
        tabs.setAccessibleName("Platform selection tabs")
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {c['dark_border']};
                border-radius: 8px;
                background: {c['dark_card']};
            }}
            QTabBar::tab {{
                background: {c['dark_input']};
                color: {c['text_muted']};
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 13px;
                min-height: 20px;
            }}
            QTabBar::tab:selected {{
                background: {c['dark_card']};
                color: {c['text']};
                font-weight: bold;
            }}
        """)

        tabs.addTab(self._make_tab(c, _MAC_OLLAMA), "\U0001F34E  Mac (Ollama)")
        tabs.addTab(self._make_tab(c, _WINDOWS_OLLAMA), "\U0001F5A5  Windows (Ollama)")
        tabs.addTab(self._make_tab(c, _LINUX_OLLAMA), "\U0001F427  Linux (Ollama)")
        tabs.addTab(self._make_tab(c, _LM_STUDIO), "\U0001F4BB  LM Studio (All)")
        tabs.addTab(self._make_tab(c, _CLOUD_SETUP), "\u2601  Cloud (API Key)")

        root.addWidget(tabs, stretch=1)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close setup guide")
        close_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setFixedHeight(APP_SETTINGS["touch_target_min"])
        close_btn.setFixedWidth(120)
        close_btn.setStyleSheet(
            f"QPushButton {{ background: {c['primary']}; color: white; "
            f"border: none; border-radius: 8px; font-weight: bold; "
            f"font-size: 13px; }}"
        )
        close_btn.clicked.connect(self.accept)
        root.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    @staticmethod
    def _make_tab(c: dict, text: str) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)

        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(
            f"font-size: 13px; color: {c['text']}; line-height: 1.5;"
        )
        lbl.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        layout.addWidget(lbl)
        layout.addStretch()

        scroll.setWidget(container)
        return scroll

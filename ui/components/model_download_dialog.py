"""First-time model download dialog for STT with detailed error guidance."""

import platform

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton,
    QScrollArea, QWidget,
)
from PyQt6.QtCore import Qt

from config.settings import get_colors
from stt.stt_settings_store import load_stt_settings
from stt.workers import ModelDownloadWorker

_SIZE_ESTIMATES = {
    "tiny": "~75 MB",
    "base": "~145 MB",
    "small": "~465 MB",
    "medium": "~1.5 GB",
    "large-v2": "~3 GB",
}

# ---------------------------------------------------------------------------
# Platform-specific troubleshooting for STT model download failures
# ---------------------------------------------------------------------------

_TROUBLESHOOT_MAC = """\
1) What is the issue?
   The speech-to-text model failed to download. This model is required \
for voice dictation (microphone button). It only needs to download once.

2) How to fix it:
   Check your internet connection, ensure Python dependencies are \
installed, and retry the download.

3) Step-by-step instructions (Mac):
   a) Check internet: Open Safari and load any website. If it fails, \
fix your network connection first.
   b) Open Terminal (Cmd + Space, type "Terminal", press Enter).
   c) Install/update the whisper dependency:
        pip3 install --upgrade openai-whisper
      If pip3 is not found, install Python first:
        brew install python
   d) If you see "Permission denied":
        pip3 install --user openai-whisper
   e) If you see "SSL certificate" errors:
        pip3 install --upgrade certifi
   f) Close this dialog and click the microphone button again to retry.
   g) If it still fails, try downloading the model manually:
        python3 -c "import whisper; whisper.load_model('tiny')"

   If none of the above works, check your firewall settings \u2014 the \
download needs to reach https://huggingface.co."""

_TROUBLESHOOT_WINDOWS = """\
1) What is the issue?
   The speech-to-text model failed to download. This model is required \
for voice dictation (microphone button). It only needs to download once.

2) How to fix it:
   Check your internet connection, ensure Python dependencies are \
installed, and retry the download.

3) Step-by-step instructions (Windows):
   a) Check internet: Open your browser and load any website. If it \
fails, fix your network connection first.
   b) Open Command Prompt (press Windows key, type "cmd", press Enter).
   c) Install/update the whisper dependency:
        pip install --upgrade openai-whisper
      If pip is not found, download Python from https://python.org \
and check "Add to PATH" during installation.
   d) If you see "Access denied":
        pip install --user openai-whisper
   e) If you see "SSL" or "certificate" errors:
        pip install --upgrade certifi
   f) Close this dialog and click the microphone button again to retry.
   g) If it still fails, try downloading the model manually:
        python -c "import whisper; whisper.load_model('tiny')"

   If none of the above works, check Windows Defender Firewall \u2014 the \
download needs to reach https://huggingface.co. You may need to allow \
Python through the firewall."""

_TROUBLESHOOT_LINUX = """\
1) What is the issue?
   The speech-to-text model failed to download. This model is required \
for voice dictation (microphone button). It only needs to download once.

2) How to fix it:
   Check your internet connection, ensure Python dependencies are \
installed, and retry the download.

3) Step-by-step instructions (Linux):
   a) Check internet: Open your browser or run: ping -c 3 google.com
   b) Open a terminal.
   c) Install/update the whisper dependency:
        pip3 install --upgrade openai-whisper
      If pip3 is not found:
        Ubuntu/Debian:  sudo apt install python3-pip
        Fedora:         sudo dnf install python3-pip
        Arch:           sudo pacman -S python-pip
   d) If you see "Permission denied":
        pip3 install --user openai-whisper
   e) If you see "SSL certificate" errors:
        pip3 install --upgrade certifi
   f) Close this dialog and click the microphone button again to retry.
   g) If it still fails, try downloading the model manually:
        python3 -c "import whisper; whisper.load_model('tiny')"

   If none of the above works, check your firewall (ufw, iptables) \u2014 \
the download needs to reach https://huggingface.co."""


def _get_troubleshoot_text() -> str:
    """Return platform-appropriate troubleshooting text."""
    system = platform.system()
    if system == "Darwin":
        return _TROUBLESHOOT_MAC
    elif system == "Windows":
        return _TROUBLESHOOT_WINDOWS
    return _TROUBLESHOOT_LINUX


class ModelDownloadDialog(QDialog):
    """Modal dialog that downloads the whisper model on first use."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloading Speech Model")
        self.setMinimumWidth(480)
        self.setModal(True)
        self._worker = None
        self._build_ui()

    def _build_ui(self):
        c = get_colors()
        self.setStyleSheet(f"QDialog {{ background-color: {c['dark_bg']}; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        settings = load_stt_settings()
        model_size = settings["model_size"]
        size_est = _SIZE_ESTIMATES.get(model_size, "unknown size")

        header = QLabel("Downloading Speech-to-Text Model")
        header.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {c['text']};"
        )
        layout.addWidget(header)

        info = QLabel(
            f"Model: {model_size} ({size_est})\n"
            "This only needs to happen once. The model will be cached "
            "locally for offline use."
        )
        info.setWordWrap(True)
        info.setStyleSheet(f"font-size: 13px; color: {c['text_muted']};")
        layout.addWidget(info)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)  # indeterminate
        self._progress.setFixedHeight(20)
        layout.addWidget(self._progress)

        self._status_label = QLabel("Downloading...")
        self._status_label.setStyleSheet(
            f"font-size: 12px; color: {c['text_muted']};"
        )
        layout.addWidget(self._status_label)

        # Error detail area — hidden until an error occurs
        self._error_scroll = QScrollArea()
        self._error_scroll.setWidgetResizable(True)
        self._error_scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )
        self._error_scroll.setMaximumHeight(280)
        self._error_scroll.setVisible(False)

        error_container = QWidget()
        error_container.setStyleSheet(
            f"QWidget {{ background: {c['dark_card']}; "
            f"border: 1px solid {c['dark_border']}; border-radius: 8px; }}"
        )
        error_layout = QVBoxLayout(error_container)
        error_layout.setContentsMargins(16, 12, 16, 12)

        self._error_detail = QLabel()
        self._error_detail.setWordWrap(True)
        self._error_detail.setStyleSheet(
            f"font-size: 12px; color: {c['text']}; line-height: 1.4; border: none;"
        )
        self._error_detail.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        error_layout.addWidget(self._error_detail)

        self._error_scroll.setWidget(error_container)
        layout.addWidget(self._error_scroll)

        # Buttons
        btn_row = QVBoxLayout()
        btn_row.setSpacing(8)

        self._retry_btn = QPushButton("Retry Download")
        self._retry_btn.setAccessibleName("Retry model download")
        self._retry_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._retry_btn.setFixedHeight(36)
        self._retry_btn.setVisible(False)
        self._retry_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {c['primary']}, stop:1 {c['tertiary']});
                color: white; border: none; border-radius: 8px;
                padding: 0 20px; font-weight: bold;
            }}
        """)
        self._retry_btn.clicked.connect(self._on_retry)
        btn_row.addWidget(self._retry_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setAccessibleName("Cancel model download")
        self._cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cancel_btn.setFixedHeight(36)
        self._cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['dark_input']}; color: {c['text']};
                border: 1px solid {c['dark_border']}; border-radius: 8px;
                padding: 0 20px;
            }}
        """)
        self._cancel_btn.clicked.connect(self._on_cancel)
        btn_row.addWidget(self._cancel_btn, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addLayout(btn_row)

    def start(self):
        """Begin the download worker."""
        self._worker = ModelDownloadWorker(self)
        self._worker.finished_signal.connect(self._on_finished)
        self._worker.error_signal.connect(self._on_error)
        self._worker.start()

    def _on_finished(self):
        self._status_label.setText("Download complete!")
        c = get_colors()
        self._status_label.setStyleSheet(
            f"font-size: 12px; color: {c['success']}; font-weight: bold;"
        )
        self.accept()

    def _on_error(self, msg: str):
        c = get_colors()
        self._status_label.setText(f"Download failed: {msg}")
        self._status_label.setStyleSheet(
            f"font-size: 12px; color: {c['error']}; font-weight: bold;"
        )
        self._progress.setRange(0, 1)
        self._progress.setValue(0)

        # Show detailed troubleshooting
        troubleshoot = _get_troubleshoot_text()
        self._error_detail.setText(troubleshoot)
        self._error_scroll.setVisible(True)
        self._retry_btn.setVisible(True)

        # Resize to fit
        self.setMinimumHeight(520)

    def _on_retry(self):
        c = get_colors()
        self._status_label.setText("Downloading...")
        self._status_label.setStyleSheet(
            f"font-size: 12px; color: {c['text_muted']};"
        )
        self._progress.setRange(0, 0)
        self._error_scroll.setVisible(False)
        self._retry_btn.setVisible(False)
        self.start()

    def _on_cancel(self):
        if self._worker and self._worker.isRunning():
            self._worker.terminate()
        self.reject()

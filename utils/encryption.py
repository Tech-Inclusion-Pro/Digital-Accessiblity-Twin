"""Field-level AES-256 encryption via Fernet (cryptography library)."""

import base64
import os
import sys
import uuid
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def _get_support_dir() -> Path:
    if sys.platform == "darwin":
        d = Path.home() / "Library" / "Application Support" / "AccessTwin"
    else:
        d = Path.home() / ".accesstwin"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _get_machine_id() -> str:
    """Derive a stable per-machine identifier."""
    try:
        if sys.platform == "darwin":
            import subprocess
            result = subprocess.run(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                capture_output=True, text=True, timeout=5,
            )
            for line in result.stdout.splitlines():
                if "IOPlatformUUID" in line:
                    return line.split('"')[-2]
    except Exception:
        pass
    return str(uuid.getnode())


class EncryptionManager:
    """AES-256 field-level encryption using Fernet."""

    def __init__(self):
        self._fernet = self._build_fernet()

    def _build_fernet(self) -> Fernet:
        support_dir = _get_support_dir()
        salt_path = support_dir / ".salt"
        if salt_path.exists():
            salt = salt_path.read_bytes()
        else:
            salt = os.urandom(16)
            salt_path.write_bytes(salt)

        machine_id = _get_machine_id()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480_000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
        return Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string and return base-64 ciphertext."""
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt base-64 ciphertext back to a string."""
        return self._fernet.decrypt(ciphertext.encode()).decode()

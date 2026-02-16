# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for AccessTwin — Digital Accessibility Twin Manager."""

import sys
import os

block_cipher = None

# Determine platform-specific settings
is_mac = sys.platform == 'darwin'
is_win = sys.platform == 'win32'

# Data files to bundle
datas = [
    ('data', 'data'),
    ('assets', 'assets'),
]

# Hidden imports that PyInstaller may miss
hiddenimports = [
    'PyQt6.QtWidgets',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'bcrypt',
    'aiohttp',
    'cryptography',
    'cryptography.fernet',
    'cryptography.hazmat.primitives.kdf.pbkdf2',
    'docx',
    'openpyxl',
    'numpy',
    'sounddevice',
    'faster_whisper',
    'config',
    'config.brand',
    'config.constants',
    'config.settings',
    'models',
    'models.database',
    'models.auth',
    'models.user',
    'models.student_profile',
    'models.support',
    'models.document',
    'models.evaluation',
    'models.tracking',
    'models.consultation_log',
    'models.insight_log',
    'models.audit',
    'ai',
    'ai.backend_manager',
    'ai.ai_settings_store',
    'ai.privacy_aggregator',
    'ai.ollama_client',
    'ai.lmstudio_client',
    'ai.gpt4all_client',
    'ai.cloud_client',
    'ai.prompts',
    'ai.prompts.coach_prompt',
    'ai.prompts.insights_prompt',
    'ai.prompts.student_insights_prompt',
    'stt',
    'stt.engine',
    'stt.stt_settings_store',
    'stt.workers',
    'ui',
    'ui.accessibility',
    'ui.accessibility_prefs',
    'ui.color_blind_engine',
    'ui.cursor_trail',
    'ui.reading_ruler',
    'ui.focus_manager',
    'ui.theme',
    'ui.theme_engine',
    'ui.navigation',
    'ui.components',
    'ui.screens',
    'utils',
    'utils.encryption',
    'utils.validators',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if is_mac:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='AccessTwin',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        icon='assets/AppIcon.icns',
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='AccessTwin',
    )
    app = BUNDLE(
        coll,
        name='AccessTwin.app',
        icon='assets/AppIcon.icns',
        bundle_identifier='com.techinclusionpro.accesstwin',
        info_plist={
            'CFBundleDisplayName': 'AccessTwin',
            'CFBundleShortVersionString': '2.4.0',
            'CFBundleVersion': '2.4.0',
            'NSHighResolutionCapable': True,
            'NSMicrophoneUsageDescription': 'AccessTwin uses the microphone for speech-to-text voice input.',
            'LSMinimumSystemVersion': '12.0',
        },
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='AccessTwin',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        icon='assets/AppIcon.icns' if not is_win else None,
    )

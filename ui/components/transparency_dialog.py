"""Reusable AI transparency dialog — 'How was this decided?' for all AI features."""

from dataclasses import dataclass, field

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget,
)
from PyQt6.QtCore import Qt

from config.settings import get_colors, APP_SETTINGS


@dataclass
class TransparencyInfo:
    """Data shown in the transparency dialog for a specific AI feature."""

    feature_name: str = ""
    provider_type: str = ""
    provider: str = ""
    model: str = ""
    principles: list = field(default_factory=list)
    privacy_rules: list = field(default_factory=list)
    data_summary: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)


class TransparencyDialog(QDialog):
    """'How was this decided?' dialog showing AI configuration, principles,
    data provided, confidence disclaimers, and warnings."""

    def __init__(self, info: TransparencyInfo, parent=None):
        super().__init__(parent)
        self.info = info
        self.setWindowTitle("How was this decided?")
        self.setMinimumWidth(520)
        self.setMinimumHeight(480)
        self.setAccessibleName("AI Transparency Information")
        self._build_ui()

    def _build_ui(self):
        c = get_colors()
        self.setStyleSheet(f"QDialog {{ background-color: {c['dark_bg']}; }}")

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        # Title
        title = QLabel("How was this decided?")
        title.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {c['text']};"
        )
        title.setAccessibleName("How was this decided?")
        root.addWidget(title)

        # Subtitle — feature name
        if self.info.feature_name:
            subtitle = QLabel(self.info.feature_name)
            subtitle.setStyleSheet(
                f"font-size: 14px; color: {c['primary_text']};"
            )
            subtitle.setAccessibleName(f"Feature: {self.info.feature_name}")
            root.addWidget(subtitle)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background: transparent; }}"
        )
        scroll.setAccessibleName("Transparency details")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # 1. AI Configuration
        layout.addWidget(self._build_section(
            c, "AI Configuration",
            self._format_config(),
        ))

        # 2. Guiding Principles
        if self.info.principles:
            layout.addWidget(self._build_section(
                c, "Guiding Principles",
                self._format_list(self.info.principles),
            ))

        # 3. Privacy Rules
        if self.info.privacy_rules:
            layout.addWidget(self._build_section(
                c, "Privacy Rules",
                self._format_list(self.info.privacy_rules),
            ))

        # 4. Information Provided to AI
        if self.info.data_summary:
            layout.addWidget(self._build_section(
                c, "Information Provided to AI",
                self._format_data_summary(),
            ))

        # 5. Model Confidence
        layout.addWidget(self._build_section(
            c, "Model Confidence",
            "AI-generated content is based on pattern matching and "
            "statistical probabilities. It does not truly \"understand\" "
            "the student. Outputs may contain inaccuracies, omissions, "
            "or inappropriate suggestions. Always apply your own professional "
            "judgement and consult the student directly.",
        ))

        # 6. Warnings & Limitations
        if self.info.warnings:
            layout.addWidget(self._build_section(
                c, "Warnings & Limitations",
                self._format_list(self.info.warnings),
            ))

        layout.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll, stretch=1)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close transparency dialog")
        close_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setFixedHeight(APP_SETTINGS["touch_target_min"])
        close_btn.setFixedWidth(120)
        close_btn.setStyleSheet(
            f"QPushButton {{ background: {c['primary']}; color: white; "
            f"border: none; border-radius: 8px; font-weight: bold; font-size: 13px; }}"
        )
        close_btn.clicked.connect(self.accept)
        root.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def _build_section(self, c, heading: str, body_text: str) -> QWidget:
        """Build a dark-card styled section with heading and body."""
        card = QWidget()
        card.setStyleSheet(
            f"QWidget {{ background: {c['dark_card']}; "
            f"border: 1px solid {c['dark_border']}; border-radius: 8px; }}"
        )
        card.setAccessibleName(heading)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(6)

        h = QLabel(heading)
        h.setStyleSheet(
            f"font-size: 13px; font-weight: bold; color: {c['text']}; border: none;"
        )
        layout.addWidget(h)

        body = QLabel(body_text)
        body.setWordWrap(True)
        body.setStyleSheet(
            f"font-size: 12px; color: {c['text_muted']}; border: none;"
        )
        body.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        layout.addWidget(body)

        return card

    def _format_config(self) -> str:
        parts = []
        if self.info.provider_type:
            label = "Local (on-device)" if self.info.provider_type == "local" else "Cloud"
            parts.append(f"Type: {label}")
        if self.info.provider:
            parts.append(f"Provider: {self.info.provider}")
        if self.info.model:
            parts.append(f"Model: {self.info.model}")
        if not parts:
            parts.append("No AI backend configured.")
        return "\n".join(parts)

    def _format_list(self, items: list) -> str:
        return "\n".join(f"  \u2022  {item}" for item in items)

    def _format_data_summary(self) -> str:
        lines = []
        for key, value in self.info.data_summary.items():
            lines.append(f"  \u2022  {key}: {value}")
        return "\n".join(lines)

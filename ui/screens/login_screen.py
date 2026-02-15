"""Three-tab login screen: Student Login / Teacher Login / Register."""

import json
import os
import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox, QCheckBox, QComboBox,
    QStackedWidget, QScrollArea, QSizePolicy, QDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap


def _get_asset_path(filename: str) -> str:
    """Get the path to an asset file."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, "assets", filename)

from config.settings import get_colors
from config.brand import ROLE_ACCENTS, BRAND_COLORS
from config.constants import SECURITY_QUESTIONS
from models.auth import AuthManager
from ui.accessibility import AccessibilityManager
from ui.components.accessibility_toolbar import AccessibilityToolbar
from ui.focus_manager import FocusManager


def _get_accent_colors():
    """Get accent colors, adapted for color-blind mode."""
    c = get_colors()
    return {
        "student": c.get("tertiary", ROLE_ACCENTS["student"]["accent"]),
        "teacher": c.get("secondary", ROLE_ACCENTS["teacher"]["accent"]),
        "primary": c.get("primary", BRAND_COLORS["primary"]),
        "primary_text": c.get("primary_text", "#b065d6"),
    }


# ─── Password Recovery Dialog ────────────────────────────────────────

class PasswordRecoveryDialog(QDialog):
    def __init__(self, auth_manager: AuthManager, parent=None):
        super().__init__(parent)
        self.auth = auth_manager
        self.username = None
        self.has_q2 = False
        self.setWindowTitle("Recover Password")
        self.setMinimumWidth(420)
        self.setMaximumWidth(600)
        self.setAccessibleName("Password recovery dialog")
        self._build()

    def _build(self):
        c = get_colors()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Password Recovery")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {c['primary_text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setAccessibleName("Password Recovery")
        layout.addWidget(title)

        # Stacked sections
        self.email_section = QWidget()
        self.questions_section = QWidget()
        self.reset_section = QWidget()
        self._build_email_section(c)
        self._build_questions_section(c)
        self._build_reset_section(c)

        layout.addWidget(self.email_section)
        layout.addWidget(self.questions_section)
        layout.addWidget(self.reset_section)
        self.questions_section.hide()
        self.reset_section.hide()

        layout.addStretch()

        cancel = QPushButton("Cancel")
        cancel.setAccessibleName("Cancel password recovery")
        cancel.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        cancel.setMinimumHeight(44)
        cancel.clicked.connect(self.reject)
        layout.addWidget(cancel)

    # ── sections ──

    def _recovery_input_style(self, c):
        return f"""
            QLineEdit {{
                background-color: {c['dark_input']}; color: {c['text']};
                border: 1px solid rgba(255,255,255,0.15); border-radius: 12px;
                padding: 8px 14px; font-size: 13pt;
            }}
            QLineEdit:focus {{ border: 2px solid {c['primary']}; }}
        """

    def _build_email_section(self, c):
        layout = QVBoxLayout(self.email_section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        lbl = QLabel("Enter your username:")
        lbl.setAccessibleName("Enter your username")
        layout.addWidget(lbl)
        self.recovery_username = QLineEdit()
        self.recovery_username.setPlaceholderText("Your username")
        self.recovery_username.setAccessibleName("Username for recovery")
        self.recovery_username.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.recovery_username.setMinimumHeight(48)
        self.recovery_username.setStyleSheet(self._recovery_input_style(c))
        layout.addWidget(self.recovery_username)
        self.email_error = QLabel("")
        self.email_error.setStyleSheet(f"color: {c['error']};")
        self.email_error.hide()
        layout.addWidget(self.email_error)
        btn = QPushButton("Find Account")
        btn.setAccessibleName("Find account")
        btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        btn.setMinimumHeight(48)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {c['primary']}, stop:1 {c['tertiary']});
                color: white; border: none; border-radius: 12px;
                padding: 8px 16px; font-weight: bold; font-size: 13pt;
            }}
        """)
        btn.clicked.connect(self._on_find)
        layout.addWidget(btn)

    def _build_questions_section(self, c):
        layout = QVBoxLayout(self.questions_section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        self.q1_label = QLabel("Question 1:")
        self.q1_label.setAccessibleName("Security question 1")
        layout.addWidget(self.q1_label)
        self.a1_input = QLineEdit()
        self.a1_input.setPlaceholderText("Answer (not case sensitive)")
        self.a1_input.setAccessibleName("Answer to security question 1")
        self.a1_input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.a1_input.setMinimumHeight(48)
        self.a1_input.setStyleSheet(self._recovery_input_style(c))
        layout.addWidget(self.a1_input)
        self.q2_label = QLabel("Question 2:")
        self.q2_label.setAccessibleName("Security question 2")
        layout.addWidget(self.q2_label)
        self.a2_input = QLineEdit()
        self.a2_input.setPlaceholderText("Answer (not case sensitive)")
        self.a2_input.setAccessibleName("Answer to security question 2")
        self.a2_input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.a2_input.setMinimumHeight(48)
        self.a2_input.setStyleSheet(self._recovery_input_style(c))
        layout.addWidget(self.a2_input)
        self.q_error = QLabel("")
        self.q_error.setStyleSheet(f"color: {c['error']};")
        self.q_error.hide()
        layout.addWidget(self.q_error)
        btn = QPushButton("Verify Answers")
        btn.setAccessibleName("Verify security answers")
        btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        btn.setMinimumHeight(48)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {c['primary']}, stop:1 {c['tertiary']});
                color: white; border: none; border-radius: 12px;
                padding: 8px 16px; font-weight: bold; font-size: 13pt;
            }}
        """)
        btn.clicked.connect(self._on_verify)
        layout.addWidget(btn)

    def _build_reset_section(self, c):
        layout = QVBoxLayout(self.reset_section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(QLabel("Enter your new password:"))
        self.new_pw = QLineEdit()
        self.new_pw.setPlaceholderText("New password (8+ characters)")
        self.new_pw.setAccessibleName("New password")
        self.new_pw.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.new_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pw.setMinimumHeight(48)
        self.new_pw.setStyleSheet(self._recovery_input_style(c))
        layout.addWidget(self.new_pw)
        self.confirm_pw = QLineEdit()
        self.confirm_pw.setPlaceholderText("Confirm new password")
        self.confirm_pw.setAccessibleName("Confirm new password")
        self.confirm_pw.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.confirm_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_pw.setMinimumHeight(48)
        self.confirm_pw.setStyleSheet(self._recovery_input_style(c))
        layout.addWidget(self.confirm_pw)
        self.r_error = QLabel("")
        self.r_error.setStyleSheet(f"color: {c['error']};")
        self.r_error.hide()
        layout.addWidget(self.r_error)
        btn = QPushButton("Reset Password")
        btn.setAccessibleName("Reset password")
        btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        btn.setMinimumHeight(48)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {c['primary']}, stop:1 {c['tertiary']});
                color: white; border: none; border-radius: 12px;
                padding: 8px 16px; font-weight: bold; font-size: 13pt;
            }}
        """)
        btn.clicked.connect(self._on_reset)
        layout.addWidget(btn)

    # ── handlers ──

    def _on_find(self):
        name = self.recovery_username.text().strip()
        if not name:
            self.email_error.setText("Please enter your username")
            self.email_error.show()
            return
        ok, msg, q1, q2 = self.auth.get_security_questions(name)
        if ok:
            self.username = name
            self.q1_label.setText(f"Q1: {q1}")
            if q2:
                self.has_q2 = True
                self.q2_label.setText(f"Q2: {q2}")
            else:
                self.has_q2 = False
                self.q2_label.hide()
                self.a2_input.hide()
            self.email_section.hide()
            self.questions_section.show()
            FocusManager.set_focus_after_transition(self.a1_input)
        else:
            self.email_error.setText(msg)
            self.email_error.show()

    def _on_verify(self):
        a1 = self.a1_input.text().strip()
        if not a1:
            self.q_error.setText("Please answer the security question")
            self.q_error.show()
            return
        a2 = self.a2_input.text().strip() if self.has_q2 else None
        if self.has_q2 and not a2:
            self.q_error.setText("Please answer both questions")
            self.q_error.show()
            return
        ok, msg = self.auth.verify_security_answers(self.username, a1, a2)
        if ok:
            self.questions_section.hide()
            self.reset_section.show()
            FocusManager.set_focus_after_transition(self.new_pw)
        else:
            self.q_error.setText(msg)
            self.q_error.show()

    def _on_reset(self):
        pw = self.new_pw.text()
        confirm = self.confirm_pw.text()
        if not pw or not confirm:
            self.r_error.setText("Please fill in both fields")
            self.r_error.show()
            return
        if pw != confirm:
            self.r_error.setText("Passwords do not match")
            self.r_error.show()
            return
        ok, msg = self.auth.reset_password(self.username, pw)
        if ok:
            QMessageBox.information(self, "Success", "Password reset. You can now log in.")
            self.accept()
        else:
            self.r_error.setText(msg)
            self.r_error.show()


# ─── Main Login Screen ───────────────────────────────────────────────

class LoginScreen(QWidget):
    """Three-tab login screen: Student Login / Teacher Login / Register."""

    login_successful = pyqtSignal()

    TAB_STUDENT = 0
    TAB_TEACHER = 1
    TAB_REGISTER = 2

    def __init__(self, auth_manager: AuthManager, a11y: AccessibilityManager):
        super().__init__()
        self.auth = auth_manager
        self.a11y = a11y
        self._pw_visible = {"student": False, "teacher": False, "register": False}
        self._current_tab = 0

        # Track styled widgets for dynamic re-styling
        self._styled_widgets = []

        self._build_ui()

        # Listen for accessibility changes to re-apply styles
        self.a11y.settings_changed.connect(self._on_a11y_changed)

    # ── build ──

    def _build_ui(self):
        c = get_colors()
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Accessibility toolbar (visible pre-login)
        self.a11y_toolbar = AccessibilityToolbar(self)
        root.addWidget(self.a11y_toolbar)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setAccessibleName("Login screen content")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.addStretch()

        center = QHBoxLayout()
        center.addStretch()

        # Card container — responsive width
        self.container = QFrame()
        self.container.setObjectName("loginCard")
        self.container.setMinimumWidth(420)
        self.container.setMaximumWidth(600)
        self.container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        clayout = QVBoxLayout(self.container)
        clayout.setContentsMargins(36, 28, 36, 28)
        clayout.setSpacing(12)

        # Logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = _get_asset_path("logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled = pixmap.scaled(
                120, 120,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_label.setPixmap(scaled)
        logo_label.setMinimumHeight(120)
        logo_label.setAccessibleName("AccessTwin logo")
        clayout.addWidget(logo_label)

        # App title
        self.title_label = QLabel("AccessTwin")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setAccessibleName("AccessTwin")
        clayout.addWidget(self.title_label)

        self.subtitle_label = QLabel("Digital Accessibility Twin Manager")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        clayout.addWidget(self.subtitle_label)
        clayout.addSpacing(8)

        # ── Tab card ──
        self.tab_card = QFrame()
        self.tab_card.setObjectName("tabCard")
        tc_layout = QVBoxLayout(self.tab_card)
        tc_layout.setContentsMargins(0, 0, 0, 0)
        tc_layout.setSpacing(0)

        # Tab header
        tab_header = QWidget()
        tab_header.setObjectName("tabHeader")
        th_layout = QVBoxLayout(tab_header)
        th_layout.setContentsMargins(0, 0, 0, 0)
        th_layout.setSpacing(0)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(0)

        self.tab_btns = []
        tab_labels = ["Student Login", "Teacher Login", "Register"]
        for i, label in enumerate(tab_labels):
            btn = QPushButton(label)
            btn.setAccessibleName(f"{label} tab")
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            idx = i
            btn.clicked.connect(lambda checked, x=idx: self._switch_tab(x))
            btn_row.addWidget(btn)
            self.tab_btns.append(btn)
        th_layout.addLayout(btn_row)

        # Underlines
        ul_row = QHBoxLayout()
        ul_row.setContentsMargins(0, 0, 0, 0)
        ul_row.setSpacing(0)
        self.underlines = []
        for _ in range(3):
            line = QFrame()
            line.setFixedHeight(3)
            ul_row.addWidget(line)
            self.underlines.append(line)
        th_layout.addLayout(ul_row)

        tc_layout.addWidget(tab_header)

        # Content stack
        self.content_stack = QStackedWidget()

        self.content_stack.addWidget(self._build_login_page("student"))
        self.content_stack.addWidget(self._build_login_page("teacher"))
        self.content_stack.addWidget(self._build_register_page())

        tc_layout.addWidget(self.content_stack)
        clayout.addWidget(self.tab_card)

        # Privacy note
        self.privacy_label = QLabel("Secure, local-only data storage")
        self.privacy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        clayout.addWidget(self.privacy_label)

        # ── Example / Demo buttons ──
        clayout.addSpacing(8)
        example_divider_row = QHBoxLayout()
        example_divider_row.setContentsMargins(0, 0, 0, 0)
        div_left = QFrame()
        div_left.setFrameShape(QFrame.Shape.HLine)
        div_left.setFixedHeight(1)
        example_divider_row.addWidget(div_left, stretch=1)
        self.example_divider_label = QLabel("  or explore an example  ")
        self.example_divider_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        example_divider_row.addWidget(self.example_divider_label)
        div_right = QFrame()
        div_right.setFrameShape(QFrame.Shape.HLine)
        div_right.setFixedHeight(1)
        example_divider_row.addWidget(div_right, stretch=1)
        clayout.addLayout(example_divider_row)
        # Store divider lines for re-styling
        self._example_div_left = div_left
        self._example_div_right = div_right
        clayout.addSpacing(8)

        example_row = QHBoxLayout()
        example_row.setSpacing(12)

        self.student_example_btn = QPushButton("See Student Example")
        self.student_example_btn.setAccessibleName(
            "View a student example without logging in"
        )
        self.student_example_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.student_example_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.student_example_btn.setMinimumHeight(44)
        self.student_example_btn.clicked.connect(lambda: self._on_example_login("student"))
        example_row.addWidget(self.student_example_btn)

        self.teacher_example_btn = QPushButton("See Teacher Example")
        self.teacher_example_btn.setAccessibleName(
            "View a teacher example without logging in"
        )
        self.teacher_example_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.teacher_example_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.teacher_example_btn.setMinimumHeight(44)
        self.teacher_example_btn.clicked.connect(lambda: self._on_example_login("teacher"))
        example_row.addWidget(self.teacher_example_btn)

        clayout.addLayout(example_row)

        center.addWidget(self.container)
        center.addStretch()
        scroll_layout.addLayout(center)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        root.addWidget(scroll)

        self._apply_styles()
        self._switch_tab(self.TAB_STUDENT)

    # ── dynamic styling ──

    def _apply_styles(self):
        """Apply all styles using current colors (responds to color-blind changes)."""
        c = get_colors()
        accents = _get_accent_colors()

        # Card container
        self.container.setStyleSheet(f"""
            QFrame#loginCard {{
                background-color: {c['dark_card']};
                border-radius: 20px;
                border-bottom: 2px solid {c.get('dark_border', '#1c2a4a')};
            }}
        """)

        # Title / subtitle
        self.title_label.setStyleSheet(
            f"font-size: 26px; font-weight: bold; color: {accents['primary_text']};"
        )
        self.subtitle_label.setStyleSheet(
            f"color: {c['text_muted']}; font-size: 12pt;"
        )

        # Tab card
        self.tab_card.setStyleSheet(f"""
            QFrame#tabCard {{
                background-color: {c['dark_bg']};
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 16px;
            }}
        """)

        # Content stack
        self.content_stack.setStyleSheet("background: transparent;")

        # Privacy label
        self.privacy_label.setStyleSheet(
            f"color: {c['text_muted']}; font-size: 11pt;"
        )

        # Example section
        self.example_divider_label.setStyleSheet(
            f"color: {c['text_muted']}; font-size: 10pt;"
        )
        for div in (self._example_div_left, self._example_div_right):
            div.setStyleSheet(f"background-color: {c.get('dark_border', 'rgba(255,255,255,0.1)')};")

        self.student_example_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {accents['student']};
                border: 2px solid {accents['student']};
                border-radius: 12px;
                padding: 6px 16px; font-size: 12pt; font-weight: bold;
            }}
            QPushButton:hover {{
                background: {accents['student']}; color: white;
            }}
            QPushButton:focus {{
                outline: 3px solid {accents['student']}; outline-offset: 2px;
            }}
        """)
        self.teacher_example_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {accents['teacher']};
                border: 2px solid {accents['teacher']};
                border-radius: 12px;
                padding: 6px 16px; font-size: 12pt; font-weight: bold;
            }}
            QPushButton:hover {{
                background: {accents['teacher']}; color: white;
            }}
            QPushButton:focus {{
                outline: 3px solid {accents['teacher']}; outline-offset: 2px;
            }}
        """)

        # Re-style all tracked input widgets
        for entry in self._styled_widgets:
            kind = entry["kind"]
            widget = entry["widget"]
            if kind == "input":
                self._apply_input_style(widget, c)
            elif kind == "pw_wrapper":
                obj_name = widget.objectName()
                widget.setStyleSheet(f"""
                    QFrame#{obj_name} {{
                        background-color: {c['dark_input']};
                        border: 1px solid rgba(255,255,255,0.15);
                        border-radius: 12px;
                    }}
                """)
            elif kind == "pw_input":
                widget.setStyleSheet(f"""
                    QLineEdit {{
                        background: transparent; border: none;
                        color: {c['text']}; padding: 8px 14px; font-size: 13pt;
                    }}
                """)
            elif kind == "eye_btn":
                widget.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent; border: none;
                        color: {c['text_muted']}; font-size: 14pt;
                        padding: 0; min-height: 0; min-width: 0;
                    }}
                    QPushButton:hover {{ color: {accents['primary_text']}; }}
                """)
            elif kind == "field_label":
                widget.setStyleSheet(
                    f"font-weight: bold; font-size: 13pt; color: {accents['primary_text']};"
                )
            elif kind == "forgot_btn":
                widget.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent; border: none;
                        color: {c['text']}; font-size: 11pt; font-weight: bold;
                        padding: 2px 4px; min-height: 0; min-width: 0;
                    }}
                    QPushButton:hover {{ color: {accents['primary_text']}; }}
                """)
            elif kind == "login_btn":
                accent = entry.get("accent_key", "primary")
                accent_color = accents.get(accent, accents["primary"])
                widget.setStyleSheet(f"""
                    QPushButton {{
                        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                            stop:0 {accent_color}, stop:1 {accents['primary']});
                        color: white; border: none; border-radius: 12px;
                        padding: 8px 24px; font-size: 14pt; font-weight: bold; min-height: 44px;
                    }}
                    QPushButton:hover {{
                        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                            stop:0 {accents['primary_text']}, stop:1 {accents['primary']});
                    }}
                    QPushButton:focus {{
                        outline: 3px solid {accent_color}; outline-offset: 2px;
                    }}
                """)
            elif kind == "error_label":
                widget.setStyleSheet(f"color: {c['error']}; font-size: 11pt;")
            elif kind == "helper_label":
                widget.setStyleSheet(f"color: {c['text_muted']}; font-size: 10pt;")
            elif kind == "combo":
                self._apply_combo_style(widget, c)

        # Re-style tab buttons
        self._switch_tab(self._current_tab)

    def _on_a11y_changed(self):
        """Re-apply all styles when accessibility settings change."""
        self._apply_styles()

    # ── tabs ──

    def _switch_tab(self, index: int):
        self._current_tab = index
        self.content_stack.setCurrentIndex(index)
        c = get_colors()
        accents = _get_accent_colors()
        tab_accent_keys = ["student", "teacher", "primary"]

        for i, btn in enumerate(self.tab_btns):
            accent_color = accents[tab_accent_keys[i]]
            if i == index:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent; border: none;
                        color: white; font-size: 13pt; font-weight: bold;
                        padding: 12px 0; min-height: 0; min-width: 0;
                    }}
                """)
                self.underlines[i].setStyleSheet(f"background-color: {accent_color};")
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent; border: none;
                        color: {c['text_muted']}; font-size: 13pt; font-weight: bold;
                        padding: 12px 0; min-height: 0; min-width: 0;
                    }}
                    QPushButton:hover {{ color: rgba(255,255,255,0.7); }}
                """)
                self.underlines[i].setStyleSheet("background-color: transparent;")

    # ── login page (shared for student / teacher) ──

    def _build_login_page(self, role: str) -> QWidget:
        c = get_colors()
        accents = _get_accent_colors()

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(4)

        # Username
        u_label = self._field_label("Username", c)
        layout.addWidget(u_label)
        layout.addSpacing(6)
        username = QLineEdit()
        username.setPlaceholderText("Enter your username")
        username.setAccessibleName(f"{role.title()} login username")
        username.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._apply_input_style(username, c)
        self._styled_widgets.append({"kind": "input", "widget": username})
        u_label.setBuddy(username)
        layout.addWidget(username)
        layout.addSpacing(16)

        # Password
        p_label = self._field_label("Password", c)
        layout.addWidget(p_label)
        layout.addSpacing(6)

        pw_wrapper = QFrame()
        pw_wrapper.setObjectName(f"{role}PwWrapper")
        pw_wrapper.setMinimumHeight(48)
        pw_wrapper.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        pw_wrapper.setStyleSheet(f"""
            QFrame#{role}PwWrapper {{
                background-color: {c['dark_input']};
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 12px;
            }}
        """)
        self._styled_widgets.append({"kind": "pw_wrapper", "widget": pw_wrapper})
        pw_lay = QHBoxLayout(pw_wrapper)
        pw_lay.setContentsMargins(0, 0, 4, 0)
        pw_lay.setSpacing(0)

        password = QLineEdit()
        password.setPlaceholderText("Enter your password")
        password.setEchoMode(QLineEdit.EchoMode.Password)
        password.setAccessibleName(f"{role.title()} login password")
        password.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        password.setMinimumHeight(44)
        password.setStyleSheet(f"""
            QLineEdit {{
                background: transparent; border: none;
                color: {c['text']}; padding: 8px 14px; font-size: 13pt;
            }}
        """)
        self._styled_widgets.append({"kind": "pw_input", "widget": password})
        pw_lay.addWidget(password)

        eye = QPushButton("\u25C9")
        eye.setFixedSize(36, 36)
        eye.setAccessibleName("Toggle password visibility")
        eye.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        eye.setCursor(Qt.CursorShape.PointingHandCursor)
        eye.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none;
                color: {c['text_muted']}; font-size: 14pt;
                padding: 0; min-height: 0; min-width: 0;
            }}
            QPushButton:hover {{ color: {accents['primary_text']}; }}
        """)
        self._styled_widgets.append({"kind": "eye_btn", "widget": eye})
        eye.clicked.connect(lambda: self._toggle_pw(role, password, eye))
        pw_lay.addWidget(eye)

        p_label.setBuddy(password)
        layout.addWidget(pw_wrapper)
        layout.addSpacing(12)

        # Forgot password
        row = QHBoxLayout()
        row.addStretch()
        forgot = QPushButton("Forgot password?")
        forgot.setAccessibleName("Recover your password")
        forgot.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        forgot.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot.setMinimumHeight(28)
        forgot.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none;
                color: {c['text']}; font-size: 11pt; font-weight: bold;
                padding: 2px 4px; min-height: 0; min-width: 0;
            }}
            QPushButton:hover {{ color: {accents['primary_text']}; }}
        """)
        self._styled_widgets.append({"kind": "forgot_btn", "widget": forgot})
        forgot.clicked.connect(self._on_forgot)
        row.addWidget(forgot)
        layout.addLayout(row)
        layout.addSpacing(12)

        # Error
        error_label = QLabel("")
        error_label.setStyleSheet(f"color: {c['error']}; font-size: 11pt;")
        error_label.setWordWrap(True)
        error_label.hide()
        self._styled_widgets.append({"kind": "error_label", "widget": error_label})
        layout.addWidget(error_label)

        # Sign In button
        accent_key = "student" if role == "student" else "teacher"
        login_btn = QPushButton("Sign In")
        login_btn.setAccessibleName(f"Sign in as {role}")
        login_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setMinimumHeight(48)
        self._styled_widgets.append({
            "kind": "login_btn", "widget": login_btn, "accent_key": accent_key,
        })
        login_btn.clicked.connect(lambda: self._on_login(role, username, password, error_label))
        password.returnPressed.connect(login_btn.click)
        layout.addWidget(login_btn)

        layout.addStretch()

        # Store references for accessibility
        setattr(self, f"_{role}_username", username)
        setattr(self, f"_{role}_password", password)

        return page

    # ── register page ──

    def _build_register_page(self) -> QWidget:
        c = get_colors()
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        sc = QWidget()
        layout = QVBoxLayout(sc)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(4)

        # Role selector
        r_label = self._field_label("I am a...", c)
        layout.addWidget(r_label)
        layout.addSpacing(6)
        self.role_combo = QComboBox()
        self.role_combo.addItem("Student", "student")
        self.role_combo.addItem("Teacher", "teacher")
        self.role_combo.setAccessibleName("Select your role")
        self.role_combo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.role_combo.setMinimumHeight(48)
        self._apply_combo_style(self.role_combo, c)
        self._styled_widgets.append({"kind": "combo", "widget": self.role_combo})
        r_label.setBuddy(self.role_combo)
        layout.addWidget(self.role_combo)
        layout.addSpacing(16)

        # Username
        u_label = self._field_label("Username", c)
        layout.addWidget(u_label)
        layout.addSpacing(6)
        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Choose a username (min 3 characters)")
        self.reg_username.setAccessibleName("Registration username")
        self.reg_username.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._apply_input_style(self.reg_username, c)
        self._styled_widgets.append({"kind": "input", "widget": self.reg_username})
        u_label.setBuddy(self.reg_username)
        layout.addWidget(self.reg_username)
        layout.addSpacing(16)

        # Password with eye
        p_label = self._field_label("Password", c)
        layout.addWidget(p_label)
        layout.addSpacing(6)
        pw_wrap = QFrame()
        pw_wrap.setObjectName("regPwWrap")
        pw_wrap.setMinimumHeight(48)
        pw_wrap.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        pw_wrap.setStyleSheet(f"""
            QFrame#regPwWrap {{
                background-color: {c['dark_input']};
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 12px;
            }}
        """)
        self._styled_widgets.append({"kind": "pw_wrapper", "widget": pw_wrap})
        pw_l = QHBoxLayout(pw_wrap)
        pw_l.setContentsMargins(0, 0, 4, 0)
        pw_l.setSpacing(0)
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Create a password (min 8 characters)")
        self.reg_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_password.setAccessibleName("Create password")
        self.reg_password.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.reg_password.setMinimumHeight(44)
        self.reg_password.setStyleSheet(f"""
            QLineEdit {{
                background: transparent; border: none;
                color: {c['text']}; padding: 8px 14px; font-size: 13pt;
            }}
        """)
        self._styled_widgets.append({"kind": "pw_input", "widget": self.reg_password})
        pw_l.addWidget(self.reg_password)
        reg_eye = QPushButton("\u25C9")
        reg_eye.setFixedSize(36, 36)
        reg_eye.setAccessibleName("Toggle password visibility")
        reg_eye.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        reg_eye.setCursor(Qt.CursorShape.PointingHandCursor)
        reg_eye.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none;
                color: {c['text_muted']}; font-size: 14pt;
                padding: 0; min-height: 0; min-width: 0;
            }}
            QPushButton:hover {{ color: {c['primary_text']}; }}
        """)
        self._styled_widgets.append({"kind": "eye_btn", "widget": reg_eye})
        reg_eye.clicked.connect(lambda: self._toggle_pw("register", self.reg_password, reg_eye))
        pw_l.addWidget(reg_eye)
        p_label.setBuddy(self.reg_password)
        layout.addWidget(pw_wrap)
        layout.addSpacing(16)

        # Confirm password
        cp_label = self._field_label("Confirm Password", c)
        layout.addWidget(cp_label)
        layout.addSpacing(6)
        self.reg_confirm = QLineEdit()
        self.reg_confirm.setPlaceholderText("Confirm your password")
        self.reg_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_confirm.setAccessibleName("Confirm password")
        self.reg_confirm.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._apply_input_style(self.reg_confirm, c)
        self._styled_widgets.append({"kind": "input", "widget": self.reg_confirm})
        cp_label.setBuddy(self.reg_confirm)
        layout.addWidget(self.reg_confirm)
        layout.addSpacing(16)

        # Security question
        sq_label = self._field_label("Security Question", c)
        layout.addWidget(sq_label)
        layout.addSpacing(6)
        self.sec_q1 = QComboBox()
        self.sec_q1.addItems(SECURITY_QUESTIONS)
        self.sec_q1.setAccessibleName("Select a security question")
        self.sec_q1.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.sec_q1.setMinimumHeight(48)
        self._apply_combo_style(self.sec_q1, c)
        self._styled_widgets.append({"kind": "combo", "widget": self.sec_q1})
        sq_label.setBuddy(self.sec_q1)
        layout.addWidget(self.sec_q1)
        layout.addSpacing(16)

        # Security answer
        sa_label = self._field_label("Security Answer", c)
        layout.addWidget(sa_label)
        layout.addSpacing(6)
        self.sec_a1 = QLineEdit()
        self.sec_a1.setPlaceholderText("Answer to your security question")
        self.sec_a1.setAccessibleName("Security answer")
        self.sec_a1.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._apply_input_style(self.sec_a1, c)
        self._styled_widgets.append({"kind": "input", "widget": self.sec_a1})
        sa_label.setBuddy(self.sec_a1)
        layout.addWidget(self.sec_a1)
        layout.addSpacing(4)
        self.helper_label = QLabel("Used for password recovery. Keep it memorable!")
        self.helper_label.setStyleSheet(f"color: {c['text_muted']}; font-size: 10pt;")
        self._styled_widgets.append({"kind": "helper_label", "widget": self.helper_label})
        layout.addWidget(self.helper_label)
        layout.addSpacing(12)

        # Consent checkbox
        self.consent_cb = QCheckBox("I agree to the terms of use and privacy policy")
        self.consent_cb.setAccessibleName("Agree to terms of use and privacy policy")
        self.consent_cb.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        layout.addWidget(self.consent_cb)
        layout.addSpacing(16)

        # Error
        self.reg_error = QLabel("")
        self.reg_error.setStyleSheet(f"color: {c['error']}; font-size: 11pt;")
        self.reg_error.setWordWrap(True)
        self.reg_error.hide()
        self._styled_widgets.append({"kind": "error_label", "widget": self.reg_error})
        layout.addWidget(self.reg_error)

        # Create Account button
        reg_btn = QPushButton("Create Account")
        reg_btn.setAccessibleName("Create a new account")
        reg_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        reg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reg_btn.setMinimumHeight(48)
        self._styled_widgets.append({
            "kind": "login_btn", "widget": reg_btn, "accent_key": "primary",
        })
        reg_btn.clicked.connect(self._on_register)
        self.sec_a1.returnPressed.connect(reg_btn.click)
        layout.addWidget(reg_btn)
        layout.addSpacing(8)

        scroll.setWidget(sc)
        page_layout.addWidget(scroll)
        return page

    # ── helpers ──

    def _field_label(self, text: str, c: dict) -> QLabel:
        accents = _get_accent_colors()
        lbl = QLabel(text)
        lbl.setMinimumHeight(22)
        lbl.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        lbl.setStyleSheet(
            f"font-weight: bold; font-size: 13pt; color: {accents['primary_text']};"
        )
        lbl.setAccessibleName(text)
        self._styled_widgets.append({"kind": "field_label", "widget": lbl})
        return lbl

    @staticmethod
    def _apply_input_style(w: QLineEdit, c: dict):
        w.setMinimumHeight(48)
        w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        w.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c['dark_input']}; color: {c['text']};
                border: 1px solid rgba(255,255,255,0.15); border-radius: 12px;
                padding: 8px 14px; font-size: 13pt;
            }}
            QLineEdit:focus {{ border: 2px solid {c['primary']}; }}
        """)

    @staticmethod
    def _apply_combo_style(w: QComboBox, c: dict):
        w.setMinimumHeight(48)
        w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        w.setStyleSheet(f"""
            QComboBox {{
                background-color: {c['dark_input']}; color: {c['text']};
                border: 1px solid rgba(255,255,255,0.15); border-radius: 12px;
                padding: 8px 14px; font-size: 13pt;
            }}
            QComboBox:focus {{ border: 2px solid {c['primary']}; }}
            QComboBox QAbstractItemView {{
                background-color: {c['dark_card']}; color: {c['text']};
                selection-background-color: {c['primary']};
                font-size: 13pt;
            }}
        """)

    def _toggle_pw(self, key, line_edit, btn):
        self._pw_visible[key] = not self._pw_visible[key]
        if self._pw_visible[key]:
            line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            btn.setText("\u25CE")
        else:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            btn.setText("\u25C9")

    # ── actions ──

    def _on_login(self, role, username_input, password_input, error_label):
        username = username_input.text().strip()
        password = password_input.text()
        if not username or not password:
            self._show_error(error_label, "Please enter both username and password")
            return
        ok, msg = self.auth.login(username, password, expected_role=role)
        if ok:
            self.login_successful.emit()
        else:
            self._show_error(error_label, msg)

    def _on_register(self):
        username = self.reg_username.text().strip()
        password = self.reg_password.text()
        confirm = self.reg_confirm.text()
        role = self.role_combo.currentData()
        sq = self.sec_q1.currentText()
        sa = self.sec_a1.text().strip()

        if not username or not password:
            self._show_error(self.reg_error, "Please fill in all fields")
            return
        if password != confirm:
            self._show_error(self.reg_error, "Passwords do not match")
            return
        if not sa:
            self._show_error(self.reg_error, "Please answer the security question")
            return
        if not self.consent_cb.isChecked():
            self._show_error(self.reg_error, "You must agree to the terms to create an account")
            return

        ok, msg = self.auth.register(
            username, password, role,
            security_question_1=sq,
            security_answer_1=sa,
        )
        if ok:
            self.login_successful.emit()
        else:
            self._show_error(self.reg_error, msg)

    def _on_forgot(self):
        dlg = PasswordRecoveryDialog(self.auth, self)
        dlg.exec()

    def _on_example_login(self, role: str):
        """Log in with a demo account so users can explore the app without registering."""
        demo_accounts = {
            "student": "maya",
            "teacher": "rtorres",
        }
        username = demo_accounts.get(role)
        if not username:
            return

        ok, msg = self.auth.login(username, "Demo1234", expected_role=role)
        if ok:
            self.login_successful.emit()
        else:
            QMessageBox.information(
                self,
                "Example Not Available",
                "Demo data has not been set up yet.\n\n"
                "To create example data, run this command in a terminal:\n\n"
                "  cd /Users/roccocatrone/accesstwin\n"
                "  python3 seed_demo_data.py\n\n"
                "Then try again.",
            )

    @staticmethod
    def _show_error(label: QLabel, msg: str):
        label.setText(f"\u25B3 {msg}")
        label.show()
        label.setAccessibleDescription(f"Error: {msg}")

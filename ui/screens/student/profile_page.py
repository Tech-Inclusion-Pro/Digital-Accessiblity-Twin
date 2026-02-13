"""Student profile page — 5-tab view for managing accessibility profile."""

import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QScrollArea, QFormLayout, QLineEdit, QTextEdit,
    QComboBox, QListWidget, QListWidgetItem, QMessageBox, QGridLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal

from config.settings import get_colors
from models.student_profile import StudentProfile
from models.support import SupportEntry
from ui.components.support_card import SupportCard
from ui.components.empty_state import EmptyState


class StudentProfilePage(QWidget):
    """5-tab profile editor: Strengths, Supports, History, Goals, Stakeholders."""

    def __init__(self, db_manager, auth_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.auth = auth_manager
        self._profile = None
        self._build_ui()

    def _build_ui(self):
        c = get_colors()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        header = QLabel("My Accessibility Profile")
        header.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {c['text']};")
        header.setAccessibleName("My Accessibility Profile")
        layout.addWidget(header)

        # Create Profile section (shown when no profile exists)
        self._create_section = QWidget()
        create_layout = QVBoxLayout(self._create_section)
        create_layout.setContentsMargins(0, 0, 0, 0)

        create_form = QFormLayout()
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Your display name")
        self._name_input.setAccessibleName("Profile name")
        self._name_input.setFixedHeight(40)
        create_form.addRow("Name:", self._name_input)
        create_layout.addLayout(create_form)

        create_btn = QPushButton("Create Profile")
        create_btn.setAccessibleName("Create accessibility profile")
        create_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_btn.setFixedHeight(44)
        create_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {c['primary']}, stop:1 {c['tertiary']});
                color: white; border: none; border-radius: 8px;
                padding: 8px 24px; font-weight: bold;
            }}
        """)
        create_btn.clicked.connect(self._create_profile)
        create_layout.addWidget(create_btn)

        self._create_section.setVisible(False)
        layout.addWidget(self._create_section)

        # Tabs
        self._tabs = QTabWidget()
        self._tabs.setAccessibleName("Profile sections")
        layout.addWidget(self._tabs, stretch=1)

        self._build_strengths_tab()
        self._build_supports_tab()
        self._build_history_tab()
        self._build_goals_tab()
        self._build_stakeholders_tab()

    # -- Strengths Tab --
    def _build_strengths_tab(self):
        c = get_colors()
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(8)

        self._strengths_list = QListWidget()
        self._strengths_list.setAccessibleName("Strengths list")
        layout.addWidget(self._strengths_list, stretch=1)

        add_row = QHBoxLayout()
        self._strength_input = QLineEdit()
        self._strength_input.setPlaceholderText("Add a strength...")
        self._strength_input.setAccessibleName("New strength")
        self._strength_input.setFixedHeight(40)
        add_row.addWidget(self._strength_input, stretch=1)

        add_btn = QPushButton("Add")
        add_btn.setAccessibleName("Add strength")
        add_btn.setFixedHeight(40)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['primary']}; color: white;
                border: none; border-radius: 8px; padding: 0 16px;
            }}
        """)
        add_btn.clicked.connect(self._add_strength)
        add_row.addWidget(add_btn)

        rm_btn = QPushButton("Remove Selected")
        rm_btn.setAccessibleName("Remove selected strength")
        rm_btn.setFixedHeight(40)
        rm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rm_btn.clicked.connect(self._remove_strength)
        add_row.addWidget(rm_btn)

        layout.addLayout(add_row)
        self._tabs.addTab(w, "Strengths")

    def _add_strength(self):
        text = self._strength_input.text().strip()
        if not text or not self._profile:
            return
        items = self._profile.strengths
        items.append(text)
        self._save_json_field("strengths", items)
        self._strength_input.clear()
        self._refresh_strengths()

    def _remove_strength(self):
        row = self._strengths_list.currentRow()
        if row < 0 or not self._profile:
            return
        items = self._profile.strengths
        if row < len(items):
            items.pop(row)
            self._save_json_field("strengths", items)
            self._refresh_strengths()

    def _refresh_strengths(self):
        self._strengths_list.clear()
        if self._profile:
            for s in self._profile.strengths:
                self._strengths_list.addItem(QListWidgetItem(s))

    # -- Supports Tab --
    def _build_supports_tab(self):
        c = get_colors()
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(8)

        # Filter row
        filter_row = QHBoxLayout()
        self._filter_combo = QComboBox()
        self._filter_combo.setAccessibleName("Filter supports by category")
        self._filter_combo.addItem("All Categories", "all")
        for cat in ["Technology", "Physical", "Sensory", "Communication",
                     "Social", "Academic", "Behavioral", "Other"]:
            self._filter_combo.addItem(cat, cat.lower())
        self._filter_combo.currentIndexChanged.connect(self._refresh_supports)
        filter_row.addWidget(QLabel("Filter:"))
        filter_row.addWidget(self._filter_combo)
        filter_row.addStretch()
        layout.addLayout(filter_row)

        # Supports grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self._supports_container = QWidget()
        self._supports_grid = QGridLayout(self._supports_container)
        self._supports_grid.setSpacing(10)
        self._supports_grid.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self._supports_container)
        layout.addWidget(scroll, stretch=1)

        # Add support form
        form_label = QLabel("Add New Support")
        form_label.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {c['text']};")
        layout.addWidget(form_label)

        form = QFormLayout()
        self._sup_cat = QComboBox()
        self._sup_cat.setAccessibleName("Support category")
        for cat in ["Technology", "Physical", "Sensory", "Communication",
                     "Social", "Academic", "Behavioral", "Other"]:
            self._sup_cat.addItem(cat, cat.lower())
        form.addRow("Category:", self._sup_cat)

        self._sup_desc = QLineEdit()
        self._sup_desc.setPlaceholderText("Describe the support...")
        self._sup_desc.setAccessibleName("Support description")
        self._sup_desc.setFixedHeight(40)
        form.addRow("Description:", self._sup_desc)

        self._sup_udl = QLineEdit()
        self._sup_udl.setPlaceholderText("e.g. Engagement, Representation (comma-sep)")
        self._sup_udl.setAccessibleName("UDL mapping tags")
        self._sup_udl.setFixedHeight(40)
        form.addRow("UDL Tags:", self._sup_udl)

        self._sup_pour = QLineEdit()
        self._sup_pour.setPlaceholderText("e.g. Perceivable, Operable (comma-sep)")
        self._sup_pour.setAccessibleName("POUR mapping tags")
        self._sup_pour.setFixedHeight(40)
        form.addRow("POUR Tags:", self._sup_pour)

        layout.addLayout(form)

        add_sup_btn = QPushButton("Add Support")
        add_sup_btn.setAccessibleName("Add support entry")
        add_sup_btn.setFixedHeight(44)
        add_sup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_sup_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['primary']}; color: white;
                border: none; border-radius: 8px; padding: 0 20px;
                font-weight: bold;
            }}
        """)
        add_sup_btn.clicked.connect(self._add_support)
        layout.addWidget(add_sup_btn)

        self._tabs.addTab(w, "Supports")

    def _add_support(self):
        if not self._profile:
            return
        desc = self._sup_desc.text().strip()
        if not desc:
            QMessageBox.warning(self, "Missing Info", "Please enter a description.")
            return

        cat = self._sup_cat.currentData()
        udl_tags = [t.strip() for t in self._sup_udl.text().split(",") if t.strip()]
        pour_tags = [t.strip() for t in self._sup_pour.text().split(",") if t.strip()]

        udl_dict = {t: True for t in udl_tags}
        pour_dict = {t: True for t in pour_tags}

        session = self.db.get_session()
        try:
            entry = SupportEntry(
                profile_id=self._profile.id,
                category=cat,
                description=desc,
                udl_mapping=json.dumps(udl_dict),
                pour_mapping=json.dumps(pour_dict),
                status="active",
            )
            session.add(entry)
            session.commit()
        finally:
            session.close()

        self._sup_desc.clear()
        self._sup_udl.clear()
        self._sup_pour.clear()
        self._refresh_supports()

    def _refresh_supports(self):
        # Clear grid
        while self._supports_grid.count():
            item = self._supports_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._profile:
            return

        session = self.db.get_session()
        try:
            q = session.query(SupportEntry).filter(
                SupportEntry.profile_id == self._profile.id
            )
            cat_filter = self._filter_combo.currentData()
            if cat_filter and cat_filter != "all":
                q = q.filter(SupportEntry.category == cat_filter)

            supports = q.order_by(SupportEntry.created_at.desc()).all()
            for i, s in enumerate(supports):
                card = SupportCard(s)
                self._supports_grid.addWidget(card, i // 2, i % 2)
        finally:
            session.close()

    # -- History Tab --
    def _build_history_tab(self):
        c = get_colors()
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(8)

        self._history_list = QListWidget()
        self._history_list.setAccessibleName("History list")
        layout.addWidget(self._history_list, stretch=1)

        add_row = QHBoxLayout()
        self._history_input = QLineEdit()
        self._history_input.setPlaceholderText("Add a history entry...")
        self._history_input.setAccessibleName("New history entry")
        self._history_input.setFixedHeight(40)
        add_row.addWidget(self._history_input, stretch=1)

        add_btn = QPushButton("Add")
        add_btn.setAccessibleName("Add history entry")
        add_btn.setFixedHeight(40)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['primary']}; color: white;
                border: none; border-radius: 8px; padding: 0 16px;
            }}
        """)
        add_btn.clicked.connect(self._add_history)
        add_row.addWidget(add_btn)

        rm_btn = QPushButton("Remove Selected")
        rm_btn.setAccessibleName("Remove selected history entry")
        rm_btn.setFixedHeight(40)
        rm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rm_btn.clicked.connect(self._remove_history)
        add_row.addWidget(rm_btn)

        layout.addLayout(add_row)
        self._tabs.addTab(w, "History")

    def _add_history(self):
        text = self._history_input.text().strip()
        if not text or not self._profile:
            return
        items = self._profile.history
        items.append(text)
        self._save_json_field("history", items)
        self._history_input.clear()
        self._refresh_history()

    def _remove_history(self):
        row = self._history_list.currentRow()
        if row < 0 or not self._profile:
            return
        items = self._profile.history
        if row < len(items):
            items.pop(row)
            self._save_json_field("history", items)
            self._refresh_history()

    def _refresh_history(self):
        self._history_list.clear()
        if self._profile:
            for h in self._profile.history:
                self._history_list.addItem(QListWidgetItem(h))

    # -- Goals Tab --
    def _build_goals_tab(self):
        c = get_colors()
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(8)

        self._goals_list = QListWidget()
        self._goals_list.setAccessibleName("Goals list")
        layout.addWidget(self._goals_list, stretch=1)

        add_row = QHBoxLayout()
        self._goal_input = QLineEdit()
        self._goal_input.setPlaceholderText("Add a goal or hope...")
        self._goal_input.setAccessibleName("New goal")
        self._goal_input.setFixedHeight(40)
        add_row.addWidget(self._goal_input, stretch=1)

        add_btn = QPushButton("Add")
        add_btn.setAccessibleName("Add goal")
        add_btn.setFixedHeight(40)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['primary']}; color: white;
                border: none; border-radius: 8px; padding: 0 16px;
            }}
        """)
        add_btn.clicked.connect(self._add_goal)
        add_row.addWidget(add_btn)

        rm_btn = QPushButton("Remove Selected")
        rm_btn.setAccessibleName("Remove selected goal")
        rm_btn.setFixedHeight(40)
        rm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rm_btn.clicked.connect(self._remove_goal)
        add_row.addWidget(rm_btn)

        layout.addLayout(add_row)
        self._tabs.addTab(w, "Goals")

    def _add_goal(self):
        text = self._goal_input.text().strip()
        if not text or not self._profile:
            return
        items = self._profile.hopes
        items.append(text)
        self._save_json_field("hopes", items)
        self._goal_input.clear()
        self._refresh_goals()

    def _remove_goal(self):
        row = self._goals_list.currentRow()
        if row < 0 or not self._profile:
            return
        items = self._profile.hopes
        if row < len(items):
            items.pop(row)
            self._save_json_field("hopes", items)
            self._refresh_goals()

    def _refresh_goals(self):
        self._goals_list.clear()
        if self._profile:
            for g in self._profile.hopes:
                self._goals_list.addItem(QListWidgetItem(g))

    # -- Stakeholders Tab --
    def _build_stakeholders_tab(self):
        c = get_colors()
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(8)

        self._stakeholders_list = QListWidget()
        self._stakeholders_list.setAccessibleName("Stakeholders list")
        layout.addWidget(self._stakeholders_list, stretch=1)

        add_row = QHBoxLayout()
        self._stakeholder_input = QLineEdit()
        self._stakeholder_input.setPlaceholderText("Add a stakeholder (name - role)...")
        self._stakeholder_input.setAccessibleName("New stakeholder")
        self._stakeholder_input.setFixedHeight(40)
        add_row.addWidget(self._stakeholder_input, stretch=1)

        add_btn = QPushButton("Add")
        add_btn.setAccessibleName("Add stakeholder")
        add_btn.setFixedHeight(40)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['primary']}; color: white;
                border: none; border-radius: 8px; padding: 0 16px;
            }}
        """)
        add_btn.clicked.connect(self._add_stakeholder)
        add_row.addWidget(add_btn)

        rm_btn = QPushButton("Remove Selected")
        rm_btn.setAccessibleName("Remove selected stakeholder")
        rm_btn.setFixedHeight(40)
        rm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rm_btn.clicked.connect(self._remove_stakeholder)
        add_row.addWidget(rm_btn)

        layout.addLayout(add_row)
        self._tabs.addTab(w, "Stakeholders")

    def _add_stakeholder(self):
        text = self._stakeholder_input.text().strip()
        if not text or not self._profile:
            return
        items = self._profile.stakeholders
        items.append(text)
        self._save_json_field("stakeholders", items)
        self._stakeholder_input.clear()
        self._refresh_stakeholders()

    def _remove_stakeholder(self):
        row = self._stakeholders_list.currentRow()
        if row < 0 or not self._profile:
            return
        items = self._profile.stakeholders
        if row < len(items):
            items.pop(row)
            self._save_json_field("stakeholders", items)
            self._refresh_stakeholders()

    def _refresh_stakeholders(self):
        self._stakeholders_list.clear()
        if self._profile:
            for s in self._profile.stakeholders:
                self._stakeholders_list.addItem(QListWidgetItem(s))

    # -- Shared helpers --

    def _save_json_field(self, field: str, value: list):
        session = self.db.get_session()
        try:
            profile = session.query(StudentProfile).get(self._profile.id)
            setattr(profile, field, value)
            session.commit()
            # Refresh local reference
            self._profile = profile
        finally:
            session.close()

    def _create_profile(self):
        name = self._name_input.text().strip()
        user = self.auth.get_current_user()
        if not name or not user:
            QMessageBox.warning(self, "Missing Info", "Please enter a name.")
            return

        session = self.db.get_session()
        try:
            profile = StudentProfile(user_id=user.id, name=name)
            session.add(profile)
            session.commit()
            session.refresh(profile)
            self._profile = profile
        finally:
            session.close()

        self._create_section.setVisible(False)
        self._tabs.setVisible(True)
        self.refresh_data()

    def refresh_data(self):
        user = self.auth.get_current_user()
        if not user:
            return

        session = self.db.get_session()
        try:
            self._profile = session.query(StudentProfile).filter(
                StudentProfile.user_id == user.id
            ).first()
        finally:
            session.close()

        if self._profile:
            self._create_section.setVisible(False)
            self._tabs.setVisible(True)
            self._refresh_strengths()
            self._refresh_supports()
            self._refresh_history()
            self._refresh_goals()
            self._refresh_stakeholders()
        else:
            self._create_section.setVisible(True)
            self._tabs.setVisible(False)

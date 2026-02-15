"""Student profile page — 5-tab view for managing accessibility profile."""

import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QScrollArea, QFormLayout, QLineEdit, QTextEdit,
    QComboBox, QMessageBox, QGridLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal

from config.settings import get_colors
from models.student_profile import StudentProfile
from models.support import SupportEntry
from ui.components.support_card import SupportCard
from ui.components.empty_state import EmptyState
from ui.components.profile_item_card import ProfileItemCard
from ui.components.edit_item_dialog import EditItemDialog
from ui.components.mic_button import MicButton

PRIORITY_CHOICES = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("non-negotiable", "Non-Negotiable"),
]


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

    # ------------------------------------------------------------------
    # Generic card-tab builder
    # ------------------------------------------------------------------

    def _build_card_tab(self, tab_name, input_placeholder, input_accessible,
                        add_accessible, add_callback):
        """Build a tab with a scrollable card area and an add-item form.

        Returns ``(scroll_layout, line_edit, priority_combo)`` so each tab
        can store references for its own add / refresh logic.
        """
        c = get_colors()
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(8)

        # Scrollable card area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        container = QWidget()
        card_layout = QVBoxLayout(container)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(6)
        card_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll, stretch=1)

        # Add-item form row
        add_row = QHBoxLayout()

        line_edit = QLineEdit()
        line_edit.setPlaceholderText(input_placeholder)
        line_edit.setAccessibleName(input_accessible)
        line_edit.setFixedHeight(40)
        add_row.addWidget(line_edit, stretch=1)
        add_row.addWidget(MicButton(target=line_edit))

        priority_combo = QComboBox()
        priority_combo.setAccessibleName("Priority level")
        for value, display in PRIORITY_CHOICES:
            priority_combo.addItem(display, value)
        priority_combo.setCurrentIndex(1)  # default Medium
        priority_combo.setFixedHeight(40)
        add_row.addWidget(priority_combo)

        add_btn = QPushButton("Add")
        add_btn.setAccessibleName(add_accessible)
        add_btn.setFixedHeight(40)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['primary']}; color: white;
                border: none; border-radius: 8px; padding: 0 16px;
            }}
        """)
        add_btn.clicked.connect(add_callback)
        add_row.addWidget(add_btn)

        layout.addLayout(add_row)
        self._tabs.addTab(w, tab_name)
        return card_layout, line_edit, priority_combo

    def _populate_cards(self, card_layout, items, edit_callback, remove_callback):
        """Clear *card_layout* and add a ``ProfileItemCard`` for each item."""
        # Remove existing cards (but keep the trailing stretch)
        while card_layout.count() > 1:
            item = card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, entry in enumerate(items):
            card = ProfileItemCard(i, entry["text"], entry["priority"])
            card.edit_requested.connect(edit_callback)
            card.remove_requested.connect(remove_callback)
            card_layout.insertWidget(card_layout.count() - 1, card)

    # -- Strengths Tab --
    def _build_strengths_tab(self):
        self._strengths_card_layout, self._strength_input, self._strength_priority = \
            self._build_card_tab(
                "Strengths", "Add a strength...", "New strength",
                "Add strength", self._add_strength,
            )

    def _add_strength(self):
        text = self._strength_input.text().strip()
        if not text or not self._profile:
            return
        priority = self._strength_priority.currentData()
        items = self._profile.strengths
        items.append({"text": text, "priority": priority})
        self._save_json_field("strengths", items)
        self._strength_input.clear()
        self._refresh_strengths()

    def _edit_strength(self, index):
        if not self._profile:
            return
        items = self._profile.strengths_items
        if index >= len(items):
            return
        current = items[index]
        dlg = EditItemDialog(current["text"], current["priority"], self)
        if dlg.exec() == EditItemDialog.DialogCode.Accepted:
            result = dlg.get_result()
            if result:
                raw = self._profile.strengths
                raw[index] = {"text": result[0], "priority": result[1]}
                self._save_json_field("strengths", raw)
                self._refresh_strengths()

    def _remove_strength(self, index):
        if not self._profile:
            return
        items = self._profile.strengths
        if index < len(items):
            items.pop(index)
            self._save_json_field("strengths", items)
            self._refresh_strengths()

    def _refresh_strengths(self):
        if self._profile:
            self._populate_cards(
                self._strengths_card_layout,
                self._profile.strengths_items,
                self._edit_strength,
                self._remove_strength,
            )

    # -- Supports Tab (unchanged — uses SupportCard) --
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
        sup_desc_row = QHBoxLayout()
        sup_desc_row.addWidget(self._sup_desc, stretch=1)
        sup_desc_row.addWidget(MicButton(target=self._sup_desc))
        form.addRow("Description:", sup_desc_row)

        self._sup_udl = QLineEdit()
        self._sup_udl.setPlaceholderText("e.g. Engagement, Representation (comma-sep)")
        self._sup_udl.setAccessibleName("UDL mapping tags")
        self._sup_udl.setFixedHeight(40)
        sup_udl_row = QHBoxLayout()
        sup_udl_row.addWidget(self._sup_udl, stretch=1)
        sup_udl_row.addWidget(MicButton(target=self._sup_udl))
        form.addRow("UDL Tags:", sup_udl_row)

        self._sup_pour = QLineEdit()
        self._sup_pour.setPlaceholderText("e.g. Perceivable, Operable (comma-sep)")
        self._sup_pour.setAccessibleName("POUR mapping tags")
        self._sup_pour.setFixedHeight(40)
        sup_pour_row = QHBoxLayout()
        sup_pour_row.addWidget(self._sup_pour, stretch=1)
        sup_pour_row.addWidget(MicButton(target=self._sup_pour))
        form.addRow("POUR Tags:", sup_pour_row)

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
        self._history_card_layout, self._history_input, self._history_priority = \
            self._build_card_tab(
                "History", "Add a history entry...", "New history entry",
                "Add history entry", self._add_history,
            )

    def _add_history(self):
        text = self._history_input.text().strip()
        if not text or not self._profile:
            return
        priority = self._history_priority.currentData()
        items = self._profile.history
        items.append({"text": text, "priority": priority})
        self._save_json_field("history", items)
        self._history_input.clear()
        self._refresh_history()

    def _edit_history(self, index):
        if not self._profile:
            return
        items = self._profile.history_items
        if index >= len(items):
            return
        current = items[index]
        dlg = EditItemDialog(current["text"], current["priority"], self)
        if dlg.exec() == EditItemDialog.DialogCode.Accepted:
            result = dlg.get_result()
            if result:
                raw = self._profile.history
                raw[index] = {"text": result[0], "priority": result[1]}
                self._save_json_field("history", raw)
                self._refresh_history()

    def _remove_history(self, index):
        if not self._profile:
            return
        items = self._profile.history
        if index < len(items):
            items.pop(index)
            self._save_json_field("history", items)
            self._refresh_history()

    def _refresh_history(self):
        if self._profile:
            self._populate_cards(
                self._history_card_layout,
                self._profile.history_items,
                self._edit_history,
                self._remove_history,
            )

    # -- Goals Tab --
    def _build_goals_tab(self):
        self._goals_card_layout, self._goal_input, self._goal_priority = \
            self._build_card_tab(
                "Goals", "Add a goal or hope...", "New goal",
                "Add goal", self._add_goal,
            )

    def _add_goal(self):
        text = self._goal_input.text().strip()
        if not text or not self._profile:
            return
        priority = self._goal_priority.currentData()
        items = self._profile.hopes
        items.append({"text": text, "priority": priority})
        self._save_json_field("hopes", items)
        self._goal_input.clear()
        self._refresh_goals()

    def _edit_goal(self, index):
        if not self._profile:
            return
        items = self._profile.hopes_items
        if index >= len(items):
            return
        current = items[index]
        dlg = EditItemDialog(current["text"], current["priority"], self)
        if dlg.exec() == EditItemDialog.DialogCode.Accepted:
            result = dlg.get_result()
            if result:
                raw = self._profile.hopes
                raw[index] = {"text": result[0], "priority": result[1]}
                self._save_json_field("hopes", raw)
                self._refresh_goals()

    def _remove_goal(self, index):
        if not self._profile:
            return
        items = self._profile.hopes
        if index < len(items):
            items.pop(index)
            self._save_json_field("hopes", items)
            self._refresh_goals()

    def _refresh_goals(self):
        if self._profile:
            self._populate_cards(
                self._goals_card_layout,
                self._profile.hopes_items,
                self._edit_goal,
                self._remove_goal,
            )

    # -- Stakeholders Tab --
    def _build_stakeholders_tab(self):
        self._stakeholders_card_layout, self._stakeholder_input, self._stakeholder_priority = \
            self._build_card_tab(
                "Stakeholders", "Add a stakeholder (name - role)...",
                "New stakeholder", "Add stakeholder", self._add_stakeholder,
            )

    def _add_stakeholder(self):
        text = self._stakeholder_input.text().strip()
        if not text or not self._profile:
            return
        priority = self._stakeholder_priority.currentData()
        items = self._profile.stakeholders
        items.append({"text": text, "priority": priority})
        self._save_json_field("stakeholders", items)
        self._stakeholder_input.clear()
        self._refresh_stakeholders()

    def _edit_stakeholder(self, index):
        if not self._profile:
            return
        items = self._profile.stakeholders_items
        if index >= len(items):
            return
        current = items[index]
        dlg = EditItemDialog(current["text"], current["priority"], self)
        if dlg.exec() == EditItemDialog.DialogCode.Accepted:
            result = dlg.get_result()
            if result:
                raw = self._profile.stakeholders
                raw[index] = {"text": result[0], "priority": result[1]}
                self._save_json_field("stakeholders", raw)
                self._refresh_stakeholders()

    def _remove_stakeholder(self, index):
        if not self._profile:
            return
        items = self._profile.stakeholders
        if index < len(items):
            items.pop(index)
            self._save_json_field("stakeholders", items)
            self._refresh_stakeholders()

    def _refresh_stakeholders(self):
        if self._profile:
            self._populate_cards(
                self._stakeholders_card_layout,
                self._profile.stakeholders_items,
                self._edit_stakeholder,
                self._remove_stakeholder,
            )

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

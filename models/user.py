"""User account model."""

import json
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Text

from models.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    role = Column(String(20), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    settings_json = Column(Text, default="{}")
    security_question_1 = Column(String(255), nullable=True)
    security_answer_1 = Column(String(255), nullable=True)
    security_question_2 = Column(String(255), nullable=True)
    security_answer_2 = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    @property
    def settings(self) -> dict:
        return json.loads(self.settings_json or "{}")

    @settings.setter
    def settings(self, value: dict):
        self.settings_json = json.dumps(value)

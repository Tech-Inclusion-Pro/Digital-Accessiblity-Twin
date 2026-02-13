"""Student accessibility profile model."""

import json
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey

from models.database import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    strengths_json = Column(Text, default="[]")
    supports_json = Column(Text, default="[]")
    history_json = Column(Text, default="[]")
    hopes_json = Column(Text, default="[]")
    stakeholders_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    @property
    def strengths(self) -> list:
        return json.loads(self.strengths_json or "[]")

    @strengths.setter
    def strengths(self, value: list):
        self.strengths_json = json.dumps(value)

    @property
    def supports(self) -> list:
        return json.loads(self.supports_json or "[]")

    @supports.setter
    def supports(self, value: list):
        self.supports_json = json.dumps(value)

    @property
    def history(self) -> list:
        return json.loads(self.history_json or "[]")

    @history.setter
    def history(self, value: list):
        self.history_json = json.dumps(value)

    @property
    def hopes(self) -> list:
        return json.loads(self.hopes_json or "[]")

    @hopes.setter
    def hopes(self, value: list):
        self.hopes_json = json.dumps(value)

    @property
    def stakeholders(self) -> list:
        return json.loads(self.stakeholders_json or "[]")

    @stakeholders.setter
    def stakeholders(self, value: list):
        self.stakeholders_json = json.dumps(value)

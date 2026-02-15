"""Insight log model — persists AI-generated insight reports with timestamps."""

import json
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey

from models.database import Base


class InsightLog(Base):
    __tablename__ = "insight_logs"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Text, nullable=False)  # "student" or "teacher"
    content = Column(Text, nullable=False)
    conversation_json = Column(Text, nullable=True, default="[]")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def conversation(self) -> list:
        """Deserialise the stored JSON into a list of {role, content} dicts."""
        try:
            return json.loads(self.conversation_json) if self.conversation_json else []
        except (json.JSONDecodeError, TypeError):
            return []

    @conversation.setter
    def conversation(self, value: list):
        """Serialise a list of {role, content} dicts to JSON for storage."""
        self.conversation_json = json.dumps(value, ensure_ascii=False)

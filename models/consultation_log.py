"""Consultation log model — persists coach conversations per student + teacher."""

import json
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey

from models.database import Base


class ConsultationLog(Base):
    __tablename__ = "consultation_logs"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    teacher_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_json = Column(Text, nullable=False, default="[]")
    summary = Column(Text, nullable=True)
    message_count = Column(Integer, default=0)
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

"""Document upload model."""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Text, LargeBinary, ForeignKey

from models.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    teacher_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=True)
    file_blob = Column(LargeBinary, nullable=True)
    purpose_description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

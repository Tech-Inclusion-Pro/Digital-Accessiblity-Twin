"""Support entry model."""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey

from models.database import Base


class SupportEntry(Base):
    __tablename__ = "support_entries"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(50), nullable=True)
    description = Column(Text, nullable=False)
    udl_mapping = Column(Text, default="{}")
    pour_mapping = Column(Text, default="{}")
    status = Column(String(20), default="active")
    effectiveness_rating = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

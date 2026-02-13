"""Tracking / implementation log model."""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey

from models.database import Base


class TrackingLog(Base):
    __tablename__ = "tracking_logs"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    logged_by_role = Column(String(20), nullable=False)
    support_id = Column(Integer, ForeignKey("support_entries.id"), nullable=True)
    implementation_notes = Column(Text, nullable=True)
    outcome_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

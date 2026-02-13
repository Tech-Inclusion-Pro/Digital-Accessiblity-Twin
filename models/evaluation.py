"""Twin evaluation model."""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey

from models.database import Base


class TwinEvaluation(Base):
    __tablename__ = "twin_evaluations"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    ai_analysis_json = Column(Text, default="{}")
    suggestions_json = Column(Text, default="[]")
    confidence_scores = Column(Text, default="{}")
    reasoning_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

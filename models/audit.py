"""Audit log and consent record models."""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean

from models.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False)
    detail = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ConsentRecord(Base):
    __tablename__ = "consent_records"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    consent_type = Column(String(100), nullable=False)
    granted = Column(Boolean, default=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

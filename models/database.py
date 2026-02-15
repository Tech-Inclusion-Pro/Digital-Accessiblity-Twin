"""Database setup and session management."""

import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


def get_data_directory() -> Path:
    """Get the application data directory."""
    if sys.platform == "darwin":
        app_support = Path.home() / "Library" / "Application Support" / "AccessTwin"
    else:
        app_support = Path.home() / ".accesstwin"
    app_support.mkdir(parents=True, exist_ok=True)
    return app_support


class DatabaseManager:
    """Database connection and session management."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            data_dir = get_data_directory()
            self.db_path = data_dir / "accesstwin.db"
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)

        # Import all models so metadata is populated before create_all
        from models.user import User  # noqa: F401
        from models.student_profile import StudentProfile  # noqa: F401
        from models.support import SupportEntry  # noqa: F401
        from models.document import Document  # noqa: F401
        from models.evaluation import TwinEvaluation  # noqa: F401
        from models.tracking import TrackingLog  # noqa: F401
        from models.audit import AuditLog, ConsentRecord  # noqa: F401
        from models.consultation_log import ConsultationLog  # noqa: F401
        from models.insight_log import InsightLog  # noqa: F401

        Base.metadata.create_all(self.engine)

        # Ensure conversation_json column exists on insight_logs
        # (added after initial table creation)
        from sqlalchemy import inspect as sa_inspect, text
        inspector = sa_inspect(self.engine)
        if "insight_logs" in inspector.get_table_names():
            columns = [col["name"] for col in inspector.get_columns("insight_logs")]
            if "conversation_json" not in columns:
                with self.engine.connect() as conn:
                    conn.execute(text(
                        "ALTER TABLE insight_logs "
                        "ADD COLUMN conversation_json TEXT DEFAULT '[]'"
                    ))
                    conn.commit()

        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

    def get_session(self):
        """Return a new database session."""
        return self.SessionLocal()

"""Shared test fixtures."""

import sys
import os

import pytest

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def tmp_db(tmp_path):
    """Return a DatabaseManager backed by a temp file."""
    db_path = str(tmp_path / "test.db")
    from models.database import DatabaseManager
    return DatabaseManager(db_path=db_path)


@pytest.fixture
def auth_manager(tmp_db):
    """Return an AuthManager using a temp database."""
    from models.auth import AuthManager
    return AuthManager(tmp_db)

"""Database layer tests."""

import pytest
from models.user import User
from models.student_profile import StudentProfile
from models.support import SupportEntry


class TestDatabaseCreation:
    def test_tables_created(self, tmp_db):
        from sqlalchemy import inspect
        inspector = inspect(tmp_db.engine)
        names = inspector.get_table_names()
        assert "users" in names
        assert "student_profiles" in names
        assert "support_entries" in names
        assert "documents" in names
        assert "twin_evaluations" in names
        assert "tracking_logs" in names
        assert "audit_logs" in names
        assert "consent_records" in names


class TestUserCRUD:
    def test_create_and_read_user(self, tmp_db):
        session = tmp_db.get_session()
        try:
            user = User(
                username="testuser",
                password_hash="fakehash",
                role="student",
                display_name="Test User",
            )
            session.add(user)
            session.commit()
            session.refresh(user)

            assert user.id is not None
            fetched = session.query(User).filter(User.username == "testuser").first()
            assert fetched is not None
            assert fetched.role == "student"
        finally:
            session.close()

    def test_user_settings_json(self, tmp_db):
        session = tmp_db.get_session()
        try:
            user = User(username="u2", password_hash="h", role="teacher")
            user.settings = {"theme": "dark", "font_size": 18}
            session.add(user)
            session.commit()
            session.refresh(user)

            assert user.settings["theme"] == "dark"
        finally:
            session.close()


class TestStudentProfile:
    def test_create_profile(self, tmp_db):
        session = tmp_db.get_session()
        try:
            user = User(username="student1", password_hash="h", role="student")
            session.add(user)
            session.commit()
            session.refresh(user)

            profile = StudentProfile(
                user_id=user.id,
                name="Student One",
            )
            profile.strengths = ["reading", "math"]
            session.add(profile)
            session.commit()
            session.refresh(profile)

            assert profile.strengths == ["reading", "math"]
        finally:
            session.close()


class TestEncryption:
    def test_encrypt_decrypt_roundtrip(self):
        from utils.encryption import EncryptionManager
        em = EncryptionManager()
        plaintext = "Sensitive student data: IEP details"
        ciphertext = em.encrypt(plaintext)
        assert ciphertext != plaintext
        assert em.decrypt(ciphertext) == plaintext

    def test_different_ciphertexts(self):
        from utils.encryption import EncryptionManager
        em = EncryptionManager()
        ct1 = em.encrypt("hello")
        ct2 = em.encrypt("hello")
        # Fernet uses random IV, so ciphertexts differ
        assert ct1 != ct2

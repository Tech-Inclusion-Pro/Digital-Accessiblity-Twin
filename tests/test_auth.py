"""Authentication tests."""

import pytest


class TestRegistration:
    def test_register_student(self, auth_manager):
        ok, msg = auth_manager.register(
            "alice", "password123", "student",
            security_question_1="Favorite color?",
            security_answer_1="blue",
        )
        assert ok, msg
        assert auth_manager.current_user is not None
        assert auth_manager.current_user.role == "student"

    def test_register_teacher(self, auth_manager):
        ok, msg = auth_manager.register(
            "teacher1", "password123", "teacher",
            security_question_1="Pet name?",
            security_answer_1="rex",
        )
        assert ok, msg
        assert auth_manager.current_user.role == "teacher"

    def test_register_duplicate(self, auth_manager):
        auth_manager.register("dup", "password123", "student",
                              security_question_1="Q?", security_answer_1="a")
        ok, msg = auth_manager.register("dup", "password456", "student",
                                        security_question_1="Q?", security_answer_1="b")
        assert not ok
        assert "already exists" in msg

    def test_register_short_password(self, auth_manager):
        ok, msg = auth_manager.register("user2", "short", "student",
                                        security_question_1="Q?", security_answer_1="a")
        assert not ok
        assert "8 characters" in msg

    def test_register_short_username(self, auth_manager):
        ok, msg = auth_manager.register("ab", "password123", "student",
                                        security_question_1="Q?", security_answer_1="a")
        assert not ok
        assert "3 characters" in msg

    def test_register_invalid_role(self, auth_manager):
        ok, msg = auth_manager.register("user3", "password123", "admin",
                                        security_question_1="Q?", security_answer_1="a")
        assert not ok
        assert "Invalid role" in msg


class TestLogin:
    def test_login_success(self, auth_manager):
        auth_manager.register("bob", "mypassword", "student",
                              security_question_1="Q?", security_answer_1="a")
        auth_manager.logout()

        ok, msg = auth_manager.login("bob", "mypassword", expected_role="student")
        assert ok, msg

    def test_login_wrong_password(self, auth_manager):
        auth_manager.register("carol", "correct_pw", "teacher",
                              security_question_1="Q?", security_answer_1="a")
        auth_manager.logout()

        ok, msg = auth_manager.login("carol", "wrong_pw", expected_role="teacher")
        assert not ok
        assert "Incorrect password" in msg

    def test_login_wrong_role(self, auth_manager):
        auth_manager.register("dave", "password123", "student",
                              security_question_1="Q?", security_answer_1="a")
        auth_manager.logout()

        ok, msg = auth_manager.login("dave", "password123", expected_role="teacher")
        assert not ok
        assert "registered as a student" in msg
        assert "Student Login" in msg

    def test_login_nonexistent(self, auth_manager):
        ok, msg = auth_manager.login("nobody", "pass", expected_role="student")
        assert not ok
        assert "No account found" in msg


class TestPasswordRecovery:
    def test_security_questions(self, auth_manager):
        auth_manager.register("eve", "password123", "student",
                              security_question_1="Color?", security_answer_1="red")
        ok, msg, q1, q2 = auth_manager.get_security_questions("eve")
        assert ok
        assert q1 == "Color?"

    def test_verify_answers(self, auth_manager):
        auth_manager.register("frank", "password123", "student",
                              security_question_1="City?", security_answer_1="Boston")
        ok, msg = auth_manager.verify_security_answers("frank", "boston")
        assert ok  # case-insensitive

    def test_reset_password(self, auth_manager):
        auth_manager.register("grace", "oldpass123", "teacher",
                              security_question_1="Q?", security_answer_1="a")
        auth_manager.logout()

        ok, msg = auth_manager.reset_password("grace", "newpass123")
        assert ok

        ok, msg = auth_manager.login("grace", "newpass123", expected_role="teacher")
        assert ok


class TestPasswordHashing:
    def test_hash_differs(self, auth_manager):
        h1 = auth_manager.hash_password("same")
        h2 = auth_manager.hash_password("same")
        assert h1 != h2  # different salts

    def test_verify(self, auth_manager):
        h = auth_manager.hash_password("test123")
        assert auth_manager.verify_password("test123", h)
        assert not auth_manager.verify_password("wrong", h)

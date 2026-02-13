"""Role-based authentication manager."""

from datetime import datetime, timezone

import bcrypt

from models.database import DatabaseManager
from models.user import User
from models.audit import AuditLog


class AuthManager:
    """Handle user authentication with role enforcement."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.current_user: User = None

    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    def register(self, username: str, password: str, role: str,
                 display_name: str = None, email: str = None,
                 security_question_1: str = None, security_answer_1: str = None,
                 security_question_2: str = None, security_answer_2: str = None) -> tuple:
        """Register a new user with a specified role."""
        from utils.validators import validate_username, validate_password

        ok, msg = validate_username(username)
        if not ok:
            return False, msg

        ok, msg = validate_password(password)
        if not ok:
            return False, msg

        if not security_question_1 or not security_answer_1:
            return False, "Security question is required"

        if role not in ("student", "teacher"):
            return False, "Invalid role"

        session = self.db.get_session()
        try:
            existing = session.query(User).filter(User.username == username).first()
            if existing:
                return False, "An account with this username already exists"

            user = User(
                username=username,
                password_hash=self.hash_password(password),
                role=role,
                display_name=display_name or username,
                email=email,
                security_question_1=security_question_1,
                security_answer_1=security_answer_1.lower().strip() if security_answer_1 else None,
                security_question_2=security_question_2,
                security_answer_2=security_answer_2.lower().strip() if security_answer_2 else None,
            )
            session.add(user)
            session.flush()

            session.add(AuditLog(
                user_id=user.id,
                action="register",
                detail=f"New {role} account created",
            ))
            session.commit()
            session.refresh(user)

            self.current_user = user
            return True, "Account created successfully"
        except Exception as e:
            session.rollback()
            return False, f"Registration failed: {e}"
        finally:
            session.close()

    def login(self, username: str, password: str, expected_role: str = None) -> tuple:
        """Log in an existing user. If expected_role is set, enforce tab match."""
        if not username or not password:
            return False, "Username and password are required"

        session = self.db.get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if not user:
                return False, "No account found with this username"

            if expected_role and user.role != expected_role:
                return False, (
                    f"This account is registered as a {user.role}. "
                    f"Please use the {user.role.title()} Login tab."
                )

            if not self.verify_password(password, user.password_hash):
                session.add(AuditLog(user_id=user.id, action="login_failed"))
                session.commit()
                return False, "Incorrect password"

            session.add(AuditLog(user_id=user.id, action="login_success"))
            session.commit()

            self.current_user = user
            return True, "Login successful"
        finally:
            session.close()

    def logout(self):
        if self.current_user:
            session = self.db.get_session()
            try:
                session.add(AuditLog(
                    user_id=self.current_user.id,
                    action="logout",
                ))
                session.commit()
            finally:
                session.close()
        self.current_user = None

    def is_authenticated(self) -> bool:
        return self.current_user is not None

    def get_current_user(self) -> User:
        return self.current_user

    # -- password recovery --

    def get_security_questions(self, username: str) -> tuple:
        session = self.db.get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if not user:
                return False, "No account found with this username", None, None
            if not user.security_question_1:
                return False, "No security questions set for this account", None, None
            return True, "Questions found", user.security_question_1, user.security_question_2
        finally:
            session.close()

    def verify_security_answers(self, username: str, answer_1: str, answer_2: str = None) -> tuple:
        session = self.db.get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if not user:
                return False, "No account found with this username"
            if not user.security_answer_1:
                return False, "No security answers set"
            if answer_1.lower().strip() != user.security_answer_1.lower().strip():
                return False, "Security answer does not match"
            if user.security_question_2 and user.security_answer_2:
                if not answer_2 or answer_2.lower().strip() != user.security_answer_2.lower().strip():
                    return False, "Security answers do not match"
            return True, "Answers verified"
        finally:
            session.close()

    def reset_password(self, username: str, new_password: str) -> tuple:
        from utils.validators import validate_password
        ok, msg = validate_password(new_password)
        if not ok:
            return False, msg

        session = self.db.get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if not user:
                return False, "No account found with this username"
            user.password_hash = self.hash_password(new_password)
            session.add(AuditLog(user_id=user.id, action="password_reset"))
            session.commit()
            return True, "Password reset successfully"
        except Exception as e:
            session.rollback()
            return False, f"Password reset failed: {e}"
        finally:
            session.close()

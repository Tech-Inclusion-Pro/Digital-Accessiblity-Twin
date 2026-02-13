"""Input validators for registration / forms."""

import re


def validate_username(username: str) -> tuple:
    if not username:
        return False, "Username is required"
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(username) > 50:
        return False, "Username must be 50 characters or fewer"
    if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
        return False, "Username may only contain letters, numbers, dots, hyphens, and underscores"
    return True, ""


def validate_password(password: str) -> tuple:
    if not password:
        return False, "Password is required"
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    return True, ""


def validate_email(email: str) -> tuple:
    if not email:
        return True, ""  # email is optional
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Please enter a valid email address"
    return True, ""

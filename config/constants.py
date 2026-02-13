"""Application-wide enums and constants."""

from enum import Enum


class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"


class SupportCategory(str, Enum):
    SENSORY = "sensory"
    MOTOR = "motor"
    COGNITIVE = "cognitive"
    COMMUNICATION = "communication"
    SOCIAL_EMOTIONAL = "social_emotional"
    EXECUTIVE_FUNCTION = "executive_function"
    ENVIRONMENTAL = "environmental"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SupportStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


SECURITY_QUESTIONS = [
    "What was the name of your first pet?",
    "What city were you born in?",
    "What is your mother's maiden name?",
    "What was the name of your elementary school?",
    "What is your favorite book?",
    "What was the make of your first car?",
    "What is your favorite movie?",
    "What street did you grow up on?",
]

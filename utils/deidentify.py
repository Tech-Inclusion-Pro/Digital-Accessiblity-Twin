"""Rule-based de-identification for student-shared overviews.

Scrubs direct identifiers (names, emails, phones, schools) from free text
before it leaves the student's machine. This is deliberately conservative:
it can over-redact, and the student always reviews the result before sharing.
"""

import re
import secrets
from datetime import datetime


# Role words that appear in stakeholder entries but are not names.
_ROLE_STOPWORDS = {
    "mom", "mother", "dad", "father", "parent", "parents", "guardian",
    "brother", "sister", "sibling", "aunt", "uncle", "cousin",
    "grandma", "grandpa", "grandmother", "grandfather",
    "teacher", "tutor", "aide", "paraprofessional", "para", "coach",
    "counselor", "counsellor", "therapist", "psychologist", "nurse",
    "case", "manager", "advocate", "specialist", "coordinator",
    "principal", "student", "friend", "doctor", "and", "the", "my",
    "her", "his", "their", "our",
}

_HONORIFICS = r"(?:Mr|Mrs|Ms|Miss|Mx|Dr|Prof|Professor|Coach|Nurse|Principal)"

_RELATIONS = (
    r"(?:mom|mother|dad|father|brother|sister|aunt|uncle|cousin|"
    r"grandma|grandpa|grandmother|grandfather|guardian|friend)"
)

_SCHOOL_SUFFIXES = (
    r"(?:Elementary|Middle|High)\s+School|School|Academy|University|College|Institute"
)


def generate_alias() -> str:
    """Generate a short shareable alias like 'Student K4'."""
    letter = secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ")
    digit = secrets.choice("23456789")
    return f"Student {letter}{digit}"


def collect_known_names(profile) -> set:
    """Gather name tokens from the profile's own name and stakeholder entries.

    Returns lowercase tokens at least 3 chars long, minus role stopwords.
    """
    tokens = set()

    def add_tokens(text):
        for tok in re.findall(r"[A-Za-z][A-Za-z'\-]+", text or ""):
            low = tok.lower()
            if len(low) >= 3 and low not in _ROLE_STOPWORDS:
                tokens.add(low)

    add_tokens(getattr(profile, "name", "") or "")

    for item in (getattr(profile, "stakeholders", None) or []):
        text = item.get("text", "") if isinstance(item, dict) else str(item)
        # Only capitalized words in stakeholder text are name candidates;
        # lowercase words there are role descriptions ("my mom", "case manager").
        for tok in re.findall(r"\b[A-Z][A-Za-z'\-]{2,}\b", text):
            low = tok.lower()
            if low not in _ROLE_STOPWORDS:
                tokens.add(low)

    return tokens


def scrub_text(text: str, known_names: set = None) -> tuple:
    """Redact direct identifiers from *text*.

    Returns (scrubbed_text, redactions) where redactions is a list of
    (label, original) tuples describing what was removed.
    """
    if not text:
        return text, []

    known_names = known_names or set()
    redactions = []

    def record(label):
        def _sub(match):
            redactions.append((label, match.group(0)))
            return f"[{label}]"
        return _sub

    # Emails and phone numbers first (before name rules touch their innards).
    text = re.sub(
        r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}",
        record("email removed"), text,
    )
    text = re.sub(
        r"(?<!\d)(?:\+?1[\s.\-]?)?(?:\(\d{3}\)|\d{3})[\s.\-]\d{3}[\s.\-]\d{4}(?!\d)",
        record("phone removed"), text,
    )

    # Named schools: "Lincoln Park High School", "Roosevelt Academy".
    text = re.sub(
        rf"\b(?:[A-Z][A-Za-z'\-]+\s+){{1,3}}(?:{_SCHOOL_SUFFIXES})\b",
        record("school removed"), text,
    )

    # Honorific + capitalized name(s): "Ms. Rivera", "Dr. Chen-Park".
    text = re.sub(
        rf"\b{_HONORIFICS}\.?\s+[A-Z][A-Za-z'\-]+(?:\s+[A-Z][A-Za-z'\-]+)?",
        record("staff name removed"), text,
    )

    # Relation + capitalized name: "my mom Karen", "brother Luis".
    def _relation_sub(match):
        redactions.append(("family name removed", match.group(2)))
        return f"{match.group(1)} [name removed]"

    text = re.sub(
        rf"\b((?:my|our|his|her|their)?\s*{_RELATIONS})\s+([A-Z][A-Za-z'\-]+)",
        _relation_sub, text, flags=re.IGNORECASE,
    )

    # Known names from the profile (any casing, including possessives).
    for name in sorted(known_names, key=len, reverse=True):
        text = re.sub(
            rf"\b{re.escape(name)}(?:['’]s)?\b",
            record("name removed"), text, flags=re.IGNORECASE,
        )

    return text, redactions


def coarsen_date(value) -> str:
    """Reduce a datetime or ISO string to season + year (e.g. 'Summer 2026')."""
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return ""
    month = value.month
    if month in (12, 1, 2):
        season = "Winter"
    elif month in (3, 4, 5):
        season = "Spring"
    elif month in (6, 7, 8):
        season = "Summer"
    else:
        season = "Fall"
    return f"{season} {value.year}"

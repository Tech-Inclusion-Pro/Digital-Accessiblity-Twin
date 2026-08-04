"""Build and parse de-identified 'Share Overview' Markdown files.

The overview is the student-controlled, teacher-safe export: it contains
generalized themes and scrubbed support/outcome data, and deliberately
excludes the student's name, history, stakeholders, and AI chat logs.
"""

import re
from datetime import datetime, timezone

from ai.privacy_aggregator import (
    PrivacyAggregator,
    _extract_text,
    _generalise,
    _STRENGTH_THEME_MAP,
    _GOAL_THEME_MAP,
)
from utils.deidentify import collect_known_names, scrub_text, coarsen_date

OVERVIEW_VERSION = 1
_MAX_OUTCOMES = 10


def build_overview_markdown(profile, supports, tracking_logs=None, alias="Student"):
    """Return (markdown, redactions) for a de-identified overview.

    Redactions is a list of (label, original) tuples for the review UI.
    """
    tracking_logs = tracking_logs or []
    known_names = collect_known_names(profile)
    redactions = []

    def scrub(text):
        cleaned, r = scrub_text(text, known_names)
        redactions.extend(r)
        return cleaned

    agg = PrivacyAggregator.aggregate(profile, supports, tracking_logs)
    safe = agg["teacher_safe"]

    # Theme generalization can fall back to raw leading words — scrub those too.
    strength_themes = sorted({
        scrub(_generalise(_extract_text(s), _STRENGTH_THEME_MAP))
        for s in (profile.strengths or [])
    })
    goal_themes = sorted({
        scrub(_generalise(_extract_text(g), _GOAL_THEME_MAP))
        for g in (profile.hopes or [])
    })

    shared_when = coarsen_date(datetime.now(timezone.utc))

    lines = [
        "---",
        f"accesstwin_overview: {OVERVIEW_VERSION}",
        f"alias: {alias}",
        f"shared: {shared_when}",
        "---",
        "",
        f"# Accessibility Overview — {alias}",
        "",
        "*Shared by the student through AccessTwin. This overview is "
        "de-identified: it describes what helps and what doesn't, without "
        "personal details. Import it into your own AccessTwin portal.*",
        "",
        "*If you use this overview with an AI tool, do not add the "
        "student's name, school, or other identifying details to your "
        "questions.*",
        "",
    ]

    if strength_themes:
        lines.append("## Strengths")
        lines.extend(f"- {t}" for t in strength_themes)
        lines.append("")

    if goal_themes:
        lines.append("## Goals")
        lines.extend(f"- {t}" for t in goal_themes)
        lines.append("")

    working, attention = [], []
    if supports:
        lines.append("## Supports")
        for s in supports:
            desc = scrub(s.description or "")
            heading = s.category + (f" — {s.subcategory}" if s.subcategory else "")
            lines.append(f"### {heading}")
            rating = (
                f"{s.effectiveness_rating:g}/5"
                if s.effectiveness_rating is not None else "not rated"
            )
            lines.append(f"- Status: {s.status} | Effectiveness: {rating}")
            if desc:
                lines.append(f"- {desc}")
            lines.append("")

            if s.effectiveness_rating is not None:
                target = working if s.effectiveness_rating >= 4 else (
                    attention if s.effectiveness_rating <= 2 else None
                )
                if target is not None:
                    target.append(f"{heading}: {desc or 'support'} ({rating})")

        if safe["udl_principles"]:
            lines.append(f"**UDL principles:** {', '.join(safe['udl_principles'])}")
        if safe["pour_principles"]:
            lines.append(f"**POUR principles:** {', '.join(safe['pour_principles'])}")
        lines.append("")

    if working:
        lines.append("## What's Working")
        lines.extend(f"- {w}" for w in working)
        lines.append("")
    if attention:
        lines.append("## Needs Attention")
        lines.extend(f"- {a}" for a in attention)
        lines.append("")

    outcome_lines = []
    for log in tracking_logs[:_MAX_OUTCOMES]:
        note = scrub(log.outcome_notes or "")
        if note.strip():
            when = coarsen_date(log.created_at)
            prefix = f"({when}, {log.logged_by_role}) " if when else ""
            outcome_lines.append(f"- {prefix}{note}")
    if outcome_lines:
        lines.append("## Recent Outcomes")
        lines.extend(outcome_lines)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n", redactions


def build_ai_prompt(overview_markdown: str) -> str:
    """Wrap a de-identified overview in a coaching prompt for external AI.

    For teachers who prefer their own AI tool: bakes in UDL/POUR framing and
    the privacy-hygiene warning so both travel with the paste.
    """
    return (
        "You are an accessibility coach for a teacher. Below is a "
        "de-identified accessibility overview that a student chose to share. "
        "Using UDL (Universal Design for Learning) and POUR (Perceivable, "
        "Operable, Understandable, Robust) principles, help the teacher "
        "understand which supports work for this student and suggest "
        "concrete, classroom-ready ideas to try.\n"
        "\n"
        "PRIVACY NOTE FOR THE TEACHER: do not add the student's name, "
        "school, or any other identifying details to this conversation.\n"
        "\n"
        "--- STUDENT OVERVIEW ---\n"
        f"{overview_markdown.strip()}\n"
        "--- END OVERVIEW ---\n"
        "\n"
        "My question: [describe the lesson, material, or idea you want to "
        "test for this student]\n"
    )


def parse_overview_markdown(text: str) -> dict | None:
    """Parse an overview MD file into a dict, or None if not a valid overview.

    Returns {alias, shared, strengths, goals, supports, outcomes} where
    supports is a list of {category, subcategory, status,
    effectiveness_rating, description}.
    """
    fm = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not fm:
        return None
    front = dict(
        (k.strip(), v.strip())
        for k, v in (
            line.split(":", 1) for line in fm.group(1).splitlines() if ":" in line
        )
    )
    if "accesstwin_overview" not in front:
        return None

    result = {
        "alias": front.get("alias", "Student"),
        "shared": front.get("shared", ""),
        "strengths": [],
        "goals": [],
        "supports": [],
        "outcomes": [],
    }

    section = None
    current = None
    for line in text[fm.end():].splitlines():
        stripped = line.strip()

        if stripped.startswith("## "):
            section = stripped[3:].strip().lower()
            current = None
            continue

        if stripped.startswith("### ") and section == "supports":
            heading = stripped[4:].strip()
            if " — " in heading:
                category, subcategory = heading.split(" — ", 1)
            else:
                category, subcategory = heading, None
            current = {
                "category": category.strip(),
                "subcategory": subcategory.strip() if subcategory else None,
                "status": "active",
                "effectiveness_rating": None,
                "description": "",
            }
            result["supports"].append(current)
            continue

        if not stripped.startswith("- "):
            continue
        item = stripped[2:].strip()

        if section == "strengths":
            result["strengths"].append(item)
        elif section == "goals":
            result["goals"].append(item)
        elif section == "recent outcomes":
            result["outcomes"].append(item)
        elif section == "supports" and current is not None:
            meta = re.match(
                r"Status:\s*(\S+)\s*\|\s*Effectiveness:\s*([\d.]+)?", item
            )
            if meta:
                current["status"] = meta.group(1)
                if meta.group(2):
                    current["effectiveness_rating"] = float(meta.group(2))
            elif current["description"]:
                current["description"] += " " + item
            else:
                current["description"] = item

    return result

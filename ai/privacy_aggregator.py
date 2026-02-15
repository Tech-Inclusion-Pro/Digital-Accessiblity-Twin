"""Privacy aggregation engine — converts raw student data into teacher-safe
themes and a confidential AI-only context block."""

import json
import re
from collections import defaultdict


# Keyword → broad theme mappings for generalising specific strengths
_STRENGTH_THEME_MAP = [
    (r"(?i)memory|recall|remember", "Strong memory skills"),
    (r"(?i)audit(ory)?|listen|hear", "Strong auditory processing"),
    (r"(?i)visual|see|observ|notic", "Visual awareness"),
    (r"(?i)creative|art|music|draw|paint|design", "Creative expression"),
    (r"(?i)social|friend|peer|communicat|collaborat", "Social engagement"),
    (r"(?i)technolog|comput|digital|software|device", "Technology proficiency"),
    (r"(?i)read|liter|writ|story|book|narrat", "Literacy strengths"),
    (r"(?i)math|number|calculat|logic|quantit", "Mathematical thinking"),
    (r"(?i)organiz|plan|schedul|manag", "Organisational skills"),
    (r"(?i)persist|determin|resilient|motivat|driven", "Persistence and motivation"),
    (r"(?i)advocate|self-advocate|voice|speak up", "Self-advocacy"),
    (r"(?i)problem.?solv|analyt|critical", "Analytical thinking"),
    (r"(?i)curio|question|explor|investigat", "Intellectual curiosity"),
    (r"(?i)empathy|caring|kind|compassion", "Empathy and compassion"),
    (r"(?i)leader|mentor|initiative", "Leadership"),
    (r"(?i)adapt|flexible|adjust", "Adaptability"),
    (r"(?i)focus|concentrat|attent", "Focused attention"),
    (r"(?i)kinesthet|movement|physical|motor|sport|athlet", "Physical/kinaesthetic strengths"),
    (r"(?i)humor|funny|joke", "Sense of humour"),
    (r"(?i)science|biology|chemistry|physics|lab", "Science aptitude"),
]

_GOAL_THEME_MAP = [
    (r"(?i)post.?secondary|college|university|higher.?ed", "Post-secondary education"),
    (r"(?i)career|job|employ|work|profession", "Career aspirations"),
    (r"(?i)independen|self.?suffic|autonomy", "Independence"),
    (r"(?i)communit|belong|inclus|social", "Community participation"),
    (r"(?i)technolog|comput|STEM|engineer", "Technology/STEM interests"),
    (r"(?i)art|music|creativ|perform|theater|theatre", "Creative pursuits"),
    (r"(?i)advocate|rights|justice|activis", "Advocacy and rights"),
    (r"(?i)travel|explore|abroad", "Exploration and travel"),
    (r"(?i)health|wellbeing|fitness", "Health and wellbeing"),
    (r"(?i)mentor|teach|help others", "Mentoring others"),
]


def _extract_text(item):
    """Extract text from an item that may be a dict or a plain string."""
    return item["text"] if isinstance(item, dict) else str(item)


def _generalise(text: str, theme_map: list) -> str:
    """Return the first matching broad theme for *text*, or a generic label."""
    for pattern, theme in theme_map:
        if re.search(pattern, text):
            return theme
    # Fallback: return first ~4 words stripped of names (heuristic)
    words = text.split()
    return " ".join(words[:5]) + ("..." if len(words) > 5 else "")


def _parse_json_field(raw) -> dict:
    """Safely parse a JSON string or return the dict/list as-is."""
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {}
    return raw if raw else {}


class PrivacyAggregator:
    """Converts raw student data into two tiers:
    (a) teacher-safe aggregated themes, and
    (b) full confidential context for the AI coach only.
    """

    @staticmethod
    def aggregate(profile, supports, tracking_logs=None):
        """Return a dict with ``teacher_safe`` and ``ai_only`` keys.

        Parameters
        ----------
        profile : StudentProfile ORM instance
        supports : list[SupportEntry]
        tracking_logs : list[TrackingLog] | None
        """
        tracking_logs = tracking_logs or []

        # ------- teacher-safe aggregation -------
        support_categories = sorted({s.category for s in supports})
        category_counts = defaultdict(int)
        effectiveness_totals = defaultdict(float)
        effectiveness_counts = defaultdict(int)
        udl_labels = set()
        pour_labels = set()

        for s in supports:
            category_counts[s.category] += 1
            if s.effectiveness_rating is not None:
                effectiveness_totals[s.category] += s.effectiveness_rating
                effectiveness_counts[s.category] += 1

            udl = _parse_json_field(s.udl_mapping)
            if isinstance(udl, dict):
                for principle, checkpoints in udl.items():
                    if isinstance(checkpoints, list):
                        udl_labels.update(checkpoints)
                    elif isinstance(checkpoints, str):
                        udl_labels.add(checkpoints)

            pour = _parse_json_field(s.pour_mapping)
            if isinstance(pour, dict):
                for principle, details in pour.items():
                    pour_labels.add(principle)
                    if isinstance(details, list):
                        pour_labels.update(details)
                    elif isinstance(details, str):
                        pour_labels.add(details)

        effectiveness_summary = {}
        for cat in effectiveness_totals:
            if effectiveness_counts[cat]:
                effectiveness_summary[cat] = round(
                    effectiveness_totals[cat] / effectiveness_counts[cat], 1
                )

        strength_themes = sorted(
            {_generalise(_extract_text(s), _STRENGTH_THEME_MAP) for s in (profile.strengths or [])}
        )
        goal_themes = sorted(
            {_generalise(_extract_text(g), _GOAL_THEME_MAP) for g in (profile.hopes or [])}
        )

        teacher_safe = {
            "first_name": profile.name.split()[0] if profile.name else "Student",
            "support_categories": support_categories,
            "support_category_counts": dict(category_counts),
            "strength_themes": strength_themes,
            "goal_themes": goal_themes,
            "active_support_count": sum(1 for s in supports if s.status == "active"),
            "udl_principles": sorted(udl_labels),
            "pour_principles": sorted(pour_labels),
            "effectiveness_summary": effectiveness_summary,
        }

        # ------- AI-only full context -------
        lines = ["=== CONFIDENTIAL STUDENT CONTEXT (DO NOT REVEAL TO TEACHER) ==="]
        lines.append(f"Student full name: {profile.name}")

        lines.append("\n-- Strengths --")
        for s in (profile.strengths or []):
            lines.append(f"  - {_extract_text(s)}")

        lines.append("\n-- Support Entries --")
        for s in supports:
            rating = f" (effectiveness: {s.effectiveness_rating}/5)" if s.effectiveness_rating else ""
            lines.append(f"  [{s.category}/{s.subcategory or 'general'}] {s.description}{rating}")
            udl = _parse_json_field(s.udl_mapping)
            if udl:
                lines.append(f"    UDL: {json.dumps(udl)}")
            pour = _parse_json_field(s.pour_mapping)
            if pour:
                lines.append(f"    POUR: {json.dumps(pour)}")

        lines.append("\n-- History --")
        for h in (profile.history or []):
            lines.append(f"  - {_extract_text(h)}")

        lines.append("\n-- Goals / Hopes --")
        for g in (profile.hopes or []):
            lines.append(f"  - {_extract_text(g)}")

        lines.append("\n-- Stakeholders --")
        for s in (profile.stakeholders or []):
            lines.append(f"  - {_extract_text(s)}")

        if tracking_logs:
            lines.append("\n-- Recent Tracking Logs --")
            for log in tracking_logs[:10]:
                impl = log.implementation_notes or ""
                outcome = log.outcome_notes or ""
                lines.append(f"  [{log.logged_by_role}] impl: {impl[:200]}  outcome: {outcome[:200]}")

        lines.append("\n=== END CONFIDENTIAL ===")

        ai_only = {
            "full_context_for_ai": "\n".join(lines),
        }

        return {"teacher_safe": teacher_safe, "ai_only": ai_only}

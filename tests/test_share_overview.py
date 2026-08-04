"""Tests for de-identification and Share Overview build/parse."""

from datetime import datetime, timezone
from types import SimpleNamespace

from utils.deidentify import (
    collect_known_names, scrub_text, coarsen_date, generate_alias,
)
from utils.share_overview import (
    build_overview_markdown, parse_overview_markdown, build_ai_prompt,
)


def _profile(**kwargs):
    defaults = dict(
        name="Jordan Alvarez",
        strengths=[{"text": "Great memory for facts"}],
        supports=[],
        history=[{"text": "Diagnosed with ADHD in 3rd grade at Lincoln Elementary"}],
        hopes=[{"text": "Wants to go to college for engineering"}],
        stakeholders=[{"text": "Mom - Karen Alvarez"}, {"text": "Ms. Rivera (case manager)"}],
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _support(**kwargs):
    defaults = dict(
        category="environmental", subcategory="seating",
        description="Preferential seating near the front",
        udl_mapping="{}", pour_mapping="{}",
        status="active", effectiveness_rating=4.0,
        created_at=datetime(2026, 3, 10, tzinfo=timezone.utc),
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _log(**kwargs):
    defaults = dict(
        logged_by_role="student", support_id=1,
        implementation_notes="", outcome_notes="It helped a lot",
        created_at=datetime(2026, 7, 2, tzinfo=timezone.utc),
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# ---------------------------------------------------------------- deidentify

class TestScrubText:
    def test_known_names_removed_case_insensitive(self):
        names = collect_known_names(_profile())
        out, red = scrub_text("jordan asked KAREN for help", names)
        assert "jordan" not in out.lower().replace("[name removed]", "")
        assert "karen" not in out.lower().replace("[name removed]", "")
        assert len(red) == 2

    def test_possessive_form_removed(self):
        names = collect_known_names(_profile())
        out, _ = scrub_text("Jordan's notes were on Rivera's desk", names)
        assert "Jordan" not in out
        assert "Rivera" not in out

    def test_email_and_phone_removed(self):
        out, red = scrub_text(
            "Reach me at jordan.a@example.com or (312) 555-0142", set()
        )
        assert "example.com" not in out
        assert "555" not in out
        labels = {label for label, _ in red}
        assert labels == {"email removed", "phone removed"}

    def test_honorific_name_removed(self):
        out, _ = scrub_text("Ms. Thompson lets me use headphones", set())
        assert "Thompson" not in out
        assert "[staff name removed]" in out

    def test_relation_name_removed_keeps_relation(self):
        out, _ = scrub_text("My mom Diane reminds me to use my planner", set())
        assert "Diane" not in out
        assert "mom" in out.lower()

    def test_school_name_removed(self):
        out, _ = scrub_text("I transferred from Lakeview Middle School", set())
        assert "Lakeview" not in out
        assert "[school removed]" in out

    def test_clean_text_untouched(self):
        text = "Extra time on tests helps me finish without panicking"
        out, red = scrub_text(text, set())
        assert out == text
        assert red == []


class TestHelpers:
    def test_collect_known_names_skips_role_words(self):
        names = collect_known_names(_profile())
        assert "jordan" in names and "karen" in names and "rivera" in names
        assert "mom" not in names and "case" not in names

    def test_coarsen_date(self):
        assert coarsen_date(datetime(2026, 7, 2)) == "Summer 2026"
        assert coarsen_date("2026-01-15T10:00:00+00:00") == "Winter 2026"
        assert coarsen_date(None) == ""
        assert coarsen_date("not-a-date") == ""

    def test_generate_alias_format(self):
        alias = generate_alias()
        assert alias.startswith("Student ")
        assert len(alias) == len("Student A1")


# ------------------------------------------------------------------- builder

class TestBuildOverview:
    def test_excludes_identity_and_private_sections(self):
        md, _ = build_overview_markdown(
            _profile(), [_support()], [_log()], alias="Student K4"
        )
        assert "Jordan" not in md
        assert "Alvarez" not in md
        assert "Karen" not in md
        assert "Rivera" not in md
        assert "ADHD" not in md          # history never included
        assert "Stakeholder" not in md
        assert "Student K4" in md

    def test_dates_are_coarse(self):
        md, _ = build_overview_markdown(
            _profile(), [_support()], [_log()], alias="Student K4"
        )
        assert "2026-07" not in md
        assert "Summer 2026" in md

    def test_outcome_notes_scrubbed(self):
        log = _log(outcome_notes="Ms. Chen said Jordan improved")
        md, red = build_overview_markdown(_profile(), [_support()], [log])
        assert "Chen" not in md
        assert "Jordan" not in md
        assert red  # something was redacted

    def test_includes_ai_hygiene_guidance(self):
        md, _ = build_overview_markdown(_profile(), [_support()], [])
        assert "do not add the student's name" in md.lower()

    def test_effectiveness_buckets(self):
        supports = [
            _support(effectiveness_rating=5.0),
            _support(category="instructional", subcategory=None,
                     description="Verbal-only instructions",
                     effectiveness_rating=1.0),
        ]
        md, _ = build_overview_markdown(_profile(), supports, [])
        assert "## What's Working" in md
        assert "## Needs Attention" in md


# -------------------------------------------------------------------- parser

class TestParseOverview:
    def test_roundtrip(self):
        supports = [
            _support(),
            _support(category="instructional", subcategory=None,
                     description="Written instructions provided",
                     status="inactive", effectiveness_rating=2.5),
        ]
        md, _ = build_overview_markdown(
            _profile(), supports, [_log()], alias="Student K4"
        )
        data = parse_overview_markdown(md)

        assert data is not None
        assert data["alias"] == "Student K4"
        assert data["strengths"]
        assert len(data["supports"]) == 2

        first = data["supports"][0]
        assert first["category"] == "environmental"
        assert first["subcategory"] == "seating"
        assert first["status"] == "active"
        assert first["effectiveness_rating"] == 4.0
        assert "seating" in first["description"].lower()

        second = data["supports"][1]
        assert second["subcategory"] is None
        assert second["status"] == "inactive"
        assert second["effectiveness_rating"] == 2.5
        assert data["outcomes"]

    def test_rejects_plain_markdown(self):
        assert parse_overview_markdown("# Just a document\n\n- hello\n") is None
        assert parse_overview_markdown(
            "---\ntitle: notes\n---\n\n# Notes\n"
        ) is None


# ---------------------------------------------------------------- AI prompt

class TestBuildAiPrompt:
    def test_wraps_overview_with_framing_and_warning(self):
        md, _ = build_overview_markdown(
            _profile(), [_support()], [], alias="Student K4"
        )
        prompt = build_ai_prompt(md)
        assert "--- STUDENT OVERVIEW ---" in prompt
        assert "Student K4" in prompt
        assert "UDL" in prompt and "POUR" in prompt
        assert "PRIVACY NOTE" in prompt
        assert "My question:" in prompt
        # The de-identified content survives intact.
        assert "Jordan" not in prompt and "Alvarez" not in prompt


# -------------------------------------------------- teacher import pipeline

class TestOverviewImportPipeline:
    def test_imported_overview_visible_via_import_purposes_filter(self, tmp_db):
        """An overview import must surface through the same Document filter
        that every teacher page (evaluate, insights, home, etc.) uses."""
        import json
        from config.constants import IMPORT_PURPOSES
        from models.user import User
        from models.student_profile import StudentProfile
        from models.support import SupportEntry
        from models.document import Document
        from models.evaluation import TwinEvaluation

        md, _ = build_overview_markdown(
            _profile(), [_support()], [_log()], alias="Student K4"
        )
        data = parse_overview_markdown(md)

        session = tmp_db.get_session()
        try:
            teacher = User(role="teacher", username="t1", password_hash="x")
            session.add(teacher)
            session.flush()

            profile = StudentProfile(
                user_id=teacher.id,
                name=data["alias"],
                strengths_json=json.dumps(
                    [{"text": s} for s in data["strengths"]]
                ),
            )
            session.add(profile)
            session.flush()
            for se in data["supports"]:
                session.add(SupportEntry(
                    profile_id=profile.id,
                    category=se["category"],
                    subcategory=se["subcategory"],
                    description=se["description"],
                    status=se["status"],
                    effectiveness_rating=se["effectiveness_rating"],
                ))
            doc = Document(
                teacher_user_id=teacher.id,
                filename="Student_K4_overview.md",
                file_type="md",
                file_blob=md.encode("utf-8"),
                purpose_description="overview_import",
            )
            session.add(doc)
            session.flush()
            session.add(TwinEvaluation(
                document_id=doc.id, student_profile_id=profile.id
            ))
            session.commit()

            # The exact query pattern used by the teacher pages.
            import_docs = session.query(Document).filter(
                Document.teacher_user_id == teacher.id,
                Document.purpose_description.in_(IMPORT_PURPOSES),
            ).all()
            profile_ids = {
                ev.student_profile_id
                for d in import_docs
                for ev in session.query(TwinEvaluation).filter(
                    TwinEvaluation.document_id == d.id
                ).all()
            }
            assert profile.id in profile_ids

            found = session.query(StudentProfile).get(profile.id)
            assert found.name == "Student K4"
            supports = session.query(SupportEntry).filter(
                SupportEntry.profile_id == profile.id
            ).all()
            assert supports and supports[0].effectiveness_rating == 4.0
        finally:
            session.close()

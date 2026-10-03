from datetime import datetime, timezone

from shorts.clients.llm import StubLLMClient
from shorts.generation.script_writer import ScriptWriter, validate_script
from shorts.models import MatchData


def build_match() -> MatchData:
    return MatchData(
        match_id="1234",
        home_team="Arsenal",
        away_team="Chelsea",
        competition="Premier League",
        completed_at=datetime(2026, 6, 5, 19, 45, tzinfo=timezone.utc),
        home_score=2,
        away_score=1,
        home_xg=1.8,
        away_xg=0.7,
        home_possession=58.0,
        away_possession=42.0,
        shot_count_home=14,
        shot_count_away=8,
        key_events=["Saka 18'", "Havertz 61'"],
    )


def test_validate_script_rejects_hype_phrases():
    errors = validate_script(
        "Unbelievable scenes as Arsenal totally destroyed Chelsea tonight in chaos."
    )

    assert "contains banned phrase" in errors[0]


def test_script_writer_formats_prompt_from_match():
    writer = ScriptWriter(
        llm_client=StubLLMClient(
            "Arsenal controlled the half-space, won xG 1.8 to 0.7, and forced Chelsea deeper after halftime. "
            "Their structure narrowed central access while the back line held a cleaner rest-defense shape all night."
        )
    )

    draft = writer.generate(build_match())

    assert draft.provider == "stub-llm"
    assert "half-space" in draft.text

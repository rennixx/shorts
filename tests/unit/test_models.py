from datetime import datetime, timezone

from shorts.models import MatchData, ScriptDraft


def test_match_data_builds_stable_slug():
    match = MatchData(
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

    assert match.slug == "1234-arsenal-vs-chelsea"


def test_script_draft_counts_words_from_text():
    draft = ScriptDraft(
        text="Arsenal won the half-space battle and controlled the higher xG zones tonight.",
        provider="stub-llm",
    )

    assert draft.word_count == 12

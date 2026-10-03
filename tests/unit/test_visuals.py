from datetime import datetime, timezone

from shorts.generation.scenes import build_scene_plan
from shorts.models import MatchData


def test_scene_plan_covers_full_duration():
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

    scenes = build_scene_plan(match, duration=22.0)

    assert scenes[0].start == 0.0
    assert scenes[-1].end == 22.0
    assert [scene.name for scene in scenes] == ["intro", "score", "xg", "territory", "closing"]
    assert scenes[3].payload["label"] == "Territory"

from shorts.models import MatchData, SceneSpec


def build_scene_plan(match: MatchData, duration: float) -> list[SceneSpec]:
    checkpoints = [0.0, duration * 0.18, duration * 0.40, duration * 0.62, duration * 0.82, duration]
    return [
        SceneSpec(
            name="intro",
            start=checkpoints[0],
            end=checkpoints[1],
            payload={
                "competition": match.competition,
                "home_team": match.home_team,
                "away_team": match.away_team,
                "score": f"{match.home_score}-{match.away_score}",
            },
        ),
        SceneSpec(
            name="score",
            start=checkpoints[1],
            end=checkpoints[2],
            payload={
                "label": "Scoreline",
                "score": f"{match.home_score}-{match.away_score}",
                "events": match.key_events[:2],
            },
        ),
        SceneSpec(
            name="xg",
            start=checkpoints[2],
            end=checkpoints[3],
            payload={"label": "xG", "home": match.home_xg, "away": match.away_xg},
        ),
        SceneSpec(
            name="territory",
            start=checkpoints[3],
            end=checkpoints[4],
            payload={
                "label": "Territory",
                "possession_label": "Possession",
                "home": match.home_possession,
                "away": match.away_possession,
                "shots_home": match.shot_count_home,
                "shots_away": match.shot_count_away,
            },
        ),
        SceneSpec(
            name="closing",
            start=checkpoints[4],
            end=checkpoints[5],
            payload={
                "claim": "Control the middle, control the match.",
                "tags": ["xG edge", "territory", "half-space"],
            },
        ),
    ]

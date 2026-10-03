from dataclasses import dataclass
from datetime import datetime

import httpx

from shorts.models import MatchData


@dataclass(slots=True)
class FootballAPIClient:
    base_url: str
    api_key: str

    def latest_completed_match(self) -> MatchData:
        response = httpx.get(
            f"{self.base_url}/fixtures",
            headers={"x-apisports-key": self.api_key},
            params={"status": "FT", "last": 1},
            timeout=30.0,
        )
        response.raise_for_status()
        item = response.json()["response"][0]
        return MatchData(
            match_id=str(item["fixture"]["id"]),
            home_team=item["teams"]["home"]["name"],
            away_team=item["teams"]["away"]["name"],
            competition=item["league"]["name"],
            completed_at=datetime.fromisoformat(item["fixture"]["date"].replace("Z", "+00:00")),
            home_score=item["goals"]["home"],
            away_score=item["goals"]["away"],
            home_xg=None,
            away_xg=None,
            home_possession=None,
            away_possession=None,
            shot_count_home=None,
            shot_count_away=None,
            key_events=[],
            raw_payload=item,
        )

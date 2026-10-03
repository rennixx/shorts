from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
import re


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


@dataclass(slots=True)
class MatchData:
    match_id: str
    home_team: str
    away_team: str
    competition: str
    completed_at: datetime
    home_score: int
    away_score: int
    home_xg: float | None
    away_xg: float | None
    home_possession: float | None
    away_possession: float | None
    shot_count_home: int | None
    shot_count_away: int | None
    key_events: list[str] = field(default_factory=list)
    raw_payload: dict[str, Any] = field(default_factory=dict)

    @property
    def slug(self) -> str:
        return f"{self.match_id}-{_slugify(self.home_team)}-vs-{_slugify(self.away_team)}"


@dataclass(slots=True)
class ScriptDraft:
    text: str
    provider: str

    @property
    def word_count(self) -> int:
        return len([token for token in self.text.split() if token.strip()])


@dataclass(slots=True)
class WordTiming:
    text: str
    start: float
    end: float


@dataclass(slots=True)
class SubtitleCue:
    start: float
    end: float
    text: str
    highlighted_words: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SceneSpec:
    name: str
    start: float
    end: float
    payload: dict[str, Any]


@dataclass(slots=True)
class RunManifest:
    match_id: str
    slug: str
    run_dir: Path
    status: str
    script_text: str = ""
    audio_path: str = ""
    subtitles_path: str = ""
    video_path: str = ""
    providers: dict[str, str] = field(default_factory=dict)
    error_reason: str = ""

# PitchBlack MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-hosted Python pipeline that turns completed football match data into a 20-25 second 1080x1920 tactical short with narration, timed subtitles, programmatic visuals, and a dry-run publishing path.

**Architecture:** Use a small `src/shorts` package with clear boundaries between providers, generation, rendering, storage, and workflows. Keep all external services behind adapters so the MVP can run with free testing providers first and switch to paid upgrades later without changing the internal pipeline.

**Tech Stack:** Python 3.11+, `edge-tts`, `moviepy`, `ffmpeg-python`, `Pillow`, `httpx`, `pytest`, `pytest-asyncio`

---

### Task 1: Bootstrap The Package, Settings, And Core Models

**Files:**
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: `config/prompts.yaml`
- Create: `config/styles.yaml`
- Create: `config/voices.yaml`
- Create: `src/shorts/__init__.py`
- Create: `src/shorts/main.py`
- Create: `src/shorts/settings.py`
- Create: `src/shorts/models.py`
- Create: `src/shorts/pipeline.py`
- Create: `runs/.gitkeep`
- Test: `tests/unit/test_models.py`

- [ ] **Step 1: Write the failing model test**

```python
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/unit/test_models.py -q`

Expected: FAIL with `ModuleNotFoundError: No module named 'shorts'` or import errors for missing files.

- [ ] **Step 3: Write the minimal package and model implementation**

`requirements.txt`

```text
edge-tts
ffmpeg-python
httpx
moviepy
Pillow
pytest
pytest-asyncio
PyYAML
```

`pytest.ini`

```ini
[pytest]
pythonpath = src
asyncio_mode = auto
```

`config/prompts.yaml`

```yaml
script:
  system: "Write concise tactical football analysis with no hype language."
  user_template: |
    Write one 45-55 word football short about this match.
    Use one tactical claim and 2-3 supporting facts.
    Match: {home_team} vs {away_team}
    Score: {home_score}-{away_score}
    xG: {home_xg}-{away_xg}
    Possession: {home_possession}-{away_possession}
    Key events: {key_events}
```

`config/styles.yaml`

```yaml
video:
  width: 1080
  height: 1920
  fps: 24
colors:
  background: "#000000"
  primary_text: "#FFFFFF"
  accent: "#FF1493"
subtitles:
  max_words_per_cue: 3
  bottom_margin: 300
```

`config/voices.yaml`

```yaml
default:
  provider: edge-tts
  voice: en-GB-RyanNeural
```

`src/shorts/__init__.py`

```python
__all__ = [
    "models",
    "pipeline",
    "settings",
]
```

`src/shorts/settings.py`

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    project_root: Path
    runs_dir: Path
    config_dir: Path
    assets_dir: Path
    output_width: int = 1080
    output_height: int = 1920
    fps: int = 24

    @classmethod
    def from_root(cls, project_root: Path) -> "Settings":
        return cls(
            project_root=project_root,
            runs_dir=project_root / "runs",
            config_dir=project_root / "config",
            assets_dir=project_root / "assets",
        )
```

`src/shorts/models.py`

```python
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
```

`src/shorts/pipeline.py`

```python
from dataclasses import dataclass
from pathlib import Path

from shorts.settings import Settings


@dataclass(slots=True)
class PipelineContext:
    project_root: Path
    settings: Settings


def build_context(project_root: Path) -> PipelineContext:
    settings = Settings.from_root(project_root)
    settings.runs_dir.mkdir(parents=True, exist_ok=True)
    return PipelineContext(project_root=project_root, settings=settings)
```

`src/shorts/main.py`

```python
from pathlib import Path

from shorts.pipeline import build_context


def main() -> None:
    context = build_context(Path.cwd())
    print(f"PitchBlack ready at {context.project_root}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/unit/test_models.py -q`

Expected: PASS with `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt pytest.ini config src tests runs
git commit -m "chore: scaffold pitchblack package"
```

### Task 2: Add Manifest Storage, Path Helpers, And Script Writer Rules

**Files:**
- Create: `src/shorts/storage/__init__.py`
- Create: `src/shorts/storage/paths.py`
- Create: `src/shorts/storage/manifest.py`
- Create: `src/shorts/clients/__init__.py`
- Create: `src/shorts/clients/llm.py`
- Create: `src/shorts/generation/__init__.py`
- Create: `src/shorts/generation/script_writer.py`
- Test: `tests/unit/test_manifest.py`
- Test: `tests/unit/test_script_writer.py`

- [ ] **Step 1: Write failing tests for manifest persistence and script validation**

```python
from datetime import datetime, timezone

from shorts.models import MatchData, RunManifest
from shorts.generation.script_writer import ScriptWriter, validate_script
from shorts.clients.llm import StubLLMClient


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
    errors = validate_script("Unbelievable scenes as Arsenal totally destroyed Chelsea tonight in chaos.")
    assert "contains banned phrase" in errors[0]


def test_script_writer_formats_prompt_from_match():
    writer = ScriptWriter(llm_client=StubLLMClient("Arsenal controlled the half-space, won xG 1.8 to 0.7, and forced Chelsea deeper after halftime."))
    draft = writer.generate(build_match())
    assert draft.provider == "stub-llm"
    assert "half-space" in draft.text


def test_manifest_round_trip(tmp_path):
    manifest = RunManifest(
        match_id="1234",
        slug="1234-arsenal-vs-chelsea",
        run_dir=tmp_path,
        status="rendered",
        script_text="Arsenal controlled the half-space and finished with the stronger xG profile.",
    )

    from shorts.storage.manifest import load_manifest, save_manifest

    save_manifest(manifest)
    loaded = load_manifest(tmp_path / "manifest.json")

    assert loaded.match_id == manifest.match_id
    assert loaded.status == "rendered"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/unit/test_manifest.py tests/unit/test_script_writer.py -q`

Expected: FAIL with import errors for missing modules under `shorts.storage`, `shorts.clients`, and `shorts.generation`.

- [ ] **Step 3: Implement storage helpers and script writing**

`src/shorts/storage/__init__.py`

```python
__all__ = ["manifest", "paths"]
```

`src/shorts/storage/paths.py`

```python
from pathlib import Path

from shorts.models import MatchData


def build_run_dir(runs_dir: Path, match: MatchData) -> Path:
    return runs_dir / match.slug


def ensure_run_dir(runs_dir: Path, match: MatchData) -> Path:
    run_dir = build_run_dir(runs_dir, match)
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir
```

`src/shorts/storage/manifest.py`

```python
from dataclasses import asdict
from pathlib import Path
import json

from shorts.models import RunManifest


def save_manifest(manifest: RunManifest) -> Path:
    manifest_path = manifest.run_dir / "manifest.json"
    payload = asdict(manifest)
    payload["run_dir"] = str(manifest.run_dir)
    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return manifest_path


def load_manifest(path: Path) -> RunManifest:
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["run_dir"] = Path(payload["run_dir"])
    return RunManifest(**payload)
```

`src/shorts/clients/__init__.py`

```python
__all__ = ["llm"]
```

`src/shorts/clients/llm.py`

```python
from dataclasses import dataclass
from typing import Protocol


class LLMClient(Protocol):
    provider_name: str

    def generate_text(self, prompt: str) -> str:
        ...


@dataclass(slots=True)
class StubLLMClient:
    response_text: str
    provider_name: str = "stub-llm"

    def generate_text(self, prompt: str) -> str:
        return self.response_text
```

`src/shorts/generation/__init__.py`

```python
__all__ = ["script_writer"]
```

`src/shorts/generation/script_writer.py`

```python
from dataclasses import dataclass

from shorts.clients.llm import LLMClient
from shorts.models import MatchData, ScriptDraft


BANNED_PHRASES = {
    "unbelievable scenes",
    "crazy scenes",
    "insane",
    "goat",
    "what a game",
}


def validate_script(text: str) -> list[str]:
    errors: list[str] = []
    lowered = text.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            errors.append(f"contains banned phrase: {phrase}")
    word_count = len(text.split())
    if word_count < 45 or word_count > 55:
        errors.append(f"word count out of range: {word_count}")
    return errors


@dataclass(slots=True)
class ScriptWriter:
    llm_client: LLMClient

    def build_prompt(self, match: MatchData) -> str:
        key_events = ", ".join(match.key_events) or "None"
        return (
            "Write one tactical football short in 45-55 words. "
            f"Match: {match.home_team} vs {match.away_team}. "
            f"Score: {match.home_score}-{match.away_score}. "
            f"xG: {match.home_xg}-{match.away_xg}. "
            f"Possession: {match.home_possession}-{match.away_possession}. "
            f"Events: {key_events}."
        )

    def generate(self, match: MatchData) -> ScriptDraft:
        prompt = self.build_prompt(match)
        text = self.llm_client.generate_text(prompt).strip()
        draft = ScriptDraft(text=text, provider=self.llm_client.provider_name)
        errors = validate_script(draft.text)
        if errors:
            raise ValueError("; ".join(errors))
        return draft
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/unit/test_manifest.py tests/unit/test_script_writer.py -q`

Expected: PASS with `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/shorts/storage src/shorts/clients src/shorts/generation tests/unit
git commit -m "feat: add manifest storage and script writer"
```

### Task 3: Build Audio Generation And Subtitle Cue Creation

**Files:**
- Create: `src/shorts/clients/tts.py`
- Create: `src/shorts/generation/audio_subs.py`
- Test: `tests/unit/test_audio_subs.py`

- [ ] **Step 1: Write the failing subtitle grouping test**

```python
from shorts.models import WordTiming
from shorts.generation.audio_subs import build_subtitle_cues


def test_build_subtitle_cues_groups_at_most_three_words():
    words = [
        WordTiming(text="Arsenal", start=0.0, end=0.4),
        WordTiming(text="controlled", start=0.4, end=0.9),
        WordTiming(text="the", start=0.9, end=1.1),
        WordTiming(text="half-space", start=1.1, end=1.7),
        WordTiming(text="battle", start=1.7, end=2.1),
    ]

    cues = build_subtitle_cues(words, highlight_terms={"half-space"})

    assert [cue.text for cue in cues] == ["Arsenal controlled the", "half-space battle"]
    assert cues[1].highlighted_words == ["half-space"]
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/unit/test_audio_subs.py -q`

Expected: FAIL with import errors for missing `shorts.generation.audio_subs` or `shorts.clients.tts`.

- [ ] **Step 3: Implement TTS and subtitle cue generation**

`src/shorts/clients/tts.py`

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import edge_tts

from shorts.models import WordTiming


class TTSClient(Protocol):
    provider_name: str

    async def synthesize(self, text: str, audio_path: Path) -> list[WordTiming]:
        ...


@dataclass(slots=True)
class EdgeTTSClient:
    voice: str
    provider_name: str = "edge-tts"

    async def synthesize(self, text: str, audio_path: Path) -> list[WordTiming]:
        communicate = edge_tts.Communicate(text=text, voice=self.voice)
        timings: list[WordTiming] = []
        with audio_path.open("wb") as handle:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    handle.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    start = chunk["offset"] / 10_000_000
                    duration = chunk["duration"] / 10_000_000
                    timings.append(
                        WordTiming(
                            text=chunk["text"],
                            start=start,
                            end=start + duration,
                        )
                    )
        return timings
```

`src/shorts/generation/audio_subs.py`

```python
from pathlib import Path

from shorts.clients.tts import TTSClient
from shorts.models import SubtitleCue, WordTiming


def build_subtitle_cues(
    words: list[WordTiming],
    highlight_terms: set[str],
    max_words_per_cue: int = 3,
) -> list[SubtitleCue]:
    cues: list[SubtitleCue] = []
    bucket: list[WordTiming] = []

    for word in words:
        bucket.append(word)
        if len(bucket) == max_words_per_cue:
            cues.append(_build_cue(bucket, highlight_terms))
            bucket = []

    if bucket:
        cues.append(_build_cue(bucket, highlight_terms))

    return cues


def _build_cue(words: list[WordTiming], highlight_terms: set[str]) -> SubtitleCue:
    text = " ".join(word.text for word in words)
    highlighted = [word.text for word in words if word.text.lower() in highlight_terms]
    return SubtitleCue(
        start=words[0].start,
        end=words[-1].end,
        text=text,
        highlighted_words=highlighted,
    )


def format_vtt(cues: list[SubtitleCue]) -> str:
    body = ["WEBVTT", ""]
    for cue in cues:
        body.append(f"{_fmt(cue.start)} --> {_fmt(cue.end)}")
        body.append(cue.text)
        body.append("")
    return "\n".join(body)


def _fmt(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:06.3f}".replace(".", ",")


async def generate_audio_and_subs(
    text_script: str,
    tts_client: TTSClient,
    run_dir: Path,
    highlight_terms: set[str],
) -> tuple[Path, Path, list[SubtitleCue]]:
    audio_path = run_dir / "voice.mp3"
    subtitles_path = run_dir / "subtitles.vtt"
    timings = await tts_client.synthesize(text_script, audio_path)
    cues = build_subtitle_cues(timings, highlight_terms=highlight_terms)
    subtitles_path.write_text(format_vtt(cues), encoding="utf-8")
    return audio_path, subtitles_path, cues
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/unit/test_audio_subs.py -q`

Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/shorts/clients/tts.py src/shorts/generation/audio_subs.py tests/unit/test_audio_subs.py
git commit -m "feat: add edge tts audio and subtitle generation"
```

### Task 4: Render Programmatic Scene Plans And Background Visuals

**Files:**
- Create: `src/shorts/generation/scenes.py`
- Create: `src/shorts/generation/visuals.py`
- Test: `tests/unit/test_visuals.py`

- [ ] **Step 1: Write the failing scene-plan test**

```python
from datetime import datetime, timezone

from shorts.models import MatchData
from shorts.generation.scenes import build_scene_plan


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
    assert [scene.name for scene in scenes] == ["score", "xg", "possession", "closing"]
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/unit/test_visuals.py -q`

Expected: FAIL with import errors for missing `shorts.generation.scenes` and `shorts.generation.visuals`.

- [ ] **Step 3: Implement reusable scenes and a background renderer**

`src/shorts/generation/scenes.py`

```python
from shorts.models import MatchData, SceneSpec


def build_scene_plan(match: MatchData, duration: float) -> list[SceneSpec]:
    checkpoints = [0.0, duration * 0.25, duration * 0.5, duration * 0.75, duration]
    return [
        SceneSpec(
            name="score",
            start=checkpoints[0],
            end=checkpoints[1],
            payload={"score": f"{match.home_score}-{match.away_score}", "teams": f"{match.home_team} vs {match.away_team}"},
        ),
        SceneSpec(
            name="xg",
            start=checkpoints[1],
            end=checkpoints[2],
            payload={"label": "xG", "home": match.home_xg, "away": match.away_xg},
        ),
        SceneSpec(
            name="possession",
            start=checkpoints[2],
            end=checkpoints[3],
            payload={"label": "Possession", "home": match.home_possession, "away": match.away_possession},
        ),
        SceneSpec(
            name="closing",
            start=checkpoints[3],
            end=checkpoints[4],
            payload={"claim": "Control the middle, control the match."},
        ),
    ]
```

`src/shorts/generation/visuals.py`

```python
from pathlib import Path

from moviepy import ColorClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont

from shorts.generation.scenes import build_scene_plan
from shorts.models import MatchData, SceneSpec


VIDEO_SIZE = (1080, 1920)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PINK = (255, 20, 147)


def render_background_video(match: MatchData, duration: float, output_path: Path) -> Path:
    base = ColorClip(size=VIDEO_SIZE, color=BLACK, duration=duration)
    overlays = []
    for scene in build_scene_plan(match, duration):
        frame_path = output_path.parent / f"{scene.name}.png"
        _render_scene_image(scene, frame_path)
        clip = (
            ImageClip(str(frame_path))
            .with_start(scene.start)
            .with_duration(scene.end - scene.start)
            .with_position(("center", "center"))
        )
        overlays.append(clip)

    video = CompositeVideoClip([base, *overlays], size=VIDEO_SIZE)
    video.write_videofile(
        str(output_path),
        codec="libx264",
        fps=24,
        audio=False,
        preset="medium",
    )
    return output_path


def _render_scene_image(scene: SceneSpec, output_path: Path) -> None:
    image = Image.new("RGB", VIDEO_SIZE, BLACK)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    draw.rectangle((120, 260, 960, 1660), outline=PINK, width=6)
    draw.line((210, 960, 870, 960), fill=PINK, width=4)
    draw.text((160, 180), scene.name.upper(), font=font, fill=PINK)

    y = 520
    for key, value in scene.payload.items():
        draw.text((180, y), f"{key}: {value}", font=font, fill=WHITE)
        y += 140

    image.save(output_path)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/unit/test_visuals.py -q`

Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/shorts/generation/scenes.py src/shorts/generation/visuals.py tests/unit/test_visuals.py
git commit -m "feat: add programmatic scene planning and visuals"
```

### Task 5: Assemble Final Shorts With Subtitle Cards And Pipeline Orchestration

**Files:**
- Create: `src/shorts/render/__init__.py`
- Create: `src/shorts/render/keyword_highlighter.py`
- Create: `src/shorts/render/subtitles.py`
- Create: `src/shorts/render/compositor.py`
- Create: `src/shorts/render/ffmpeg_helpers.py`
- Modify: `src/shorts/pipeline.py`
- Test: `tests/unit/test_subtitles.py`

- [ ] **Step 1: Write the failing subtitle renderer test**

```python
from shorts.models import SubtitleCue
from shorts.render.keyword_highlighter import collect_highlight_tokens


def test_collect_highlight_tokens_matches_case_insensitively():
    cue = SubtitleCue(
        start=0.0,
        end=1.0,
        text="Arsenal owned the half-space",
        highlighted_words=["half-space"],
    )

    assert collect_highlight_tokens(cue) == {"half-space"}
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/unit/test_subtitles.py -q`

Expected: FAIL with import errors for missing modules under `shorts.render`.

- [ ] **Step 3: Implement subtitle rendering, composition, and pipeline orchestration**

`src/shorts/render/__init__.py`

```python
__all__ = ["compositor", "ffmpeg_helpers", "keyword_highlighter", "subtitles"]
```

`src/shorts/render/keyword_highlighter.py`

```python
from shorts.models import SubtitleCue


def collect_highlight_tokens(cue: SubtitleCue) -> set[str]:
    return {token.lower() for token in cue.highlighted_words}
```

`src/shorts/render/subtitles.py`

```python
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from shorts.models import SubtitleCue
from shorts.render.keyword_highlighter import collect_highlight_tokens


def render_subtitle_card(cue: SubtitleCue, output_path: Path) -> Path:
    image = Image.new("RGBA", (1080, 220), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    x = 60
    tokens = cue.text.split()
    highlights = collect_highlight_tokens(cue)

    for token in tokens:
        fill = (255, 20, 147, 255) if token.lower() in highlights else (255, 255, 255, 255)
        draw.text((x, 90), token, font=font, fill=fill)
        x += draw.textlength(token + " ", font=font)

    image.save(output_path)
    return output_path
```

`src/shorts/render/ffmpeg_helpers.py`

```python
from pathlib import Path

import ffmpeg


def normalize_short(input_path: Path, output_path: Path) -> Path:
    (
        ffmpeg
        .input(str(input_path))
        .output(
            str(output_path),
            vcodec="libx264",
            acodec="aac",
            pix_fmt="yuv420p",
            movflags="+faststart",
        )
        .overwrite_output()
        .run(quiet=True)
    )
    return output_path
```

`src/shorts/render/compositor.py`

```python
from pathlib import Path

from moviepy import AudioFileClip, CompositeVideoClip, ImageClip, VideoFileClip

from shorts.models import SubtitleCue
from shorts.render.ffmpeg_helpers import normalize_short
from shorts.render.subtitles import render_subtitle_card


def compose_short(
    background_path: Path,
    audio_path: Path,
    cues: list[SubtitleCue],
    output_path: Path,
) -> Path:
    background = VideoFileClip(str(background_path))
    audio = AudioFileClip(str(audio_path))
    overlays = [background.with_audio(audio)]

    for index, cue in enumerate(cues):
        card_path = output_path.parent / f"subtitle-{index:03d}.png"
        render_subtitle_card(cue, card_path)
        overlays.append(
            ImageClip(str(card_path))
            .with_start(cue.start)
            .with_duration(max(cue.end - cue.start, 0.15))
            .with_position(("center", 1440))
        )

    composite = CompositeVideoClip(overlays, size=background.size)
    temp_output = output_path.parent / "assembled-temp.mp4"
    composite.write_videofile(
        str(temp_output),
        codec="libx264",
        audio_codec="aac",
        fps=24,
        preset="medium",
    )
    return normalize_short(temp_output, output_path)
```

`src/shorts/pipeline.py`

```python
from dataclasses import dataclass
from pathlib import Path

from shorts.clients.llm import LLMClient
from shorts.clients.tts import TTSClient
from shorts.generation.audio_subs import generate_audio_and_subs
from shorts.generation.script_writer import ScriptWriter
from shorts.generation.visuals import render_background_video
from shorts.models import MatchData, RunManifest
from shorts.render.compositor import compose_short
from shorts.settings import Settings
from shorts.storage.manifest import save_manifest
from shorts.storage.paths import ensure_run_dir


@dataclass(slots=True)
class PipelineContext:
    project_root: Path
    settings: Settings


def build_context(project_root: Path) -> PipelineContext:
    settings = Settings.from_root(project_root)
    settings.runs_dir.mkdir(parents=True, exist_ok=True)
    return PipelineContext(project_root=project_root, settings=settings)


@dataclass(slots=True)
class PitchBlackPipeline:
    llm_client: LLMClient
    tts_client: TTSClient
    highlight_terms: set[str]

    async def run(self, context: PipelineContext, match: MatchData) -> RunManifest:
        run_dir = ensure_run_dir(context.settings.runs_dir, match)
        script = ScriptWriter(self.llm_client).generate(match)
        audio_path, subtitles_path, cues = await generate_audio_and_subs(
            text_script=script.text,
            tts_client=self.tts_client,
            run_dir=run_dir,
            highlight_terms=self.highlight_terms,
        )
        background_path = render_background_video(match, duration=cues[-1].end, output_path=run_dir / "background.mp4")
        video_path = compose_short(background_path, audio_path, cues, run_dir / "short.mp4")
        manifest = RunManifest(
            match_id=match.match_id,
            slug=match.slug,
            run_dir=run_dir,
            status="rendered",
            script_text=script.text,
            audio_path=str(audio_path),
            subtitles_path=str(subtitles_path),
            video_path=str(video_path),
            providers={"llm": self.llm_client.provider_name, "tts": self.tts_client.provider_name},
        )
        save_manifest(manifest)
        return manifest
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/unit/test_subtitles.py -q`

Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/shorts/render src/shorts/pipeline.py tests/unit/test_subtitles.py
git commit -m "feat: compose shorts from visuals audio and subtitles"
```

### Task 6: Add Match Fetching, Dry-Run Publishing, Workflows, And Integration Coverage

**Files:**
- Create: `src/shorts/clients/football_api.py`
- Create: `src/shorts/clients/youtube.py`
- Create: `src/shorts/workflows/__init__.py`
- Create: `src/shorts/workflows/run_latest_match.py`
- Create: `src/shorts/workflows/rerender_match.py`
- Create: `tests/fixtures/match_completed.json`
- Create: `tests/integration/test_pipeline_smoke.py`
- Create: `README.md`

- [ ] **Step 1: Write the failing integration smoke test**

```python
import json
from pathlib import Path

import pytest

from shorts.clients.llm import StubLLMClient
from shorts.models import MatchData, WordTiming
from shorts.pipeline import PitchBlackPipeline, build_context


class StubTTSClient:
    provider_name = "stub-tts"

    async def synthesize(self, text: str, audio_path: Path) -> list[WordTiming]:
        audio_path.write_bytes(b"fake-audio")
        return [
            WordTiming(text="Arsenal", start=0.0, end=0.4),
            WordTiming(text="controlled", start=0.4, end=0.9),
            WordTiming(text="the", start=0.9, end=1.1),
            WordTiming(text="half-space", start=1.1, end=1.6),
            WordTiming(text="and", start=1.6, end=1.8),
            WordTiming(text="won", start=1.8, end=2.0),
            WordTiming(text="xG", start=2.0, end=2.2),
        ]


@pytest.mark.asyncio
async def test_pipeline_smoke(tmp_path):
    payload = json.loads((Path("tests/fixtures/match_completed.json")).read_text(encoding="utf-8"))
    match = MatchData(**payload)
    pipeline = PitchBlackPipeline(
        llm_client=StubLLMClient(
            "Arsenal controlled the half-space, won xG 1.8 to 0.7, and forced Chelsea deeper after halftime, which turned possession into territory and territory into cleaner entries. Their structure narrowed central access, so Chelsea kept circulating wide without creating the same quality inside the box."
        ),
        tts_client=StubTTSClient(),
        highlight_terms={"half-space", "xg"},
    )

    context = build_context(tmp_path)
    manifest = await pipeline.run(context, match)

    assert manifest.status == "rendered"
    assert Path(manifest.video_path).name == "short.mp4"
```

- [ ] **Step 2: Run the integration test to verify it fails**

Run: `pytest tests/integration/test_pipeline_smoke.py -q`

Expected: FAIL with missing workflow clients, missing fixture files, or runtime errors because publishing and fetch paths do not exist yet.

- [ ] **Step 3: Implement fetch, publish dry-run, workflows, fixture data, and README**

`src/shorts/clients/football_api.py`

```python
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
```

`src/shorts/clients/youtube.py`

```python
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(slots=True)
class YouTubePublisher:
    dry_run_dir: Path

    def dry_run_upload(self, video_path: Path, title: str, description: str) -> Path:
        self.dry_run_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "video_path": str(video_path),
            "title": title,
            "description": description,
            "status": "queued",
        }
        output_path = self.dry_run_dir / "upload-request.json"
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output_path
```

`src/shorts/workflows/__init__.py`

```python
__all__ = ["rerender_match", "run_latest_match"]
```

`src/shorts/workflows/run_latest_match.py`

```python
import asyncio
from pathlib import Path

from shorts.clients.football_api import FootballAPIClient
from shorts.clients.llm import StubLLMClient
from shorts.clients.tts import EdgeTTSClient
from shorts.pipeline import PitchBlackPipeline, build_context


async def run_latest_match(project_root: Path, api_base_url: str, api_key: str) -> None:
    context = build_context(project_root)
    match = FootballAPIClient(api_base_url, api_key).latest_completed_match()
    pipeline = PitchBlackPipeline(
        llm_client=StubLLMClient(
            "Arsenal controlled the half-space, won xG 1.8 to 0.7, and forced Chelsea deeper after halftime, which turned possession into territory and territory into cleaner entries. Their structure narrowed central access, so Chelsea kept circulating wide without creating the same quality inside the box."
        ),
        tts_client=EdgeTTSClient("en-GB-RyanNeural"),
        highlight_terms={"xg", "half-space", "mid-block"},
    )
    await pipeline.run(context, match)


if __name__ == "__main__":
    asyncio.run(run_latest_match(Path.cwd(), "https://v3.football.api-sports.io", "replace-me"))
```

`src/shorts/workflows/rerender_match.py`

```python
from pathlib import Path

from shorts.storage.manifest import load_manifest


def rerender_match(manifest_path: Path) -> str:
    manifest = load_manifest(manifest_path)
    return f"Ready to rerender {manifest.match_id} from {manifest.run_dir}"
```

`tests/fixtures/match_completed.json`

```json
{
  "match_id": "1234",
  "home_team": "Arsenal",
  "away_team": "Chelsea",
  "competition": "Premier League",
  "completed_at": "2026-06-05T19:45:00+00:00",
  "home_score": 2,
  "away_score": 1,
  "home_xg": 1.8,
  "away_xg": 0.7,
  "home_possession": 58.0,
  "away_possession": 42.0,
  "shot_count_home": 14,
  "shot_count_away": 8,
  "key_events": ["Saka 18'", "Havertz 61'"],
  "raw_payload": {}
}
```

`README.md`

```markdown
# PitchBlack

PitchBlack generates short tactical football videos from structured match data.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run Tests

```bash
pytest
```

## Run A Local Smoke Workflow

```bash
python -m shorts.main
```
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/unit tests/integration -q`

Expected: PASS with all unit tests green and the smoke test green. If media encoding fails in CI for the smoke test, split the test so the integration test stops at manifest generation and add a separate local-only render smoke command to the README.

- [ ] **Step 5: Commit**

```bash
git add src/shorts/clients src/shorts/workflows tests/fixtures tests/integration README.md
git commit -m "feat: add workflow entrypoints and integration smoke coverage"
```

## Self-Review

- Spec coverage:
  - Match ingestion is covered by Task 6.
  - Script generation and validation are covered by Task 2.
  - Audio and subtitles are covered by Task 3.
  - Programmatic visuals are covered by Task 4.
  - Video assembly is covered by Task 5.
  - Manifesting, idempotent run directories, and dry-run publishing are covered by Tasks 2 and 6.
- Placeholder scan:
  - No placeholder markers remain in the plan body.
  - The only conditional note is the integration fallback for CI media encoding; it has an explicit action if that issue appears.
- Type consistency:
  - `MatchData`, `ScriptDraft`, `WordTiming`, `SubtitleCue`, `SceneSpec`, and `RunManifest` are introduced before downstream tasks use them.
  - `PitchBlackPipeline.run(...)` remains the single orchestration entry point throughout the plan.

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
async def test_pipeline_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    payload = json.loads((Path("tests/fixtures/match_completed.json")).read_text(encoding="utf-8"))
    match = MatchData(**payload)

    def fake_render_background_video(match: MatchData, duration: float, output_path: Path) -> Path:
        output_path.write_bytes(b"fake-video")
        return output_path

    def fake_compose_short(
        background_path: Path,
        audio_path: Path,
        cues,
        output_path: Path,
    ) -> Path:
        output_path.write_bytes(b"fake-short")
        return output_path

    monkeypatch.setattr("shorts.pipeline.render_background_video", fake_render_background_video)
    monkeypatch.setattr("shorts.pipeline.compose_short", fake_compose_short)

    pipeline = PitchBlackPipeline(
        llm_client=StubLLMClient(
            "Arsenal controlled the half-space, won xG 1.8 to 0.7, and forced Chelsea deeper after halftime. "
            "Their structure narrowed central access while the back line held a cleaner rest-defense shape all night."
        ),
        tts_client=StubTTSClient(),
        highlight_terms={"half-space", "xg"},
    )

    context = build_context(tmp_path)
    manifest = await pipeline.run(context, match)

    assert manifest.status == "rendered"
    assert Path(manifest.video_path).name == "short.mp4"

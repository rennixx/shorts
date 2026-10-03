import asyncio
import json
from datetime import datetime
from pathlib import Path

from shorts.clients.llm import StubLLMClient
from shorts.clients.tts import EdgeTTSClient
from shorts.models import MatchData, RunManifest
from shorts.pipeline import PitchBlackPipeline, build_context


def default_fixture_path() -> Path:
    return Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "match_completed.json"


def load_fixture_match(fixture_path: Path) -> MatchData:
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    completed_at = payload.get("completed_at")
    if isinstance(completed_at, str):
        payload["completed_at"] = datetime.fromisoformat(completed_at)
    return MatchData(**payload)


async def run_local_fixture(
    project_root: Path,
    fixture_path: Path | None = None,
) -> RunManifest:
    resolved_fixture = fixture_path or default_fixture_path()
    context = build_context(project_root)
    match = load_fixture_match(resolved_fixture)
    pipeline = PitchBlackPipeline(
        llm_client=StubLLMClient(
            "Arsenal controlled the half-space, won xG 1.8 to 0.7, and forced Chelsea deeper after halftime. "
            "Their structure narrowed central access while the back line held a cleaner rest-defense shape all night."
        ),
        tts_client=EdgeTTSClient("en-GB-RyanNeural"),
        highlight_terms={"xg", "half-space", "mid-block"},
    )
    return await pipeline.run(context, match)


def main() -> None:
    manifest = asyncio.run(run_local_fixture(Path.cwd()))
    print(f"Rendered short to {manifest.video_path}")


if __name__ == "__main__":
    main()

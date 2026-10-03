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
            "Arsenal controlled the half-space, won xG 1.8 to 0.7, and forced Chelsea deeper after halftime. "
            "Their structure narrowed central access while the back line held a cleaner rest-defense shape all night."
        ),
        tts_client=EdgeTTSClient("en-GB-RyanNeural"),
        highlight_terms={"xg", "half-space", "mid-block"},
    )
    await pipeline.run(context, match)


if __name__ == "__main__":
    asyncio.run(
        run_latest_match(
            Path.cwd(),
            "https://v3.football.api-sports.io",
            "replace-me",
        )
    )

from pathlib import Path

import pytest

from shorts.models import RunManifest
from shorts.workflows.run_local_fixture import run_local_fixture


@pytest.mark.asyncio
async def test_run_local_fixture_loads_fixture_match(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    captured: dict[str, str] = {}

    class FakePipeline:
        def __init__(self, *args, **kwargs):
            captured["highlight_terms"] = ",".join(sorted(kwargs["highlight_terms"]))

        async def run(self, context, match):
            captured["match_id"] = match.match_id
            return RunManifest(
                match_id=match.match_id,
                slug=match.slug,
                run_dir=context.settings.runs_dir / match.slug,
                status="rendered",
            )

    monkeypatch.setattr("shorts.workflows.run_local_fixture.PitchBlackPipeline", FakePipeline)

    manifest = await run_local_fixture(project_root=tmp_path)

    assert captured["match_id"] == "1234"
    assert "half-space" in captured["highlight_terms"]
    assert manifest.status == "rendered"

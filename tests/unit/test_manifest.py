from pathlib import Path

from shorts.models import RunManifest
from shorts.storage.manifest import load_manifest, save_manifest


def test_manifest_round_trip(tmp_path: Path):
    manifest = RunManifest(
        match_id="1234",
        slug="1234-arsenal-vs-chelsea",
        run_dir=tmp_path,
        status="rendered",
        script_text="Arsenal controlled the half-space and finished with the stronger xG profile.",
    )

    save_manifest(manifest)
    loaded = load_manifest(tmp_path / "manifest.json")

    assert loaded.match_id == manifest.match_id
    assert loaded.status == "rendered"

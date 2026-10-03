from pathlib import Path

from shorts.storage.manifest import load_manifest


def rerender_match(manifest_path: Path) -> str:
    manifest = load_manifest(manifest_path)
    return f"Ready to rerender {manifest.match_id} from {manifest.run_dir}"

from dataclasses import asdict
import json
from pathlib import Path

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

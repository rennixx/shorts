from dataclasses import dataclass
import json
from pathlib import Path


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

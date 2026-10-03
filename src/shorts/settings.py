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

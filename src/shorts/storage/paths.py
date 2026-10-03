from pathlib import Path

from shorts.models import MatchData


def build_run_dir(runs_dir: Path, match: MatchData) -> Path:
    return runs_dir / match.slug


def ensure_run_dir(runs_dir: Path, match: MatchData) -> Path:
    run_dir = build_run_dir(runs_dir, match)
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir

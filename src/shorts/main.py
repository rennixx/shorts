from pathlib import Path

from shorts.pipeline import build_context


def main() -> None:
    context = build_context(Path.cwd())
    print(f"PitchBlack ready at {context.project_root}")


if __name__ == "__main__":
    main()

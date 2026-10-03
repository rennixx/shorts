from pathlib import Path

import ffmpeg


def normalize_short(input_path: Path, output_path: Path) -> Path:
    (
        ffmpeg.input(str(input_path))
        .output(
            str(output_path),
            vcodec="libx264",
            acodec="aac",
            af="volume=4dB",
            strict="-2",
            pix_fmt="yuv420p",
            movflags="+faststart",
        )
        .overwrite_output()
        .run(quiet=True)
    )
    return output_path

from pathlib import Path

from shorts.render.compositor import finalize_short


def test_finalize_short_replaces_output_with_temp_file(tmp_path: Path):
    temp_output = tmp_path / "assembled-temp.mp4"
    final_output = tmp_path / "short.mp4"
    temp_output.write_bytes(b"new-video")
    final_output.write_bytes(b"old-video")

    result = finalize_short(temp_output, final_output)

    assert result == final_output
    assert final_output.read_bytes() == b"new-video"
    assert not temp_output.exists()

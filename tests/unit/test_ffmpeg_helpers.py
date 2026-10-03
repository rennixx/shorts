from pathlib import Path

from shorts.render.ffmpeg_helpers import normalize_short


def test_normalize_short_enables_legacy_aac_support(monkeypatch):
    captured: dict[str, object] = {}

    class FakeCommand:
        def output(self, output_path: str, **kwargs):
            captured["output_path"] = output_path
            captured["kwargs"] = kwargs
            return self

        def overwrite_output(self):
            captured["overwrite_output"] = True
            return self

        def run(self, quiet: bool):
            captured["quiet"] = quiet
            return None

    def fake_input(path: str):
        captured["input_path"] = path
        return FakeCommand()

    monkeypatch.setattr("shorts.render.ffmpeg_helpers.ffmpeg.input", fake_input)

    normalize_short(Path("input.mp4"), Path("output.mp4"))

    assert captured["kwargs"]["acodec"] == "aac"
    assert captured["kwargs"]["af"] == "volume=4dB"
    assert captured["kwargs"]["strict"] == "-2"

from pathlib import Path

from shorts.clients.tts import TTSClient
from shorts.models import SubtitleCue, WordTiming


def build_subtitle_cues(
    words: list[WordTiming],
    highlight_terms: set[str],
    max_words_per_cue: int = 3,
) -> list[SubtitleCue]:
    cues: list[SubtitleCue] = []
    bucket: list[WordTiming] = []

    for word in words:
        bucket.append(word)
        if len(bucket) == max_words_per_cue:
            cues.append(_build_cue(bucket, highlight_terms))
            bucket = []

    if bucket:
        cues.append(_build_cue(bucket, highlight_terms))

    return cues


def _build_cue(words: list[WordTiming], highlight_terms: set[str]) -> SubtitleCue:
    lowered_terms = {term.lower() for term in highlight_terms}
    text = " ".join(word.text for word in words)
    highlighted = [word.text for word in words if word.text.lower() in lowered_terms]
    return SubtitleCue(
        start=words[0].start,
        end=words[-1].end,
        text=text,
        highlighted_words=highlighted,
    )


def format_vtt(cues: list[SubtitleCue]) -> str:
    body = ["WEBVTT", ""]
    for cue in cues:
        body.append(f"{_fmt(cue.start)} --> {_fmt(cue.end)}")
        body.append(cue.text)
        body.append("")
    return "\n".join(body)


def _fmt(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:06.3f}".replace(".", ",")


async def generate_audio_and_subs(
    text_script: str,
    tts_client: TTSClient,
    run_dir: Path,
    highlight_terms: set[str],
) -> tuple[Path, Path, list[SubtitleCue]]:
    audio_path = run_dir / "voice.mp3"
    subtitles_path = run_dir / "subtitles.vtt"
    timings = await tts_client.synthesize(text_script, audio_path)
    cues = build_subtitle_cues(timings, highlight_terms=highlight_terms)
    subtitles_path.write_text(format_vtt(cues), encoding="utf-8")
    return audio_path, subtitles_path, cues

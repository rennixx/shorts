from pathlib import Path
import shutil

try:
    from moviepy.editor import AudioFileClip, CompositeVideoClip, ImageClip, VideoFileClip
except ImportError:
    from moviepy import AudioFileClip, CompositeVideoClip, ImageClip, VideoFileClip

from shorts.models import SubtitleCue
from shorts.render.subtitles import render_subtitle_card


def _clip_with_audio(clip, audio):
    if hasattr(clip, "with_audio"):
        return clip.with_audio(audio)
    return clip.set_audio(audio)


def _clip_with_start(clip, value: float):
    if hasattr(clip, "with_start"):
        return clip.with_start(value)
    return clip.set_start(value)


def _clip_with_duration(clip, value: float):
    if hasattr(clip, "with_duration"):
        return clip.with_duration(value)
    return clip.set_duration(value)


def _clip_with_position(clip, value):
    if hasattr(clip, "with_position"):
        return clip.with_position(value)
    return clip.set_position(value)


def finalize_short(temp_output: Path, output_path: Path) -> Path:
    if output_path.exists():
        output_path.unlink()
    shutil.move(str(temp_output), str(output_path))
    return output_path


def compose_short(
    background_path: Path,
    audio_path: Path,
    cues: list[SubtitleCue],
    output_path: Path,
) -> Path:
    background = VideoFileClip(str(background_path))
    audio = AudioFileClip(str(audio_path))
    overlays = [_clip_with_audio(background, audio)]

    for index, cue in enumerate(cues):
        card_path = output_path.parent / f"subtitle-{index:03d}.png"
        render_subtitle_card(cue, card_path)
        clip = ImageClip(str(card_path))
        clip = _clip_with_start(clip, cue.start)
        clip = _clip_with_duration(clip, max(cue.end - cue.start, 0.15))
        clip = _clip_with_position(clip, ("center", 1440))
        overlays.append(clip)

    composite = CompositeVideoClip(overlays, size=background.size)
    temp_output = output_path.parent / "assembled-temp.mp4"
    composite.write_videofile(
        str(temp_output),
        codec="libx264",
        audio_codec="aac",
        fps=24,
        preset="medium",
        logger=None,
    )
    composite.close()
    background.close()
    audio.close()
    for overlay in overlays[1:]:
        overlay.close()
    return finalize_short(temp_output, output_path)

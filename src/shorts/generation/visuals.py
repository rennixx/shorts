from pathlib import Path

try:
    from moviepy.editor import ColorClip, CompositeVideoClip, ImageClip
except ImportError:
    from moviepy import ColorClip, CompositeVideoClip, ImageClip
import math

from PIL import Image, ImageDraw, ImageFont

from shorts.generation.scenes import build_scene_plan
from shorts.models import MatchData, SceneSpec


VIDEO_SIZE = (1080, 1920)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PINK = (255, 20, 147)
SOFT_PINK = (255, 110, 190)
GRID = (36, 10, 28)
MUTED = (170, 170, 170)


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


def _clip_with_opacity(clip, value: float):
    if hasattr(clip, "with_opacity"):
        return clip.with_opacity(value)
    return clip.set_opacity(value)


def _load_font(size: int, mono: bool = False, bold: bool = False):
    candidates = []
    if mono and bold:
        candidates.extend(
            [
                "C:/Windows/Fonts/consolab.ttf",
                "C:/Windows/Fonts/lucon.ttf",
            ]
        )
    elif mono:
        candidates.extend(
            [
                "C:/Windows/Fonts/consola.ttf",
                "C:/Windows/Fonts/lucon.ttf",
            ]
        )
    elif bold:
        candidates.extend(
            [
                "C:/Windows/Fonts/segoeuib.ttf",
                "C:/Windows/Fonts/arialbd.ttf",
            ]
        )
    else:
        candidates.extend(
            [
                "C:/Windows/Fonts/segoeui.ttf",
                "C:/Windows/Fonts/arial.ttf",
            ]
        )

    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def _draw_base(image: Image.Image) -> ImageDraw.ImageDraw:
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, VIDEO_SIZE[0], VIDEO_SIZE[1]), fill=BLACK)

    for x in range(60, VIDEO_SIZE[0], 80):
        draw.line((x, 0, x, VIDEO_SIZE[1]), fill=GRID, width=1)
    for y in range(120, VIDEO_SIZE[1], 120):
        draw.line((0, y, VIDEO_SIZE[0], y), fill=GRID, width=1)

    draw.rectangle((70, 120, 1010, 1800), outline=(90, 16, 60), width=3)
    draw.line((110, 1650, 970, 1650), fill=(80, 18, 56), width=2)
    draw.ellipse((820, 120, 1040, 340), outline=(80, 18, 56), width=3)
    return draw


def _draw_corner_label(draw: ImageDraw.ImageDraw, text: str) -> None:
    font = _load_font(34, mono=True, bold=True)
    draw.rounded_rectangle((110, 150, 360, 210), radius=18, fill=(22, 22, 22), outline=PINK, width=2)
    draw.text((132, 165), text.upper(), font=font, fill=PINK)


def _draw_team_pair(draw: ImageDraw.ImageDraw, left: str, right: str, top: int) -> None:
    name_font = _load_font(44, bold=True)
    draw.text((120, top), left.upper(), font=name_font, fill=WHITE)
    draw.text((120, top + 56), right.upper(), font=name_font, fill=SOFT_PINK)


def _draw_score_hero(draw: ImageDraw.ImageDraw, score: str, top: int) -> None:
    score_font = _load_font(180, mono=True, bold=True)
    draw.text((120, top), score, font=score_font, fill=WHITE)
    draw.text((126, top + 12), score, font=score_font, fill=PINK)


def _draw_stat_bar(draw: ImageDraw.ImageDraw, top: int, label: str, home_value: float | int | None, away_value: float | int | None) -> None:
    label_font = _load_font(30, mono=True, bold=True)
    value_font = _load_font(54, bold=True)
    bar_left = 120
    bar_right = 960
    width = bar_right - bar_left
    home = float(home_value or 0)
    away = float(away_value or 0)
    total = home + away or 1.0
    home_width = int(width * (home / total))

    draw.text((120, top), label.upper(), font=label_font, fill=PINK)
    draw.rounded_rectangle((120, top + 56, 960, top + 118), radius=18, fill=(20, 20, 20), outline=(60, 60, 60), width=2)
    draw.rounded_rectangle((120, top + 56, 120 + home_width, top + 118), radius=18, fill=PINK)
    draw.text((120, top + 132), f"{home:g}", font=value_font, fill=WHITE)
    draw.text((848, top + 132), f"{away:g}", font=value_font, fill=SOFT_PINK)


def _draw_event_cards(draw: ImageDraw.ImageDraw, events: list[str], top: int) -> None:
    font = _load_font(32, bold=True)
    for index, event in enumerate(events):
        y = top + (index * 96)
        draw.rounded_rectangle((120, y, 960, y + 72), radius=20, fill=(16, 16, 16), outline=(80, 80, 80), width=2)
        draw.text((150, y + 18), event, font=font, fill=WHITE)


def _draw_tag_row(draw: ImageDraw.ImageDraw, tags: list[str], top: int) -> None:
    font = _load_font(28, mono=True, bold=True)
    x = 120
    for tag in tags:
        width = int(draw.textlength(tag.upper(), font=font)) + 40
        draw.rounded_rectangle((x, top, x + width, top + 54), radius=18, fill=(18, 18, 18), outline=PINK, width=2)
        draw.text((x + 20, top + 14), tag.upper(), font=font, fill=PINK)
        x += width + 18


def render_background_video(match: MatchData, duration: float, output_path: Path) -> Path:
    base = ColorClip(size=VIDEO_SIZE, color=BLACK, duration=duration)
    overlays = []

    for scene in build_scene_plan(match, duration):
        frame_path = output_path.parent / f"{scene.name}.png"
        _render_scene_image(scene, frame_path)
        clip = ImageClip(str(frame_path))
        clip = _clip_with_start(clip, scene.start)
        clip = _clip_with_duration(clip, scene.end - scene.start)
        clip = _clip_with_position(clip, ("center", "center"))
        overlays.append(clip)

        accent = ColorClip(size=(1080, 4), color=PINK, duration=scene.end - scene.start)
        accent = _clip_with_start(accent, scene.start)
        accent = _clip_with_position(
            accent,
            lambda t, start=scene.start: (0, 1480 + int(math.sin((t - start) * 1.8) * 12)),
        )
        accent = _clip_with_opacity(accent, 0.75)
        overlays.append(accent)

    video = CompositeVideoClip([base, *overlays], size=VIDEO_SIZE)
    video.write_videofile(
        str(output_path),
        codec="libx264",
        fps=24,
        audio=False,
        preset="medium",
        logger=None,
    )
    video.close()
    base.close()
    for overlay in overlays:
        overlay.close()
    return output_path


def _render_scene_image(scene: SceneSpec, output_path: Path) -> None:
    image = Image.new("RGB", VIDEO_SIZE, BLACK)
    draw = _draw_base(image)
    _draw_corner_label(draw, scene.name)

    if scene.name == "intro":
        _draw_team_pair(draw, scene.payload["home_team"], scene.payload["away_team"], 380)
        _draw_score_hero(draw, scene.payload["score"], 560)
        comp_font = _load_font(34, mono=True, bold=True)
        draw.text((120, 850), scene.payload["competition"].upper(), font=comp_font, fill=MUTED)
        draw.rounded_rectangle((120, 980, 960, 1120), radius=28, fill=(14, 14, 14), outline=(60, 24, 45), width=2)
        draw.text((150, 1018), "TACTICAL SNAPSHOT", font=_load_font(54, bold=True), fill=WHITE)
    elif scene.name == "score":
        draw.text((120, 360), scene.payload["label"].upper(), font=_load_font(34, mono=True, bold=True), fill=PINK)
        _draw_score_hero(draw, scene.payload["score"], 450)
        _draw_event_cards(draw, scene.payload.get("events", []), 860)
    elif scene.name == "xg":
        draw.text((120, 360), "CHANCE QUALITY", font=_load_font(34, mono=True, bold=True), fill=PINK)
        _draw_stat_bar(draw, 500, "xG", scene.payload["home"], scene.payload["away"])
        draw.text((120, 860), "BETTER ACCESS, BETTER SHOTS", font=_load_font(62, bold=True), fill=WHITE)
        draw.text((120, 950), "The cleaner team shape usually wins the xG map.", font=_load_font(34), fill=MUTED)
    elif scene.name == "territory":
        draw.text((120, 360), "FIELD TILT", font=_load_font(34, mono=True, bold=True), fill=PINK)
        _draw_stat_bar(draw, 500, scene.payload["possession_label"], scene.payload["home"], scene.payload["away"])
        _draw_stat_bar(draw, 820, "Shots", scene.payload["shots_home"], scene.payload["shots_away"])
        draw.text((120, 1150), "Territory is pressure over time.", font=_load_font(56, bold=True), fill=WHITE)
    elif scene.name == "closing":
        draw.text((120, 420), scene.payload["claim"].upper(), font=_load_font(74, bold=True), fill=WHITE)
        draw.text((120, 620), "ONE TAKEAWAY", font=_load_font(34, mono=True, bold=True), fill=PINK)
        _draw_tag_row(draw, scene.payload.get("tags", []), 760)
        draw.text((120, 980), "PITCHBLACK", font=_load_font(52, mono=True, bold=True), fill=SOFT_PINK)

    image.save(output_path)

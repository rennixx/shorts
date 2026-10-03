from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from shorts.models import SubtitleCue
from shorts.render.keyword_highlighter import collect_highlight_tokens


def render_subtitle_card(cue: SubtitleCue, output_path: Path) -> Path:
    image = Image.new("RGBA", (1080, 260), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    font = _load_font(58)
    x = 90
    tokens = cue.text.split()
    highlights = collect_highlight_tokens(cue)
    text_width = int(sum(draw.textlength(token + " ", font=font) for token in tokens))
    card_left = max(40, (1080 - text_width) // 2 - 40)
    card_right = min(1040, card_left + text_width + 80)

    draw.rounded_rectangle(
        (card_left, 74, card_right, 186),
        radius=30,
        fill=(0, 0, 0, 200),
        outline=(255, 20, 147, 180),
        width=2,
    )
    x = card_left + 34

    for token in tokens:
        fill = (255, 20, 147, 255) if token.lower() in highlights else (255, 255, 255, 255)
        draw.text((x, 98), token, font=font, fill=fill)
        x += draw.textlength(token + " ", font=font)

    image.save(output_path)
    return output_path


def _load_font(size: int):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()

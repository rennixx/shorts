from shorts.models import SubtitleCue
from shorts.render.keyword_highlighter import collect_highlight_tokens


def test_collect_highlight_tokens_matches_case_insensitively():
    cue = SubtitleCue(
        start=0.0,
        end=1.0,
        text="Arsenal owned the half-space",
        highlighted_words=["half-space"],
    )

    assert collect_highlight_tokens(cue) == {"half-space"}

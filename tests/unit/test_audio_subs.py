from shorts.generation.audio_subs import build_subtitle_cues
from shorts.models import WordTiming


def test_build_subtitle_cues_groups_at_most_three_words():
    words = [
        WordTiming(text="Arsenal", start=0.0, end=0.4),
        WordTiming(text="controlled", start=0.4, end=0.9),
        WordTiming(text="the", start=0.9, end=1.1),
        WordTiming(text="half-space", start=1.1, end=1.7),
        WordTiming(text="battle", start=1.7, end=2.1),
    ]

    cues = build_subtitle_cues(words, highlight_terms={"half-space"})

    assert [cue.text for cue in cues] == [
        "Arsenal controlled the",
        "half-space battle",
    ]
    assert cues[1].highlighted_words == ["half-space"]

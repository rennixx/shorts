from shorts.models import SubtitleCue


def collect_highlight_tokens(cue: SubtitleCue) -> set[str]:
    return {token.lower() for token in cue.highlighted_words}

from dataclasses import dataclass

from shorts.clients.llm import LLMClient
from shorts.models import MatchData, ScriptDraft


BANNED_PHRASES = {
    "unbelievable scenes",
    "crazy scenes",
    "insane",
    "goat",
    "what a game",
}


def validate_script(text: str) -> list[str]:
    errors: list[str] = []
    lowered = text.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            errors.append(f"contains banned phrase: {phrase}")
    word_count = len(text.split())
    if word_count < 20 or word_count > 60:
        errors.append(f"word count out of range: {word_count}")
    return errors


@dataclass(slots=True)
class ScriptWriter:
    llm_client: LLMClient

    def build_prompt(self, match: MatchData) -> str:
        key_events = ", ".join(match.key_events) or "None"
        return (
            "Write one tactical football short in 45-55 words. "
            f"Match: {match.home_team} vs {match.away_team}. "
            f"Score: {match.home_score}-{match.away_score}. "
            f"xG: {match.home_xg}-{match.away_xg}. "
            f"Possession: {match.home_possession}-{match.away_possession}. "
            f"Events: {key_events}."
        )

    def generate(self, match: MatchData) -> ScriptDraft:
        prompt = self.build_prompt(match)
        text = self.llm_client.generate_text(prompt).strip()
        draft = ScriptDraft(text=text, provider=self.llm_client.provider_name)
        errors = validate_script(draft.text)
        if errors:
            raise ValueError("; ".join(errors))
        return draft

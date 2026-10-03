from dataclasses import dataclass
from typing import Protocol


class LLMClient(Protocol):
    provider_name: str

    def generate_text(self, prompt: str) -> str:
        ...


@dataclass(slots=True)
class StubLLMClient:
    response_text: str
    provider_name: str = "stub-llm"

    def generate_text(self, prompt: str) -> str:
        return self.response_text

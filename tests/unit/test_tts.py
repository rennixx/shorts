from pathlib import Path

import pytest

from shorts.clients.tts import EdgeTTSClient
from shorts.models import WordTiming


@pytest.mark.asyncio
async def test_edge_tts_client_requests_word_boundaries(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    captured: dict[str, object] = {}

    class FakeCommunicate:
        def __init__(self, text: str, voice: str, **kwargs):
            captured["text"] = text
            captured["voice"] = voice
            captured["kwargs"] = kwargs

        async def stream(self):
            yield {"type": "audio", "data": b"abc"}
            yield {
                "type": "WordBoundary",
                "offset": 0,
                "duration": 5_000_000,
                "text": "Arsenal",
            }

    monkeypatch.setattr("shorts.clients.tts.edge_tts.Communicate", FakeCommunicate)

    client = EdgeTTSClient("en-GB-RyanNeural")
    timings = await client.synthesize("Arsenal", tmp_path / "voice.mp3")

    assert captured["kwargs"]["boundary"] == "WordBoundary"
    assert timings == [WordTiming(text="Arsenal", start=0.0, end=0.5)]

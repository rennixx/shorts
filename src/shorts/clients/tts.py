from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import edge_tts

from shorts.models import WordTiming


class TTSClient(Protocol):
    provider_name: str

    async def synthesize(self, text: str, audio_path: Path) -> list[WordTiming]:
        ...


@dataclass(slots=True)
class EdgeTTSClient:
    voice: str
    rate: str = "-5%"
    volume: str = "+35%"
    pitch: str = "+0Hz"
    provider_name: str = "edge-tts"

    async def synthesize(self, text: str, audio_path: Path) -> list[WordTiming]:
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice,
            rate=self.rate,
            volume=self.volume,
            pitch=self.pitch,
            boundary="WordBoundary",
        )
        timings: list[WordTiming] = []

        with audio_path.open("wb") as handle:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    handle.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    start = chunk["offset"] / 10_000_000
                    duration = chunk["duration"] / 10_000_000
                    timings.append(
                        WordTiming(
                            text=chunk["text"],
                            start=start,
                            end=start + duration,
                        )
                    )

        return timings

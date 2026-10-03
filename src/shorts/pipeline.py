from dataclasses import dataclass
from pathlib import Path

from shorts.clients.llm import LLMClient
from shorts.clients.tts import TTSClient
from shorts.generation.audio_subs import generate_audio_and_subs
from shorts.generation.script_writer import ScriptWriter
from shorts.generation.visuals import render_background_video
from shorts.models import MatchData, RunManifest
from shorts.render.compositor import compose_short
from shorts.settings import Settings
from shorts.storage.manifest import save_manifest
from shorts.storage.paths import ensure_run_dir


@dataclass(slots=True)
class PipelineContext:
    project_root: Path
    settings: Settings


def build_context(project_root: Path) -> PipelineContext:
    settings = Settings.from_root(project_root)
    settings.runs_dir.mkdir(parents=True, exist_ok=True)
    return PipelineContext(project_root=project_root, settings=settings)


@dataclass(slots=True)
class PitchBlackPipeline:
    llm_client: LLMClient
    tts_client: TTSClient
    highlight_terms: set[str]

    async def run(self, context: PipelineContext, match: MatchData) -> RunManifest:
        run_dir = ensure_run_dir(context.settings.runs_dir, match)
        script = ScriptWriter(self.llm_client).generate(match)
        audio_path, subtitles_path, cues = await generate_audio_and_subs(
            text_script=script.text,
            tts_client=self.tts_client,
            run_dir=run_dir,
            highlight_terms=self.highlight_terms,
        )
        duration = cues[-1].end if cues else 22.0
        background_path = render_background_video(
            match,
            duration=duration,
            output_path=run_dir / "background.mp4",
        )
        video_path = compose_short(background_path, audio_path, cues, run_dir / "short.mp4")
        manifest = RunManifest(
            match_id=match.match_id,
            slug=match.slug,
            run_dir=run_dir,
            status="rendered",
            script_text=script.text,
            audio_path=str(audio_path),
            subtitles_path=str(subtitles_path),
            video_path=str(video_path),
            providers={"llm": self.llm_client.provider_name, "tts": self.tts_client.provider_name},
        )
        save_manifest(manifest)
        return manifest

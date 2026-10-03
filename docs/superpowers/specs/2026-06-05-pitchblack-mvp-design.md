# PitchBlack MVP Design

## Summary

PitchBlack is a self-hosted pipeline that generates 20-25 second tactical football YouTube Shorts from structured match data. The MVP should be reliable, deterministic, and visually distinctive without depending on paid AI services to complete a render.

The product tone is clinical, analytical, and technology-forward. Each short should feel like a tactical data bulletin rather than a generic AI sports clip.

## Product Goal

Build a server-run Python pipeline that can:

1. Fetch completed match data.
2. Generate one concise tactical script.
3. Produce narration and timed subtitles.
4. Render programmatic football/data visuals.
5. Assemble a final 1080x1920 short.
6. Publish the result or queue it for review.

## MVP Decisions

### Canonical Architecture

The MVP will use a Python-first, self-hosted architecture. External AI providers are optional quality upgrades, not core dependencies.

The system must remain functional if optional AI video generation is unavailable.

### Visual Strategy

The MVP uses a hybrid visual strategy with a strong bias toward programmatic visuals:

- Programmatic visuals are the default backbone of every short.
- AI-generated visuals may be added later as optional augmentation.
- The pipeline must still complete successfully without AI-generated visuals.

The target ratio is approximately 80% programmatic visuals and 20% optional AI augmentation once enhancement providers are introduced.

### Content Strategy

Each short should communicate exactly one tactical takeaway about a match. Scripts should be grounded in available match data such as xG, possession, shot profile, or key events.

The MVP must avoid overclaiming. If the source data is weak or incomplete, the system should either generate a lower-confidence script template or skip publishing entirely.

## Brand Direction

### Tone

- Clinical
- Tactical
- Serious
- Minimal
- No motivational filler
- No generic sports hype

### Visual Identity

- Background: OLED black `#000000`
- Primary text: white `#FFFFFF`
- Accent color: deep pink `#FF1493`
- Typography: pixel-inspired display font for labels and accents

For readability, spoken subtitles should use a clean, high-legibility font. The design should preserve the pixel identity for labels, stat chips, scene markers, and highlighted keywords rather than forcing the full spoken subtitle track into a novelty font.

### Visual Language

The visual system should feel like a live tactical dashboard. Preferred motifs include:

- Pitch outlines
- Passing lanes
- Heat zones
- Data nodes
- Stat pulses
- Minimal camera drift
- Sparse transitions

Disallowed visual patterns:

- Stock player footage
- Generic motivational sports edits
- Random abstract AI motion with no football meaning
- Overcrowded overlays that reduce readability on mobile

## System Architecture

### Execution Model

The system runs on a self-hosted server. The orchestration layer may be cron-driven, service-driven, or manually triggered during development, but the internal pipeline design should remain independent from the scheduler.

### Core Pipeline

1. `fetch_match_data`
   Retrieve match result, scoreline, teams, competition, xG, possession, shots, and key events.

2. `generate_script`
   Create a short analytical script of roughly 45-55 words with one clear claim and 2-3 supporting facts.

3. `generate_audio_and_subs`
   Produce a narration file and timestamped subtitle output from the script.

4. `render_programmatic_visuals`
   Generate a full-length background animation using code-driven football/data visuals.

5. `assemble_video`
   Combine visuals, audio, subtitles, highlighted terms, and export settings into the final 9:16 short.

6. `publish_or_queue`
   Upload directly or save the final output plus metadata for manual review and retries.

### Provider Model

External services should be isolated behind adapters so free test providers can be replaced later with higher-quality providers without reshaping the rest of the pipeline.

Likely provider categories:

- Football data provider
- LLM provider
- TTS provider
- Optional AI visual provider
- YouTube publishing provider

## Functional Requirements

### Match Data

The system must:

- Detect or receive completed matches to process.
- Normalize incoming data into one internal match model.
- Reject or downgrade runs where required fields are missing.

Minimum useful fields:

- Match identifier
- Teams
- Final score
- Competition
- Match completion timestamp
- xG or equivalent attacking quality metric if available
- Possession if available
- Shot count if available
- Key events if available

### Script Generation

The script generator must:

- Produce one tactical takeaway per short.
- Keep script length near the spoken target for 20-25 seconds.
- Avoid hype language, cliches, and empty intensity.
- Use factual support from available match data.

Recommended script structure:

- Hook
- Tactical claim
- Supporting statistic or event
- Closing insight

Hooks should vary across templates so the output does not feel mechanically repetitive.

### Audio and Subtitles

The narration module must:

- Produce speech audio from the approved script.
- Produce aligned subtitle timing data.
- Support swapping voice providers later.

Subtitle requirements:

- Center-safe placement
- Short phrase groupings, ideally 1-3 words
- Strong contrast
- Highlight key tactical terms in deep pink

### Programmatic Visuals

The visual renderer must:

- Generate a complete background video without external AI.
- Use football-relevant geometry and motion rather than generic animation.
- Support multiple reusable scene templates.

Recommended scene primitives:

- Animated pitch grid
- Passing lane lines
- Possession split cards
- xG emphasis panels
- Shot map dots
- Team name and score lockups
- Minimal transition wipes

### Video Assembly

The compositor must:

- Export 1080x1920 video.
- Align duration to narration length.
- Burn subtitles cleanly within safe mobile margins.
- Mix audio at a consistent target level.
- Produce a final MP4 artifact suitable for Shorts upload.

### Publishing

The publishing layer must:

- Track whether a short was rendered, queued, failed, or published.
- Prevent duplicate uploads for the same match unless explicitly rerun.
- Store title, description, tags, and publish result metadata.

## Reliability and Error Handling

The MVP should optimize for graceful failure over partial corruption.

Required behaviors:

- If match data is incomplete, skip publish and record the reason.
- If script generation fails, stop the run and record failure state.
- If optional AI visual generation fails, continue with programmatic-only visuals.
- If upload fails, keep the rendered assets and retry metadata.

Every run should produce a manifest containing:

- `match_id`
- Team names
- Script text
- Provider choices used
- Asset file paths
- Render duration
- Publish status
- Error reason if failed

## Testing Strategy

The MVP should be tested in layers:

### Unit Tests

- Data normalization
- Script validation rules
- Subtitle timing parsing
- Keyword highlighting logic
- Manifest generation

### Integration Tests

- End-to-end render from fixture match data
- TTS plus subtitle generation
- Final video assembly
- Publish dry-run path

### Manual QA

Before enabling automated publishing, verify:

- Audio length fits 20-25 seconds
- Text remains readable on mobile
- Subtitle safe margins are respected
- Highlight colors are correct
- Visual pacing matches the narration
- Final output feels consistent with the brand

## Recommended Repository Structure

```text
shorts/
  docs/
    superpowers/
      specs/
  config/
    voices.yaml
    prompts.yaml
    styles.yaml
  assets/
    fonts/
    overlays/
  src/
    shorts/
      __init__.py
      main.py
      pipeline.py
      models.py
      settings.py
      logging.py
      clients/
        football_api.py
        llm.py
        tts.py
        youtube.py
      generation/
        script_writer.py
        audio_subs.py
        visuals.py
        scenes.py
      render/
        compositor.py
        subtitles.py
        keyword_highlighter.py
        ffmpeg_helpers.py
      storage/
        paths.py
        manifest.py
      workflows/
        run_latest_match.py
        rerender_match.py
  tests/
    unit/
    integration/
    fixtures/
  runs/
    .gitkeep
  requirements.txt
  README.md
```

## File Responsibilities

- `clients/`: external service adapters and provider wrappers
- `generation/`: script, audio/subtitle generation, and programmatic scene creation
- `render/`: composition, subtitle rendering, and export helpers
- `storage/`: run manifests, paths, and idempotent file handling
- `workflows/`: operational entry points for automated and manual runs

This separation keeps provider churn isolated and preserves a stable internal pipeline.

## Future Upgrade Path

Later upgrades may include:

- Higher-quality paid TTS
- Higher-quality LLM script generation
- Optional Higgsfield or similar AI scene augmentation
- Multi-template storytelling by competition or match type
- Review queue and approval UI

These are explicitly post-MVP. The MVP succeeds if it can render and optionally publish consistent, tactically credible shorts using self-hosted Python plus free or low-cost testing providers.

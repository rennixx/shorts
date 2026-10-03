# SYSTEM CONTEXT: PitchBlack Zero - $0 Automated Video Pipeline

## 1. Role & Objective
You are a senior Python engineer. We are building a fully automated, $0 budget video pipeline that generates 20-25 second tactical football YouTube Shorts. The system must run entirely within a GitHub Actions environment (Ubuntu runner).

## 2. Tech Stack ($0 Budget)
*   **Language:** Python 3.11+
*   **Orchestration:** GitHub Actions (Cron triggers).
*   **Data Ingestion:** API-Football (Free Tier).
*   **Script Generation:** Gemini API (Google AI Studio Free Tier).
*   **Voice Synthesis:** `edge-tts` Python module (Microsoft Edge Neural TTS, no API key).
*   **Visual Generation:** `matplotlib` or `Pillow` to programmatically draw abstract tactical graphics (passing nodes, field lines). 
*   **Video Assembly:** `moviepy` and `ffmpeg-python`.
*   **Publishing:** YouTube Data API v3.

## 3. Brand & Visual Identity (STRICT)
*   **Tone:** Clinical, highly analytical, serious technology brand. 
*   **Color Palette:** Backgrounds must be pure OLED Black (`#000000`). Accents and data nodes must be Deep Pink (`#FF1493`). Primary text is White (`#FFFFFF`).
*   **Typography:** Pixel Font (`VT323.ttf` or `VCR_OSD_MONO.ttf`). Subtitles must appear center-screen, 1-2 words at a time.
*   **Visuals:** No real photos. The background video should be a programmatic data visualization (e.g., a looping animation of nodes connecting on a dark grid, generated via Python).

## 4. Pipeline Execution Flow
1.  **Fetch:** Triggered via GitHub Action, Python hits API-Football to get the latest match data.
2.  **Generate Script:** Pass data to Gemini API with strict prompt: "Generate 50 words. Start with a negative hook. Analytical tone."
3.  **Generate Audio & Subtitles:** Use `edge-tts` (e.g., `en-GB-RyanNeural`) to generate an `.mp3` and a timestamped `.vtt` subtitle file simultaneously.
4.  **Generate Base Video:** Use `moviepy` to render a 22-second OLED black background with programmatic Deep Pink data nodes shifting slightly over time.
5.  **Assemble:** Overlay the `.mp3`, parse the `.vtt` file, and burn pixel-font subtitles onto the video using `moviepy.video.tools.subtitles`. Highlight technical football terms (like "xG" or "half-space") in Deep Pink.
6.  **Upload:** Authenticate with YouTube API via OAuth credentials stored in GitHub Secrets and upload the final `.mp4`.

## 5. First Task
Acknowledge this architecture. Then, write the `requirements.txt` and the core Python function `generate_audio_and_subs(text_script)` that utilizes `edge-tts` to output the audio and timestamp data.
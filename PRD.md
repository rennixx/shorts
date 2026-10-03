# PRD: Project PitchBlack - Automated Football Shorts Engine

## 1. Objective
Build and deploy a fully automated, hybrid video generation pipeline that produces 20–25 second tactical football shorts. The system must ingest match data, generate an analytical script, synthesize voice, generate minimalist b-roll, stitch the assets via FFmpeg, and publish to YouTube Shorts within 15 minutes of a match concluding.

## 2. Brand & Visual Identity
*   **Tone:** Clinical, highly analytical, serious technology brand. No motivational filler.
*   **Color Palette:** OLED Black (`#000000`), Clean White (`#FFFFFF`) for primary text, Deep Pink (`#FF1493`) for accents and keyword highlights.
*   **Typography:** Minimalist Pixel Font (e.g., "VCR OSD Mono" or "VT323").
*   **Visuals:** Abstract geometric shapes, 3D tactical diagrams, data nodes. No generic stock footage of players.

## 3. System Architecture (Hybrid Make.com + Cloud Function)

### Phase 1: Orchestration & Data Ingestion (Make.com)
*   **Trigger:** Webhook or scheduled cron job checking a Football API (e.g., API-Football / FootyStats) for match completion.
*   **Payload:** Match result, key events, xG (Expected Goals), and possession stats.

### Phase 2: Asset Generation (Make.com API Routing)
*   **Script Generation:** Send data payload to LLM (OpenAI/DeepSeek). 
    *   *Constraint:* 50-word limit. Must use a negative hook or curiosity gap in the first 4 words.
*   **Voice Synthesis:** Route script to ElevenLabs API. 
    *   *Constraint:* Calm, deep, authoritative voice profile. Output as `.mp3`.
*   **Subtitle Timestamps:** Route audio to Whisper API to get word-level timestamps (`.json` or `.srt`).
*   **Visual Generation:** Send LLM-generated scene prompts to a Video API (Runway Gen-3 / Luma Dream Machine) to output two 12-second abstract background clips.

### Phase 3: The Assembly Engine (Custom Cloud Function)
*   **Environment:** Node.js or Go serverless function (AWS Lambda / Google Cloud Run) executing `ffmpeg`.
*   **Inputs:** URL links to the `.mp3` voice, the video `.mp4` files, and the word-level `.json` timestamps.
*   **FFmpeg Processing:**
    1.  Concatenate the background video clips.
    2.  Overlay the `.mp3` audio track.
    3.  Generate center-screen, word-by-word subtitles using the Pixel Font.
    4.  Apply logic to color specific technical keywords (e.g., "xG", "mid-block", "half-space") with the Deep Pink hex (`#FF1493`).
*   **Output:** Final 1080x1920 (9:16 aspect ratio) `.mp4` file URL.

### Phase 4: Distribution (Make.com)
*   **YouTube API:** Receive the final `.mp4` URL from the Cloud Function.
*   **Publishing:** Upload as a Short with LLM-generated title. 
    *   *Constraint:* Zero hashtags in the title. Hide 3 tags in the description.

## 4. MVP Milestones
*   **Day 1-2:** Set up Make.com scenarios and test API connections (Football API, LLM, TTS).
*   **Day 3-4:** Write and deploy the Node.js/Go FFmpeg Cloud Function.
*   **Day 5:** End-to-end integration testing and visual QA.
*   **Day 6:** World Cup kickoff. System goes live.
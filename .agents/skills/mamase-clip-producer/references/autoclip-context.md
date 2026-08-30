# AutoClip Context & Architecture Reference

## Overview
AutoClip is a Docker-first local web app that converts a ZIP content package into a browser-ready vertical narrated MP4 video.

## Runtime & System Specifications
- **Runtime**: Docker is mandatory and is the primary supported runtime for MVP.
- **Host Requirements**: Host only needs Docker / Docker Compose. No host Python, FFmpeg, ffprobe, Thai fonts, or TTS dependencies required.
- **Port Mapping**: Container listens on port 8000; Docker Compose maps host `9999:8000`. UI is accessed at `http://localhost:9999`.
- **Primary Command**: `docker compose up --build`
- **Backend**: Python 3.12 + FastAPI.
- **Frontend**: Simple HTML/JavaScript (lightweight React only with clear benefit).
- **Media Engine**: FFmpeg for rendering and ffprobe for media duration/metadata.
- **Storage**: Local filesystem only; no database; in-memory job registry.

## Input Contract & Security
- **ZIP Root**: Must contain `script.json` and `images/` directory. `audio/` is optional (for BGM).
- **Paths**: All paths in `script.json` are relative to ZIP root. Absolute paths and `../` path traversal are strictly forbidden.
- **Scene Order**: Scene order comes ONLY from the `scenes` array in `script.json`, never inferred from filenames.
- **Supported Images**: `.jpg`, `.jpeg`, `.png`, `.webp`.
- **Supported Audio**: Optional BGM supported: `.mp3`, `.wav`, `.m4a`, `.aac`.
- **Security**: Strict ZIP validation prior to extraction (reject zip-slip, symlinks, executables, scripts, unsupported files, oversized archives).

## Workspace & Pipeline
- **Isolation**: Each job uses `workspaces/<job-id>/` with `source/`, `extracted/`, `generated-audio/`, `rendered-scenes/`, `subtitles/`, and `output/final.mp4`.
- **Pipeline Flow**:
  1. Upload ZIP
  2. Validate archive
  3. Secure extraction
  4. Parse `script.json`
  5. Validate assets
  6. Generate TTS WAV per scene
  7. Probe audio duration via ffprobe
  8. Build UTF-8 SRT subtitles
  9. Render individual scenes (FFmpeg)
  10. Concatenate scenes
  11. Mix optional BGM / ducking & loudness normalization (`loudnorm`)
  12. Produce `final.mp4`

## TTS & Thai Language Support
- **TTS Architecture**: Pluggable `TtsProvider` interface.
- **Thai Encoding**: Thai text remains UTF-8 end-to-end; no silent transliteration.
- **Subtitles**: Subtitle text comes directly from narration/subtitle fields; no speech-to-text. One subtitle block per scene.
- **Thai Fonts**: Docker image bundles redistributable fonts (`Noto Sans Thai`, `TLWG`).

## Video Specifications
- **Format**: MP4, H.264, 1080x1920 (9:16 vertical), 30 fps, `yuv420p`.
- **Audio Format**: AAC, 48 kHz stereo.
- **Image Fitting**: Preserve aspect ratio; fill 1080x1920 and center-crop excess (cover scale). No distortion/stretching.
- **Duration**: Scene duration is governed by the narration audio duration (+ optional configured padding).

## Channel & Content Standards
- **Channel**: Mamase — จักรวาลของใจ
- **Themes**: Strange places worldwide, mysterious science, unexpected space stories, nature extremes, verified trending topics.
- **Review Gate (Mandatory Workflow)**: Before every production round, show the complete script to **พี่พี** for review. Generate images, JSON, and ZIP packages **only after approval**.

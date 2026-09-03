# AutoClip

AutoClip is a Docker-first local web app that converts one content ZIP into a browser-ready vertical MP4. It validates and extracts the package securely, creates per-scene audio through a pluggable TTS interface, renders image motion and Thai subtitles with FFmpeg, concatenates scenes, optionally mixes `audio/bgm.*`, and exposes progress, preview, and download endpoints.

## Start with Docker

Docker and Docker Compose are the only host requirements.

```sh
docker compose up --build
```

Open <http://localhost:9999>. Container logs are available with:

```sh
docker compose logs -f autoclip
```

The container runs FastAPI on port 8000; Compose maps `9999:8000`. Workspaces persist in `./workspaces`.

## MVP scope and architecture

HTTP routes only handle upload/status/download behavior. `JobService` schedules work on a bounded thread pool and updates an in-memory `JobRegistry`. `PackageService` owns ZIP extraction and contract validation. TTS providers live under `app/infrastructure/tts`; media commands are centralized in `FfmpegRunner`, `FfprobeRunner`, `SceneRenderer`, and `VideoComposer`.

Job progress is delivered through `GET /api/jobs/{jobId}/events` using Server-Sent Events. A transport-neutral `JobEventPublisher` fans progress, safe user logs, completion, and failure events to a separate bounded queue for every connected tab. The stream sends 15-second heartbeats and disables proxy buffering. `GET /api/jobs/{jobId}` remains the reconnect/page-refresh snapshot and includes up to 200 retained user log entries plus completed-video metadata.

Pipeline:

```text
ZIP → secure extraction → Pydantic script parsing → asset validation
    → TTS WAV per scene → ffprobe duration → UTF-8 SRT
    → uniform H.264/AAC scene → ordered concat → optional BGM duck/mix
    → loudness normalization → final.mp4
```

Jobs use unique server-generated UUID directories and retain all intermediate files for inspection. The registry itself is intentionally non-persistent and resets when the process restarts.

Adjacent scenes use a subtle 0.20-second video and audio crossfade by default. A scene can optionally set `transition` to control its transition into the next scene: `none`, `fade`, `dissolve`, `wipe_left`, `wipe_right`, `wipe_up`, `wipe_down`, `slide_left`, `slide_right`, `slide_up`, or `slide_down`. Missing values fall back to `video.transition` in `config.yaml`; `video.transition_seconds` controls the shared duration. The final scene's transition is ignored.

## ZIP contract

`script.json` must be at ZIP root. Asset paths are relative to that root. Scene array order is authoritative.

```json
{
  "project": {"id": "lake-natron", "title": "Lake Natron", "language": "th-TH", "resolution": "1080x1920", "fps": 30},
  "voice": {"provider": "local", "voice": "thai-male-01", "speed": 1.0},
  "scenes": [
    {"id": "scene-01", "image": "images/scene-01.png", "narration": "คุณเชื่อไหม เรื่องนี้มีอยู่จริงบนโลกของเรา", "motion": "slow_zoom_in"}
  ]
}
```

Supported images are JPG, JPEG, PNG, and WebP. Optional BGM is discovered as `audio/bgm.mp3`, `.wav`, `.m4a`, or `.aac`. Images use cover scaling: aspect ratio is preserved and excess is center-cropped. Absolute paths, traversal, links, executable/script extensions, duplicate ZIP paths, missing assets, and configured size-limit violations are rejected.

## TTS state

`TtsProvider` isolates provider behavior from jobs and rendering. The default `local` provider uses VachanaTTS2 through ONNX Runtime and produces real Thai speech locally. `thonburian` uses the F5 reference-voice pipeline, while `bird-f5` uses Bird/F5-TTS-THAI (`f5-tts-th`) with the configured Thai reference WAV/transcript. Both F5 providers require a valid reference voice. The standalone `/tts` page lets you select the engine, preview, and download WAV audio. `DummyTtsProvider` remains available for deterministic tests.

## Image motion

Scenes keep using the original `motion` field; no scene-video asset is added to the ZIP contract. Supported camera motions are `none`, `slow_zoom_in`, `slow_zoom_out`, `pan_left_to_right`, `pan_right_to_left`, `pan_up`, `pan_down`, `zoom_in`, `zoom_out`, `zoom_in_top_left`, `zoom_in_top_right`, `zoom_in_bottom_left`, `zoom_in_bottom_right`, `pan_left_to_right_zoom_in`, `pan_right_to_left_zoom_in`, `pan_up_zoom_in`, `pan_down_zoom_in`, `drift_top_left`, `drift_top_right`, `drift_bottom_left`, `drift_bottom_right`, `cinematic_push_in`, `cinematic_pull_out`, `gentle_float`, and `documentary_pan`. `auto` is deterministic and cycles through safe presets by scene ID. Optional `motion_speed` (`slow`, `normal`, `fast`), `motion_intensity` (0.05–0.35), and `focus` (`center`, `top`, `bottom`, `left`, `right`, or a corner) are backward-compatible. Motion is the camera movement inside a scene; `transition` is the effect between scenes. Rendering uses FFmpeg scale/crop/zoompan with a fixed 9:16 canvas, H.264, and `yuv420p`; it is not AI image-to-video.

The home page also provides standalone Thai Text to Speech: enter up to 2,000 characters, select a voice and speed, preview the result in the browser, or download the WAV. Its API is `POST /api/tts` with form fields `text`, `voice`, and `speed`. `DummyTtsProvider` remains available for deterministic tests. Future Google, ElevenLabs, and Azure adapters can implement the same protocol without changing the pipeline.

The VachanaTTS Python package is Apache-2.0, but consumers should independently review the license/provenance of its distributed voice weights before commercial deployment. AutoClip does not claim commercial rights to third-party model weights.

## Thai subtitles and fonts

The Docker image installs redistributable `fonts-noto-core` and `fonts-thai-tlwg`. FFmpeg/libass is configured for `Noto Sans Thai`, UTF-8 input, and an explicit 1080×1920 subtitle coordinate space. The Docker integration test burns text containing Thai consonants, vowels, and tone marks. Subtitle size, outline, and bottom margin are configured in `config.yaml`.

## Sample and API

Build the checked-in Thai sample package (no third-party Python libraries needed):

```sh
docker compose run --rm autoclip python scripts/build_sample_zip.py
```

This writes `dist/lake-natron.zip`.

```sh
curl -F file=@dist/lake-natron.zip http://localhost:9999/api/jobs
curl http://localhost:9999/api/jobs/JOB_ID
curl -o final.mp4 http://localhost:9999/api/jobs/JOB_ID/video
curl http://localhost:9999/health
curl -o thai.wav -F 'text=สวัสดี นี่คือระบบสร้างเสียงภาษาไทย' -F voice=thai-male-01 -F speed=1.0 http://localhost:9999/api/tts
```

The UI restores one state snapshot and then uses browser `EventSource` for live updates. Completion redirects to `/jobs/{jobId}/preview`, which shows the video, project metadata, download action, and a generate-another action. Failed jobs stay on the progress page with retained logs, a stable error code, and a safe public message.

## Tests

Run everything, including the real FFmpeg Thai render test, inside Docker:

```sh
docker compose run --rm autoclip pytest
```

Host-native development is secondary:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Configuration and media details

Set `AUTOCLIP_CONFIG` to select a YAML file. `AUTOCLIP_WORKSPACE`, `AUTOCLIP_TTS_PROVIDER`, `AUTOCLIP_MAX_UPLOAD_MB`, and `AUTOCLIP_MAX_EXTRACTED_MB` override common settings. Scene videos are H.264/yuv420p at configured 1080×1920/30 fps with AAC 48 kHz stereo. Dummy/local narration is normalized to WAV. Final audio uses `loudnorm`; BGM uses looping, low gain, side-chain compression beneath narration, and a short fade-in.

To remove old retained workspaces manually:

```sh
docker compose run --rm autoclip python scripts/cleanup_workspaces.py --older-than-hours 24
```

## Troubleshooting and limitations

- If health is not `UP`, inspect `docker compose logs autoclip`; both `ffmpeg` and `ffprobe` must exist.
- Rendering and Thai TTS use CPU inside the standard container. The current macOS Docker environment cannot expose the host Apple GPU as a CUDA device; no GPU is required. The worker pool is intentionally limited to two jobs.
- If subtitle rendering fails, verify `ffmpeg -filters` includes `subtitles` and `fc-match 'Noto Sans Thai'` resolves inside the container.
- In-memory job status is lost after restart, although generated workspace files remain.
- One subtitle block per scene is supported; phrase-level timing is future work.
- The local voice quality and pronunciation may need tuning for foreign names and technical terms; pronunciation overrides are future work.
- The Docker image is larger and its first build takes longer because all four local voice models are embedded.
- Automatic cleanup, persistence, cloud providers, authentication, publishing, and content generation are deliberately out of scope.

Next steps are confirming model-weight licensing for the intended deployment, adding pronunciation overrides, and adding an optional GPU provider only for environments where Docker has a supported CUDA runtime.

For the optional RunPod shot-rendering integration (Wan image-to-video, F5 Thai
narration, and optional LatentSync), see
[docs/runpod-shot-pipeline.md](docs/runpod-shot-pipeline.md). It deliberately
keeps the ZIP contract and normal AutoClip review-to-history workflow unchanged.
# Project History and persistence

AutoClip stores project/job metadata in `workspaces/autoclip.db` (SQLite with foreign keys and WAL); media remains under `workspaces/`. Completed jobs can be opened from `/history` and their video endpoint continues to work after an application restart. Direct ZIP uploads and AI projects are both indexed. Delete moves a project to Trash (`/api/trash/{id}/restore` restores it); permanent deletion is explicit. `GET /api/storage` reports usage and `POST /api/storage/cleanup` removes disposable job intermediates. Keep projects are excluded from automatic retention cleanup.

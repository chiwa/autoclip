# RunPod shot pipeline for AutoClip

Status: design baseline, verified against the current RunPod pod on 2026-09-03.

## Purpose

RunPod is an optional per-scene render engine.  It does not replace AutoClip's
existing product flow:

```text
AI chat -> scene preview/review -> confirm -> render -> final preview -> history
```

The existing `ffmpeg_motion` renderer remains the reliable fallback.  A scene
may use `runpod` to create a true moving shot, and may optionally use
LatentSync when the scene contains a speaking presenter.

## What is installed and verified on the current pod

| Component | State | Intended role |
| --- | --- | --- |
| NVIDIA A40 (46 GB VRAM) | available | GPU for all remote generation |
| ComfyUI on port 8188 | running | Wan 2.2 image-to-video API |
| Wan 2.2 TI2V 5B, UMT5 encoder, VAE | installed | visual motion from an input image |
| F5-TTS-THAI source + Python environment | installed | Thai WAV generation from narration + reference voice |
| F5-TTS-TH-V2 weights | installed | preferred Thai model variant for fewer skipped/repeated words |
| LatentSync 1.6 checkpoints | installed | optional presenter lip-sync |
| Nginx port 7270 -> localhost:7271 | configured, target absent | reserved location for a new authenticated API service |

F5-TTS and LatentSync currently have CLI/Python entry points only.  They are
not HTTP APIs yet.  Do not wire AutoClip directly to their files or assume
that port 7270 is healthy until the API service has been deployed.

## Scene contract inside AutoClip

Keep the current ZIP contract unchanged (`script.json`, `images/`, optional
`audio/`).  The AI/project preview may add render choices in AutoClip's own
database and job payload; they do not need to be put in an imported ZIP.

```json
{
  "id": "scene-03",
  "image": "images/scene-03.png",
  "narration": "ข้อความบรรยายภาษาไทย",
  "motion": "cinematic_push_in",
  "transition": "dissolve",
  "render_engine": "runpod",
  "runpod": {
    "visual_mode": "wan_i2v",
    "lip_sync": false,
    "prompt": "Cinematic documentary shot ...",
    "negative_prompt": "text, watermark, flicker, jitter"
  }
}
```

`render_engine` defaults to `ffmpeg_motion`; `runpod` is a per-scene override.
`lip_sync: true` is valid only for a shot with a clear, front-facing speaking
person.  B-roll, landscape, space, animal, and documentary scenes should not
spend GPU time on LatentSync.

## Separate operations and retry graph

Each operation is independent and persists its output.  Never turn this into
one opaque "make shot" request.

```text
source image + prompt --Wan--> wan-visual.mp4
narration + reference voice --F5--> narration.wav
wan-visual.mp4 + narration.wav --LatentSync (optional)--> lipsync.mp4

final scene = lipsync.mp4 when lip-sync is enabled; otherwise wan-visual.mp4
AutoClip composes final scenes, subtitles, transitions, music, and loudness.
```

| Change or failure | Retry only |
| --- | --- |
| Visual/prompt/seed is wrong | Wan |
| Thai pronunciation or voice is wrong | F5; then LatentSync if it exists |
| Mouth timing/face quality is wrong | LatentSync |
| Subtitle, transition, BGM, or final concat is wrong | AutoClip composer |

If F5 output changes, invalidate the prior lip-sync result but retain the Wan
video.  If Wan output changes, invalidate only the dependent lip-sync result.

## Planned RunPod API boundary

Create one small FastAPI service on the pod.  AutoClip's backend calls it;
the browser never calls it directly.  It is a job API, not a long-running HTTP
request API.

```text
POST /v1/jobs/wan
POST /v1/jobs/f5
POST /v1/jobs/latentsync
GET  /v1/jobs/{job_id}
GET  /v1/jobs/{job_id}/artifact/{name}
GET  /health
```

All `POST` requests should return `202 Accepted` with a server-generated
`job_id`; status is `queued`, `running`, `succeeded`, `failed`, or `cancelled`.
Require an `Idempotency-Key` header.  Repeating a request with the same key and
same input returns the original job rather than consuming the GPU twice.

Suggested request bodies:

```json
// POST /v1/jobs/wan
{
  "source_image": {"upload_id": "..."},
  "prompt": "...",
  "negative_prompt": "...",
  "width": 704,
  "height": 1280,
  "frames": 81,
  "fps": 16,
  "seed": 42,
  "steps": 12,
  "cfg": 5.0
}
```

```json
// POST /v1/jobs/f5
{
  "text": "...",
  "reference_audio": {"voice_id": "mamase-th-01"},
  "reference_text": "...",
  "model": "f5-th-v2",
  "speed": 0.9,
  "seed": 42
}
```

```json
// POST /v1/jobs/latentsync
{
  "video": {"artifact_id": "wan-job-id/wan-visual.mp4"},
  "audio": {"artifact_id": "f5-job-id/narration.wav"},
  "inference_steps": 20,
  "guidance_scale": 1.5
}
```

The service validates ownership and artifact existence before queuing a child
job.  It should use a one-GPU-worker queue initially; running Wan and
LatentSync together without resource scheduling risks out-of-memory failures.

## Media requirements

Wan's current workflow validates dimensions divisible by 32.  Use `704x1280`
as the safe portrait baseline.  Do not request `1080x1920` directly from this
workflow because 1080 is not divisible by 32.  AutoClip normalizes successful
shots to the final `1080x1920`, H.264, `yuv420p`, 30 fps scene format before
composition.

Wan's current runner defaults to a horizontal 640x352 clip, 33 frames at
16 fps.  The future API must override these with validated portrait values;
never inherit that test-script default silently.

F5 should write a lossless WAV first.  LatentSync must receive exactly that
WAV.  During final composition, AutoClip resamples audio to AAC 48 kHz stereo,
normalizes loudness, and keeps narration as the authoritative track.  Preserve
the original artifacts for review; do not overwrite them with normalized files.

## Artifact layout and retention

Use one directory per remote job under the persistent RunPod workspace:

```text
/workspace/autoclip-jobs/<job_id>/
  request.json
  status.json
  input/source-image.png
  output/wan-visual.mp4
  output/narration.wav
  output/lipsync.mp4
  logs/worker.log
```

AutoClip downloads/copies the selected artifacts to its existing project
workspace before its own final render.  Store hashes, source job IDs, model
version, seed, prompts, and timestamps in SQLite so History can reproduce or
retry a scene.

Treat `/workspace` persistence as an operational requirement to verify in the
RunPod console before production use.  Job files are large: successful jobs
need retention policies, a project-level **Keep** flag, explicit Trash/Restore,
and scheduled cleanup of disposable intermediates.  A cleanup task must never
remove queued/running jobs or artifacts referenced by a kept project.

## Security and network boundary

- Keep RunPod SSH keys, browser/Jupyter tokens, and the API bearer token out
  of the repository and out of `script.json`.
- AutoClip stores the RunPod base URL and bearer token in server-side
  environment/configuration only.  The browser receives no RunPod credential.
- Put the FastAPI service behind the existing Nginx proxy only after adding
  bearer-token authentication, upload size limits, request IDs, and health
  checks.  Do not expose ComfyUI, F5, or LatentSync as unauthenticated public
  services.
- Validate uploaded images/audio by MIME, size, extension, and decoded content;
  generate a server-side filename rather than using user-provided paths.
- Log prompt IDs and job IDs, never tokens or reference-audio contents.

## Delivery order

1. Confirm a single portrait Wan run through the existing ComfyUI workflow.
2. Confirm F5 TH V2 generates a WAV from a short approved Thai sentence and a
   properly consented reference voice (clean, about 3-8 seconds).
3. Confirm LatentSync against a presenter clip plus that exact F5 WAV.
4. Implement the authenticated async RunPod API and its queue.
5. Add AutoClip's provider adapter, per-scene progress, retry buttons, and
   artifact links in History.
6. Add end-to-end tests with a fake RunPod client; keep real GPU smoke tests
   separate and manually controlled.

## Operational checks

The API's `/health` should report component readiness without exposing secrets:

```json
{
  "status": "ok",
  "wan": "ready",
  "f5": "ready",
  "latentsync": "ready",
  "queue_depth": 0,
  "gpu": {"name": "...", "free_vram_mb": 0}
}
```

Before each deployment verify GPU visibility, free `/workspace` disk, model
files, queue recovery after a restart, and that a failed job exposes a safe
error code while technical logs remain server-side.

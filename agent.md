# Wan2.2 TI2V RunPod Setup Notes

เอกสารนี้เป็น runbook สำหรับสร้าง environment Wan2.2 TI2V 5B บน RunPod ใหม่ให้เหมือนเครื่องที่ทดสอบสำเร็จแล้ว ห้ามติดตั้ง ComfyUI, CUDA หรือโมเดลขนาดใหญ่บน local Mac งานทั้งหมดต้องทำภายใน RunPod และเก็บไฟล์ใหญ่ใต้ `/workspace`

## เครื่องที่เคยทดสอบสำเร็จ

- RunPod GPU Pod, Ubuntu 24.04
- NVIDIA A40, VRAM 46,068 MiB (ประมาณ 48 GB)
- NVIDIA driver 580.159.03
- Driver CUDA compatibility 13.0
- CUDA toolkit 12.8
- Python 3.12.3
- PyTorch 2.8.0+cu128; CUDA ใช้งานได้
- ComfyUI 0.34.0, commit `95d755cd8107a72258d452b5d3657273d571f07d`
- FFmpeg 6.1.1
- ใช้ native ComfyUI nodes เท่านั้น ไม่ติดตั้ง custom nodes

PyTorch cu128 แสดงคำเตือนว่า optimized CUDA operations บางรายการต้องใช้ cu130 แต่ generation ทำงานสำเร็จด้วย eager/PyTorch backend จึงไม่ต้องเปลี่ยน CUDA หรือ PyTorch โดยไม่มีเหตุจำเป็น

## ตัวติดตั้งสำหรับ Pod ใหม่

ตัวติดตั้งที่เก็บถาวรใน local repository:

```text
/Users/zengcode/projects/autoclip/installation.sh
```

สคริปต์นี้ต้องรันบน Linux RunPod เท่านั้น และจะหยุดทันทีหากรันบน macOS โดยจะ:

1. ตรวจ Linux, NVIDIA GPU, CUDA-enabled PyTorch, RAM และพื้นที่ `/workspace`
2. ต้องการพื้นที่ว่างอย่างน้อย 25 GiB และแนะนำ Pod disk อย่างน้อย 80 GiB สำหรับ Wan, F5-TTS และ LatentSync ครบชุด
3. ติดตั้ง ComfyUI commit ที่เคยทดสอบแล้วลง `/workspace/ComfyUI`
4. สร้าง venv แบบ `--system-site-packages` เพื่อใช้ PyTorch/CUDA ของ RunPod image
5. แสดง manifest ของไฟล์เกิน 1 GB ก่อนดาวน์โหลด
6. ดาวน์โหลดต่อจากไฟล์ `.part` ได้ และ retry เมื่อ network สะดุด
7. ไม่ดาวน์โหลดโมเดลซ้ำเมื่อไฟล์เดิมมีขนาดและ SHA-256 ถูกต้อง
8. ไม่เขียนทับไฟล์เดิมที่ขนาดหรือ hash ผิด แต่จะหยุดให้ตรวจสอบก่อน
9. ตรวจว่า safetensors ทั้งสามไฟล์เปิดอ่านได้
10. ติดตั้ง F5-TTS-THAI V2 และ LatentSync 1.6 ใน Python 3.10 virtualenv แยกกัน
11. ดาวน์โหลด checkpoint ของ F5-TTS และ LatentSync โดยตรวจขนาดและ SHA-256 และไม่โหลดซ้ำ
12. สร้าง start script, UI workflow, API workflow, API runner และ installation log ใต้ `/workspace`

Pod template ต้องมี `git`, `curl`, `python3`, `python3-venv`, `nvidia-smi`, `sha256sum` และ CUDA-enabled PyTorch อยู่แล้ว ตัวติดตั้งตั้งใจไม่ติดตั้ง CUDA/PyTorch ชุดใหญ่เอง เพื่อป้องกัน version mismatch

### การเชื่อมต่อ Pod ใหม่

ให้ถือว่า RunPod ถูกสร้างใหม่ทุกครั้ง และข้อมูลต่อไปนี้อาจเปลี่ยนทั้งหมด:

- Pod ID
- IP หรือ SSH hostname
- SSH username
- SSH port
- private key path หรือ key pair ที่ RunPod กำหนด

ห้าม hardcode หรือใช้ SSH command จากงานรอบก่อน Agent ต้องขอหรืออ่าน **SSH command ล่าสุดของ Pod ปัจจุบัน** จากผู้ใช้/RunPod Console ก่อนเสมอ แล้วทดสอบเชื่อมต่อและยืนยันว่า shell ที่ได้เป็น remote Linux Pod ไม่ใช่ local Mac

ตัวอย่างรูปแบบเท่านั้น ห้ามคัดลอกค่าตัวอย่างไปใช้จริง:

```bash
ssh CURRENT_USER@CURRENT_HOST -p CURRENT_PORT -i /path/to/current/private_key
```

ถ้า SSH command ล่าสุดไม่มี `-p` ก็ไม่ต้องเพิ่มเอง และถ้า RunPod ให้ key path ใหม่ ให้ใช้ path ใหม่นั้น อย่าเดาว่ายังเป็น `~/.ssh/id_ed25519`

### กฎ SSH key สำหรับ RunPod

- **ห้ามใช้ `~/.ssh/id_ed25519` กับ RunPod** เพราะ key นี้สงวนไว้สำหรับ GitHub
- Dedicated key ที่แนะนำสำหรับ RunPod คือ `~/.ssh/id_ed25519_runpod`
- ใช้ private key path ที่ผู้ใช้ระบุใน SSH command ล่าสุดเท่านั้น
- หาก SSH command จาก RunPod แสดง `~/.ssh/id_ed25519` ให้หยุดและแจ้งผู้ใช้ให้เปลี่ยนเป็น dedicated RunPod key ก่อน ห้ามเชื่อมต่อด้วย GitHub key
- ห้ามสร้าง, เปลี่ยน, ลบ หรือ overwrite SSH key โดยไม่ได้รับคำสั่งจากผู้ใช้โดยตรง
- ห้ามแสดง, อ่านออกมาใน log, อัปโหลด หรือส่งต่อเนื้อหาของ private key
- การเพิ่ม key ใน RunPod ให้ใช้เฉพาะ public key เช่น `~/.ssh/id_ed25519_runpod.pub`

ตัวอย่างการเชื่อมต่อที่ถูกต้อง:

```bash
ssh CURRENT_USER@CURRENT_HOST -p CURRENT_PORT -i ~/.ssh/id_ed25519_runpod
```

### Trigger: ผู้ใช้บอกว่า "สร้าง RunPod ขึ้นมาใหม่"

เมื่อผู้ใช้แจ้งว่า **สร้าง RunPod ขึ้นมาใหม่**, **สร้าง Pod ใหม่**, **recreate Pod** หรือข้อความความหมายเดียวกัน ให้ถือทันทีว่า:

- Pod/session เดิมถูกปิดหรือใช้ต่อไม่ได้
- process, installation และไฟล์ใต้ `/workspace` ของ Pod เดิมไม่มีอยู่แล้ว เว้นแต่ผู้ใช้ยืนยันว่าใช้ persistent volume เดิม
- SSH hostname/IP, username, port, Pod ID และ private key เดิมหมดอายุสำหรับงานปัจจุบัน
- ห้ามพยายาม reconnect ไปยัง SSH target เก่า
- ห้ามสรุปว่าโมเดลยังดาวน์โหลดอยู่หรือ ComfyUI ยังทำงานอยู่จากผลของ session ก่อน

ลำดับการทำงานใหม่:

1. ขอ SSH command ล่าสุดของ Pod ใหม่จากผู้ใช้ หากยังไม่ได้ให้มา
2. ใช้ command นั้นตามที่ได้รับ ห้ามเดาหรือดึงค่าจาก session เก่า
3. หลัง SSH สำเร็จ ให้ตรวจ `hostname`, OS, `nvidia-smi`, CUDA, Python, PyTorch, RAM และพื้นที่ `/workspace`
4. ตรวจว่ามี persistent files/model เดิมอยู่จริงหรือไม่จาก remote filesystem
5. ถ้า environment ยังไม่มี ให้ส่ง local `installation.sh` ไปรันผ่าน SSH
6. ก่อนดาวน์โหลดไฟล์เกิน 1 GB ต้องรายงาน manifest ตามกติกาเดิม
7. หลังติดตั้ง ให้ start ComfyUI, ตรวจ port 8188 และทำ generation/verification ตามคำขอ

การบอกว่า "สร้าง RunPod ขึ้นมาใหม่" ไม่ได้หมายความว่า agent สามารถสร้าง Pod ผ่าน RunPod account ได้เองโดยอัตโนมัติ หากผู้ใช้ต้องการให้ agent กดสร้าง Pod ด้วย ต้องมี browser/session ที่ login อยู่และต้องได้รับคำขอให้ทำ action นั้นโดยตรง

### วิธีรันจาก local Mac

หลังสร้าง Pod ให้เริ่มจาก SSH command ล่าสุดที่ RunPod แสดง แล้วเติมคำสั่ง remote สำหรับรับ installer ผ่าน stdin ตัวอย่างต่อไปนี้เป็น placeholder เท่านั้น:

```bash
cd /Users/zengcode/projects/autoclip
ssh CURRENT_USER@CURRENT_HOST -p CURRENT_PORT -i /path/to/current/private_key 'bash -s -- --yes' < installation.sh
```

ตัด `--yes` ออกหากต้องการให้สคริปต์ถามยืนยันหลังแสดงรายละเอียดโมเดลขนาดใหญ่:

```bash
ssh CURRENT_USER@CURRENT_HOST -p CURRENT_PORT -i /path/to/current/private_key 'bash -s' < installation.sh
```

## โมเดลที่จำเป็นเท่านั้น

Source repository:

```text
Comfy-Org/Wan_2.2_ComfyUI_Repackaged
```

### Diffusion model

- ชื่อ: `wan2.2_ti2v_5B_fp16.safetensors`
- ขนาด: 9,999,658,848 bytes
- SHA-256: `456f901338bd9eadbded3828b819109a9b68e8a525ca5cf8d0049a69fcfeca1e`
- ปลายทาง: `/workspace/ComfyUI/models/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors`

### Text encoder

- ชื่อ: `umt5_xxl_fp8_e4m3fn_scaled.safetensors`
- ขนาด: 6,735,906,897 bytes
- SHA-256: `c3355d30191f1f066b26d93fba017ae9809dce6c627dda5f6a66eaa651204f68`
- ปลายทาง: `/workspace/ComfyUI/models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors`

### VAE

- ชื่อ: `wan2.2_vae.safetensors`
- ขนาด: 1,409,400,960 bytes
- SHA-256: `e40321bd36b9709991dae2530eb4ac303dd168276980d3e9bc4b6e2b75fed156`
- ปลายทาง: `/workspace/ComfyUI/models/vae/wan2.2_vae.safetensors`

ไม่ต้องดาวน์โหลด Wan2.2 14B, Diffusers repository, GGUF, LoRA, WanVideoWrapper หรือ custom nodes สำหรับ workflow นี้

## เสียงไทยและ lip sync แบบฟรี ไม่ใช้ API

- F5-TTS-THAI V2 repository: `VYNCX/F5-TTS-THAI`, commit `7b0989f5f67378cdea12a117e140c11ac0a9f57d`
- F5 checkpoint: `model_350000.pt`, 1,348,534,439 bytes, SHA-256 `b9f9304f5ea0c4519d210c0c391d0b090e3b42acb07724ac92577d9c4dcce5ae`
- F5 destination: `/workspace/models/f5-tts-th-v2/model_350000.pt`
- LatentSync repository: `ByteDance/LatentSync`, commit `a229c3948406bc2cf6eaf4873e662e70c6a04746`
- LatentSync checkpoint: `latentsync_unet.pt`, 5,072,222,488 bytes, SHA-256 `0a478e89eb660f82da4c35dbdde8a5adfb27f99d1b4e50edd03729e1e98316d3`
- LatentSync destination: `/workspace/tools/LatentSync/checkpoints/latentsync_unet.pt`
- environments: `/workspace/tools/F5-TTS-THAI/.venv` และ `/workspace/tools/LatentSync/.venv`
- ทำงานใน Pod แบบ local/offline หลังดาวน์โหลดโมเดลแล้ว ไม่เรียก paid API

ค่าที่ทดสอบสำเร็จสำหรับ LatentSync คือ 30 inference steps, guidance scale 1.5 และ `--enable_deepcache` จากนั้นใช้ FFmpeg motion interpolation และ Lanczos upscale ส่งออก 1080x1920, 30 fps, H.264 CRF 18, AAC 192 kbps การส่งออก Full HD เป็นการ upscale จาก Wan output 704x1280 ไม่ใช่ native Full HD generation

## ไฟล์ที่ตัวติดตั้งสร้างบน RunPod

```text
/workspace/ComfyUI/
/workspace/start-comfyui.sh
/workspace/wan22-ti2v-workflow.json
/workspace/wan22-ti2v-api.json
/workspace/wan22-ti2v.py
/workspace/WAN22-INSTALL.log
/workspace/models/f5-tts-th-v2/model_350000.pt
/workspace/tools/F5-TTS-THAI/
/workspace/tools/LatentSync/
```

## เปิด ComfyUI

```bash
/workspace/start-comfyui.sh
```

ComfyUI จะ listen ที่:

```text
0.0.0.0:8188
```

อย่าใส่ `--normalvram` เพราะ ComfyUI version ที่ทดสอบไม่รองรับ argument นี้ ค่า default จะเลือก `NORMAL_VRAM` ให้อัตโนมัติบน A40

ตรวจสถานะจากภายใน Pod:

```bash
curl -fsS http://127.0.0.1:8188/system_stats
```

## เรียก image-to-video ผ่าน API runner

```bash
/workspace/wan22-ti2v.py /path/to/input.png \
  --prompt "A gentle cinematic camera push-in, subtle natural motion." \
  --negative-prompt "low quality, blurry, flicker, jitter, text, watermark" \
  --width 640 \
  --height 352 \
  --frames 33 \
  --steps 12 \
  --cfg 5 \
  --seed 42 \
  --fps 16
```

ข้อกำหนด:

- width และ height ต้องหารด้วย 32 ลงตัว
- เริ่มที่ 640x352, 33 frames, 12 steps เพื่อหลีกเลี่ยง CUDA OOM
- เพิ่ม resolution, frames หรือ steps ทีละอย่างและตรวจ VRAM ก่อน
- Output อยู่ใต้ `/workspace/ComfyUI/output/video/`

Native graph ที่ใช้:

```text
UNETLoader + CLIPLoader + VAELoader
  -> ModelSamplingSD3 (shift 8)
  -> Wan22ImageToVideoLatent
  -> KSampler
  -> VAEDecode
  -> CreateVideo
  -> SaveVideo
```

Sampler defaults:

- sampler: `uni_pc`
- scheduler: `simple`
- denoise: `1.0`
- CFG: `5.0`
- batch size: `1`

## ผลทดสอบเดิม

ไฟล์ที่เคยสร้างสำเร็จบน Pod เก่า:

```text
/workspace/ComfyUI/output/video/wan22-ti2v_00001_.mp4
```

ค่าที่ใช้:

- 640x352
- 33 frames
- 16 fps
- 12 steps
- CFG 5.0
- seed 424242
- `uni_pc` + `simple`
- denoise 1.0
- ModelSamplingSD3 shift 8
- H.264, yuv420p
- duration 2.0625 seconds
- generation time 24.88 secondsบน A40 หลังโหลดโมเดล

## AutoClip integration and ZIP generation

This section is the durable contract between AutoClip on the local Mac and
RunPod generation. Preserve the product workflow:

```text
สร้างวิดีโอ → upload ZIP → Scene Preview/review → choose render engine
→ Generate → progress/live log → final preview → History
```

### Product boundaries

- **สร้างวิดีโอ** (`/`) imports ZIP and selects `ffmpeg_motion` or `wan2.2`.
- **สร้างด้วย AI** (`/ai`) generates script, images, and ZIP only after the
  user reviews the scene preview.
- Wan is a renderer inside Create Video, never a separate product flow.
- Even with Wan, FFmpeg does final scene ordering, narration, subtitles,
  transitions, BGM ducking/mix, loudness normalization, and MP4 export.
- Never silently fall back from `wan2.2` to `ffmpeg_motion`. Return a safe,
  stable error such as `WAN_NOT_CONFIGURED` or `WAN_UNAVAILABLE`.

### ZIP contract (do not change without approval)

```text
script.json                 # required at ZIP root
images/<scene>.png|jpg|webp # required assets; relative POSIX paths only
audio/bgm.mp3|wav|m4a|aac   # optional BGM
```

- Scene array order is the final video order.
- Supported image types: PNG/JPG/JPEG/WebP.
- Reject absolute paths, `..`, symlinks, executable files, duplicate paths,
  unsupported assets, credentials, private keys, tokens, and SSH details.
- Use `PackageService` to validate every created ZIP, and run `unzip -t`.
- `tts_text` is an optional pronunciation override; use `narration` when it
  is absent.

Minimal scene:

```json
{"id":"scene-01","image":"images/scene-01.png","narration":"ข้อความบรรยาย","tts_text":"optional pronunciation","motion":"cinematic_push_in","transition":"fade"}
```

### Optional per-scene Wan plan

Keep visual-generation intent in an optional `wan` object, so old ZIPs remain
compatible with FFmpeg Motion:

```json
{
  "wan": {
    "prompt": "Subject, natural motion, camera, lighting.",
    "negative_prompt": "text, watermark, flicker, jitter, distorted hands",
    "seed": 42,
    "frames": 81,
    "lip_sync": false,
    "character_id": "mamase-presenter-v1"
  }
}
```

- Preview must let the user edit prompt, negative prompt, seed, frames,
  lip-sync, and character ID before Generate; do not require raw JSON editing.
- `lip_sync: true` is future F5 + LatentSync intent. Wan-only rendering must
  not claim that lip sync has already happened.
- `character_id` references a registered local character only. Do not place
  reference WAVs, URLs, filesystem paths, Pod data, or secrets in the ZIP.

### Native RunPod connection

AutoClip native reads these gitignored `.env` values:

```dotenv
AUTOCLIP_WAN_ENABLED=false
AUTOCLIP_WAN_COMFY_URL=http://127.0.0.1:18188
AUTOCLIP_WAN_REQUEST_TIMEOUT_SECONDS=120
AUTOCLIP_WAN_GENERATION_TIMEOUT_SECONDS=900
AUTOCLIP_WAN_POLL_INTERVAL_SECONDS=2
```

- AutoClip uses the fixed localhost URL; the SSH tunnel absorbs changing Pod
  IP/port. Do not hardcode Pod endpoint details in ZIP or tracked config.
- Keep SSH key use outside browser and AutoClip UI. Use the latest Pod SSH
  command and dedicated RunPod key only.
- Before enabling Wan: confirm SSH, ComfyUI `8188`, local tunnel `18188`, and
  `/system_stats` through the tunnel.
- Docker is later: native uses `127.0.0.1:18188`; Docker uses
  `host.docker.internal:18188`.

### Logging and media quality rules

Server logs must be grep-friendly and safe:

```text
event=<event> job_id=<uuid> render_engine=<engine> scene_id=<optional>
```

Minimum events: `job_received`, `job_started`, `package_validated`,
`tts_started`, `tts_completed`, `scene_render_started`,
`scene_render_completed`, `subtitle_window`, `compose_completed`,
`job_completed`, `job_failed`. Include elapsed time, scene index, motion,
transition, and safe error code. Never log tokens, private keys, or sensitive
reference-audio data.

Subtitles must not dissolve over each other during a transition: burn each
subtitle only outside its entering/leaving xfade window. Prefer `fade` for
short-form documentary/anime content; use `dissolve` only deliberately.

### Completion checklist

1. Validate script/assets and ZIP integrity.
2. Check scene order, narration, motion, transition, and optional Wan plan.
3. Run relevant tests and `git diff --check`.
4. Restart native server after backend/static changes and verify `/health`.
5. State accurately whether Wan is a UI/contract only or is connected and
   smoke-tested against the current RunPod.

### RunPod live monitor

Use the tracked read-only monitor rather than pasting a host/key into a shell
command. It reads only `RUNPOD_SSH_*` fields from ignored `.env` (or explicit
shell variables) and shows ComfyUI queue, GPU usage, recent outputs and the
latest ComfyUI log lines. It never prints `.env` values or private keys.

```bash
./scripts/monitor-runpod.sh
```

### Current Wan capability

AutoClip now has engine selection, SQLite `render_engine` persistence,
editable Wan Preview data, structured investigation logs, and FFmpeg final
composition. The native Wan client has been smoke-tested against the current
RunPod: upload image → queue native ComfyUI Wan 2.2 workflow → poll history →
download MP4 → add narration/subtitles → compose final video. `lip_sync: true`
is still an explicit future F5 + LatentSync stage, not a claim that lip sync
has already occurred.

## Mamase editorial playbook and clip-generation procedure

### Channel identity

Channel name: **Mamase จักรวาลของใจ**. The channel makes Thai vertical
short-form videos for YouTube Shorts, TikTok, and Reels about unusual places
around the world, accessible science, surprising space facts, and timely
trends/news. Tone: curious, warm, credible, cinematic, and never sensational
at the expense of accuracy.

The recurring presenter is an original, friendly Thai anime adult male:
slightly tousled black hair, thin rectangular glasses, navy blazer over black
shirt, welcoming smile, and an explanatory pointing gesture. Keep this visual
identity consistent through `character_id: "mamase-presenter-v1"`; do not add
in-image text to presenter or scene art unless the user explicitly asks.

### Required creative approval order

For a new public clip, do this in order:

1. Discuss the topic and the desired angle with the user.
2. Present the complete Thai script and scene outline for review first.
3. Wait for approval or requested revision before generating images, JSON, or
   ZIP. The user may explicitly waive this for a quick technical test package.
4. Generate one suitable vertical image per scene; regenerate only the weak
   scene rather than recreating the entire clip.
5. Build/validate the ZIP and return the artifact.
6. On Create Video, let the user review/edit narration, subtitles, motion,
   transition, TTS pronunciation, and optional Wan plan before Generate.

Never present generated fiction or an unverified claim as a factual script.
For science, space, current events, or other time-sensitive claims, verify
against authoritative current sources before writing the final script.

### Default clip structure

Aim for 45-70 seconds unless the user requests a short technical test. A usual
format is 5-8 content scenes plus an optional 3-4 second presenter intro and a
brief Mamase branding outro:

```text
Hook → reveal/context → why/how → unexpected twist → meaning/safety context
→ warm ending/CTA → optional Mamase brand scene
```

- Hook must create curiosity in the first 2-3 seconds without misleading.
- Narration must be natural Thai, short enough to be spoken clearly, and use
  Thai phonetic spelling or `tts_text` for difficult foreign names.
- Avoid gore, graphic remains, frightening imagery, and unsupported medical or
  scientific implications. State nuance where a popular myth is misleading.
- Use varied visuals: aerial/wide, environmental detail, close documentary
  subject, people/presenter only when useful, then a closing wide shot.
- Keep lower-center composition reasonably clean for Thai subtitles.
- Match image style inside one clip: cinematic documentary for facts/nature,
  clean semi-realistic anime only for the presenter.

### Scene and transition rules

- Use one image per scene with `motion`, `motion_speed`, `motion_intensity`,
  `focus`, and the transition from that scene into the next.
- Prefer `fade` as the default transition. Use `dissolve` sparingly; it can
  look noisy in FFmpeg. Use directional transitions only when they reinforce
  the story rather than distract.
- Safe motion defaults: `cinematic_push_in`, `gentle_float`,
  `documentary_pan`, and a limited `auto` sequence. Do not animate a scene
  whose subject would look unnatural with camera motion.
- `transition: "none"` is an intentional hard cut; use it for a punchline or
  sharp reveal only.
- The final scene's transition is ignored.
- Keep subtitles out of transition windows, as specified above.

### BGM and voice policy

- A ZIP may include only one optional `audio/bgm.*`. It must be music the user
  owns or is licensed to use commercially. Never copy audio from YouTube or a
  podcast as BGM/reference material.
- AutoClip mixes BGM under narration. The story must remain intelligible with
  BGM disabled.
- Reference voice audio belongs in protected local/RunPod configuration, not
  the ZIP. Only use a voice reference when the person has given permission.
- For normal B-roll, use narration audio and no lip-sync. Enable lip-sync only
  for a clear front-facing presenter/talking-character scene.

### Named working examples

- **Lake Natron**: frame the lake as a striking high-alkalinity salt lake;
  explain that mineral/salt preservation can make dead animals look stone-like
  without claiming the lake magically turns living animals into stone. Include
  the flamingo breeding contrast. Existing short technical packages include a
  two-scene test and a Wan-plan presenter test.
- **Black-hole topic**: use a factual, non-alarmist angle. Gaia BH1 is roughly
  1,500-1,560 light-years away and is dormant; explain discovery through its
  companion star's motion and that it presents no threat to Earth.

### ZIP delivery checklist for a new clip

```text
script.json at ZIP root
images/ exists and every scene image path resolves
scene order matches approved script
Thai narration and tts_text are reviewed
motion/transition are intentionally chosen
optional wan data exists only if the user wants Wan control
optional BGM is licensed and named audio/bgm.<supported extension>
ZIP passes unzip -t and PackageService validation
```

ตรวจด้วย `ffprobe` พบ 33 frames และ full decode ด้วย FFmpeg สำเร็จโดยไม่มี error

## Verification หลังติดตั้ง

```bash
nvidia-smi
curl -fsS http://127.0.0.1:8188/system_stats
sha256sum \
  /workspace/ComfyUI/models/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors \
  /workspace/ComfyUI/models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors \
  /workspace/ComfyUI/models/vae/wan2.2_vae.safetensors
```

ตรวจวิดีโอ:

```bash
ffprobe -v error -show_entries \
  format=duration,size,format_name:stream=codec_name,width,height,pix_fmt,r_frame_rate,nb_frames \
  -of json /workspace/ComfyUI/output/video/OUTPUT.mp4

ffmpeg -v error -i /workspace/ComfyUI/output/video/OUTPUT.mp4 -f null -
```

## หลักการสำหรับ agent ครั้งต่อไป

- ขอ/อ่าน SSH command ล่าสุดจาก RunPod Console ก่อนทำงานทุกครั้ง เพราะ IP, hostname, username, port และ key อาจเปลี่ยน
- ห้ามนำ SSH target, Pod ID หรือ private key path จาก session เก่ากลับมาใช้โดยไม่ตรวจสอบ
- ใช้ SSH command ที่ผู้ใช้ให้มาเป็น source of truth และอย่าแก้ username, host, port หรือ key ด้วยการคาดเดา
- ห้ามใช้ `~/.ssh/id_ed25519` กับ RunPod; key นี้สงวนไว้สำหรับ GitHub ให้ใช้ dedicated RunPod key ที่ผู้ใช้ระบุ เช่น `~/.ssh/id_ed25519_runpod`
- เชื่อม SSH เข้า RunPod และตรวจ `hostname`, `uname -a`, `nvidia-smi` ก่อนติดตั้งทุกครั้ง
- ห้ามติดตั้งหรือดาวน์โหลดโมเดลบน local Mac
- ก่อนดาวน์โหลดไฟล์เกิน 1 GB ต้องรายงานชื่อ, source URL/repository, ขนาด และ destination
- ตรวจไฟล์เดิมก่อนดาวน์โหลดเสมอ และห้ามดาวน์โหลดซ้ำโดยไม่จำเป็น
- หาก URL, compatibility หรือ checksum ไม่แน่นอน ให้หยุดและตรวจสอบจาก official source ก่อน
- หลีกเลี่ยง destructive changes; ถ้าไฟล์เดิมผิด hash ให้รายงานและขอคำสั่งแทนการลบหรือเขียนทับ
- เก็บไฟล์ใหญ่ทั้งหมดใต้ `/workspace`
- ใช้ native ComfyUI workflow; อย่าติดตั้ง custom nodes ถ้าไม่มี requirement ใหม่
- หลัง generation ต้องตรวจ output ด้วย FFprobe และ full FFmpeg decode ก่อนรายงานว่าสำเร็จ

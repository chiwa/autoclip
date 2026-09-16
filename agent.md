# Wan2.2 TI2V RunPod Setup Notes

เอกสารนี้เป็น runbook สำหรับสร้าง environment Wan2.2 TI2V 5B บน RunPod ใหม่ให้เหมือนเครื่องที่ทดสอบสำเร็จแล้ว ห้ามติดตั้ง ComfyUI, CUDA หรือโมเดลขนาดใหญ่บน local Mac งานทั้งหมดต้องทำภายใน RunPod และเก็บไฟล์ใหญ่ใต้ `/workspace`

## Thai Java Zone shared visual style bible

กฎส่วนนี้ใช้กับงาน **Thai Java Zone ทุกชิ้น** และต้องถูกนำไปใช้กับภาพ,
shot list, scene plan และ image/video generation prompt ทุกซีน:

- ใช้ภาษาภาพแบบ **clean modern software-engineering explainer** ที่อ่านแนวคิด
  หลักได้ทันทีบนจอมือถือ
- หนึ่งซีนอธิบายหนึ่งแนวคิดที่ชัดเจนเท่านั้น ใช้ภาพ developer workspace,
  backend system หรือ software architecture ที่สมจริง เป็นมืออาชีพ และตรงกับ
  narration ของซีน
- จัดองค์ประกอบให้สมดุล มี visual hierarchy ชัด ลดของตกแต่งและรายละเอียดที่
  ไม่ช่วยอธิบายเรื่อง ใช้ soft natural lighting, dark neutral tech background
  และ subtle depth
- สร้างและส่งมอบเป็นแนวตั้ง 9:16 โดยรักษาวัตถุสำคัญให้อยู่ใน motion-safe
  และ subtitle-safe areas
- ห้ามมีข้อความ, subtitle, watermark, logo, label, fake UI text หรือข้อความ
  ที่โมเดลภาพสร้างขึ้นภายในภาพ เว้นแต่ผู้ใช้สั่งเป็นกรณีพิเศษ
- ห้ามใช้ cyberpunk, futuristic holograms, fantasy technology, excessive neon,
  glowing monoliths หรือ sci-fi movie-poster aesthetics โดยเด็ดขาด
- ทุก scene prompt ต้อง inherit base style นี้ก่อนเติมรายละเอียดเฉพาะซีน ห้าม
  คิด visual direction, art style, palette หรือโลกภาพใหม่แยกกันในแต่ละซีน
  ความต่อเนื่องทั้งชุดเป็นข้อบังคับ ไม่ใช่คำแนะนำ

กฎ Thai Java Zone นี้มีขอบเขตเฉพาะช่องดังกล่าว และไม่แทนที่ visual language
หรือข้อกำหนดเฉพาะช่องอื่น เช่น Mamase

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

ComfyUI บน A40 นี้ใช้ dynamic VRAM เป็น runtime ที่ยืนยันแล้ว. `--highvram`
รองรับใน CLI แต่การทดลองกับ Wan shot ยาวทำให้ service ไม่กลับมาที่ 8188 จึง
ห้ามตั้งเป็น default หรือใส่ใน installer. อาจทดลองเฉพาะช็อต 81 frames เมื่อ
queue ว่างและต้องมี rollback/health check ทันที. อย่าใส่ `--normalvram`
เพราะ ComfyUI version ที่ทดสอบไม่รองรับ argument นี้.

`/workspace/start-comfyui.sh` ส่ง argument ผ่านไปยัง ComfyUI จึงใช้
`/workspace/start-comfyui.sh --highvram` ได้สำหรับ controlled experiment
เท่านั้น. ตรวจ `/queue` ให้ไม่มีงานก่อนเปลี่ยน mode, restart เพียงครั้งเดียว,
แล้วตรวจ `system_stats`, `nvidia-smi` และ render smoke test ก่อนรับงานจริง.

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
- **สร้างด้วย AI** (`/ai`) is a two-stage automatic package path: the user
  supplies only a topic and optional concept; AutoClip first plans a script and
  shot list for approval, then creates images only after the script is
  approved. The user may edit a specific scene and regenerate only its image,
  then approves the visual preview before AutoClip validates and returns the
  final ZIP. The page must show a persistent live progress section (step,
  percentage, and investigation logs) in both generation stages. It has no
  chat. Use the server-only `GEMINI_API_KEY`; never expose it to the browser or
  write it into a package.
- Wan is a renderer inside Create Video, never a separate product flow.
- Even with Wan, FFmpeg does final scene ordering, narration, subtitles,
  transitions, BGM ducking/mix, loudness normalization, and MP4 export.
- Never silently fall back from `wan2.2` to `ffmpeg_motion`. Return a safe,
  stable error such as `WAN_NOT_CONFIGURED` or `WAN_UNAVAILABLE`.

### ZIP contract (do not change without approval)

One unchanged ZIP supports both render choices. Every scene always has a valid
image and FFmpeg `motion`. The optional `wan` object opts only that scene into
AI motion when the user selects Wan 2.2: scenes with `wan` use Wan and scenes
without it automatically use FFmpeg Motion. When the user selects FFmpeg
Motion, every scene uses FFmpeg and all `wan` objects are ignored. Do not add a
per-scene renderer field and do not require every scene to contain `wan`.

```text
script.json                 # required at ZIP root
video-metadata.json         # required for Title, Description, and Social Hashtags
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
- Treat `narration` as viewer-facing wording, but add `tts_text` whenever a
  scene contains English, an acronym, a foreign proper name, a scientific
  designation, a unit, or a number that Thai TTS might misread. Keep the
  correct spelling in narration/subtitles and write the whole spoken line in
  natural Thai phonetics for `tts_text`: `Parker Solar Probe` → `พาร์กเกอร์
  โซลาร์ โพรบ`, `Hubble` → `ฮับเบิล`, `N44` → `เอ็น สี่สิบสี่`, and
  `Superbubble` → `ซูเปอร์บับเบิล`. Never rely on a Thai model guessing
  English pronunciation; listen to the per-scene TTS preview before publishing.

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

For `wan2.2` jobs, the collapsed **Live technical log** may additionally show
a bounded, redacted server-side tail of `/workspace/comfyui.log` from RunPod.
The browser must never SSH to RunPod or receive any Pod credential. Stream it
only through AutoClip's existing SSE log event, remove terminal escape codes,
redact token-like values, and stop the SSH tailer when the scene render ends.

Wan outputs run at 16 fps and require a `4k + 1` frame count. Derive the frame
count from narration duration for every Wan scene, treating `wan.frames` only
as a lower bound. Never let a conventional `81` frame package default shorten
a longer narration and force `render_wan_video` to loop the source clip.

### Wan speed profile

Generate vertical Wan at **640x1152** and upscale only in the final AutoClip
composition. Write Wan narration so each shot is about **4.5–5.0 seconds**;
normal scenes use exactly `frames: 81` (about 5.06 seconds at 16 fps). Add a
new scene rather than silently stretching a Wan shot beyond that budget. The
renderer still increases frames when narration is longer, because it must not
loop a shorter AI video beneath speech.

### Thai TTS selection on Generate page

The Generate page presents exactly two narration choices: **Local — Vachana
Thai** and **RunPod — F5-TTS-THAI V2**. The selected value must travel with the
job; it must never silently fall back to another provider. RunPod F5 uses the
configured dedicated SSH connector, the protected reference WAV and reference
transcript, then copies only the generated WAV back to the job workspace.
Never expose SSH details, keys, reference audio, or remote paths to the
browser. Keep the provider disabled only through configuration when the Pod is
unavailable, and return a clear safe configuration error.

The video-page voice selector must always match its selected provider. Local
Vachana uses only `thai-male-01`, `thai-female-01`, `thai-male-02`, or
`thai-female-02`; RunPod F5 uses the protected reference voice and must not
show a misleading model-specific roster. Never allow Kokoro labels such as
`m_young_clear` to overwrite a Local Vachana ZIP voice during submit. Accept
those old labels as defensive Local aliases for already-created packages, but
generate all new Local packages with the canonical Vachana names.

### Wan sampling steps policy

The default Wan 2.2 sampling budget is **22 steps**. It is the production
speed/quality balance for the A40 RunPod. ZIPs may set `wan.steps` per scene
between 10 and 50; omitted means the configured default. The first hook scene
of every Mamase package must explicitly set `"steps": 25` for the best first
impression. Other scenes normally omit it and use 22. `steps` controls the
sampling budget; it is not the frame rate or video duration.

### Priority backlog: Wan scene retry and resume

Implement resumable Wan jobs before treating full multi-scene GPU rendering as
production-ready. Persist each scene's state (`queued`, `rendering`,
`completed`, `failed`) and its Wan video, narration WAV, subtitle, prompt ID,
seed, and safe error metadata. History must provide **Retry failed scene** and
**Retry from scene N** actions that retain successful prior scenes, regenerate
only the selected/dependent scene, then compose the final MP4 again. Never
silently discard a successfully rendered scene merely because a later one
failed. Cleanup must preserve artifacts for running jobs and projects marked
Keep.

## Mamase editorial playbook and clip-generation procedure

### Channel identity

Channel name: **Mamase จักรวาลของใจ**. The channel makes Thai vertical
short-form videos for YouTube Shorts, TikTok, and Reels about unusual places
around the world, accessible science, surprising space facts, and timely
trends/news. Tone: curious, warm, credible, cinematic, and never sensational
at the expense of accuracy.

### Visual Standard: Real Science + Cinematic Documentary (ไม่ใช่ "AI Infographic Channel")

แนวทางภาพหลักของ **“จักรวาลของใจ”** กำหนดเป็น **"Real Science + Cinematic Documentary"** (ระดับสารคดีดาราศาสตร์สากล) โดยมีแนวภาพตัวอย่างอ้างอิงอยู่ใน `dist/examples/` (ศึกษาจากช่องชั้นนำอย่าง @DeepSpaceTH และ Cosmic Documentaries):

1. **แหล่งภาพอันดับหนึ่ง (Preferred Image Sources)**:
   - ใช้ภาพถ่ายทางดาราศาสตร์และวิทยาศาสตร์ของจริงความละเอียดสูงจาก **NASA, James Webb Space Telescope (JWST), ESO (European Southern Observatory), Hubble Space Telescope, และ Caltech/IPAC** เป็นลำดับแรก
   - หลีกเลี่ยงภาพ 2D กราฟิกจำลองแบนๆ (Flat programmatic vector) หรือภาพสไตล์ AI ทั่วไปที่ดูประดิษฐ์และไร้มิติ

2. **โทนภาพและความอลังการ (Aesthetic & Mood)**:
   - **Deep Cosmic Space**: อวกาศมืดลึก จุดดาวคมกริบ กาแล็กซี ทางช้างเผือก หลุมดำ จานสะสมมวล (Accretion Disks) และเนบิวลาที่มีแสงเรืองรอง volumetric มีพลัง ดึงดูดสายตา และสมจริงตามหลักฟิสิกส์
   - **Authentic Astronomical Hardware**: โมเดลกล้องโทรทรรศน์อวกาศ แผงรับแสง หอดูดาวภาคพื้นดินที่กำลังยิง Laser Guide Star สู่ท้องฟ้า
   - **Human & Philosophical Connection**: มีภาพมนุษย์ยืนมองท้องฟ้าดวงดาวท่ามกลางธรรมชาติอันกว้างใหญ่ หรือกองไฟใต้ทางช้างเผือก เพื่อเชื่อมโยงความลึกลับของอวกาศเข้ากับจิตใจมนุษย์ (สอดคล้องกับชื่อช่อง "จักรวาลของใจ")

3. **กฎ On-Screen Graphics (Minimal Sci-Fi HUD vs No Clunky Cards)**:
   - **ห้ามใส่การ์ดข้อความสี่เหลี่ยมทึบ บุลเล็ตพอยต์ หรือ Infographic Box รกตา**
   - สำหรับคลิป Mamase ปกติ **ไม่ใช้ HUD, label, callout หรือ telemetry ในภาพ**; อนุญาตได้เฉพาะเมื่อผู้ใช้ขอภาพข้อมูลโดยตรง และต้องเล็ก โปร่งแสง และไม่ทำให้ภาพกลายเป็น infographic
   - ปล่อยให้เนื้อหาหลักเป็นหน้าที่ของเสียงบรรยาย (Voiceover) และระบบ AutoClip Subtitles โดยไม่บดบังความงามของภาพอวกาศ

### Visual quality gate: ห้ามส่งงานภาพที่ดูโล่ง/ฉุ่ย

ก่อนประกอบ ZIP ให้ตรวจภาพ master ทุก scene ในขนาดที่เห็นบนมือถือจริง
โดยเฉพาะหมวดอวกาศ/วิทยาศาสตร์ ภาพต้องมีมาตรฐาน **premium cinematic
documentary** ไม่ใช่สไลด์ดำโล่ง, infographic, หรือวัตถุเล็ก ๆ แปะอยู่บน
starfield:

ก่อนสร้าง Reel อวกาศ/วิทยาศาสตร์ ให้ **อ่าน
`assets/parker_solar_probe_reel/visual-reference.md` ก่อน**. ไฟล์นี้สรุป
visual benchmark ของ Parker แบบสั้น จึงไม่ต้องเปิด master images ทุกไฟล์;
เปิดเฉพาะภาพที่ต้องศึกษา composition เพิ่ม. ต้องทำให้ถึงหรือดีกว่ามาตรฐานนี้
แต่ห้ามคัดลอกเนื้อหา Sun/Parker ไปใส่เรื่องอื่น. ห้ามใช้ `dist/` เป็น reference
หลัก เพราะเป็น output ZIP ที่อาจถูก cleanup ได้.

- Subject หลักต้องเด่นและใหญ่พอ โดยใช้ foreground + midground + background
  หรือแสง/อนุภาค/scale cue ที่ทำให้เรื่องมีมิติ; ห้ามปล่อยยานหรือดวงจันทร์
  เล็ก ๆ ลอยอยู่ในผืนดำส่วนใหญ่ของเฟรม
- ให้ active visual composition กินพื้นที่กลางภาพราว 70–80%; subtitle safe
  area ด้านล่างเป็นพื้นที่สงบพอดี ไม่ใช่พื้นที่ดำว่างครึ่งภาพ
- ใช้แสงและบรรยากาศระดับสารคดี: direction ของแสงสมเหตุผล, reflected ice,
  volumetric particle/dust, contrast ที่ลุ่มลึก และ scale ที่สัมผัสได้; หลีกเลี่ยง
  cut-out asset บนพื้นหลังดาวธรรมดา
- Scene 2 เป็นต้นไปห้ามมี generated text, callout, แผนภาพ, numbered list,
  HUD, NASA/ESA logo, watermark, หรือ subtitle ฝังในภาพ. สำหรับ Mamase Reel
  ให้ composite เฉพาะโลโก้จริงจาก `assets/branding/mamase/logo.png` หลังสร้าง
  artwork ตาม skill `mamase-reels`; ห้ามให้โมเดลวาดโลโก้เอง
- Scene 1 เป็น **Permanent Standard Key Art**: ต้องยึดมาตรฐาน ISS (`assets/iss_why_not_fall_reel/images/scene-01-hook.png`) และ Voyager 1 (`assets/voyager1_reel/images/scene-01-hook.png`) เป็นโปสเตอร์สารคดีพรีเมียมที่หยุดฟีดทันที (1–2 วิ) สื่อปริศนาในภาพเดียว และอ่าน Topic + Thai Hook ชัดบนมือถือ ห้ามทำเป็น infographic, presentation slide หรือวัตถุขนาดใหญ่แปะบนพื้นหลัง ลำดับสายตาต้องเป็น Brand → Topic → Thai Hook → Hero Subject → Human and Dog; Hero subject ต้องเห็นรูปทรงและบริบทครบ ไม่ซูมจนเป็น texture และไม่เล็กจนเป็น sticker; คนและสุนัขใน foreground ต้องหันมอง hero subject และอยู่ในโลกที่มีแสงเงาทิศทางเดียวกัน; สร้าง raw artwork ไร้ตัวหนังสือก่อน แล้ว composite โลโก้จริงและ typography deterministic; ตรวจผ่าน 12-point QA gate แล้ว**ส่งให้ผู้ใช้อนุมัติและหยุดรอ** ห้ามสร้างซีนถัดไปหรือ ZIP ก่อน Scene 01 ได้รับการอนุมัติ
- หากต้องอธิบายกลไก ใช้ cinematic cutaway ที่ไม่มี label และยังสวยแบบภาพยนตร์
  ไม่ใช้ภาพตัดขวางแบบตำรา/slide

**Reject / regenerate** ทันที หากภาพมี dead space เกินราวหนึ่งในสามโดยไม่มี
เหตุผลทางองค์ประกอบ, starfield filler, subject เล็กหรือไม่มีจุดโฟกัส,
สไตล์ไม่ต่อเนื่อง, ตัวหนังสือหลุด/อ่านไม่ได้, โลโก้/ลายน้ำ, presenter ดูเหมือน
วางทับ, หรือภาพไม่สื่อ fact ของ narration ได้ก่อนอ่าน subtitle. ให้แก้เฉพาะ
scene ที่ไม่ผ่านก่อนสร้าง ZIP และเก็บ scene ที่ดีไว้เหมือนเดิม.

### Autonomous master-image workflow (มาตรฐาน Tianwen-2)

เมื่อผู้ใช้ขอคลิปทั้งชุด ให้ agent สร้าง master images จาก scene plan ที่ผ่าน review เองทั้งหมด **ห้ามโยนงานให้ผู้ใช้เขียน image prompt ทีละซีน**. แปลง narration เป็น visual brief: fact หลัก, subject, action, setting, scale cue และอารมณ์. แต่สำหรับ Scene 01 จะต้องปฏิบัติตาม **Scene 01 Permanent Workflow**: สร้าง raw artwork → composite deterministic typography/branding → ตรวจ QA → **ส่ง Scene 01 ให้ผู้ใช้อนุมัติและหยุดรอ** ก่อนเริ่มผลิตภาพซีนอื่นเสมอ

ทุก scene เป็น heroic factual frame: foreground subject เด่น + midground action + background ที่ให้ scale/atmosphere; ใช้ detail วิทยาศาสตร์/วิศวกรรมที่น่าเชื่อ, แสงมีทิศทาง, cinematic navy/cyan ตัด gold/orange, subtitle-safe band ด้านล่างพอดี. สร้าง native aspect ratio, ตรวจบนมือถือ, regenerate เฉพาะ scene อ่อน และห้ามใช้ black-starfield filler เพื่อให้จบงาน.

Scene 1 เท่านั้นที่มี Thai topic title + short hook; Scene 2 เป็นต้นไปไม่มี generated text, label, HUD, watermark หรือ agency logo. สำหรับ Mamase Reel ให้ใส่เฉพาะโลโก้จริงตาม skill `mamase-reels` หลังสร้าง artwork. ชุด `assets/tianwen-2-quasi-satellite-reel/images/` เป็นตัวอย่าง workflow ที่ผ่าน: key art แบบ integrated แล้วตามด้วยภาพตรง narration สำหรับ quasi-satellite, journey, close approach, surface study, sampling, return และ next mission leg. ใช้วิธีคิดนี้กับเรื่องใหม่โดยห้ามคัดลอก subject matter.

### Delivery formats and framing

Create each package for one delivery format; never crop vertical scene art into
horizontal output or the reverse.

- **Shorts / Reels / TikTok:** `1080x1920` (9:16). Keep the lower-center safe
  area clear for Thai subtitles.
- **Standard YouTube:** `1920x1080` (16:9). Use genuine horizontal assets,
  retain a clean lower-center subtitle area, and favour wide establishing shots,
  medium documentary details, and cinematic landscapes.

### Reel / Shorts production default

Mamase Reels must prioritize a very strong opening hook. The first 1–3 seconds are critical because viewers can swipe away immediately. Follow `docs/mamase-reels-standard.md` as the canonical rule: target **45–55 seconds**, normally stay under **60 seconds**, and use about 6–9 narrated content scenes followed by a separate silent 2-second branding post-roll. Content density and curiosity are more important than fixed duration. Do not add filler to hit a runtime; every few seconds must add new information, payoff, reversal, consequence, or a larger question.

#### Mandatory Reels Hook Rules

1. **The first 1–3 seconds MUST stop the viewer's thumb.**
2. **Never begin with**:
   - greetings (สวัสดีครับ, ยินดีต้อนรับ)
   - channel introductions (สู่ Mamase จักรวาลของใจ)
   - "วันนี้เราจะมาพูดถึง...", "ในคลิปนี้เราจะ..."
   - background/history
   - definitions
   - slow setup
3. **Start immediately with one of**:
   - a surprising fact
   - a contradiction
   - a strong curiosity question
   - an unexpected consequence
   - a scientifically accurate “เฮ้ย เป็นแบบนี้ได้ยังไง?” moment
4. **The hook must be truthful and scientifically defensible.** Do NOT use misleading clickbait.
5. **Prefer simple questions that a non-scientist can understand instantly.**
6. **The hook must create an open loop that makes the viewer want the next sentence.** The second sentence must immediately continue the promise of the hook.

#### Recommended Mamase Reel Structure

- **0–3 sec: HOOK** — A fact/question/contradiction strong enough to stop scrolling.
- **3–10 sec: MINIMAL CONTEXT** — Only the information required to understand the mystery. No unnecessary background.
- **10–30 sec: PAYOFF + WOW** — Deliver real information quickly. Introduce at least one surprising fact or reversal.
- **30–45 sec: TWIST / BIGGER QUESTION / FINAL PAYOFF** — End the content with another interesting implication, twist, or question. Follow it only with the separate mandatory Mamase outro and its approved one-sentence CTA.

#### Examples of Good vs Bad Hooks

- **GOOD Hooks**:
  - “บนดาวศุกร์ 1 วันยาวกว่า 1 ปี”
  - “ของหนักกว่า 400 ตันลอยอยู่เหนือหัวเรา แล้วทำไม ISS ไม่ตก?”
  - “เรารู้ได้ยังไงว่าไม่มีอะไรเร็วกว่าแสง?”
  - “ดวงอาทิตย์ร้อนหลายพันองศา แล้วทำไมอวกาศถึงหนาว?”
  - “ดาวทุกดวงที่เราเห็นด้วยตาเปล่า อยู่ใน Milky Way จริงไหม?”
- **BAD Hooks (Never use)**:
  - “สวัสดีครับ วันนี้เราจะมาพูดถึงดาวศุกร์”
  - “ดาวศุกร์เป็นดาวเคราะห์ดวงที่สองจากดวงอาทิตย์”
  - “ในคลิปนี้เราจะมาเรียนรู้เรื่องความเร็วแสง”

#### Mamase Storytelling Principle

Do not add filler just to reach duration. Every few seconds should give the viewer one of these feelings:
- “เฮ้ย จริงเหรอ?”
- “แล้วต่อไปล่ะ?”
- “ทำไมเป็นแบบนั้น?”
- “มีอะไรอีก?”
- “อยากฟังต่อ”
The viewer should feel continuous forward movement.

#### Production Rules (TTS, Visuals, CTA, Duration)

- **TTS Rule**: Google Gemini TTS voice `Fenrir`, language `th-TH`. Scene 1 automatically uses the dedicated Hook style at speed `1.10`; Scene 2 onward uses the Normal Reel style at speed `1.05`, as defined in `docs/mamase-reels-standard.md`. The spoken script must begin directly with the hook, exactly matching the `hook` metadata field. Do not insert Mamase branding, greetings ("สวัสดีครับ"), "วันนี้เราจะมา...", "รู้หรือไม่...", episode labels, or intro music before the hook.
- **Visual Rule**: The first visual scene must reinforce the hook immediately. Do not begin with generic stars, slow logo animation, or unrelated establishing shots. The first frame should visually communicate the mystery. The hero astronomical/scientific subject must dominate the frame (never a tiny pasted subject or an empty landscape that overpowers the hero subject).
- **Duration & Pacing**: Follow `docs/mamase-reels-standard.md`: target 45–55 seconds and normally remain under 60 seconds. Use about 6–9 narrated content scenes followed by the separate silent post-roll, with one visual source per content scene and no fake `visual_beats` support.
- **Topic-Specific CTA Rule**: End the Reel with one short question naturally inviting discussion (opinion, prediction, or philosophical reaction) matching the topic. Strictly forbid generic CTAs ("อย่าลืมกดไลก์", "กดติดตาม", "คอมเมนต์คุยกันหน่อย", "ขอบคุณที่รับชม", or legacy canned outros). The CTA is the final spoken sentence with zero spoken text after it.
- **Branding Rule**: Use "Mamase" or "Mamase REELS" only. Strictly NO "MAMASE PODCAST" on Reel assets, and strictly NO bilingual badges ("AVAILABLE IN THAI & ENGLISH") or flags.

#### Mamase Reel Hook Gate (Blocking QA Gate)

For Antigravity and any producing agent, treat the Reel Hook Gate as a **blocking QA gate**. Do not proceed to image generation, TTS, or rendering until the hook passes all 10 checks:

1. Hook within first 1–3 sec
2. No greeting/setup before hook
3. Simple enough for general audience
4. Creates curiosity gap
5. Scientifically accurate
6. First visual reinforces hook (hero subject dominates frame)
7. No filler
8. New information/payoff every few seconds
9. Ending leaves a strong final idea/twist
10. TTS starts directly with hook

If the answer to any major item is NO, rewrite the opening before generating TTS or visuals.

Prefer **FFmpeg Motion** for the main body of short-form clips because it is
fast, stable, and inexpensive. A Reel normally needs **0–2 Wan shots** only:
the opening Mamase presenter/hook and, if justified, one high-impact reveal.
Use FFmpeg Motion for all remaining b-roll, with varied source images and
intentional motion/focus rather than repeatedly zooming the same frame.

### Long-form YouTube pacing

For a roughly 10-minute standard YouTube video, plan about 18-22 narrative
chapters but 70-100 visual scenes/shots. Change the visual every 4-8 seconds;
hold only a deliberately important tableau for up to 8-10 seconds. A scene is
a visual shot for this purpose, not a whole chapter. Use roughly 10-15 Wan 2.2
hero shots for the highest-stakes moments and FFmpeg Motion for the remaining
explanatory shots. Every extra shot must advance the story, comparison, or
emotion; do not change images merely to create motion.

Set the intended format in `project.resolution` and make every image in the ZIP
match it. AutoClip resolves a per-job render profile from the final project
resolution, so FFmpeg scene rendering, Wan normalization, subtitles, and final
composition use the same dimensions.

The Create Video UI must always offer these output choices:

- `use_json` — use `project.resolution` from the ZIP.
- `vertical` — override the project to `1080x1920`.
- `youtube` — override the project to `1920x1080`.

An explicit UI choice overrides the ZIP only for that job; write the selected
format to the job record and log the resolved dimensions. Never mutate the
original uploaded ZIP outside that job workspace.

The recurring presenter is an original, friendly Thai anime adult male:
slightly tousled black hair, thin rectangular glasses, navy blazer over black
shirt, welcoming smile, and an explanatory pointing gesture. Keep this visual
identity consistent through `character_id: "mamase-presenter-v1"`; do not add
in-image text to presenter or scene art unless the user explicitly asks.

### Mandatory Mamase branding outro

For vertical Mamase Reels, follow `.codex/skills/mamase-reels/SKILL.md`:

- composite `assets/branding/mamase/logo.png` onto every 1080x1920 content
  scene at about 19% frame width (approximately 205x205), top-right with a
  36-pixel margin by default; inspect at mobile size;
- never ask an image model to redraw the logo;
- use `assets/branding/mamase/reels-end-scene.png` as the immutable outro
  artwork master; never crop, regenerate, recolor, retouch, change its text, or
  add another logo. A package copy may be proportionally resized to 1080x1920
  without altering the master or its composition.

The locked image is mandatory as a separate silent branding post-roll, not a
story scene. End the final content scene on the memorable scientific idea or
topic-specific question while its normal content image remains visible. Only
after narration and subtitles end, append the end card for 2.0 seconds with no
TTS and no subtitle; continue BGM briefly and fade it to silence. Use the
optional top-level `outro` object from `docs/mamase-reels-standard.md`. Never
place a narrated `brand-outro` scene in new `script.json` files.


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

### First-scene hook rule

The first 2-3 seconds must earn attention with the strongest truthful visual
and a concise spoken question or reveal. Make the opening image the most
visually arresting asset in the package, with a clear subject and motion that
is legible on a phone screen.

Every first scene must also carry a short, beautiful in-image text hook. Keep
it to roughly 2-5 Thai words or an equivalently short phrase, use large clean
Thai-capable type with high contrast, and place it away from the subtitle safe
area and the main subject. The text must sharpen curiosity without asserting
an unverified claim. Treat it as intentional title design, not a cluttered
infographic card.

For science hooks, compose the first image like a premium science-book cover
or documentary-film poster: one dominant focal subject, deliberate negative
space, and one elegant title. Never turn it into a crowded information card.

Treat that first image as **Narrative Key Art** (also called a cinematic
storytelling thumbnail): a single image that communicates the whole video's
story, stakes, and emotional promise at a glance—not merely its topic. Use a
clear cause-and-effect or before-and-after composition when it helps. The
thumbnail and Scene 1 must share this same core story image so the viewer gets
an immediate payoff after clicking.

The recurring Mamase anime presenter must appear in every first scene, using
the established friendly glasses, tousled-black-hair, navy-blazer identity and
a face-forward composition suitable for Wan/LatentSync talking shots. Keep the
same character on the right or otherwise leave the hook text readable.
The canonical visual reference is
`assets/characters/mamase-presenter-v1.png`; never replace it or substitute a
new character without the user's approval. Set `character_id` to
`mamase-presenter-v1` in the scene's Wan plan.

For unsettled science stories, use a strong question without depicting an
unverified conclusion as fact. For example, K2-18 b may open with a cinematic
exoplanet, its host star, a small JWST silhouette, and the in-image hook
`เจอสัญญาณเอเลียน?` alongside the narration `K2-18 b… เราเจอสัญญาณของเอเลียน
แล้วหรือยัง?` Do not show aliens or text that implies life has been confirmed;
immediately follow with the evidence and its limits.

### Default clip structure

Aim for 45-70 seconds unless the user requests a short technical test. A
normal public clip has **at least 8 scenes**, including the mandatory Mamase
branding outro. Add more scenes only when they introduce a distinct factual
beat, visual reveal, explanation, or emotional turn; never pad the runtime by
repeating an idea or decorative b-roll. A usual story flow is:

```text
Hook → reveal/context → why/how → unexpected twist → meaning/safety context
→ warm ending/CTA → Mamase brand scene
```

### Mamase science-storyteller voice

Write voiceover as a charismatic Thai science storyteller: curious, friendly,
slightly cheeky, conversational, and genuinely excited by surprising facts.
The delivery is an intelligent friend sharing a discovery—not a news anchor or
a textbook. Give each clip a clear rhythm:

```text
Imaginable hook → everyday scale comparison → surprising reveal
→ playful aside / “แต่เดี๋ยวก่อน...” → accurate explanation → warm wonder
```

- Turn large scientific quantities into a concrete everyday image where useful
  (for example, compare light-speed travel to laps around Earth), but retain
  the correct qualification and measurement.
- Use short natural punctuation in narration. For `tts_text`, do not use
  ellipses (`...`) only for an intentional, natural playful beat such as
  `เฮ้ย... จริงดิ?`; do not scatter them through every sentence.
- Use natural spoken asides when they make the science feel tangible and the
  narrator feel present: `แต่เดี๋ยวก่อน...`, `ย้ำนะครับ สมมุติ!`, or
  `เอ๊ะ วันนี้แดดก็ดีนี่นา`. They are reactions woven into the explanation,
  not catchphrases to repeat mechanically.
- Light humor must serve comprehension. Do not turn a hypothetical into a
  prediction, make unsupported claims, or sacrifice scientific precision for a
  stronger punchline.
- Prefer endings that invite wonder: knowing more should reveal how much there
  still is to discover.
- Gemini TTS default delivery prompt:

  `Read aloud in a natural, playful, conversational Thai voice. Sound relaxed, confident, and slightly cheeky, like you're casually telling a fascinating story to a close friend. Keep the energy lively but effortless — never sound like a news presenter, announcer, or formal narrator. Use natural changes in pitch and rhythm. Occasionally stretch or emphasize important words for personality. Add small pauses before surprising or funny moments, as if you're building anticipation. The delivery should feel spontaneous and human, with a subtle smile in the voice. Let some sentences start softly and then become more animated when the story gets interesting. Keep the pacing medium to slightly fast, but don't rush. Avoid perfectly even timing between sentences. For surprising facts, sound genuinely impressed or amused, as if you're thinking: "เฮ้ย... จริงดิ?" Overall personality: friendly, curious, mischievous, charming, expressive, slightly teasing, and naturally excited. Think of a charismatic Thai content creator explaining something interesting on TikTok or Reels — casual, fun, and easy to listen to. Never sound robotic, overly dramatic, overly cute, or like you're reading from a script.`

- Approved Mamase Google Gemini TTS profile, unless the user overrides it:

  ```json
  {
    "voice": "Fenrir",
    "pitch": 0,
    "speakingRate": 1.05
  }
  ```

  The intended feeling is **natural, playful, relaxed, confident, and naturally
  conversational**—like a thoughtful friend sharing an interesting story.
  Keep volume even and pacing energetic and crisp; do not repeatedly punch or stress words.

- Google Gemini TTS is the default provider for Native AutoClip. The UI must
  expose an editable narration-style prompt and speaking rate, with a visible
  **คืนค่า Mamase default** action that always restores the approved prompt,
  Fenrir, and `speakingRate: 1.05`. Google voices must be grouped as **ชาย** and
  **หญิง**, with Fenrir first in the male group. It uses
  silence trimming disabled by default because trimming generated narration can
  clip the first Thai syllable and make scene joins sound unnatural. Keep the
  configurable trimming feature available only as an explicit opt-in.
  Application Default Credentials from `gcloud auth application-default login`
  and the quota project set with `gcloud auth application-default
  set-quota-project`. Do not create a service-account JSON key, set
  `GOOGLE_APPLICATION_CREDENTIALS`, expose tokens, or place credentials in ZIPs.
  `AUTOCLIP_GOOGLE_CLOUD_PROJECT` is optional because Native ADC already carries
  the quota project; use it only as an explicit override. Google Gemini
  narration may be generated concurrently for
  up to six scenes per job by default (configurable through
  `AUTOCLIP_GOOGLE_TTS_PARALLELISM`), but completed audio must be mapped back to the
  original scene order before rendering.

- For the FFmpeg Motion engine only, render up to two independent scenes per
  job concurrently (`AUTOCLIP_FFMPEG_SCENE_PARALLELISM`, range 1–4). Each
  worker owns its SRT and MP4; sort outputs back into original scene order
  before final composition. Wan 2.2 and final composition stay sequential.

- YouTube Podcast Generator (`/podcast`):
  - Purpose: Long-form horizontal (16:9 1920×1080 30 FPS) visual podcast from a
    single cover image and long Thai script without requiring a ZIP package.
  - Defaults: Voice `Iapetus`, speed `0.90`, connected conversational phrasing
    with brief pauses only at punctuation/topic changes, BGM
    `assets/sounds/mamase-podcast-bg.mp3` at volume `0.08`
    (8%), subtitles enabled.
  - The Podcast UI can persist the current voice, speed, and Thai/English style
    prompts as browser-local defaults, with an explicit restore-system-defaults
    action. This must not change Reel/Generate defaults.
  - Script chunking: `PodcastChunker` splits by paragraph, sentence, and Thai word
    boundaries (via PyThaiNLP) to strictly remain within `AUTOCLIP_PODCAST_CHUNK_MAX_BYTES`
    (default 2,800 UTF-8 bytes).
  - Parallel synthesis: finish and cache all Thai chunks before starting
    English synthesis. Each language is bounded by
    `AUTOCLIP_PODCAST_CONCURRENCY` (default 3 concurrent requests) with up to 5 retries separated by at least 5 seconds, provider `Retry-After` handling, and
    persistent workspace chunk caching (`podcast_chunks/`). Losslessly stitched
    via FFmpeg concat demuxer.
  - A failed Podcast can be retried from its progress page. Reuse valid cached
    chunks and regenerate only missing/failed chunks before continuing render.
  - Video motion & audio ducking: `PodcastVideoRenderer` constructs a 6-stage
    breathing motion cycle looped with `-stream_loop -1` and mixes background
    music with `asplit=2` sidechain compression beneath spoken narration.
  - English alternate audio: `podcast-en.wav` uses the same selected BGM,
    volume, fade, sidechain ducking, and loudness normalization as the Thai
    video audio. Keep `english_narration_raw.wav` for targeted retry/repair.
  - Existing Reel defaults (`Fenrir`, 1.05, 9:16, ZIP packages) remain 100% isolated
    and intact.

- Hook must create curiosity in the first 2-3 seconds without misleading.
- Scene 1 in-image typography always has two clear layers: a concise topic
  title (for example `ดาวศุกร์`) plus a separate short hook. The title tells
  viewers what the story is about; the hook earns the next few seconds. Keep
  the hierarchy elegant, mobile-readable, and outside the subtitle safe area.
- For future clips, preserve Mamase's recognizable face, tousled black hair,
  and rectangular glasses, but do not fix one outfit forever. Match the
  wardrobe to the scene background with a professional, youthful, lightly
  playful look. Do not alter an already-approved presenter asset in a current
  package unless the user explicitly asks. Match facial expression and natural
  body language to the story beat: wonder, surprise, joy, concern, curiosity,
  or quiet reflection are all valid when appropriate.
- Narration must be natural Thai, short enough to be spoken clearly. Any
  English word, acronym, foreign name, scientific label, date, unit, or number
  that could be mispronounced requires a full Thai-phonetic `tts_text` for
  that scene; test it in the per-scene TTS preview before final publishing.
- Avoid gore, graphic remains, frightening imagery, and unsupported medical or
  scientific implications. State nuance where a popular myth is misleading.
- Use varied visuals: aerial/wide, environmental detail, close documentary
  subject, people/presenter only when useful, then a closing wide shot.
- Each scene image must illustrate its own narration directly, not merely the
  overall topic. Derive the visual subject, setting, action, and factual detail
  from that scene's spoken sentence; use an image that makes the point legible
  before the subtitle is read. Do not reuse generic decorative b-roll when a
  scene calls for a specific animal, process, place, object, or scientific
  evidence.
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
video-metadata.json at ZIP root (Title, Description, Hashtags)
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

### ปัญหาที่เคยพบในการสร้างแพ็กเกจคอนเทนต์และแนวทางหลีกเลี่ยง (Content Pitfalls to Avoid)

1. **ห้ามแก้ไขโค้ดระบบเดิม (No Unnecessary Code Modifications)**:
   - ระบบ AutoClip มีโค้ดรองรับการทำงานพื้นฐาน เช่น `video-metadata.json`, TTS, ฟอนต์, และ ZIP contract ไว้อยู่แล้ว
   - เมื่อสร้างคอนเทนต์หรือ ZIP ใหม่ **ห้ามแก้ไขโค้ดใน `app/` เด็ดขาด** ยกเว้นได้รับคำสั่งปรับปรุงฟีเจอร์จากผู้ใช้โดยตรง

2. **ต้องมี `video-metadata.json` ควบคู่เสมอ**:
   - ทุกครั้งที่สร้างไฟล์ ZIP ต้องแนบ `video-metadata.json` ไว้ที่ root ของ ZIP เสมอ
   - โครงสร้างต้องมี `"title"` (ชื่อคลิปชวนคลิก) และ `"description"` (เรื่องย่อ, คำโปรย, แท็กไลน์ช่อง และแฮชแท็ก) เพื่อให้ระบบนำไปแสดงผลบนหน้า Preview และบันทึกลงฐานข้อมูล

3. **ปัญหาตัวหนังสือเป็นสี่เหลี่ยม (Font Tofu / Missing Glyphs)**:
   - ห้ามใช้ฟอนต์อังกฤษล้วน (เช่น Helvetica) กับข้อความภาษาไทย เพราะอักขระไทยจะกลายเป็นกล่องสี่เหลี่ยม `□`
   - ต้องใช้ฟอนต์ที่รองรับทั้งภาษาไทยและอังกฤษอย่างสมบูรณ์ เช่น `SukhumvitSet.ttc` หรือ `Thonburi.ttc` บน macOS (หรือ `Noto Sans Thai` บน Linux/Docker)
   - ห้ามใช้สัญลักษณ์ Unicode แปลกปลอมที่ไม่การันตีว่ามีในฟอนต์ (เช่น `✓`, `★`, `▲`, `▼`, `➔`, `⚡`) ให้วาดสัญลักษณ์เหล่านี้เป็นเวกเตอร์ตรงด้วยโค้ด (`draw.line`, `draw.polygon`) หรือใช้ตัวเลข/ป้ายกำกับแทน

4. **ปัญหาตัวหนังสือล้นขอบภาพ (Text Overflow & Layout Safe Area)**:
   - เมื่อสร้างภาพที่มีไดอะแกรมหรือข้อความอธิบาย ต้องวัดขนาดข้อความและตัดขึ้นบรรทัดใหม่เสมอ (Auto Line/Word Wrapping) โดยกำหนดความกว้างไม่ให้เกิน Card Padding
   - ต้องเว้นพื้นที่ปลอดภัยด้านล่าง (Bottom Safe Area ตั้งแต่ $Y \ge 1350$ ในขนาด 1080x1920) ให้โปร่ง เพื่อไม่ให้ภาพหรือการ์ดไปทับซ้อนกับ Subtitle ภาษาไทยที่ระบบจะเบิร์นลงไป

5. **ความยาวและจำนวนซีนของคลิป (Pacing & Scene Count - พอดีพอพี)**:
   - **ความยาว 5–10 ซีนแล้วแต่เนื้อหา ไม่ต้อง fixed**: ให้ยึดความพอดีของเนื้อเรื่องเป็นหลัก ("พอดีพอพี") ไม่เยิ่นเย้อจนน่าเบื่อ และไม่สั้นเกินไปจนเนื้อหาขาดมิติ
   - หากเป็นประเด็นสั้นกระชับเข้าใจง่าย ใช้ 5–6 ซีน (~30–45 วินาที)
   - หากเป็นเรื่องราวที่มีมิติเชิงลึก/สารคดีน่าติดตาม (เช่น การค้นพบทางดาราศาสตร์ ทฤษฎีฟิสิกส์ หรือปริศนาจักรวาล) ขยายได้เป็น 7–10 ซีน (~50–70 วินาที) เพื่อให้เนื้อหาครบถ้วน ดื่มด่ำ ชวนคิด และอิ่มเอม

6. **ความต่างระหว่างคลิป 'วิทยาศาสตร์ความงาม' vs 'อวกาศ/จักรวาล' (Visual Direction Rule)**:
   - **หมวดวิทยาศาสตร์/ความงาม (Science & Skincare)**: ใช้ Infographic ที่มีข้อความสั้นกระชับ, ไดอะแกรม, หรือการ์ดตารางเปรียบเทียบคลีนๆ สไตล์ Modern Medical ได้
   - **หมวดอวกาศ/จักรวาล (Space & Universe)**: **ยึดมาตรฐาน "Real Science + Cinematic Documentary" (ไม่ใช่ "AI Infographic Channel")**
     - **แนวภาพอ้างอิง**: ศึกษาแนวภาพที่ผู้ใช้ชอบใน `dist/examples/` (ช่องอย่าง @DeepSpaceTH / สารคดีดาราศาสตร์ระดับสากล)
     - **แหล่งภาพจริง**: คัดเลือกและใช้ภาพถ่ายจริงความละเอียดสูงจาก **NASA, James Webb Space Telescope (JWST), ESO (European Southern Observatory), Hubble, และ Caltech/IPAC** เป็นลำดับแรก
     - **ความอลังการระดับ BBC / National Geographic ไร้ตัวหนังสือบังภาพ**: เน้นภาพอวกาศ ดวงดาว กาแล็กซี เนบิวลา หลุมดำ และเทคโนโลยีกล้องโทรทรรศน์ที่สวยงาม ยิ่งใหญ่อลังการ ดื่มด่ำ (Immersive) แบบเต็มจอ
     - **การใส่ Title บนภาพ**: **มี Title ในภาพได้บ้างเพื่อ hook คนดูให้หยุดดูคลิป** (เช่น ชื่อหัวข้อสไตล์สารคดีตัวหนาคมกริบ หรือ Telemetry HUD ขนาดเล็ก) **แต่ไม่จำเป็นต้องมีทุกซีน** และต้องไม่บดบังองค์ประกอบภาพหลักเด็ดขาด ปล่อยให้เนื้อหาหลักขับเคลื่อนด้วยเสียงบรรยายและ Subtitle
# คนเหนือดวง — ดวง 12 ราศีประจำสัปดาห์

- หน้าใช้งานถาวรคือ `/zodiac-weekly` และเป็น workflow/brand แยกจาก Mamase,
  Podcast และ Reels
- อินพุตหลักคือ `weekly-zodiac-batch.json` หนึ่งชุด ระบุช่วงสัปดาห์และใส่
  เนื้อหาครบ 12 ราศีได้; ถ้า `zodiacs` ว่าง ระบบใช้ข้อความมาตรฐานที่ปลอดภัย
- ภาพ master อยู่ที่ `assets/12ราศี` จำนวน 12 ไฟล์ เปลี่ยนเฉพาะป้ายวันที่
  รายสัปดาห์ ห้ามสร้างหรือแก้ title, range และ artwork ที่ฝังอยู่ในภาพ
- ผลลัพธ์บังคับต่อ batch: MP4 12 ไฟล์, ZIP งาน 12 ไฟล์, metadata JSON 12
  ไฟล์ และ UTF-8 `youtube-upload.csv` 12 แถว
- metadata แต่ละราศีต้องมี title ที่อิง hook จริง, description แบบ teaser,
  disclaimer `การดูดวงเป็นความเชื่อส่วนบุคคล โปรดใช้วิจารณญาณในการรับชม`,
  hashtag เฉพาะราศี, search tags, week, visibility และชื่อ MP4 ที่ตรงกัน
- Video rendering กับ publishing metadata เป็นคนละ layer: การแก้หรือ
  regenerate Title/Description/Hashtags/Tags ห้าม submit job, เรียก TTS หรือ
  encode scene ใหม่เด็ดขาด การ sync metadata ลง MP4 ใช้ FFmpeg stream-copy
  remux เท่านั้นและทำเมื่อ hash เปลี่ยน
- ค่าเสียงถาวร: Google Gemini voice `Iapetus`, ภาษา `th-TH`, speed `1.10`,
  mood อบอุ่น สงบ มั่นใจ ลึกลับเล็กน้อยแต่ไม่ขลังเกินจริง ห้ามอ่านแบบข่าว,
  โฆษณา, ละคร, กระซิบเวอร์ หรือเว้นช่วงประดิษฐ์ จังหวะต้องเป็นธรรมชาติ ลื่นไหล
  และกระชับขึ้นเล็กน้อย ห้ามลากเสียงหรือหยุดแบบ dramatic นาน ใช้ style prompt ที่ประกาศใน
  `app/services/zodiac_service.py` เป็น source of truth
- โครงบทถาวร: Hook ภายใน 1–3 วินาที → การงาน → การเงิน → ความรัก →
  คำแนะนำ → ปิดให้รู้สึกดีและอยากกลับมาฟังสัปดาห์หน้า
- รองรับ `visual` ใน batch JSON: ใช้ template เป็นภาพหลัก, ไม่สร้างภาพใหม่,
  overlay ข้อความจาก `week.display_th` โดยไม่เขียนทับ master และเมื่อ
  `motion.enabled=false`/`preset=none` ต้องเขียน `motion: none` ทุกซีน
- History ต้องจำแนก `zodiac`/`zodiac_batch`, เปิด batch เดิมได้หลัง restart,
  ดาวน์โหลดรายราศีหรือรวมชุดได้ และ retry เฉพาะงานที่ failed

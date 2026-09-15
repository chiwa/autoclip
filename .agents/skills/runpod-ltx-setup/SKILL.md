---
name: runpod-ltx-setup
description: >-
  Automated setup and verification runbook for provisioning RunPod GPU instances (NVIDIA A40/A100)
  with LTX-Video 2B Distilled for AutoClip. Use when launching a new RunPod instance, updating
  connection credentials in AutoClip, installing PyTorch CUDA 12.4 + LTX-Video, pre-caching weights,
  and running validation benchmarks.
---

# RunPod LTX-Video & MuseTalk Lip-sync Setup Skill

This skill documents and automates the complete provisioning of **LTX-Video 2B Distilled** (`Lightricks/LTX-Video`) and **MuseTalk Lip-sync** (`TMElyralab/MuseTalk`) on a RunPod GPU (NVIDIA A40 48GB recommended) for use in **AutoClip**.

---

## 🎯 1. Prerequisites & Specifications

- **Recommended GPU**: NVIDIA A40 (46,068 MiB usable VRAM) or A100 (40GB/80GB).
- **Environment**: Linux Ubuntu 22.04+, Python 3.12, PyTorch 2.6.0+cu124, CUDA 12.8 Toolkit (`nvcc`).
- **LTX-Video**: `ltxv-2b-0.9.6-distilled-04-25.safetensors`, base pipeline, bfloat16, 8 steps (`448x768`, 15 fps).
- **MuseTalk**: V1.5 / V1.0 unet, Whisper-tiny, DWPose, SD-VAE, Face-parsing for real-time audio-driven lip syncing.

---

## 🚀 2. Fast Provisioning Workflow

When launching a new RunPod instance:

### Step 1: Verify SSH Connectivity
```bash
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -p <PORT> -i ~/.ssh/id_ed25519 root@<HOST> "nvidia-smi"
```

### Step 2: Bootstrap Environment (LTX-Video + MuseTalk)
```bash
# 1. Run LTX-Video bootstrap
scp -P <PORT> -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no scripts/bootstrap.sh root@<HOST>:/tmp/bootstrap.sh
ssh -p <PORT> -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no root@<HOST> "bash /tmp/bootstrap.sh /workspace/ltx-video-poc"

# 2. Run automated MuseTalk provisioning (installs mmcv-lite, patches PyTorch 2.6 weights_only, downloads all weights)
scp -P <PORT> -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no resources/setup_musetalk.sh root@<HOST>:/tmp/setup_musetalk.sh
ssh -p <PORT> -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no root@<HOST> "bash /tmp/setup_musetalk.sh /workspace/musetalk"
```

The MuseTalk setup script automatically handles:
1. Cloning repository to `/workspace/musetalk`.
2. Installing PyTorch CUDA 12.4, OpenMMLab stack (`mmengine==0.10.7`, `mmcv-lite==2.1.0`, `mmdet==3.3.0`, `mmpose==1.3.2`).
3. Applying runtime patch for `mmcv.utils.ext_loader.DummyExt` to prevent missing C++ op crashes on DWPose init.
4. Applying PyTorch 2.6 `weights_only=False` patch for legacy `.pth` checkpoints (BiSeNet ResNet18, DWPose).
5. Downloading all required models (`MuseTalk V1.5`, `whisper-tiny`, `sd-vae-ft-mse`, `DWPose`, `face-parse-bisent`).
6. Linking `config.json` for diffusers UNet.

### Step 3: Verify MuseTalk Inference
```bash
ssh -p <PORT> -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no root@<HOST> \
  "cd /workspace/musetalk && .venv/bin/python -m scripts.inference --inference_config configs/inference/test.yaml --use_float16"
```

---

## ⚙️ 3. AutoClip Configuration

Update `.env`:
```dotenv
AUTOCLIP_LTX_ENABLED=true
AUTOCLIP_LTX_SSH_HOST=<HOST>
AUTOCLIP_LTX_SSH_PORT=<PORT>
AUTOCLIP_LTX_SSH_USER=root
AUTOCLIP_LTX_SSH_KEY_PATH=/Users/zengcode/.ssh/id_ed25519

AUTOCLIP_MUSETALK_ENABLED=true
AUTOCLIP_MUSETALK_SSH_HOST=<HOST>
AUTOCLIP_MUSETALK_SSH_PORT=<PORT>
AUTOCLIP_MUSETALK_SSH_USER=root
AUTOCLIP_MUSETALK_SSH_KEY_PATH=/Users/zengcode/.ssh/id_ed25519
```

And in `config.yaml`:
```yaml
ltx:
  enabled: true
  width: 448
  height: 768
  fps: 15
  steps: 8
  seed: 171198
musetalk:
  enabled: true
  bbox_shift: 0
  version: v1.5
```

---

## 🧪 4. AutoClip End-to-End Verification

```bash
# Run unit tests
.venv/bin/pytest tests/unit/test_render_engine.py

# Submit a package with LTX engine and lip-sync
curl -s -X POST http://127.0.0.1:8000/api/jobs \
  -F "file=@dist/package-with-lip-sync.zip" \
  -F "render_engine=ltx" \
  -F "tts_provider=google-gemini"
```

---

## ⚠️ 5. Known Limitations & Lip-sync Quality Workarounds

### The Blurry Mouth Problem
LTX-Video 2B is memory-intensive and is hardcoded to generate **`448x768`** resolution videos to fit within the memory limits of a 48GB A40 instance. 
If this video is upscaled to standard `1080x1920` using standard FFmpeg Lanczos, the result loses sharpness. 
If MuseTalk is run on the upscaled `1080x1920` video, the face is already blurry, causing the generated mouth to look out of place or equally blurred.

### The Static High-Res Hook Solution
For critical scenes where the presenter's face must be crystal clear (e.g., the Hook scene `scene-01-hook`), the best workaround is to **bypass LTX-Video entirely**.

Instead of sending the image to LTX for motion generation:
1. Send the original `1080x1920` static image (`scene-xx.png`) directly to MuseTalk.
2. MuseTalk natively supports static images. It will repeat the image to match the audio duration and animate only the lips.
3. The resulting video will have **zero camera/head motion** (static), but the presenter will remain **100% sharp at 1080x1920**.

*Note: In `job_service.py`, there is a manual patch that allows routing an image directly to MuseTalk if LTX is bypassed. When writing a skill or a `script.json`, keep in mind that removing the `ltx` options from a scene but leaving `lip_sync: true` might be the desired approach to achieve this crystal clear static lip-sync.*


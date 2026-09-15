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
# Copy and execute bootstrap script
scp -P <PORT> -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no scripts/bootstrap.sh root@<HOST>:/tmp/bootstrap.sh
ssh -p <PORT> -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no root@<HOST> "bash /tmp/bootstrap.sh /workspace/ltx-video-poc"
```

The bootstrap script performs:
1. Cloning and installing LTX-Video (`/workspace/ltx-video-poc`).
2. Cloning and installing MuseTalk (`/workspace/musetalk`).
3. Downloading all model weights (MuseTalk UNet, Whisper-tiny, DWPose, LatentSync SyncNet, SD-VAE, Face-parse).
4. Building mmcv with CUDA ops.

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


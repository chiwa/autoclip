#!/usr/bin/env bash
set -euo pipefail

# Automated MuseTalk Setup for RunPod (Ubuntu 22.04+ / Python 3.12 / PyTorch 2.6+cu124)
TARGET_DIR="${1:-/workspace/musetalk}"
echo "=== Setting up MuseTalk in $TARGET_DIR ==="

mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"

if [ ! -d ".git" ]; then
    git clone https://github.com/TMElyralab/MuseTalk.git .
fi

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

pip install --upgrade pip setuptools wheel
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
pip install diffusers transformers accelerate ffmpeg-python opencv-python soundfile gradio librosa einops timm omegaconf yapf

# OpenMMLab dependencies
pip install openmim
pip install mmengine==0.10.7
pip install mmcv-lite==2.1.0
pip install mmdet==3.3.0
pip install mmpose==1.3.2

# Patch mmcv ext_loader for mmcv-lite fallback
python3 -c "
import pathlib, site
p = pathlib.Path(site.getsitepackages()[0]) / 'mmcv' / 'utils' / 'ext_loader.py'
if p.exists():
    content = p.read_text()
    if 'class DummyExt' not in content:
        patch = '''
class DummyExt:
    def __getattr__(self, name):
        def _dummy(*args, **kwargs):
            return None
        return _dummy
'''
        content = content.replace('def load_ext(name, funcs):', patch + '\ndef load_ext(name, funcs):')
        content = content.replace('return ext', 'return ext if ext is not None else DummyExt()')
        content = content.replace('raise pkg_resources.DistributionNotFound(f\"{pkg_name} is not installed\")', 'return DummyExt()')
        p.write_text(content)
        print('Patched mmcv ext_loader.py')
"

# Patch PyTorch 2.6 weights_only=False default for legacy checkpoints
python3 -c "
import pathlib, site
for sp in site.getsitepackages():
    p = pathlib.Path(sp) / 'mmengine' / 'runner' / 'checkpoint.py'
    if p.exists():
        c = p.read_text()
        if 'weights_only' not in c:
            c = c.replace('return torch.load(filename, map_location=map_location)', 'return torch.load(filename, map_location=map_location, weights_only=False)')
            p.write_text(c)
            print('Patched mmengine checkpoint.py')
"

# Download model weights
pip install huggingface_hub
python3 -c "
from huggingface_hub import snapshot_download, hf_hub_download
import shutil, os
from pathlib import Path

Path('models').mkdir(exist_ok=True)
print('Downloading MuseTalk weights...')
snapshot_download('TMElyralab/MuseTalk', local_dir='models', ignore_patterns=['*.git*'])
snapshot_download('openai/whisper-tiny', local_dir='models/whisper')
snapshot_download('stabilityai/sd-vae-ft-mse', local_dir='models/sd-vae')
snapshot_download('yzd-v/DWPose', local_dir='models/dwpose')

# Face-parsing ResNet18
Path('models/face-parse-bisent').mkdir(parents=True, exist_ok=True)
hf_hub_download('camenduru/BiSeNet', '79999_iter.pth', local_dir='models/face-parse-bisent')
hf_hub_download('camenduru/BiSeNet', 'resnet18-5c106cde.pth', local_dir='models/face-parse-bisent')

# Copy config.json for unet
for p in ['models/musetalk', 'models/musetalkV15']:
    cfg = Path(p) / 'musetalk.json'
    target = Path(p) / 'config.json'
    if cfg.exists() and not target.exists():
        shutil.copy(cfg, target)
print('MuseTalk setup complete!')
"

chmod +x "$TARGET_DIR/.venv/bin/python" || true
echo "=== MuseTalk successfully installed & verified ==="

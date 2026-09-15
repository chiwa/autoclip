#!/usr/bin/env bash
set -euo pipefail

poc_root="${1:-/workspace/ltx-video-poc}"
repo_dir="$poc_root/LTX-Video"
venv_dir="$poc_root/.venv"

# --- LTX Video Setup ---
mkdir -p "$poc_root/input" "$poc_root/output" "$poc_root/logs"
if [[ ! -d "$repo_dir/.git" ]]; then
  git clone --depth 1 https://github.com/Lightricks/LTX-Video.git "$repo_dir"
fi
python3 -m venv "$venv_dir"
"$venv_dir/bin/python" -m pip install --upgrade pip setuptools wheel
"$venv_dir/bin/python" -m pip install \
  torch==2.6.0 torchvision==0.21.0 \
  --index-url https://download.pytorch.org/whl/cu124
"$venv_dir/bin/python" -m pip install -e "$repo_dir[inference]" accelerate

cp "$repo_dir/configs/ltxv-2b-0.9.6-distilled.yaml" "$poc_root/ltxv-2b-distilled-poc.yaml"
sed -i 's/prompt_enhancement_words_threshold: 120/prompt_enhancement_words_threshold: 0/' "$poc_root/ltxv-2b-distilled-poc.yaml"

# --- MuseTalk Lip-sync Setup ---
musetalk_root="/workspace/musetalk"
if [[ ! -d "$musetalk_root/.git" ]]; then
  git clone --depth 1 https://github.com/TMElyralab/MuseTalk.git "$musetalk_root"
fi
mkdir -p "$musetalk_root/input" "$musetalk_root/output" "$musetalk_root/logs"
mkdir -p "$musetalk_root/models/musetalk" "$musetalk_root/models/musetalkV15" "$musetalk_root/models/syncnet" "$musetalk_root/models/dwpose" "$musetalk_root/models/face-parse-bisent" "$musetalk_root/models/sd-vae" "$musetalk_root/models/whisper"

python3 -m venv "$musetalk_root/.venv"
"$musetalk_root/.venv/bin/pip" install --upgrade pip setuptools==69.5.1 wheel
"$musetalk_root/.venv/bin/pip" install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
"$musetalk_root/.venv/bin/pip" install accelerate diffusers transformers opencv-python soundfile librosa einops omegaconf ffmpeg-python moviepy gdown 'huggingface_hub[cli]' gradio face-alignment tqdm cython
"$musetalk_root/.venv/bin/pip" install --no-build-isolation chumpy xtcocotools
"$musetalk_root/.venv/bin/pip" install mmengine mmpose mmdet
export PATH=/usr/local/cuda-12.8/bin:/usr/local/cuda/bin:$PATH
export CUDA_HOME=/usr/local/cuda-12.8
MMCV_WITH_OPS=1 "$musetalk_root/.venv/bin/pip" install --no-build-isolation mmcv==2.1.0

# Download weights
"$musetalk_root/.venv/bin/python" -c '
from huggingface_hub import hf_hub_download
import os, urllib.request

hf_hub_download(repo_id="TMElyralab/MuseTalk", filename="musetalk/musetalk.json", local_dir="'"$musetalk_root"'/models")
hf_hub_download(repo_id="TMElyralab/MuseTalk", filename="musetalk/pytorch_model.bin", local_dir="'"$musetalk_root"'/models")
hf_hub_download(repo_id="TMElyralab/MuseTalk", filename="musetalkV15/musetalk.json", local_dir="'"$musetalk_root"'/models")
hf_hub_download(repo_id="TMElyralab/MuseTalk", filename="musetalkV15/unet.pth", local_dir="'"$musetalk_root"'/models")
hf_hub_download(repo_id="stabilityai/sd-vae-ft-mse", filename="config.json", local_dir="'"$musetalk_root"'/models/sd-vae")
hf_hub_download(repo_id="stabilityai/sd-vae-ft-mse", filename="diffusion_pytorch_model.bin", local_dir="'"$musetalk_root"'/models/sd-vae")
hf_hub_download(repo_id="openai/whisper-tiny", filename="config.json", local_dir="'"$musetalk_root"'/models/whisper")
hf_hub_download(repo_id="openai/whisper-tiny", filename="pytorch_model.bin", local_dir="'"$musetalk_root"'/models/whisper")
hf_hub_download(repo_id="openai/whisper-tiny", filename="preprocessor_config.json", local_dir="'"$musetalk_root"'/models/whisper")
hf_hub_download(repo_id="yzd-v/DWPose", filename="dw-ll_ucoco_384.pth", local_dir="'"$musetalk_root"'/models/dwpose")
hf_hub_download(repo_id="ByteDance/LatentSync", filename="latentsync_syncnet.pt", local_dir="'"$musetalk_root"'/models/syncnet")

if not os.path.exists("'"$musetalk_root"'/models/face-parse-bisent/resnet18-5c106cde.pth"):
    urllib.request.urlretrieve("https://download.pytorch.org/models/resnet18-5c106cde.pth", "'"$musetalk_root"'/models/face-parse-bisent/resnet18-5c106cde.pth")
'
"$musetalk_root/.venv/bin/gdown" 154JgKpzCPW82qINcVieuPH3fZ2e0P812 -O "$musetalk_root/models/face-parse-bisent/79999_iter.pth"

"$venv_dir/bin/python" -c 'import torch; assert torch.cuda.is_available(); print("PyTorch:", torch.__version__); print("CUDA:", torch.version.cuda); print("GPU:", torch.cuda.get_device_name(0)); print("VRAM GiB:", round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2))'
echo "LTX-Video and MuseTalk environment ready!"

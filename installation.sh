#!/usr/bin/env bash
# Recreate the verified Wan2.2 TI2V 5B + ComfyUI environment on a RunPod Pod.
# Run this script INSIDE the Pod. All persistent files are stored under /workspace.
set -Eeuo pipefail

WORKSPACE=${WORKSPACE:-/workspace}
COMFY_DIR="$WORKSPACE/ComfyUI"
COMFY_REF=${COMFY_REF:-95d755cd8107a72258d452b5d3657273d571f07d}
HF_REPO="https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main"
TOOLS_DIR="$WORKSPACE/tools"
F5_DIR="$TOOLS_DIR/F5-TTS-THAI"
F5_REF=${F5_REF:-7b0989f5f67378cdea12a117e140c11ac0a9f57d}
LATENTSYNC_DIR="$TOOLS_DIR/LatentSync"
LATENTSYNC_REF=${LATENTSYNC_REF:-a229c3948406bc2cf6eaf4873e662e70c6a04746}
F5_MODEL_DIR="$WORKSPACE/models/f5-tts-th-v2"
ASSUME_YES=0
[[ ${1:-} == "--yes" ]] && ASSUME_YES=1

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null || die "Required command not found: $1"; }

[[ $(uname -s) == Linux ]] || die "This installer must run inside the Linux RunPod, not on macOS."
[[ -d "$WORKSPACE" ]] || die "$WORKSPACE does not exist. Attach a persistent /workspace volume first."
need git; need curl; need python3; need nvidia-smi; need sha256sum

printf '\n== Remote environment ==\n'
nvidia-smi
python3 --version
free -h
df -h "$WORKSPACE"
python3 - <<'PY' || die "A CUDA-enabled PyTorch installation is required in the RunPod base image."
import torch
assert torch.cuda.is_available(), "PyTorch cannot access CUDA"
print("PyTorch:", torch.__version__, "CUDA:", torch.version.cuda)
print("GPU:", torch.cuda.get_device_name(0), "VRAM bytes:", torch.cuda.get_device_properties(0).total_memory)
PY

avail_kb=$(df -Pk "$WORKSPACE" | awk 'NR==2 {print $4}')
(( avail_kb >= 25 * 1024 * 1024 )) || die "At least 25 GiB free under $WORKSPACE is required."

printf '\n== Install ComfyUI ==\n'
if [[ ! -d "$COMFY_DIR/.git" ]]; then
  git init "$COMFY_DIR"
  git -C "$COMFY_DIR" remote add origin https://github.com/Comfy-Org/ComfyUI.git
fi
current=$(git -C "$COMFY_DIR" rev-parse HEAD 2>/dev/null || true)
if [[ $current != "$COMFY_REF" ]]; then
  git -C "$COMFY_DIR" fetch --depth 1 origin "$COMFY_REF"
  git -C "$COMFY_DIR" checkout --detach FETCH_HEAD
fi
python3 -m venv --system-site-packages "$COMFY_DIR/.venv"
"$COMFY_DIR/.venv/bin/python" -m pip install --upgrade pip
"$COMFY_DIR/.venv/bin/pip" install -r "$COMFY_DIR/requirements.txt"

printf '\n== System tools for video, Thai TTS, and lip sync ==\n'
if ! command -v ffmpeg >/dev/null || ! command -v python3.10 >/dev/null; then
  [[ $(id -u) == 0 ]] || die "Run as root to install FFmpeg and Python 3.10."
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ffmpeg software-properties-common ca-certificates git curl libgl1 libglib2.0-0
  if ! command -v python3.10 >/dev/null; then
    add-apt-repository -y ppa:deadsnakes/ppa
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      python3.10 python3.10-dev python3.10-venv python3.10-distutils
  fi
fi

declare -a MODEL_ROWS=(
  "diffusion_models|wan2.2_ti2v_5B_fp16.safetensors|9999658848|456f901338bd9eadbded3828b819109a9b68e8a525ca5cf8d0049a69fcfeca1e|split_files/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors"
  "text_encoders|umt5_xxl_fp8_e4m3fn_scaled.safetensors|6735906897|c3355d30191f1f066b26d93fba017ae9809dce6c627dda5f6a66eaa651204f68|split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"
  "vae|wan2.2_vae.safetensors|1409400960|e40321bd36b9709991dae2530eb4ac303dd168276980d3e9bc4b6e2b75fed156|split_files/vae/wan2.2_vae.safetensors"
)

missing=0
printf '\n== Large model manifest (reported before download) ==\n'
for row in "${MODEL_ROWS[@]}"; do
  IFS='|' read -r folder name size hash rel <<<"$row"
  dest="$COMFY_DIR/models/$folder/$name"
  printf '%s | %s bytes | %s/%s | %s\n' "$name" "$size" "$HF_REPO" "$rel" "$dest"
  if [[ -f $dest ]]; then
    actual_size=$(stat -c %s "$dest")
    [[ $actual_size == "$size" ]] || die "Existing model has the wrong size; refusing to overwrite: $dest"
    printf '%s  %s\n' "$hash" "$dest" | sha256sum -c - >/dev/null || die "Existing model has the wrong SHA-256; refusing to overwrite: $dest"
    printf 'Verified existing model: %s\n' "$name"
  else
    missing=1
  fi
done

if (( missing )); then
  if (( ! ASSUME_YES )); then
    read -r -p "Download the missing files listed above? [y/N] " answer
    [[ $answer == y || $answer == Y ]] || die "Model download cancelled. Re-run with --yes for unattended setup."
  fi
  for row in "${MODEL_ROWS[@]}"; do
    IFS='|' read -r folder name size hash rel <<<"$row"
    dest="$COMFY_DIR/models/$folder/$name"
    [[ -f $dest ]] && continue
    mkdir -p "$(dirname "$dest")"
    part="$dest.part"
    curl -L --fail --retry 5 --retry-delay 5 -C - -o "$part" "$HF_REPO/$rel"
    [[ $(stat -c %s "$part") == "$size" ]] || die "Downloaded size mismatch: $part"
    printf '%s  %s\n' "$hash" "$part" | sha256sum -c -
    mv "$part" "$dest"
  done
fi

declare -a TALKING_MODEL_ROWS=(
  "model_350000.pt|1348534439|b9f9304f5ea0c4519d210c0c391d0b090e3b42acb07724ac92577d9c4dcce5ae|https://huggingface.co/VIZINTZOR/F5-TTS-TH-v2/resolve/main/model_350000.pt|$F5_MODEL_DIR/model_350000.pt"
  "latentsync_unet.pt|5072222488|0a478e89eb660f82da4c35dbdde8a5adfb27f99d1b4e50edd03729e1e98316d3|https://huggingface.co/ByteDance/LatentSync-1.6/resolve/main/latentsync_unet.pt|$LATENTSYNC_DIR/checkpoints/latentsync_unet.pt"
)

printf '\n== Thai voice and lip-sync large model manifest (reported before download) ==\n'
talking_missing=0
for row in "${TALKING_MODEL_ROWS[@]}"; do
  IFS='|' read -r name size hash url dest <<<"$row"
  printf '%s | %s bytes | %s | %s\n' "$name" "$size" "$url" "$dest"
  if [[ -f $dest ]]; then
    [[ $(stat -c %s "$dest") == "$size" ]] || die "Existing model has the wrong size; refusing to overwrite: $dest"
    printf '%s  %s\n' "$hash" "$dest" | sha256sum -c - >/dev/null || die "Existing model has the wrong SHA-256; refusing to overwrite: $dest"
    printf 'Verified existing model: %s\n' "$name"
  else
    talking_missing=1
  fi
done

if (( talking_missing && ! ASSUME_YES )); then
  read -r -p "Download the missing Thai voice/lip-sync files listed above? [y/N] " answer
  [[ $answer == y || $answer == Y ]] || die "Model download cancelled. Re-run with --yes for unattended setup."
fi

for row in "${TALKING_MODEL_ROWS[@]}"; do
  IFS='|' read -r name size hash url dest <<<"$row"
  [[ -f $dest ]] && continue
  mkdir -p "$(dirname "$dest")"
  part="$dest.part"
  curl -L --fail --retry 5 --retry-delay 5 -C - -o "$part" "$url"
  [[ $(stat -c %s "$part") == "$size" ]] || die "Downloaded size mismatch: $part"
  printf '%s  %s\n' "$hash" "$part" | sha256sum -c -
  mv "$part" "$dest"
done

printf '\n== Install F5-TTS-THAI V2 ==\n'
mkdir -p "$TOOLS_DIR"
if [[ ! -d "$F5_DIR/.git" ]]; then
  git init "$F5_DIR"
  git -C "$F5_DIR" remote add origin https://github.com/VYNCX/F5-TTS-THAI.git
fi
if [[ $(git -C "$F5_DIR" rev-parse HEAD 2>/dev/null || true) != "$F5_REF" ]]; then
  git -C "$F5_DIR" fetch --depth 1 origin "$F5_REF"
  git -C "$F5_DIR" checkout --detach FETCH_HEAD
fi
python3.10 -m venv "$F5_DIR/.venv"
"$F5_DIR/.venv/bin/python" -m ensurepip --upgrade
"$F5_DIR/.venv/bin/python" -m pip install --upgrade pip
"$F5_DIR/.venv/bin/python" -m pip install --extra-index-url https://download.pytorch.org/whl/cu121 \
  torch==2.5.1 torchaudio==2.5.1
"$F5_DIR/.venv/bin/python" -m pip install -e "$F5_DIR"
mkdir -p "$F5_MODEL_DIR"
cp "$F5_DIR/vocab/vocab_ipa.txt" "$F5_MODEL_DIR/vocab.txt"

printf '\n== Install LatentSync 1.6 ==\n'
if [[ ! -d "$LATENTSYNC_DIR/.git" ]]; then
  git init "$LATENTSYNC_DIR"
  git -C "$LATENTSYNC_DIR" remote add origin https://github.com/bytedance/LatentSync.git
fi
if [[ $(git -C "$LATENTSYNC_DIR" rev-parse HEAD 2>/dev/null || true) != "$LATENTSYNC_REF" ]]; then
  git -C "$LATENTSYNC_DIR" fetch --depth 1 origin "$LATENTSYNC_REF"
  git -C "$LATENTSYNC_DIR" checkout --detach FETCH_HEAD
fi
python3.10 -m venv "$LATENTSYNC_DIR/.venv"
"$LATENTSYNC_DIR/.venv/bin/python" -m pip install --upgrade pip
"$LATENTSYNC_DIR/.venv/bin/pip" install -r "$LATENTSYNC_DIR/requirements.txt"
mkdir -p "$LATENTSYNC_DIR/checkpoints/whisper"
if [[ ! -f "$LATENTSYNC_DIR/checkpoints/whisper/tiny.pt" ]]; then
  curl -L --fail --retry 5 -o "$LATENTSYNC_DIR/checkpoints/whisper/tiny.pt.part" \
    https://huggingface.co/ByteDance/LatentSync-1.6/resolve/main/whisper/tiny.pt
  mv "$LATENTSYNC_DIR/checkpoints/whisper/tiny.pt.part" "$LATENTSYNC_DIR/checkpoints/whisper/tiny.pt"
fi

"$F5_DIR/.venv/bin/python" - <<'PY'
import torch
assert torch.cuda.is_available()
print("F5-TTS GPU:", torch.__version__, torch.cuda.get_device_name(0))
PY
"$LATENTSYNC_DIR/.venv/bin/python" - <<'PY'
import torch
assert torch.cuda.is_available()
print("LatentSync GPU:", torch.__version__, torch.cuda.get_device_name(0))
PY

"$COMFY_DIR/.venv/bin/python" - <<PY
from safetensors import safe_open
for path in [
    "$COMFY_DIR/models/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors",
    "$COMFY_DIR/models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors",
    "$COMFY_DIR/models/vae/wan2.2_vae.safetensors",
]:
    with safe_open(path, framework="pt", device="cpu") as f:
        print("Readable:", path, "tensors:", len(list(f.keys())))
PY

cat > "$WORKSPACE/start-comfyui.sh" <<'EOF'
#!/usr/bin/env bash
set -Eeuo pipefail
cd /workspace/ComfyUI
exec .venv/bin/python main.py --listen 0.0.0.0 --port 8188 "$@"
EOF
chmod +x "$WORKSPACE/start-comfyui.sh"

cat > "$WORKSPACE/wan22-ti2v-api.json" <<'EOF'
{"37":{"class_type":"UNETLoader","inputs":{"unet_name":"wan2.2_ti2v_5B_fp16.safetensors","weight_dtype":"default"}},"38":{"class_type":"CLIPLoader","inputs":{"clip_name":"umt5_xxl_fp8_e4m3fn_scaled.safetensors","type":"wan","device":"default"}},"39":{"class_type":"VAELoader","inputs":{"vae_name":"wan2.2_vae.safetensors"}},"48":{"class_type":"ModelSamplingSD3","inputs":{"model":["37",0],"shift":8}},"6":{"class_type":"CLIPTextEncode","inputs":{"clip":["38",0],"text":"__PROMPT__"}},"7":{"class_type":"CLIPTextEncode","inputs":{"clip":["38",0],"text":"__NEGATIVE_PROMPT__"}},"56":{"class_type":"LoadImage","inputs":{"image":"__INPUT_IMAGE__"}},"55":{"class_type":"Wan22ImageToVideoLatent","inputs":{"vae":["39",0],"start_image":["56",0],"width":640,"height":352,"length":33,"batch_size":1}},"3":{"class_type":"KSampler","inputs":{"model":["48",0],"positive":["6",0],"negative":["7",0],"latent_image":["55",0],"seed":42,"steps":12,"cfg":5.0,"sampler_name":"uni_pc","scheduler":"simple","denoise":1.0}},"8":{"class_type":"VAEDecode","inputs":{"samples":["3",0],"vae":["39",0]}},"57":{"class_type":"CreateVideo","inputs":{"images":["8",0],"fps":16}},"58":{"class_type":"SaveVideo","inputs":{"video":["57",0],"filename_prefix":"video/wan22-ti2v","format":"auto","codec":"auto"}}}
EOF

cat > "$WORKSPACE/wan22-ti2v.py" <<'PY'
#!/usr/bin/env python3
import argparse, json, mimetypes, pathlib, time, urllib.request, uuid
def request(url, data=None, headers=None):
    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers or {}), timeout=120) as r: return json.load(r)
def upload(base, path):
    boundary="----wan22"+uuid.uuid4().hex; raw=pathlib.Path(path).read_bytes(); name=pathlib.Path(path).name
    mime=mimetypes.guess_type(path)[0] or "application/octet-stream"
    body=(f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{name}"\r\nContent-Type: {mime}\r\n\r\n'.encode()+raw+f'\r\n--{boundary}\r\nContent-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n--{boundary}--\r\n'.encode())
    return request(base+"/upload/image", body, {"Content-Type":"multipart/form-data; boundary="+boundary})
def main():
    p=argparse.ArgumentParser(description="Wan2.2 TI2V 5B ComfyUI API runner"); p.add_argument("image")
    p.add_argument("--prompt",default="A gentle cinematic camera push-in, subtle natural motion, stable composition, detailed."); p.add_argument("--negative-prompt",default="low quality, blurry, distorted, flicker, jitter, text, watermark, static")
    p.add_argument("--width",type=int,default=640); p.add_argument("--height",type=int,default=352); p.add_argument("--frames",type=int,default=33); p.add_argument("--steps",type=int,default=12); p.add_argument("--cfg",type=float,default=5); p.add_argument("--seed",type=int,default=42); p.add_argument("--fps",type=float,default=16); p.add_argument("--server",default="http://127.0.0.1:8188"); a=p.parse_args()
    if a.width%32 or a.height%32: p.error("width and height must be divisible by 32")
    g=json.loads(pathlib.Path("/workspace/wan22-ti2v-api.json").read_text()); g["56"]["inputs"]["image"]=upload(a.server,a.image)["name"]; g["6"]["inputs"]["text"]=a.prompt; g["7"]["inputs"]["text"]=a.negative_prompt; g["55"]["inputs"].update(width=a.width,height=a.height,length=a.frames); g["3"]["inputs"].update(seed=a.seed,steps=a.steps,cfg=a.cfg); g["57"]["inputs"]["fps"]=a.fps
    pid=request(a.server+"/prompt",json.dumps({"prompt":g,"client_id":uuid.uuid4().hex}).encode(),{"Content-Type":"application/json"})["prompt_id"]; print("prompt_id="+pid,flush=True)
    while True:
        history=request(a.server+"/history/"+pid)
        if pid in history:
            item=history[pid]; status=item.get("status",{})
            if status.get("status_str")=="error": raise RuntimeError(json.dumps(status,indent=2))
            files=[]
            for output in item.get("outputs",{}).values(): files += output.get("videos",[])+output.get("gifs",[])+output.get("images",[])
            for f in files:
                if pathlib.Path(f["filename"]).suffix.lower() in {".mp4",".mkv",".webm",".gif"}: print("output="+str(pathlib.Path("/workspace/ComfyUI/output")/f.get("subfolder","")/f["filename"])); return
            if status.get("completed"): raise RuntimeError("Completed without a video output")
        time.sleep(5)
if __name__ == "__main__": main()
PY
chmod +x "$WORKSPACE/wan22-ti2v.py"

template=$(find "$COMFY_DIR/.venv" -path '*/comfyui_workflow_templates_json/templates/video_wan2_2_5B_ti2v.json' -print -quit)
[[ -n $template ]] && cp "$template" "$WORKSPACE/wan22-ti2v-workflow.json"

cat > "$WORKSPACE/WAN22-INSTALL.log" <<EOF
Installed: $(date -u +%FT%TZ)
ComfyUI commit: $COMFY_REF
ComfyUI: $COMFY_DIR
Models: $COMFY_DIR/models/{diffusion_models,text_encoders,vae}
Custom nodes: none (native ComfyUI workflow)
F5-TTS-THAI commit: $F5_REF
F5-TTS-THAI: $F5_DIR
F5 model: $F5_MODEL_DIR/model_350000.pt
LatentSync commit: $LATENTSYNC_REF
LatentSync: $LATENTSYNC_DIR
LatentSync model: $LATENTSYNC_DIR/checkpoints/latentsync_unet.pt
Start: $WORKSPACE/start-comfyui.sh
API runner: $WORKSPACE/wan22-ti2v.py
API workflow: $WORKSPACE/wan22-ti2v-api.json
EOF

printf '\nInstallation complete. Start with:\n  %s/start-comfyui.sh\n' "$WORKSPACE"
printf 'Then generate with:\n  %s/wan22-ti2v.py /path/to/input.png --prompt "..."\n' "$WORKSPACE"

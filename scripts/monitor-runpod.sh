#!/usr/bin/env bash
# Live, read-only RunPod monitor for AutoClip's private ComfyUI tunnel host.
# Connection fields are read from the ignored .env file or explicit shell env.
set -euo pipefail

project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
dotenv_file="$project_root/.env"

dotenv_value() {
  local key="$1"
  [[ -f "$dotenv_file" ]] || return 0
  awk -F= -v wanted="$key" '$1 == wanted { value=$0; sub(/^[^=]*=/, "", value); gsub(/^"|"$/, "", value); print value; exit }' "$dotenv_file"
}

runpod_host=${RUNPOD_SSH_HOST:-$(dotenv_value RUNPOD_SSH_HOST)}
runpod_port=${RUNPOD_SSH_PORT:-$(dotenv_value RUNPOD_SSH_PORT)}
runpod_user=${RUNPOD_SSH_USER:-$(dotenv_value RUNPOD_SSH_USER)}
runpod_key=${RUNPOD_SSH_KEY_PATH:-$(dotenv_value RUNPOD_SSH_KEY_PATH)}
runpod_port=${runpod_port:-22}
runpod_user=${runpod_user:-root}
runpod_key=${runpod_key/#\~/$HOME}

if [[ -z "$runpod_host" || -z "$runpod_key" ]]; then
  echo "Missing RUNPOD_SSH_HOST or RUNPOD_SSH_KEY_PATH in .env (or shell environment)." >&2
  exit 2
fi
if [[ ! -r "$runpod_key" ]]; then
  echo "RunPod SSH key is not readable: $runpod_key" >&2
  exit 2
fi

exec ssh -tt -o BatchMode=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=3 \
  -p "$runpod_port" -i "$runpod_key" "$runpod_user@$runpod_host" 'bash -s' <<'REMOTE'
set -u
while true; do
  clear
  date '+%Y-%m-%d %H:%M:%S %Z'
  echo '=== COMFYUI QUEUE ==='
  curl -fsS http://127.0.0.1:8188/queue || echo 'ComfyUI queue unavailable'
  echo
  echo '=== GPU ==='
  nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw --format=csv,noheader || true
  echo '=== RECENT OUTPUTS ==='
  find /workspace/ComfyUI/output -type f -printf '%TY-%Tm-%Td %TH:%TM:%TS | %s bytes | %p\n' 2>/dev/null | sort | tail -10
  echo '=== RECENT COMFYUI LOG ==='
  tail -n 30 /workspace/comfyui.log 2>/dev/null || true
  sleep 5
done
REMOTE

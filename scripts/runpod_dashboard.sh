#!/bin/bash
# AutoClip - All-in-one RunPod Live Dashboard & Status Viewer
# Usage:
#   ./scripts/runpod_dashboard.sh        (view once)
#   ./scripts/runpod_dashboard.sh -w     (live auto-refresh every 2 seconds)

KEY="${RUNPOD_SSH_KEY_PATH:-$HOME/.ssh/id_ed25519_runpod}"
PORT="${RUNPOD_SSH_PORT:-22137}"
HOST="${RUNPOD_SSH_HOST:-69.30.85.132}"
USER="${RUNPOD_SSH_USER:-root}"

CMD='
echo "================================================================================"
echo "                   🚀 RUNPOD STATUS & LIVE DASHBOARD 🚀                         "
echo "================================================================================"
echo ""
echo "--- [1] GPU & VRAM (NVIDIA-SMI) ---"
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu --format=csv,noheader | awk -F, "{printf \"GPU: %s | VRAM: %s / %s | Load: %s | Temp: %s\n\", \$1, \$2, \$3, \$4, \$5}"
echo ""
echo "--- [2] DISK & SYSTEM MEMORY ---"
df -h /workspace | awk "NR==2 {printf \"Workspace Disk: Used %s / %s (Free %s)\n\", \$3, \$2, \$4}"
free -h | awk "/Mem:/ {printf \"RAM: Used %s / %s (Free %s)\n\", \$3, \$2, \$4}"
echo ""
echo "--- [3] COMFYUI STATUS & QUEUE ---"
if pgrep -f "ComfyUI/main.py" > /dev/null; then
  echo "Process: RUNNING (PID: $(cat /workspace/comfyui.pid 2>/dev/null || pgrep -f '\''ComfyUI/main.py'\'' | head -1))"
else
  echo "Process: STOPPED ❌"
fi
QUEUE_RUN=$(curl -s http://127.0.0.1:8188/queue | jq -r ".queue_running | length" 2>/dev/null || echo "0")
QUEUE_PEND=$(curl -s http://127.0.0.1:8188/queue | jq -r ".queue_pending | length" 2>/dev/null || echo "0")
echo "Queue: $QUEUE_RUN running | $QUEUE_PEND pending"
echo ""
echo "--- [4] RECENT GENERATED VIDEOS (Last 3) ---"
find /workspace/ComfyUI/output/autoclip -name "*.mp4" 2>/dev/null | xargs ls -lht 2>/dev/null | head -3 | awk "{printf \"- %s (%s, %s %s %s)\n\", \$9, \$5, \$6, \$7, \$8}"
echo ""
echo "--- [5] RECENT COMFYUI LOG (Last 12 lines) ---"
tail -n 12 /workspace/comfyui.log 2>/dev/null
echo "================================================================================"
'

if [ "$1" = "-w" ] || [ "$1" = "--watch" ]; then
  while true; do
    clear
    ssh -o BatchMode=yes -o StrictHostKeyChecking=no -p "$PORT" -i "$KEY" "$USER@$HOST" "$CMD"
    echo "Refreshing every 2s... (Press Ctrl+C to exit)"
    sleep 2
  done
else
  ssh -o BatchMode=yes -o StrictHostKeyChecking=no -p "$PORT" -i "$KEY" "$USER@$HOST" "$CMD"
fi

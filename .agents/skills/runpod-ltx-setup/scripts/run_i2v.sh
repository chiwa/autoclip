#!/usr/bin/env bash
set -euo pipefail

poc_root="${POC_ROOT:-/workspace/ltx-video-poc}"
usage='usage: run_i2v.sh INPUT_PATH validation|SECONDS|audio:AUDIO_PATH PROMPT'
input_path="${1:?$usage}"
duration_spec="${2:?$usage}"
prompt="${3:?$usage}"
audio_source=""

case "$duration_spec" in
  validation)
    frames=49
    fps=16
    run_name=validation
    ;;
  audio:*)
    audio_source="${duration_spec#audio:}"
    if [[ ! -f "$audio_source" ]]; then
      echo "audio file not found: $audio_source" >&2
      exit 2
    fi
    if ! command -v ffprobe >/dev/null 2>&1; then
      echo "ffprobe is required for audio-driven duration" >&2
      exit 2
    fi
    target_seconds="$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$audio_source")"
    fps=15
    frames="$("$poc_root/.venv/bin/python" -c 'import math,sys; seconds=float(sys.argv[1]); fps=int(sys.argv[2]); raw=math.ceil(seconds*fps); print(max(9, math.ceil((raw-1)/8)*8+1))' "$target_seconds" "$fps")"
    safe_audio_name="$(basename "$audio_source" | tr -cs '[:alnum:]._- ' '_' | tr ' ' '_')"
    run_name="audio-${safe_audio_name%.*}"
    ;;
  *)
    if [[ "$duration_spec" =~ ^[0-9]+([.][0-9]+)?$ ]] && "$poc_root/.venv/bin/python" -c 'import sys; raise SystemExit(0 if float(sys.argv[1]) > 0 else 1)' "$duration_spec"; then
      target_seconds="$duration_spec"
      fps=15
      frames="$("$poc_root/.venv/bin/python" -c 'import math,sys; seconds=float(sys.argv[1]); fps=int(sys.argv[2]); raw=math.ceil(seconds*fps); print(max(9, math.ceil((raw-1)/8)*8+1))' "$target_seconds" "$fps")"
      run_name="duration-${duration_spec//./p}s"
    else
      echo "duration must be validation, positive SECONDS, or audio:AUDIO_PATH" >&2
      exit 2
    fi
    ;;
esac

generated_seconds="$("$poc_root/.venv/bin/python" -c 'import sys; print(f"{int(sys.argv[1])/int(sys.argv[2]):.6f}")' "$frames" "$fps")"

cd "$poc_root/LTX-Video"
rm -f "$poc_root/logs/$run_name-exit-code"
nvidia-smi \
  --query-gpu=timestamp,memory.used,utilization.gpu,temperature.gpu \
  --format=csv,noheader -l 1 > "$poc_root/logs/$run_name-gpu.csv" &
monitor_pid=$!
trap 'kill "$monitor_pid" 2>/dev/null || true' EXIT

start_seconds=$SECONDS
set +e
"$poc_root/.venv/bin/python" inference.py \
  --prompt "$prompt" \
  --conditioning_media_paths "$input_path" \
  --conditioning_start_frames 0 \
  --height 768 \
  --width 448 \
  --num_frames "$frames" \
  --frame_rate "$fps" \
  --seed 171198 \
  --pipeline_config "$poc_root/ltxv-2b-distilled-poc.yaml" \
  --output_path "$poc_root/output" \
  > "$poc_root/logs/$run_name-inference.log" 2>&1
result_code=$?
set -e

elapsed_seconds=$((SECONDS - start_seconds))
printf '%s\n' "$result_code" > "$poc_root/logs/$run_name-exit-code"
printf 'elapsed_seconds=%s\n' "$elapsed_seconds" > "$poc_root/logs/$run_name-timing.txt"
{
  printf 'duration_spec=%s\n' "$duration_spec"
  printf 'audio_source=%s\n' "$audio_source"
  printf 'frames=%s\n' "$frames"
  printf 'fps=%s\n' "$fps"
  printf 'generated_seconds=%s\n' "$generated_seconds"
} > "$poc_root/logs/$run_name-video-plan.txt"
exit "$result_code"

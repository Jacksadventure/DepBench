#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <task-name> <candidate.patch> [logs-dir]" >&2
}

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  usage
  exit 1
fi

ROOT="${DEPBENCH_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
TASK="$1"
PATCH_FILE="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"
TASK_DIR="$ROOT/dataset/tasks/$TASK"
LOGS_DIR="${3:-$(mktemp -d "${TMPDIR:-/tmp}/depbench-${TASK}.logs.XXXXXX")}"

if [ ! -d "$TASK_DIR" ]; then
  echo "Task not found: $TASK_DIR" >&2
  echo "Run: python3 repro/download_benchmark.py" >&2
  exit 1
fi
if [ ! -f "$PATCH_FILE" ]; then
  echo "Patch file not found: $PATCH_FILE" >&2
  exit 1
fi

image="$(awk -F'"' '/^[[:space:]]*docker_image[[:space:]]*=/{print $2; exit}' "$TASK_DIR/task.toml")"
cpus="$(awk -F'= *' '/^[[:space:]]*cpus[[:space:]]*=/{print $2; exit}' "$TASK_DIR/task.toml")"
memory_mb="$(awk -F'= *' '/^[[:space:]]*memory_mb[[:space:]]*=/{print $2; exit}' "$TASK_DIR/task.toml")"

mkdir -p "$LOGS_DIR/verifier"

docker run --rm \
  --cpus "${cpus:-2}" \
  --memory "${memory_mb:-4096}m" \
  -e DEPBENCH_PRE_VERIFY_CMD="${DEPBENCH_PRE_VERIFY_CMD:-}" \
  -v "$TASK_DIR:/harbor:ro" \
  -v "$TASK_DIR/tests:/tests:ro" \
  -v "$PATCH_FILE:/candidate.patch:ro" \
  -v "$LOGS_DIR:/logs" \
  "$image" \
  bash -lc 'set -euo pipefail; cd /app; git apply /candidate.patch || git apply --3way /candidate.patch; if [ -n "${DEPBENCH_PRE_VERIFY_CMD:-}" ]; then bash -lc "$DEPBENCH_PRE_VERIFY_CMD"; fi; bash /tests/test.sh'

echo "Logs: $LOGS_DIR"
if [ -f "$LOGS_DIR/verifier/reward.txt" ]; then
  echo "Reward: $(cat "$LOGS_DIR/verifier/reward.txt")"
else
  echo "Reward file was not produced." >&2
  exit 2
fi

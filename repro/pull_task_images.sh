#!/usr/bin/env bash
set -euo pipefail

ROOT="${DEPBENCH_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
TASK_ROOT="$ROOT/dataset/tasks"

if [ ! -d "$TASK_ROOT" ]; then
  echo "Task directory not found: $TASK_ROOT" >&2
  exit 1
fi

if [ "$#" -gt 0 ]; then
  tasks=("$@")
else
  mapfile -t tasks < <(find "$TASK_ROOT" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort)
fi

for task in "${tasks[@]}"; do
  task_dir="$TASK_ROOT/$task"
  if [ ! -f "$task_dir/task.toml" ]; then
    echo "Missing task.toml for task: $task" >&2
    exit 1
  fi
  image="$(awk -F'"' '/^[[:space:]]*docker_image[[:space:]]*=/{print $2; exit}' "$task_dir/task.toml")"
  if [ -z "$image" ]; then
    echo "No docker_image in $task_dir/task.toml" >&2
    exit 1
  fi
  echo "Pulling $image"
  docker pull "$image"
done

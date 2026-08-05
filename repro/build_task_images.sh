#!/usr/bin/env bash
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

set -euo pipefail

ROOT="${DEPBENCH_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
TASK_ROOT="$ROOT/dataset/tasks"
IMAGE_PREFIX="${DEPBENCH_IMAGE_PREFIX:-depbench-local}"

if [ ! -d "$TASK_ROOT" ]; then
  echo "Task directory not found: $TASK_ROOT" >&2
  echo "Run: python3 repro/download_benchmark.py" >&2
  exit 1
fi

if [ "$#" -gt 0 ]; then
  tasks=("$@")
else
  mapfile -t tasks < <(find "$TASK_ROOT" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort)
fi

for task in "${tasks[@]}"; do
  task_dir="$TASK_ROOT/$task"
  dockerfile="$task_dir/environment/Dockerfile"
  if [ ! -f "$dockerfile" ]; then
    echo "Missing source-build Dockerfile for task: $task" >&2
    exit 1
  fi
  image="$IMAGE_PREFIX:$task"
  echo "Building $image from $dockerfile"
  docker build --pull --tag "$image" "$task_dir/environment"
done

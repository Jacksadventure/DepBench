#!/usr/bin/env bash
set -euo pipefail
cd /Data2/v-zijianluo/depbot_v4_with_tests
python _run_configs/patch_harbor_task_repo_blocker.py --check
export DOCKER_HOST=${DOCKER_HOST:-unix:///run/user/1900/docker.sock}
export PATH="$HOME/.local/bin:$PATH"
~/.local/bin/harbor run --config _run_configs/claude_code_claude48_20260626/claude_code_claude48_v4_withtest_219_conc10_2026-06-26__ready-00.json

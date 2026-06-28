#!/usr/bin/env bash
set -uo pipefail
cd /Data2/v-zijianluo/depbot_v4_with_tests
mkdir -p _run_logs harbor_jobs
job="opencode_gemini35flash_v4_withtest_219_fixed_conc5_setup1200_resume14_2026-06-28__1005-00"
config="_run_configs/opencode_gemini35flash_rerun_20260627/${job}.json"
echo $$ > "_run_logs/${job}.pid"
python _run_configs/patch_harbor_task_repo_blocker.py --check
export DOCKER_HOST=${DOCKER_HOST:-unix:///run/user/1900/docker.sock}
export PATH="$HOME/.local/bin:$PATH"
log="_run_logs/${job}.log"
echo "[$(date -Is)] START ${config} (${job})" | tee -a "$log"
~/.local/bin/harbor run --config "$config" >> "$log" 2>&1
code=$?
echo "[$(date -Is)] END ${config} exit=${code}" | tee -a "$log"
exit "$code"

#!/usr/bin/env bash
set -uo pipefail
cd /Data2/v-zijianluo/depbot_v4_with_tests
mkdir -p _run_logs harbor_jobs
echo $$ > _run_logs/claude48_agents_opencode_codex_resume_20260626.pid
python _run_configs/patch_harbor_task_repo_blocker.py --check
export DOCKER_HOST=${DOCKER_HOST:-unix:///run/user/1900/docker.sock}
export PATH="$HOME/.local/bin:$PATH"
configs=(
  "_run_configs/claude48_agents_20260626/opencode_claude48_v4_withtest_219_conc10_2026-06-26__1248-00.json"
  "_run_configs/claude48_agents_20260626/codex_claude48_v4_withtest_219_conc10_2026-06-26__1248-00.json"
)
summary="_run_logs/claude48_agents_opencode_codex_resume_20260626.summary.tsv"
echo -e "timestamp\tstatus\tconfig\tjob\texit_code" >> "$summary"
for cfg in "${configs[@]}"; do
  job=$(python3 - <<'PYJOB' "$cfg"
import json,sys
print(json.load(open(sys.argv[1]))['job_name'])
PYJOB
  )
  log="_run_logs/${job}.log"
  echo "[$(date -Is)] START $cfg ($job)" | tee -a "$log"
  ~/.local/bin/harbor run --config "$cfg" >> "$log" 2>&1
  code=$?
  if [ "$code" -eq 0 ]; then status=ok; else status=failed; fi
  echo -e "$(date -Is)\t${status}\t${cfg}\t${job}\t${code}" >> "$summary"
  echo "[$(date -Is)] END $cfg exit=$code" | tee -a "$log"
done

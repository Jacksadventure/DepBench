#!/usr/bin/env bash
set -uo pipefail
cd /Data2/v-zijianluo/depbot_v4_with_tests
mkdir -p _run_logs harbor_jobs
echo $$ > _run_logs/v4_with_test_hard14_resume_sequence_20260623__0230.pid
export DOCKER_HOST=${DOCKER_HOST:-unix:///run/user/1900/docker.sock}
export PATH="$HOME/.local/bin:$PATH"
configs=(
  "_run_configs/v4_with_test_hard14_resume_20260623/codex_cloudgpt_gpt55_v4_with_test_hard14_resume_conc10_2026-06-23__02-30-00.json"
  "_run_configs/v4_with_test_hard14_resume_20260623/opencode_gemini35flash_v4_with_test_hard14_resume_conc10_2026-06-23__02-30-00.json"
)
summary="_run_logs/v4_with_test_hard14_resume_sequence_20260623__0230.summary.tsv"
echo -e "timestamp	status	config	exit_code" >> "$summary"
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
  echo -e "$(date -Is)	${status}	${cfg}	${code}" >> "$summary"
  echo "[$(date -Is)] END $cfg exit=$code" | tee -a "$log"
done

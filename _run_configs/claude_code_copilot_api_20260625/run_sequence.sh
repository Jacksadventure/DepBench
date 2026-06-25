#!/usr/bin/env bash
set -uo pipefail
cd /Data2/v-zijianluo/depbot_v4_with_tests
mkdir -p _run_logs harbor_jobs
echo $$ > _run_logs/claude_code_copilot_api_v4_withtest_219_sequence_20260625__0400.pid
export DOCKER_HOST=${DOCKER_HOST:-unix:///run/user/1900/docker.sock}
export PATH="$HOME/.local/bin:$PATH"
configs=(
  "_run_configs/claude_code_copilot_api_20260625/claude_code_copilot_api_gpt55_v4_withtest_219_conc10_2026-06-25__0400-00.json"
  "_run_configs/claude_code_copilot_api_20260625/claude_code_copilot_api_gemini35flash_v4_withtest_219_conc10_2026-06-25__0400-00.json"
)
summary="_run_logs/claude_code_copilot_api_v4_withtest_219_sequence_20260625__0400.summary.tsv"
echo -e "timestamp	status	config	exit_code" >> "$summary"
cleanup_docker() {
  ids=$(docker ps -a -q)
  if [ -n "$ids" ]; then docker rm -f $ids >/dev/null 2>&1 || true; fi
  docker network prune -f >/dev/null 2>&1 || true
}
for cfg in "${configs[@]}"; do
  cleanup_docker
  job=$(python3 - <<'PYJOB' "$cfg"
import json,sys
print(json.load(open(sys.argv[1]))['job_name'])
PYJOB
)
  log="_run_logs/${job}.log"
  echo "[$(date -Is)] START $cfg ($job)" | tee -a "$log"
  ~/.local/bin/harbor run --config "$cfg" >> "$log" 2>&1
  code=$?
  cleanup_docker
  if [ "$code" -eq 0 ]; then status=ok; else status=failed; fi
  echo -e "$(date -Is)	${status}	${cfg}	${code}" >> "$summary"
  echo "[$(date -Is)] END $cfg exit=$code" | tee -a "$log"
done

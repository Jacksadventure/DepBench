#!/usr/bin/env bash
set -euo pipefail
cd /Data2/v-zijianluo/depbot_v4_with_tests
mkdir -p _run_logs
summary="_run_logs/guarded_leak_remaining_claude_confirmed_20260701__1455_conc13.summary.tsv"
echo -e "config\tstarted_at\tfinished_at\texit_code\tlog" > "$summary"
for cfg in \
  "_run_configs/claude_leak_guarded_20260701/guarded_leak_claude_code_gemini_confirmed18_conc13_2026-07-01__1455-00.json" \
  "_run_configs/claude_leak_guarded_20260701/guarded_leak_opencode_claude48_confirmed48_conc13_2026-07-01__1455-00.json" \
  "_run_configs/claude_leak_guarded_20260701/guarded_leak_claude_code_claude48_confirmed62_conc13_2026-07-01__1455-00.json" \
; do
  name=$(python3 - <<PY "$cfg"
import json,sys
print(json.load(open(sys.argv[1]))["job_name"])
PY
)
  log="_run_logs/${name}.log"
  start=$(date -Iseconds)
  echo "[$start] START $cfg ($name)" | tee -a "_run_logs/guarded_leak_remaining_claude_confirmed_20260701__1455_conc13.launcher.log"
  set +e
  DOCKER_HOST=unix:///run/user/1900/docker.sock harbor run --config "$cfg" > "$log" 2>&1
  code=$?
  set -e
  end=$(date -Iseconds)
  echo -e "$cfg\t$start\t$end\t$code\t$log" >> "$summary"
  echo "[$end] END $cfg exit=$code" | tee -a "_run_logs/guarded_leak_remaining_claude_confirmed_20260701__1455_conc13.launcher.log"
  if [ "$code" -ne 0 ]; then exit "$code"; fi
done

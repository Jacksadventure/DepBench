#!/usr/bin/env bash
set -euo pipefail
cd /Data2/v-zijianluo/depbot_v4_with_tests
mkdir -p _run_logs
summary="_run_logs/guarded_leak_copilot_claude48_confirmed49_20260701__0855_conc13.summary.tsv"
echo -e "config	started_at	finished_at	exit_code	log" > "$summary"
cfg="_run_configs/claude_leak_guarded_20260701/guarded_leak_copilot_cli_claude48_confirmed49_conc13_2026-07-01__0855-00.json"
name="guarded_leak_copilot_cli_claude48_confirmed49_conc13_2026-07-01__0855-00"
log="_run_logs/${name}.log"
start=$(date -Iseconds)
echo "[$start] START $cfg ($name)" | tee -a "_run_logs/guarded_leak_copilot_claude48_confirmed49_20260701__0855_conc13.launcher.log"
set +e
DOCKER_HOST=unix:///run/user/1900/docker.sock harbor run --config "$cfg" > "$log" 2>&1
code=$?
set -e
end=$(date -Iseconds)
echo -e "$cfg	$start	$end	$code	$log" >> "$summary"
echo "[$end] END $cfg exit=$code" | tee -a "_run_logs/guarded_leak_copilot_claude48_confirmed49_20260701__0855_conc13.launcher.log"
exit "$code"

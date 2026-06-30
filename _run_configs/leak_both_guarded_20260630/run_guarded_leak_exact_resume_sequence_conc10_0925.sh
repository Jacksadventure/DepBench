#!/usr/bin/env bash
set -euo pipefail

cd /Data2/v-zijianluo/depbot_v4_with_tests

run_id="guarded_leak_exact_resume_v4_withtest73_20260630__0925_conc10"
log_dir="_run_logs"
mkdir -p "$log_dir"

summary="$log_dir/${run_id}.summary.tsv"
launcher_log="$log_dir/${run_id}.launcher.log"
echo $$ > "$log_dir/${run_id}.pid"

export DOCKER_HOST="${DOCKER_HOST:-unix:///run/user/1900/docker.sock}"
export PATH="$HOME/.local/bin:$PATH"

if [[ -z "${DEPBENCH_AGENT_PROXY_URL:-}" && -f _run_logs/depbench_github_guard_proxy_latest.env ]]; then
  source _run_logs/depbench_github_guard_proxy_latest.env
  if [[ -n "${port:-}" ]]; then
    export DEPBENCH_AGENT_PROXY_URL="http://172.100.216.1:${port}"
  fi
fi

export DEPBENCH_AGENT_NO_PROXY="${DEPBENCH_AGENT_NO_PROXY:-127.0.0.1,localhost,::1,172.100.216.1,host.docker.internal,cloudgpt-openai.azure-api.net,api.github.com}"

python3 _run_configs/patch_harbor_git_history_pruner.py --check
python3 _run_configs/patch_harbor_task_repo_blocker.py --check
python3 _run_configs/patch_harbor_agent_proxy_env.py --check
python3 _run_configs/patch_harbor_copilot_auth_env.py --check
python3 _run_configs/patch_harbor_copilot_host_auth.py --check

codex_configs=(
  "_run_configs/leak_both_guarded_20260630/guarded_leak_exact_codex_gpt55_resume26_shard1of3_v4_withtest10_conc10_2026-06-30__0925-00.json"
  "_run_configs/leak_both_guarded_20260630/guarded_leak_exact_codex_gpt55_resume26_shard2of3_v4_withtest10_conc10_2026-06-30__0925-00.json"
  "_run_configs/leak_both_guarded_20260630/guarded_leak_exact_codex_gpt55_resume26_shard3of3_v4_withtest6_conc10_2026-06-30__0925-00.json"
)

copilot_configs=(
  "_run_configs/leak_both_guarded_20260630/guarded_leak_exact_copilot_cli_gpt55_v4_withtest22_conc10_2026-06-30__0925-00.json"
  "_run_configs/leak_both_guarded_20260630/guarded_leak_exact_copilot_cli_gemini35flash_v4_withtest25_conc10_2026-06-30__0925-00.json"
)

printf "config\tstarted_at\tfinished_at\texit_code\tlog\n" > "$summary"

run_config() {
  local config="$1"
  local refresh_cloudgpt="$2"
  local job log started finished code
  job="$(python3 - "$config" <<'PY'
import json
import sys

print(json.load(open(sys.argv[1]))["job_name"])
PY
)"
  log="$log_dir/${job}.log"
  started="$(date -Is)"
  echo "[$started] START $config ($job)" | tee -a "$launcher_log"
  set +e
  if [[ "$refresh_cloudgpt" == "yes" ]]; then
    scripts/with_cloudgpt_token.sh -- ~/.local/bin/harbor run --config "$config" >> "$log" 2>&1
  else
    ~/.local/bin/harbor run --config "$config" >> "$log" 2>&1
  fi
  code=$?
  set -e
  finished="$(date -Is)"
  echo "[$finished] END $config exit=$code" | tee -a "$launcher_log"
  printf "%s\t%s\t%s\t%s\t%s\n" "$config" "$started" "$finished" "$code" "$log" >> "$summary"
}

for config in "${codex_configs[@]}"; do
  run_config "$config" yes
done

for config in "${copilot_configs[@]}"; do
  run_config "$config" no
done

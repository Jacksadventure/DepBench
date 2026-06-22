# Handoff — 153200 · copilot · gpt55-clean205-launch

## Context

User requested a DepBench benchmark run excluding tasks in the drop list, for codex, Copilot CLI, Claude Code, and OpenCode using GPT-5.5.

Current branch is `v4-297-benchmark-rerun-20260615`. Current `harbor_benchmark/tasks_v4/` has 228 task dirs. The 2026-06-18 audit CSV still has 297 rows; intersecting current dirs with `verdict == WITNESSES_BREAKING_CHANGE` gives 205 runnable non-drop tasks. The remaining 23 current tasks are non-clean/drop candidates.

## Work done

- Generated filtered configs in `_run_configs/gpt55_clean205_20260619/`.
- Generated allow/drop helper lists:
  - `_run_configs/gpt55_clean205_20260619/task_names_witnessed205.json` (205 tasks)
  - `_run_configs/gpt55_clean205_20260619/drop_current23.json` (23 tasks)
- Set all configs to current local dataset path `/home/kszlzj/DepBench/harbor_benchmark/tasks_v4`.
- Set `force_build=false`, `override_memory_mb=8192`, `n_concurrent_trials=5`.
- Appended the launch variant to `harbor_benchmark/HARNESS.md`.

## Jobs launched

Launched via `nohup` with logs under `_run_logs/`:

| Agent | PID | Job dir |
|---|---:|---|
| codex | 18551 | `harbor_jobs/codex_cloudgpt_gpt55_clean205_nopreapply_conc5_2026-06-19__15-16-03/` |
| OpenCode | 18559 | `harbor_jobs/opencode_cloudgpt_gpt55_clean205_nopreapply_conc5_2026-06-19__15-16-03/` |
| Claude Code | 18567 | `harbor_jobs/claude_code_cloudgpt_gpt55_clean205_nopreapply_conc5_2026-06-19__15-16-03/` |

Codex and OpenCode remained running at the last check. Claude Code was stopped after immediate auth failures:

- Initial job `claude_code_cloudgpt_gpt55_clean205_nopreapply_conc5_2026-06-19__15-16-03` produced `apiKeySource="none"` / `Not logged in · Please run /login`.
- Patched `_run_configs/gemini_azure_agents.py` to pass CloudGPT token through both `ANTHROPIC_API_KEY` and `ANTHROPIC_AUTH_TOKEN`, then launched retry job `claude_code_cloudgpt_gpt55_clean205_nopreapply_conc5_retry1_2026-06-19__15-36-00` with PID 32674.
- Retry hit the same Claude Code auth failure and was stopped. CloudGPT/AAD is not sufficient for this Claude Code CLI path; use a real Anthropic-compatible GPT-5.5 endpoint/token or Claude Code login mechanism before rerunning.

## Copilot status

`_run_configs/gpt55_clean205_20260619/copilot.json` was generated but not launched. Harbor's Copilot adapter only forwards auth from `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, or `GITHUB_TOKEN`; none are set in this shell, and the historical `~/.local/share/copilot-api/github_token` file is absent.

The host `copilot --prompt='Say ok...' --model=gpt-5.5` works through the interactive/cache login, but the cache is not available inside fresh Harbor task containers. Do not mount the host `~/.copilot` directory into benchmark containers because it would expose the host auth cache to untrusted task code.

To launch Copilot safely, provide a supported headless token in the environment, then run:

```bash
cd /home/kszlzj/DepBench
COPILOT_GITHUB_TOKEN=<token> nohup ~/.local/bin/harbor run --config _run_configs/gpt55_clean205_20260619/copilot.json \
  > _run_logs/copilot_cli_gpt55_clean205_nopreapply_conc5_2026-06-19__15-16-03.log 2>&1 &
```

## Monitoring commands

```bash
ps -p 18551,18559 -o pid,etime,stat,cmd
for d in harbor_jobs/*gpt55_clean205*; do
  echo "==== $d"
  python3 - <<'PY' "$d/result.json"
import json, sys
r=json.load(open(sys.argv[1]))
print(json.dumps(r["stats"], indent=2))
PY
done
tail -n 80 harbor_jobs/*gpt55_clean205*/job.log
```

## Notes

- Local Maestro proxy `http://172.100.216.1:23333/api/openai/v1` timed out from the host, so the new OpenCode config uses `_run_configs.gemini_azure_agents:OpenCodeAzureGemini` with CloudGPT/AAD instead of the stale local-proxy config.
- Codex uses `_run_configs.codex_maestro_agent:CodexCloudGPT`.
- `az account get-access-token` for the CloudGPT AAD resource succeeded during preflight.

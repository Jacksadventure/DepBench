# Handoff — 175708 · copilot · gpt55-launch

## Context

User approved launching the Copilot GPT-5.5 benchmark using host Copilot auth reuse.

## Work done

- Removed four stale containers from the interrupted codex/OpenCode run:
  - `7cb1d03177f2`
  - `f43fefa02b98`
  - `6e4481c7953d`
  - `83b515937340`
- Launched Harbor with `_run_configs/gpt55_clean205_20260619/copilot_reuse_host_auth.json`.

## Running job

| Field | Value |
|---|---|
| PID | `94088` |
| Job dir | `harbor_jobs/copilot_cli_gpt55_clean205_reuse_host_auth_nopreapply_conc5_2026-06-19__17-30-00/` |
| Log | `_run_logs/copilot_cli_gpt55_clean205_reuse_host_auth_nopreapply_conc5_2026-06-19__17-30-00.log` |
| Config | `_run_configs/gpt55_clean205_20260619/copilot_reuse_host_auth.json` |

At startup check: `n_total_trials=205`, `n_running_trials=5`, `n_pending_trials=200`, `n_errored_trials=0`.

Five containers were up for the initial batch:

- `mike-engel__jwt-cli__224__dvasmks-main-1`
- `graphql-hive__graphql-config__11__sn9h7dn-main-1`
- `cosmos__cosmos-sdk__19810__eqgyutw-main-1`
- `onthegomap__planetiler__1430__ckx7xdj-main-1`
- `talsma-ict__umldoclet__709__qrhsdzc-main-1`

## Monitor

```bash
cd /home/kszlzj/DepBench
ps -p 94088 -o pid,etime,stat,cmd
python3 - <<'PY' harbor_jobs/copilot_cli_gpt55_clean205_reuse_host_auth_nopreapply_conc5_2026-06-19__17-30-00/result.json
import json, sys
r=json.load(open(sys.argv[1]))
print(json.dumps(r["stats"], indent=2))
PY
tail -n 80 harbor_jobs/copilot_cli_gpt55_clean205_reuse_host_auth_nopreapply_conc5_2026-06-19__17-30-00/job.log
```

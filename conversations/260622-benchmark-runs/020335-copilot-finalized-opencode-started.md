# Handoff — 020335 · copilot-finalized · opencode-started

## Copilot final result

- Final Copilot Harbor job:
  - `harbor_jobs/copilot_cli_gemini35flash_v4_228_nopreapply_conc6_2026-06-21__15-15-42/`
- Fixed run config:
  - `_run_configs/copilot_cli_gemini35flash_v4_228_nopreapply_conc6_2026-06-21__15-15-42.json`
- Final status from `result.json`:
  - `finished_at = 2026-06-22T00:54:22.781408`
  - `n_total_trials = 228`
  - `n_completed_trials = 228`
  - `n_errored_trials = 4`
  - `n_running_trials = 0`
  - `n_pending_trials = 0`
  - mean reward `= 0.3026315789473684`
  - reward `1.0`: `69`
  - reward `0.0`: `159`
- All 4 recorded errors are:
  - `AgentTimeoutError`

## Launch state for OpenCode

- Watcher detected Copilot completion and launched:
  - `opencode_gemini35flash_v4_228_nopreapply_conc6_2026-06-21__12-37-23`
- OpenCode config:
  - `_run_configs/opencode_gemini35flash_v4_228_nopreapply_conc6_2026-06-21__12-37-23.json`
- Monitor log:
  - `harbor_jobs/opencode_gemini35flash_v4_228_nopreapply_conc6_2026-06-21__12-37-23.monitor.log`
- Harbor process:
  - PID `528578`

## Early OpenCode health

- OpenCode is actively running with:
  - `n_running_trials = 6`
  - `n_pending_trials = 215`
- Early result snapshot already shows some executed trials and some errors.
- The current errors are all:
  - `AgentTimeoutError`

## Notes

- The earlier broken Copilot launch at `2026-06-21__10-00-03` is still useful as failure evidence for the read-only `COPILOT_HOME` issue, but the benchmark result to use is the fixed run at `2026-06-21__15-15-42`.

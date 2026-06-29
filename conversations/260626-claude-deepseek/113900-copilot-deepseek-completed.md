# Copilot CLI + DeepSeek completed

## Result

| Model | Agent | Rewards | Accuracy |
|---|---|---:|---:|
| DeepSeek | Copilot CLI | 38/219 | 17.4% |

## Job

- Config: `_run_configs/copilot_deepseek_20260626/copilot_cli_deepseek_v4_withtest_219_conc6_2026-06-26__after-claude.json`
- Job: `harbor_jobs/copilot_cli_deepseek_v4_withtest_219_conc6_2026-06-26__after-claude`
- Finished at: `2026-06-29T11:36:51.311698`
- Final stats: 219 completed, 0 running, 0 pending, 219 reward-bearing tasks.

## Notes

- Harbor recorded `NonZeroAgentExitCodeError` for all 219 trials, but verifier rewards were produced for all tasks.
- Compact reports were added under `harbor_benchmark/reports/`.
- Top-level job `config.json` and `result.json` are safe to push; raw logs/trajectories remain local.

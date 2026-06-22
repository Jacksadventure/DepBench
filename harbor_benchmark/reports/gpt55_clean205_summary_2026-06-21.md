# GPT-5.5 clean205 benchmark results — 2026-06-21

| Agent | Result tasks | Reward tasks | Pass | Fail | No reward | Missing | Pass rate | Jobs |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| copilot | 205 | 202 | 91 | 111 | 3 | 0 | 45.0% | `copilot_cli_gpt55_clean205_reuse_host_auth_nopreapply_conc5_retry1_2026-06-20__00-15-00;copilot_cli_gpt55_clean205_reuse_host_auth_resume124_conc5_2026-06-20__07-10-00;copilot_cli_gpt55_clean205_reuse_host_auth_resume58_conc5_2026-06-20__11-28-00` |
| codex | 205 | 205 | 98 | 107 | 0 | 0 | 47.8% | `codex_cloudgpt_gpt55_clean205_nopreapply_conc5_2026-06-19__15-16-03;codex_cloudgpt_gpt55_clean205_resume204_clean_conc5_2026-06-21__04-12-00` |
| opencode | 205 | 205 | 92 | 113 | 0 | 0 | 44.9% | `opencode_cloudgpt_gpt55_clean205_nopreapply_conc5_2026-06-19__15-16-03;opencode_gpt55_clean205_resume_after_codex_conc5_2026-06-21` |

Notes:
- Dataset: current `harbor_benchmark/tasks_v4` clean205 snapshot.
- Claude Code was not included because its Harbor adapter could not authenticate with the available GPT-5.5 route.
- Copilot has 3 no-reward task results from infrastructure interruption; all 205 task folders have result files.

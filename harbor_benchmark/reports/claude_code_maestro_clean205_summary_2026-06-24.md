# Claude Code Maestro clean205 results - 2026-06-24

| Model | Agent | Rewards | Accuracy | Mean reward | Source |
|---|---|---:|---:|---:|---|
| GPT-5.5 | Claude Code | 36/204 | 17.6% | 0.176 | `harbor_jobs/claude_code_maestro_gpt55_clean205_conc5_2026-06-23__16-23-00/result.json` |
| Gemini 3.5 Flash | Claude Code | 36/205 | 17.6% | 0.176 | `harbor_jobs/claude_code_maestro_gemini35flash_clean205_conc5_2026-06-23__16-23-00/result.json` |

Notes:
- Dataset: clean205 task list from `_run_configs/claude_code_maestro_20260623/task_names_clean205.json`.
- GPT-5.5 has one no-reward trial in Harbor reward stats; its Harbor mean reward is still 36/205.
- Harbor recorded `NonZeroAgentExitCodeError` for every Claude Code trial in both runs, but verifier rewards were still produced for 204/205 GPT-5.5 trials and 205/205 Gemini trials.

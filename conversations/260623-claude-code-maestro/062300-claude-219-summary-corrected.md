# Claude Code 219-task summary corrected

## Root cause

- The 2026-06-23 Claude Code Maestro runs used clean205 configs, so the first pushed totals were 205-task totals.
- The current `v4-with-test` branch has 219 tasks, so the missing hard14 segment had to be run and merged.

## Hard14 completion

- GPT-5.5 hard14 job: `harbor_jobs/claude_code_maestro_gpt55_hard14_conc5_2026-06-24__05-33-00`
  - finished at `2026-06-24T05:58:34.634525`
  - 2 pass / 11 fail / 1 no reward
- Gemini 3.5 Flash hard14 job: `harbor_jobs/claude_code_maestro_gemini35flash_hard14_conc5_2026-06-24__05-33-00`
  - finished at `2026-06-24T06:21:08.626631`
  - 2 pass / 12 fail

## Corrected 219-task totals

| Model | Agent | Rewards | Accuracy |
|---|---|---:|---:|
| GPT-5.5 | Claude Code | 38/219 | 17.4% |
| Gemini 3.5 Flash | Claude Code | 38/219 | 17.4% |

Notes:
- GPT-5.5 has 217 reward-bearing trials and 2 no-reward trials; reward-bearing accuracy is 38/217 = 17.5%.
- Gemini has 219 reward-bearing trials.
- Harbor still records `NonZeroAgentExitCodeError` for all Claude Code trials.

## Files

- Added corrected summary files:
  - `harbor_benchmark/reports/claude_code_maestro_v4_with_test219_summary_2026-06-24.md`
  - `harbor_benchmark/reports/claude_code_maestro_v4_with_test219_summary_2026-06-24.csv`
  - `harbor_benchmark/reports/claude_code_maestro_v4_with_test219_summary_2026-06-24.json`
- Updated `README.md` v4-with-test219 table with Claude Code rows.

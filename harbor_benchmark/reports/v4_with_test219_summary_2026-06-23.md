# v4-with-test219 benchmark summary — 2026-06-23

Dataset: curated 219 tasks = clean205 + hard14.

## Main GPT-5.5 merged results

| Agent | Model | Tasks | Reward tasks | Pass | Fail | No reward | Missing | Mean reward |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| codex | gpt-5.5-20260424 | 219 | 219 | 105 | 114 | 0 | 0 | 0.479 |
| copilot | gpt-5.5 | 219 | 216 | 97 | 119 | 3 | 0 | 0.449 |
| opencode | gpt-5.5-20260424 | 219 | 219 | 94 | 125 | 0 | 0 | 0.429 |

## Supplemental hard14-only results

| Agent | Model | Tasks | Reward tasks | Pass | Fail | No reward | Mean reward | Exception counts |
|---|---|---:|---:|---:|---:|---:|---:|---|
| claude_code | gpt-5.5-20260424 | 14 | 14 | 2 | 12 | 0 | 0.143 | `{"harbor.agents.installed.base.NonZeroAgentExitCodeError": 14}` |
| opencode_gemini35 | gemini-3.5-flash | 14 | 14 | 3 | 11 | 0 | 0.214 | `{"harbor.trial.trial.AgentTimeoutError": 12}` |

Notes:
- Main GPT-5.5 rows are merged into the original clean205 result sets.
- Supplemental rows are not merged into 219-task means because matching clean205 per-task baselines are not available in this branch.

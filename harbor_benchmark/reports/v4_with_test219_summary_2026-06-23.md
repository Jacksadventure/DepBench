# v4-with-test219 benchmark summary — 2026-06-24

Dataset: curated 219 tasks = clean205 + hard14.

## Main GPT-5.5 merged results

| Agent | Model | Tasks | Reward tasks | Pass | Fail | No reward | Missing | Mean reward |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| codex | gpt-5.5-20260424 | 219 | 219 | 105 | 114 | 0 | 0 | 0.479 |
| copilot | gpt-5.5 | 219 | 216 | 97 | 119 | 3 | 0 | 0.449 |
| opencode | gpt-5.5-20260424 | 219 | 219 | 94 | 125 | 0 | 0 | 0.429 |

## Gemini 3.5 Flash results

| Agent | Model | Tasks | Reward tasks | Pass | Fail | No reward | Missing | Mean reward | Exception counts |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| copilot | gemini-3.5-flash | 219 | 218 | 49 | 169 | 1 | 0 | 0.225 | `{"AgentTimeoutError": 9, "NonZeroAgentExitCodeError": 5}` |
| opencode | gemini-3.5-flash | 219 | 219 | 38 | 181 | 0 | 0 | 0.174 | `{"AgentTimeoutError": 219}` |

## Supplemental hard14-only results

| Agent | Model | Tasks | Reward tasks | Pass | Fail | No reward | Mean reward | Exception counts |
|---|---|---:|---:|---:|---:|---:|---:|---|
| claude_code | gpt-5.5-20260424 | 14 | 14 | 2 | 12 | 0 | 0.143 | `{"harbor.agents.installed.base.NonZeroAgentExitCodeError": 14}` |

# Claude Code Copilot API summary — v4-with-test219

Generated: 2026-07-01T08:01:11.467803+00:00

Claude Code via Anthropic-compatible copilot-api endpoint on 172.100.216.1:4143; full 219-task run, concurrency 10.

| Agent | Model | Pass | Fail | No reward | Reward tasks | Pass rate (reward-bearing) | Pass rate (total) |
|---|---|---:|---:|---:|---:|---:|---:|
| Claude Code | gpt-5.5 | 61 | 158 | 0 | 219 | 0.279 | 0.279 |
| Claude Code | gemini-3.5-flash | 48 | 166 | 5 | 214 | 0.224 | 0.219 |

Guarded leakage replacement notes:
- Applied 64 Claude Code + GPT-5.5 single-annotator confirmed segment1 guarded reruns; audit: `harbor_benchmark/reports/guarded_leak_claude_segment1_replacement_audit_20260701.csv`.

Artifacts:
- `v4_with_test219_claude_code_copilot_api_results_2026-06-25.csv`
- `v4_with_test219_claude_code_copilot_api_summary_2026-06-25.json`

# Claude 4.8 multi-agent summary — v4-with-test219

Generated: 2026-07-01T11:06:54.480394+00:00

| Agent | Model | Pass | Fail | No reward | Reward tasks | Pass rate (reward-bearing) | Pass rate (total) |
|---|---|---:|---:|---:|---:|---:|---:|
| copilot | claude-opus-4-8 | 76 | 141 | 2 | 217 | 0.350 | 0.347 |
| opencode | claude-opus-4-8 | 98 | 121 | 0 | 219 | 0.447 | 0.447 |

Guarded leakage replacement notes:
- Applied 49 Copilot CLI + Claude 4.8 single-annotator confirmed guarded reruns; audit: `harbor_benchmark/reports/guarded_leak_copilot_claude48_replacement_audit_20260701.csv`.

# Copilot CLI + Claude 4.8 guarded leakage rerun (2026-07-01)

Scope: 49 Copilot CLI + Claude 4.8 tasks labelled `confirmed` by Codex-only annotation; placeholder labels excluded.

| Harness | LLM | Trials | Pass | Fail | No reward | Exceptions |
|---|---|---:|---:|---:|---:|---|
| copilot_cli | claude-opus-4-8 | 49 | 7 | 42 | 0 | AgentTimeoutError:9 |

Original rewards in replaced scope: 31 pass / 18 fail / 0 no-reward.

Artifacts:
- Results CSV: `harbor_benchmark/reports/guarded_leak_copilot_claude48_rerun_results_20260701.csv`
- Replacement audit: `harbor_benchmark/reports/guarded_leak_copilot_claude48_replacement_audit_20260701.csv`
- Log artifact directory: `harbor_benchmark/reports/guarded_leak_copilot_claude48_artifacts_20260701`
- Trajectory exports: `harbor_benchmark/trajectory_exports/guarded_leak_copilot_claude48_20260701`

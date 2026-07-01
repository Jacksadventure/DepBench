# Claude segment1 guarded leakage rerun (2026-07-01)

Scope: 64 Claude Code + GPT-5.5 tasks labelled `confirmed` by the Codex-only Claude annotation segment1 and rerun with leakage guards.

| Harness | LLM | Trials | Pass | Fail | No reward | Exceptions |
|---|---|---:|---:|---:|---:|---|
| claude_code | gpt-5.5 | 64 | 7 | 57 | 0 | AgentTimeoutError:5 |

Original rewards in replaced scope: 45 pass / 19 fail / 0 no-reward.

Artifacts:
- Results CSV: `harbor_benchmark/reports/guarded_leak_claude_segment1_rerun_results_20260701.csv`
- Replacement audit: `harbor_benchmark/reports/guarded_leak_claude_segment1_replacement_audit_20260701.csv`
- Log artifact directory: `harbor_benchmark/reports/guarded_leak_claude_segment1_artifacts_20260701`
- Trajectory exports: `harbor_benchmark/trajectory_exports/guarded_leak_claude_segment1_20260701`

Notes:
- Verifier `reward.txt` is the reward source; timeout rows with `reward.txt=0` are counted as failed reward-bearing outcomes.
- Guard markers were copied with each selected trial where present.
- GitHub/Copilot/API token values in copied agent logs were redacted before committing.

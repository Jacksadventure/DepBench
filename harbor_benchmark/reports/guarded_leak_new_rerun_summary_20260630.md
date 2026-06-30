# Guarded new leakage rerun (2026-06-30)

Scope: 68 newly added `confirmed` + `agreement=both` exact `(task,harness,llm)` pairs after the full leakage-list refresh.

| Harness | LLM | Trials | Orig pass | Guarded pass | Δ pass | Fail | No reward | Exceptions | Endpoint/Auth/Docker errors |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| copilot-cli | gpt-5.5 | 13 | 9 | 7 | -2 | 6 | 0 | AgentTimeoutError:1 | 0 |
| opencode | gemini-3.5-flash | 7 | 5 | 0 | -5 | 7 | 0 | AgentTimeoutError:1 | 0 |
| opencode | gpt-5.5 | 48 | 32 | 5 | -27 | 42 | 1 | AgentTimeoutError:35, NonZeroAgentExitCodeError:1 | 0 |

Artifacts:
- Results CSV: `harbor_benchmark/reports/guarded_leak_new_rerun_results_20260630.csv`
- Log artifact directory: `harbor_benchmark/reports/guarded_leak_new_artifacts_20260630`
- Trajectory exports: `harbor_benchmark/trajectory_exports/guarded_leak_new_20260630`

Key notes:
- Rerun scope is exact (task,harness,llm) confirmed+agreement=both pairs; no task cross-product reruns are counted.
- Previous guarded exact rerun covered 97 runnable pairs and skipped 16 Codex+Gemini pairs due Codex non-GPT exclusion.
- Updated full leakage list added 68 runnable pairs: OpenCode+GPT-5.5 48, OpenCode+Gemini 7, Copilot CLI+GPT-5.5 13.
- OpenCode+GPT used native github-copilot/gpt-5.5 after OpenAI-compatible chat/completions proved invalid for gpt-5.5; OpenCode+Gemini used the 4143 Copilot API bridge because native github-copilot did not expose gemini-3.5-flash for the zed integrator.
- Guarded reruns used runtime git-history pruning, task repo blocker, and agent proxy env injection. Verifier reward.txt is the reward source; timeout rows with reward.txt=0 are counted as failed reward-bearing outcomes.
- Copied raw logs and trajectories are redacted before commit; trajectory provenance follows the prior leakage-analysis notes and no missing trajectory is fabricated.

Note: `own_project_agent_log_hits` in JSON is a conservative string-scan diagnostic over copied agent logs, not a leakage label; the annotation protocol remains authoritative for confirmed/suspect/none leakage labels.

# Combined guarded leakage rerun analysis (2026-06-30)

This combines the earlier 97 runnable exact-pair guarded rerun with the 68 newly discovered exact pairs from the full leakage-list refresh.

Accounted confirmed+both pairs: 181 / 181 (165 runnable rerun rows + 16 skipped Codex+Gemini rows).

| Harness | LLM | Trials | Orig pass | Guarded pass | Δ pass | Fail | No reward | Exceptions | Endpoint/Auth/Docker errors |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| codex | gpt-5.5 | 50 | 37 | 15 | -22 | 35 | 0 | AgentTimeoutError:2 | 0 |
| copilot-cli | gemini-3.5-flash | 25 | 9 | 5 | -4 | 20 | 0 | AgentTimeoutError:1 | 0 |
| copilot-cli | gpt-5.5 | 35 | 24 | 14 | -10 | 21 | 0 | AgentTimeoutError:2 | 0 |
| opencode | gemini-3.5-flash | 7 | 5 | 0 | -5 | 7 | 0 | AgentTimeoutError:1 | 0 |
| opencode | gpt-5.5 | 48 | 32 | 5 | -27 | 42 | 1 | AgentTimeoutError:35, NonZeroAgentExitCodeError:1 | 0 |

## Analysis from leakage-analysis notes

- The annotation protocol treats dependency documentation as allowed RQ4 evidence-gathering; leakage is own-project repo/PR/diff/fix or local git-history access that returns oracle-specific repair content.
- The drafted leakage report identified PR diff/patch and local git history as the dominant confirmed vectors; these reruns directly target those vectors through prompt constraints, runtime `.git` pruning, task-repo shell blocking, and guard proxy env injection.
- Verifier logs are included when present and reward.txt remains authoritative; no held-out test patches are exposed.
- Trajectory exports keep provenance: OpenCode/Codex preserved `trajectory.json` where available; Copilot CLI JSONL is exported as raw event records. Missing trajectories are not synthesized.

## Guard evidence

- New rerun selected rows copied guard markers with the trial artifacts. Marker counts are reported in JSON summaries and coverage reports.
- Endpoint/auth/Docker-network error counters are zero in the selected 68-row new rerun summary; invalid setup attempts (1330/1415) are documented but excluded from selected results.

Artifacts:
- Combined results CSV: `harbor_benchmark/reports/guarded_leak_combined_rerun_results_20260630.csv`
- New rerun results CSV: `harbor_benchmark/reports/guarded_leak_new_rerun_results_20260630.csv`
- Previous rerun results CSV: `harbor_benchmark/reports/guarded_leak_exact_rerun_results_20260630.csv`
- New log coverage: `harbor_benchmark/reports/guarded_leak_new_log_coverage_20260630.json`
- New artifact directory: `harbor_benchmark/reports/guarded_leak_new_artifacts_20260630`
- Combined trajectory index: `harbor_benchmark/trajectory_exports/guarded_leak_combined_20260630`

Conversation documents incorporated:
- `271034-claude-planned-leakage-analysis.md` — analysis plan: leakage is own-project fix access, not dependency docs; report leak-adjusted pass counts and verify blocking claim.
- `271117-claude-drafted-annotation-protocol.md` — protocol: reward is authoritative; verifier logs optional; leakage labels require observation-backed own-project access and oracle content.
- `300225-claude-drafted-leakage-report.md` — prior findings: solution leakage common; vectors include PR diff/patch and local git history; motivated network and git-history guards.
- `280335-gpt-imported-trajectories.md` — trajectory provenance: distinguish preserved Harbor trajectories from converted logs; do not fabricate missing trajectories.
- `280344-gpt-reconstructed-viewer-metadata.md` — viewer metadata caveat: reconstructed metadata is not original runtime metadata.
- `281336-claude-fixed-opencode-gemini-verifier.md` — verifier-log handling: verifier stdout is optional but useful when present; reward remains authoritative.
- `290448-claude-attached-verifier-logs-canonical.md` — verifier coverage: attach by task+reward; prefer gaps over mismatched verifier logs.

Note: `own_project_agent_log_hits` in JSON is a conservative string-scan diagnostic over copied agent logs, not a leakage label; the annotation protocol remains authoritative for confirmed/suspect/none leakage labels.

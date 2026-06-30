# Guarded exact leakage rerun (2026-06-30)

Scope: confirmed leaks with `agreement=both`, rerun at exact `(task, harness, LLM)` granularity.

| Harness | LLM | Trials | Pass | Fail | Exceptions | Endpoint errors |
|---|---|---:|---:|---:|---|---:|
| codex | gpt-5.5 | 50 | 15 | 35 | AgentTimeoutError:2 | 0 |
| copilot-cli | gemini-3.5-flash | 25 | 5 | 20 | AgentTimeoutError:1 | 0 |
| copilot-cli | gpt-5.5 | 22 | 7 | 15 | AgentTimeoutError:1 | 0 |

Skipped Codex+Gemini pairs: 16 (Codex non-GPT excluded/non-runnable).

Artifacts:
- Results CSV: `harbor_benchmark/reports/guarded_leak_exact_rerun_results_20260630.csv`
- Skipped CSV: `harbor_benchmark/reports/guarded_leak_exact_rerun_skipped_codex_gemini_20260630.csv`
- Log artifact directory: `harbor_benchmark/reports/guarded_leak_exact_artifacts_20260630`
- Trajectory exports: `harbor_benchmark/trajectory_exports/guarded_leak_exact_20260630`

Notes:
- Codex+GPT-5.5 combines 25 valid CloudGPT rows from 0820/0925 with 25 Copilot API rows from 0940 by user request.
- Verifier `reward.txt` is the reward source; timeout rows with `reward.txt=0` are counted as failed reward-bearing outcomes.
- Guard markers were copied with each selected trial where present.
- GitHub/Copilot/API token values in copied agent logs were redacted before committing.

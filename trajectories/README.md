# Trajectory exports

Each `.jsonl.gz` file contains one JSON object per final selected task/trial with reward metadata and trajectory JSON when available.

| LLM | Harness | Rows | With trajectory | Missing trajectory | Export |
|---|---|---:|---:|---:|---|
| claude48 | claude_code | 203 | 203 | 0 | `claude48__claude_code.jsonl.gz` |
| claude48 | copilot_cli | 203 | 203 | 0 | `claude48__copilot_cli.jsonl.gz` |
| claude48 | opencode | 203 | 203 | 0 | `claude48__opencode.jsonl.gz` |
| gemini35flash | claude_code | 203 | 203 | 0 | `gemini35flash__claude_code.jsonl.gz` |
| gemini35flash | copilot_cli | 203 | 203 | 0 | `gemini35flash__copilot_cli.jsonl.gz` |
| gemini35flash | opencode | 203 | 203 | 0 | `gemini35flash__opencode.jsonl.gz` |
| gpt55 | claude_code | 203 | 203 | 0 | `gpt55__claude_code.jsonl.gz` |
| gpt55 | codex | 203 | 203 | 0 | `gpt55__codex.jsonl.gz` |
| gpt55 | copilot_cli | 203 | 203 | 0 | `gpt55__copilot_cli.jsonl.gz` |
| gpt55 | opencode | 203 | 203 | 0 | `gpt55__opencode.jsonl.gz` |

Rows replaced by targeted, trajectory-recovery, task-metadata correction, or affected-contract reruns record `outcome_source`, `source_job`, and `trajectory_source`.

Release redactions are recorded in `analysis/release_redactions_2026-07-23.csv`.

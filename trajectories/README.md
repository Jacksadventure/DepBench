# Trajectory exports

Each `.jsonl.gz` file contains one JSON object per task/trial with reward metadata and trajectory JSON when available.

| LLM | Harness | Rows | With trajectory | Missing trajectory | Export |
|---|---|---:|---:|---:|---|
| claude48 | claude_code | 203 | 203 | 0 | `claude48__claude_code.jsonl.gz` |
| claude48 | copilot_cli | 203 | 203 | 0 | `claude48__copilot_cli.jsonl.gz` |
| claude48 | opencode | 203 | 156 | 47 | `claude48__opencode.jsonl.gz` |
| gemini35flash | claude_code | 203 | 203 | 0 | `gemini35flash__claude_code.jsonl.gz` |
| gemini35flash | copilot_cli | 203 | 203 | 0 | `gemini35flash__copilot_cli.jsonl.gz` |
| gemini35flash | opencode | 203 | 73 | 130 | `gemini35flash__opencode.jsonl.gz` |
| gpt55 | claude_code | 203 | 203 | 0 | `gpt55__claude_code.jsonl.gz` |
| gpt55 | codex | 203 | 203 | 0 | `gpt55__codex.jsonl.gz` |
| gpt55 | copilot_cli | 203 | 200 | 3 | `gpt55__copilot_cli.jsonl.gz` |
| gpt55 | opencode | 203 | 202 | 1 | `gpt55__opencode.jsonl.gz` |

Three unrelated internal-session tool-result messages were removed from the
Copilot CLI/Gemini trajectory export without changing task metadata, rewards,
or any other trajectory step. The exact artifact rows and JSON paths are
recorded in `analysis/release_redactions_2026-07-23.csv`.

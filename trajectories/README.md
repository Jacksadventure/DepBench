# Trajectory exports

Each `.jsonl.gz` file contains one JSON object per task/trial with reward metadata and trajectory JSON when available.

| LLM | Harness | Rows | With trajectory | Missing trajectory | Export |
|---|---|---:|---:|---:|---|
| claude48 | claude_code | 219 | 219 | 0 | `claude48__claude_code.jsonl.gz` |
| claude48 | copilot_cli | 219 | 219 | 0 | `claude48__copilot_cli.jsonl.gz` |
| claude48 | opencode | 219 | 171 | 48 | `claude48__opencode.jsonl.gz` |
| gemini35flash | claude_code | 219 | 219 | 0 | `gemini35flash__claude_code.jsonl.gz` |
| gemini35flash | copilot_cli | 219 | 219 | 0 | `gemini35flash__copilot_cli.jsonl.gz` |
| gemini35flash | opencode | 219 | 79 | 140 | `gemini35flash__opencode.jsonl.gz` |
| gpt55 | claude_code | 219 | 219 | 0 | `gpt55__claude_code.jsonl.gz` |
| gpt55 | codex | 219 | 219 | 0 | `gpt55__codex.jsonl.gz` |
| gpt55 | copilot_cli | 219 | 216 | 3 | `gpt55__copilot_cli.jsonl.gz` |
| gpt55 | opencode | 219 | 218 | 1 | `gpt55__opencode.jsonl.gz` |

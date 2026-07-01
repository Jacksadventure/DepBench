# LLM x Harness trajectory exports

Generated: 2026-07-01T08:01:11.467803+00:00

Each `.jsonl.gz` file contains one JSON object per task/trial with reward metadata and trajectory JSON.

| LLM | Harness | Rows | With trajectory | Existing | Converted | Missing | Export |
|---|---|---:|---:|---:|---:|---:|---|
| claude48 | claude_code | 219 | 218 | 0 | 218 | 1 | `harbor_benchmark/trajectory_exports/v4_withtest219_20260627/claude48__claude_code.jsonl.gz` |
| claude48 | copilot_cli | 219 | 219 | 0 | 219 | 0 | `harbor_benchmark/trajectory_exports/v4_withtest219_20260627/claude48__copilot_cli.jsonl.gz` |
| claude48 | opencode | 219 | 219 | 219 | 0 | 0 | `harbor_benchmark/trajectory_exports/v4_withtest219_20260627/claude48__opencode.jsonl.gz` |
| gemini35flash | claude_code | 219 | 219 | 0 | 219 | 0 | `harbor_benchmark/trajectory_exports/v4_withtest219_20260627/gemini35flash__claude_code.jsonl.gz` |
| gemini35flash | copilot_cli | 219 | 219 | 0 | 219 | 0 | `harbor_benchmark/trajectory_exports/v4_withtest219_20260627/gemini35flash__copilot_cli.jsonl.gz` |
| gemini35flash | opencode | 219 | 79 | 78 | 1 | 140 | `harbor_benchmark/trajectory_exports/v4_withtest219_20260627/gemini35flash__opencode.jsonl.gz` |
| gpt55 | claude_code | 219 | 219 | 0 | 219 | 0 | `harbor_benchmark/trajectory_exports/v4_withtest219_20260627/gpt55__claude_code.jsonl.gz` |
| gpt55 | codex | 219 | 219 | 219 | 0 | 0 | `harbor_benchmark/trajectory_exports/v4_withtest219_20260627/gpt55__codex.jsonl.gz` |
| gpt55 | copilot_cli | 219 | 216 | 0 | 216 | 3 | `harbor_benchmark/trajectory_exports/v4_withtest219_20260627/gpt55__copilot_cli.jsonl.gz` |
| gpt55 | opencode | 219 | 218 | 216 | 2 | 1 | `harbor_benchmark/trajectory_exports/v4_withtest219_20260627/gpt55__opencode.jsonl.gz` |

Guarded replacement notes:
- Confirmed+agreement=both replacements were applied on 2026-06-30 for non-Claude rows.
- Claude Code + GPT-5.5 single-annotator confirmed segment1 replacements were applied on 2026-07-01.

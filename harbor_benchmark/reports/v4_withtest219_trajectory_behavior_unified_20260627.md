# Unified trajectory behavior scan

Generated: 2026-07-01T00:07:41.113719+00:00

The scanner uses one rule set for every LLM--harness pair and excludes user/system prompt text. Confirmed+both guarded rerun trajectories were substituted before this scan. Mean rows are arithmetic means over included harness rows with trajectories, not pooled counts.

| LLM | Harness | Rows | With trajectory | Docs | API | Tests | BC hyp. |
|---|---|---:|---:|---:|---:|---:|---:|
| claude48 | claude_code | 219 | 218 | 158 | 218 | 199 | 205 |
| claude48 | copilot_cli | 219 | 219 | 59 | 216 | 201 | 203 |
| claude48 | opencode | 219 | 219 | 163 | 219 | 196 | 213 |
| gemini35flash | claude_code | 219 | 219 | 154 | 219 | 205 | 105 |
| gemini35flash | copilot_cli | 219 | 219 | 2 | 54 | 44 | 32 |
| gemini35flash | opencode | 219 | 79 | 55 | 70 | 56 | 62 |
| gpt55 | claude_code | 219 | 219 | 148 | 219 | 207 | 196 |
| gpt55 | codex | 219 | 219 | 191 | 219 | 182 | 209 |
| gpt55 | copilot_cli | 219 | 216 | 5 | 145 | 113 | 115 |
| gpt55 | opencode | 219 | 218 | 161 | 190 | 177 | 182 |
| gpt55 | Mean | 876 | 872 | 0.577 | 0.886 | 0.778 | 0.804 |
| gemini35flash | Mean | 657 | 517 | 0.470 | 0.711 | 0.615 | 0.470 |
| claude48 | Mean | 657 | 656 | 0.579 | 0.995 | 0.909 | 0.947 |

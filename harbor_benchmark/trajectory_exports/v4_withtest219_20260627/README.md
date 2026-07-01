# v4-with-test219 trajectory exports

Confirmed+agreement=both guarded rerun records were substituted into the affected group exports on 2026-06-30. Replacement rows carry `guarded_replacement=true` and endpoint provenance.

| LLM | Harness | Rows | With trajectory | Pass | Fail | No reward |
|---|---|---:|---:|---:|---:|---:|
| gpt55 | codex | 219 | 219 | 84 | 135 | 0 |
| gpt55 | copilot_cli | 219 | 216 | 88 | 128 | 3 |
| gpt55 | opencode | 219 | 218 | 68 | 150 | 1 |
| gpt55 | claude_code | 219 | 219 | 99 | 120 | 0 |
| gemini35flash | copilot_cli | 219 | 219 | 45 | 174 | 0 |
| gemini35flash | opencode | 219 | 79 | 49 | 169 | 1 |
| gemini35flash | claude_code | 219 | 219 | 48 | 166 | 5 |
| claude48 | copilot_cli | 219 | 219 | 100 | 117 | 2 |
| claude48 | opencode | 219 | 219 | 98 | 121 | 0 |
| claude48 | claude_code | 219 | 218 | 100 | 116 | 3 |

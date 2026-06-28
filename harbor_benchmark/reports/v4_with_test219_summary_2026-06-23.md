# v4-with-test219 summary

Generated: 2026-06-28T14:27:20.113937+00:00

## GPT-5.5

| Agent | Pass | Fail | No reward | Reward tasks | Pass rate |
|---|---:|---:|---:|---:|---:|
| codex | 106 | 113 | 0 | 219 | 0.484 |
| copilot | 98 | 118 | 3 | 216 | 0.454 |
| opencode | 95 | 124 | 0 | 219 | 0.434 |
| claude_code | 99 | 120 | 0 | 219 | 0.452 |

## Gemini 3.5 Flash

| Agent | Pass | Fail | No reward | Reward tasks | Pass rate |
|---|---:|---:|---:|---:|---:|
| copilot | 49 | 169 | 1 | 218 | 0.225 |
| opencode | 54 | 164 | 1 | 218 | 0.248 |
| claude_code | 48 | 166 | 5 | 214 | 0.224 |

## Claude 4.8

| Agent | Pass | Fail | No reward | Reward tasks | Pass rate |
|---|---:|---:|---:|---:|---:|
| claude_code | 100 | 116 | 3 | 216 | 0.463 |
| copilot | 100 | 117 | 2 | 217 | 0.461 |
| opencode | 98 | 121 | 0 | 219 | 0.447 |

## Excluded rows

- Codex non-GPT rows are excluded: Codex versions after v0.94.0 no longer support the chat-completions wire API (openai/codex#10157), while the Gemini Copilot-API route requires chat completions and the Claude 4.8 Codex run produced provider-level tool-result ordering failures under the responses wire API.

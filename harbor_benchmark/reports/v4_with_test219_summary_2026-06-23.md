# v4-with-test219 summary

Generated: 2026-07-02T08:55:55.835144+00:00

## GPT-5.5

| Agent | Pass | Fail | No reward | Reward tasks | Pass rate |
|---|---:|---:|---:|---:|---:|
| codex | 84 | 135 | 0 | 219 | 0.384 |
| copilot | 88 | 128 | 3 | 216 | 0.407 |
| opencode | 68 | 150 | 1 | 218 | 0.312 |
| claude_code | 61 | 158 | 0 | 219 | 0.279 |

## Gemini 3.5 Flash

| Agent | Pass | Fail | No reward | Reward tasks | Pass rate |
|---|---:|---:|---:|---:|---:|
| copilot | 45 | 174 | 0 | 219 | 0.205 |
| opencode | 49 | 169 | 1 | 218 | 0.225 |
| claude_code | 41 | 175 | 3 | 216 | 0.190 |

## Claude 4.8

| Agent | Pass | Fail | No reward | Reward tasks | Pass rate |
|---|---:|---:|---:|---:|---:|
| claude_code | 71 | 146 | 2 | 217 | 0.327 |
| copilot | 76 | 141 | 2 | 217 | 0.350 |
| opencode | 74 | 145 | 0 | 219 | 0.338 |

## Excluded rows
- Codex non-GPT rows are excluded: Codex versions after v0.94.0 no longer support the chat-completions wire API (openai/codex#10157), while the Gemini Copilot-API route requires chat completions and the Claude 4.8 Codex run produced provider-level tool-result ordering failures under the responses wire API.

## Guarded leakage replacement notes
- Confirmed+agreement=both leakage rerun results were substituted into the displayed v4-with-test219 rows on 2026-06-30.
- Claude Code + GPT-5.5 single-annotator confirmed segment1 guarded reruns were substituted on 2026-07-01.
- Copilot CLI + Claude 4.8 single-annotator confirmed guarded reruns were substituted on 2026-07-01.
- Remaining Claude-series single-annotator confirmed guarded reruns were substituted on 2026-07-02.

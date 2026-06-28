# Full 219-task result directory map

Generated: 2026-06-28T14:27:20.113937+00:00

These directories provide one local folder per displayed Agent--LLM row for inspecting task-level outputs. Claude directories are not included here. Codex non-GPT rows are excluded for the protocol reason noted below.

| Agent | Model | Result directory | Tasks | Pass | Fail | No reward |
|---|---|---|---:|---:|---:|---:|
| codex | gpt-5.5 | `harbor_jobs/v4_withtest219__codex__gpt55__full219_20260627` | 219 | 106 | 113 | 0 |
| copilot_cli | gpt-5.5 | `harbor_jobs/v4_withtest219__copilot_cli__gpt55__full219_20260627` | 219 | 98 | 118 | 3 |
| opencode | gpt-5.5 | `harbor_jobs/v4_withtest219__opencode__gpt55__full219_20260627` | 219 | 95 | 124 | 0 |
| copilot_cli | gemini-3.5-flash | `harbor_jobs/v4_withtest219__copilot_cli__gemini35flash__full219_20260627` | 219 | 49 | 169 | 1 |
| opencode | gemini-3.5-flash | `harbor_jobs/v4_withtest219__opencode__gemini35flash__full219_20260627` | 219 | 54 | 164 | 1 |

Excluded: Codex + Gemini 3.5 Flash. Codex non-GPT rows are excluded: Codex versions after v0.94.0 no longer support the chat-completions wire API (openai/codex#10157), while the Gemini Copilot-API route requires chat completions and the Claude 4.8 Codex run produced provider-level tool-result ordering failures under the responses wire API.

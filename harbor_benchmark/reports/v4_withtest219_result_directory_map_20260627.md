# Full 219-task result directory map

Generated: 2026-07-01T00:00:52.043634+00:00

These directories provide one local folder per displayed Agent--LLM row for inspecting task-level outputs. Claude directories are not included here. Codex non-GPT rows are excluded for the protocol reason noted below. Confirmed+both guarded rerun rows have been substituted into the displayed counts; replacement provenance is in `guarded_leak_replacement_audit_20260630.csv`.

| Agent | Model | Result directory | Tasks | Pass | Fail | No reward | Guarded replacements |
|---|---|---|---:|---:|---:|---:|---:|
| codex | gpt-5.5 | `harbor_jobs/v4_withtest219__codex__gpt55__full219_20260627` | 219 | 84 | 135 | 0 | 50 |
| copilot_cli | gpt-5.5 | `harbor_jobs/v4_withtest219__copilot_cli__gpt55__full219_20260627` | 219 | 88 | 128 | 3 | 35 |
| opencode | gpt-5.5 | `harbor_jobs/v4_withtest219__opencode__gpt55__full219_20260627` | 219 | 68 | 150 | 1 | 48 |
| copilot_cli | gemini-3.5-flash | `harbor_jobs/v4_withtest219__copilot_cli__gemini35flash__full219_20260627` | 219 | 45 | 174 | 0 | 25 |
| opencode | gemini-3.5-flash | `harbor_jobs/v4_withtest219__opencode__gemini35flash__full219_20260627` | 219 | 49 | 169 | 1 | 7 |

Excluded: Codex + Gemini 3.5 Flash. Codex non-GPT rows are excluded: Codex versions after v0.94.0 no longer support the chat-completions wire API (openai/codex#10157), while the Gemini Copilot-API route requires chat completions and the Claude 4.8 Codex run produced provider-level tool-result ordering failures under the responses wire API.

# Claude 4.8 multi-agent summary — v4-with-test219

Generated: 2026-06-28T14:27:20.113937+00:00

| Agent | Model | Pass | Fail | No reward | Reward tasks | Pass rate (reward-bearing) | Pass rate (total) |
|---|---|---:|---:|---:|---:|---:|---:|
| copilot | claude-opus-4-8 | 100 | 117 | 2 | 217 | 0.461 | 0.457 |
| opencode | claude-opus-4-8 | 98 | 121 | 0 | 219 | 0.447 | 0.447 |

Excluded: Codex + Claude 4.8. Codex non-GPT rows are excluded: Codex versions after v0.94.0 no longer support the chat-completions wire API (openai/codex#10157), while the Gemini Copilot-API route requires chat completions and the Claude 4.8 Codex run produced provider-level tool-result ordering failures under the responses wire API.

Artifacts:
- `v4_with_test219_claude48_multi_agent_results_2026-06-27.csv`
- `v4_with_test219_claude48_multi_agent_summary_2026-06-27.json`

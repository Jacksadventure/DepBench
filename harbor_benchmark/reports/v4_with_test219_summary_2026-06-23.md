# v4-with-test219 summary

Generated: 2026-07-01T00:00:52.043634+00:00

## GPT-5.5

| Agent | Pass | Fail | No reward | Reward tasks | Pass rate |
|---|---:|---:|---:|---:|---:|
| codex | 84 | 135 | 0 | 219 | 0.384 |
| copilot | 88 | 128 | 3 | 216 | 0.407 |
| opencode | 68 | 150 | 1 | 218 | 0.312 |
| claude_code | 99 | 120 | 0 | 219 | 0.452 |

## Gemini 3.5 Flash

| Agent | Pass | Fail | No reward | Reward tasks | Pass rate |
|---|---:|---:|---:|---:|---:|
| copilot | 45 | 174 | 0 | 219 | 0.205 |
| opencode | 49 | 169 | 1 | 218 | 0.225 |
| claude_code | 48 | 166 | 5 | 214 | 0.224 |

## Claude 4.8

| Agent | Pass | Fail | No reward | Reward tasks | Pass rate |
|---|---:|---:|---:|---:|---:|
| claude_code | 100 | 116 | 3 | 216 | 0.463 |
| copilot | 100 | 117 | 2 | 217 | 0.461 |
| opencode | 98 | 121 | 0 | 219 | 0.447 |

## Excluded rows
- Codex non-GPT rows are excluded: Codex versions after v0.94.0 no longer support the chat-completions wire API (openai/codex#10157), while the Gemini Copilot-API route requires chat completions and the Claude 4.8 Codex run produced provider-level tool-result ordering failures under the responses wire API.
- Codex non-GPT rows are excluded: Codex versions after v0.94.0 no longer support the chat-completions wire API (openai/codex#10157), while the Gemini Copilot-API route requires chat completions and the Claude 4.8 Codex run produced provider-level tool-result ordering failures under the responses wire API.

## Guarded leakage replacement notes
- Confirmed+agreement=both leakage rerun results were substituted into the displayed v4-with-test219 rows on 2026-06-30. Replacement scope: 165 runnable exact (task,harness,llm) rows; 16 Codex+Gemini rows remain excluded.
- Replacement audit: harbor_benchmark/reports/guarded_leak_replacement_audit_20260630.csv. Combined guarded rerun source: harbor_benchmark/reports/guarded_leak_combined_rerun_results_20260630.csv.
- Some replacement rows intentionally use different routed backends by user request (e.g. OpenCode GPT via native Copilot and Codex GPT mixed CloudGPT/Copilot API); see guarded leakage rerun summaries for endpoint provenance.

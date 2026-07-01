# DepBench v4

DepBench v4 is a dependency-update **breaking-change repair** benchmark. Each task is built from a real dependency-upgrade PR where the bot bumped a package, CI failed, and a human repaired the code. The agent receives the broken post-upgrade repository state and must edit source code so the hidden post-upgrade tests pass.

This README is the compact reference for the **current v4 benchmark baseline**, the **current dataset distribution**, and the **results that use the current dataset**.

## Current baseline

- **Authoritative dataset path:** `harbor_benchmark/tasks_v4/`
- **Current benchmark baseline:** **219 curated v4-with-test tasks (205 clean baseline + 14 hard with-test imports)**
- **Index file:** `harbor_benchmark/task_summary.json`
- **Harness spec:** `harbor_benchmark/HARNESS.md`

## What a task contains

Each task directory contains:

- `instruction.md` — the agent-visible prompt
- `task.toml` — metadata, timeouts, and resources
- `environment/` — runtime scaffold
- `solution/` — hidden oracle patches
- `tests/` — hidden verifier-side tests

Under the current v4 setup, the dependency manifest patch is **not** pre-applied in the agent image. The agent must infer and perform the dependency upgrade itself.

## Current 219-task distribution

| Ecosystem | Tasks | Share |
|---|---:|---:|
| npm/yarn | 79 | 36.1% |
| Maven/Java | 66 | 30.1% |
| Go | 41 | 18.7% |
| Cargo/Rust | 21 | 9.6% |
| Python | 12 | 5.5% |


The current branch keeps the published 205-task clean witnessed baseline and adds only the 14 harder with-test imports that survived the post-run quality audit. The audit removed 38 imported tasks whose hidden test deltas were too weak or whose tasks were solved by all three main GPT-5.5 agents (Copilot CLI, Codex, and OpenCode).

## Interpreting the result tables

Harbor can record both:

1. a **verifier reward** (`1.0` or `0.0`), and
2. an **exception** (for example `AgentTimeoutError`)

for the same trial. That means:

- a timed-out trial can still be a **PASS** if the verifier reward is `1.0`
- `PASS + FAIL` does not necessarily sum to `PASS + FAIL + ERR`

The tables below follow the numbers already documented in checked-in result files and handoff notes.

## Current-dataset benchmark results

### Current curated v4-with-test baseline: v4-219

| Agent | Model | Snapshot | Mean reward | Source |
|---|---|---|---:|---|
| Claude Code | Claude 4.8 | v4-with-test219 | **0.463** | `harbor_benchmark/reports/v4_with_test219_claude_code_claude48_summary_2026-06-26.json` |
| Copilot CLI | Claude 4.8 | v4-with-test219 | **0.461** | `harbor_benchmark/reports/v4_with_test219_claude48_multi_agent_summary_2026-06-27.json` |
| Claude Code | GPT-5.5 | v4-with-test219 | **0.452** | `harbor_benchmark/reports/v4_with_test219_claude_code_copilot_api_summary_2026-06-25.json` |
| OpenCode | Claude 4.8 | v4-with-test219 | **0.447** | `harbor_benchmark/reports/v4_with_test219_claude48_multi_agent_summary_2026-06-27.json` |
| Copilot CLI | GPT-5.5 | v4-with-test219 | **0.407** | `harbor_benchmark/reports/v4_with_test219_summary_2026-06-23.json` |
| Codex | GPT-5.5 | v4-with-test219 | **0.384** | `harbor_benchmark/reports/v4_with_test219_summary_2026-06-23.json` |
| OpenCode | GPT-5.5 | v4-with-test219 | **0.312** | `harbor_benchmark/reports/v4_with_test219_summary_2026-06-23.json` |
| OpenCode | Gemini 3.5 Flash | v4-with-test219 | **0.225** | `harbor_benchmark/reports/v4_with_test219_summary_2026-06-23.json` |
| Claude Code | Gemini 3.5 Flash | v4-with-test219 | **0.224** | `harbor_benchmark/reports/v4_with_test219_claude_code_copilot_api_summary_2026-06-25.json` |
| Copilot CLI | Gemini 3.5 Flash | v4-with-test219 | **0.205** | `harbor_benchmark/reports/v4_with_test219_summary_2026-06-23.json` |
| Copilot CLI | DeepSeek | v4-with-test219 | **0.174** | `harbor_benchmark/reports/copilot_deepseek_v4_with_test219_summary_2026-06-29.json` |
| Claude Code | DeepSeek | v4-with-test219 | **0.164** | `harbor_benchmark/reports/claude_code_deepseek_fresh_v4_with_test219_summary_2026-06-29.json` |

Claude Code GPT-5.5/Gemini rows are full 219-task Copilot API runs and supersede
older Maestro summaries that had auth/nonzero-exit reliability concerns. The
Claude 4.8 rows are full 219-task runs through the Anthropic/OpenAI-compatible
Claude 4.8 endpoint; Copilot CLI uses BYOK provider mode.

Codex non-GPT rows are excluded from the current comparison. Codex versions after
v0.94.0 no longer support the chat-completions wire API
(openai/codex#10157); this makes the Gemini Copilot-API route unavailable to
current Codex, and the Claude 4.8 Codex run failed with provider-level tool
message ordering errors under the responses wire API.

Confirmed+agreement=both leakage reruns have been substituted into the affected
v4-with-test219 rows. The replacement audit is
`harbor_benchmark/reports/guarded_leak_replacement_audit_20260630.csv`; the
combined rerun analysis is
`harbor_benchmark/reports/guarded_leak_combined_rerun_summary_20260630.md`.

### Current clean witnessed baseline: v4-205

#### Final / intended comparison runs

| Agent | Model | Snapshot | Mean reward | Source |
|---|---|---|---:|---|
| Copilot CLI | GPT-5.5 | clean205 | **0.450** | `conversations/260619-benchmark-runs/142134-copilot-gpt55-complete.md` |
| Codex | GPT-5.5 | clean205 | **0.478** | `harbor_jobs/codex_cloudgpt_gpt55_clean205_nopreapply_conc5_2026-06-19__15-16-03/result.json`, `harbor_jobs/codex_cloudgpt_gpt55_clean205_resume204_clean_conc5_2026-06-21__04-12-00/result.json`, `conversations/260619-benchmark-runs/125236-opencode-after-codex-launch.md` |
| OpenCode | GPT-5.5 | clean205 | **0.449** | `harbor_jobs/opencode_cloudgpt_gpt55_clean205_nopreapply_conc5_2026-06-19__15-16-03/result.json`, `harbor_jobs/opencode_gpt55_clean205_resume_after_codex_conc5_2026-06-21/result.json`, `conversations/260619-benchmark-runs/125236-opencode-after-codex-launch.md` |
| Claude Code | GPT-5.5 | clean205 | **0.176** | `harbor_benchmark/reports/claude_code_maestro_clean205_summary_2026-06-24.json` |

#### Additional clean205 runs

| Agent | Model | Snapshot | Mean reward | Source |
|---|---|---|---:|---|
| OpenCode | Gemini 3.5 Flash | clean205 | **0.273** | `harbor_jobs/opencode_gemini35flash_clean205_frozen_conc6_2026-06-22__03-11-12/result.json` |
| Claude Code | Gemini 3.5 Flash | clean205 | **0.176** | `harbor_benchmark/reports/claude_code_maestro_clean205_summary_2026-06-24.json` |

## Recommended comparison baseline

For any new v4-with-test comparison table, use:

1. the **219-task curated v4-with-test snapshot**
2. clearly labeled agent/model pairs

Use the 205-task clean witnessed snapshot only for historical clean-baseline comparisons.

The most meaningful completed current-dataset comparison already documented in-repo is:

| Agent | Model | Mean reward |
|---|---|---:|
| Claude Code | Claude 4.8 | **0.463** |
| Copilot CLI | Claude 4.8 | **0.461** |
| Claude Code | GPT-5.5 | **0.452** |
| OpenCode | Claude 4.8 | **0.447** |
| Copilot CLI | GPT-5.5 | **0.407** |
| Codex | GPT-5.5 | **0.384** |
| OpenCode | GPT-5.5 | **0.312** |
| OpenCode | Gemini 3.5 Flash | **0.225** |
| Claude Code | Gemini 3.5 Flash | **0.224** |
| Copilot CLI | Gemini 3.5 Flash | **0.205** |
| Copilot CLI | DeepSeek | **0.174** |
| Claude Code | DeepSeek | **0.164** |

## Source map

- Harness spec: `harbor_benchmark/HARNESS.md`
- Current dataset index: `harbor_benchmark/task_summary.json`
- Clean205 Copilot aggregate note: `conversations/260619-benchmark-runs/142134-copilot-gpt55-complete.md`
- Clean205 Codex/OpenCode resume note: `conversations/260619-benchmark-runs/040530-codex-opencode-resume.md`
- Clean205 OpenCode-after-Codex note: `conversations/260619-benchmark-runs/125236-opencode-after-codex-launch.md`
- Clean205 launch note + Claude auth failure: `conversations/260619-benchmark-runs/153200-copilot-gpt55-clean205-launch.md`
- Clean205 Claude Code Maestro summary: `harbor_benchmark/reports/claude_code_maestro_clean205_summary_2026-06-24.md`

- v4-with-test219 summary: `harbor_benchmark/reports/v4_with_test219_summary_2026-06-23.json`
- v4-with-test219 result directory map: `harbor_benchmark/reports/v4_withtest219_result_directory_map_20260627.md`
- v4-with-test219 Claude Code Claude 4.8 summary: `harbor_benchmark/reports/v4_with_test219_claude_code_claude48_summary_2026-06-26.md`
- v4-with-test219 Claude Code Claude 4.8 per-task results: `harbor_benchmark/reports/v4_with_test219_claude_code_claude48_results_2026-06-26.csv`
- v4-with-test219 Claude 4.8 multi-agent summary: `harbor_benchmark/reports/v4_with_test219_claude48_multi_agent_summary_2026-06-27.md`
- v4-with-test219 Claude 4.8 multi-agent per-task results: `harbor_benchmark/reports/v4_with_test219_claude48_multi_agent_results_2026-06-27.csv`
- v4-with-test219 Claude Code Copilot API summary: `harbor_benchmark/reports/v4_with_test219_claude_code_copilot_api_summary_2026-06-25.md`
- v4-with-test219 Claude Code Copilot API per-task results: `harbor_benchmark/reports/v4_with_test219_claude_code_copilot_api_results_2026-06-25.csv`
- v4-with-test219 OpenCode Gemini rerun summary: `harbor_benchmark/reports/v4_with_test219_opencode_gemini_rerun_summary_2026-06-28.md`
- v4-with-test219 Claude Code DeepSeek summary: `harbor_benchmark/reports/claude_code_deepseek_fresh_v4_with_test219_summary_2026-06-29.md`
- v4-with-test219 Copilot DeepSeek summary: `harbor_benchmark/reports/copilot_deepseek_v4_with_test219_summary_2026-06-29.md`

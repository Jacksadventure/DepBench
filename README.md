# DepBench v4

DepBench v4 is a dependency-update **breaking-change repair** benchmark. Each task is built from a real dependency-upgrade PR where the bot bumped a package, CI failed, and a human repaired the code. The agent receives the broken post-upgrade repository state and must edit source code so the hidden post-upgrade tests pass.

This README is the compact reference for the **current v4 benchmark baseline**, the **current dataset distribution**, and the **results that use the current dataset**.

## Current baseline

- **Authoritative dataset path:** `harbor_benchmark/tasks_v4/`
- **Current benchmark baseline:** **205 clean witnessed tasks**
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

## Current 205-task distribution

| Ecosystem | Tasks | Share |
|---|---:|---:|
| npm/yarn | 79 | 38.5% |
| Maven/Java | 66 | 32.2% |
| Go | 28 | 13.7% |
| Cargo/Rust | 20 | 9.8% |
| Python | 12 | 5.9% |

## Interpreting the result tables

Harbor can record both:

1. a **verifier reward** (`1.0` or `0.0`), and
2. an **exception** (for example `AgentTimeoutError`)

for the same trial. That means:

- a timed-out trial can still be a **PASS** if the verifier reward is `1.0`
- `PASS + FAIL` does not necessarily sum to `PASS + FAIL + ERR`

The tables below follow the numbers already documented in checked-in result files and handoff notes.

## Current-dataset benchmark results

### Current clean witnessed baseline: v4-205

#### Final / intended comparison runs

| Agent | Model | Snapshot | Mean reward | Source |
|---|---|---|---:|---|
| Copilot CLI | GPT-5.5 | clean205 | **0.450** | `conversations/260619-benchmark-runs/142134-copilot-gpt55-complete.md` |
| Codex | GPT-5.5 | clean205 | **0.478** | `harbor_jobs/codex_cloudgpt_gpt55_clean205_nopreapply_conc5_2026-06-19__15-16-03/result.json`, `harbor_jobs/codex_cloudgpt_gpt55_clean205_resume204_clean_conc5_2026-06-21__04-12-00/result.json`, `conversations/260619-benchmark-runs/125236-opencode-after-codex-launch.md` |
| OpenCode | GPT-5.5 | clean205 | **0.449** | `harbor_jobs/opencode_cloudgpt_gpt55_clean205_nopreapply_conc5_2026-06-19__15-16-03/result.json`, `harbor_jobs/opencode_gpt55_clean205_resume_after_codex_conc5_2026-06-21/result.json`, `conversations/260619-benchmark-runs/125236-opencode-after-codex-launch.md` |
| Claude Code | GPT-5.5 | clean205 | — | `conversations/260619-benchmark-runs/153200-copilot-gpt55-clean205-launch.md` |

#### Current in-progress clean205 run

| Agent | Model | Snapshot | Mean reward | Source |
|---|---|---|---:|---|
| OpenCode | Gemini 3.5 Flash | clean205 | **0.273** | `harbor_jobs/opencode_gemini35flash_clean205_frozen_conc6_2026-06-22__03-11-12/result.json` |

## Recommended comparison baseline

For any new v4 comparison table, use:

1. the **205-task clean witnessed snapshot**
2. clearly labeled agent/model pairs

The most meaningful completed clean205 comparison already documented in-repo is:

| Agent | Model | Mean reward |
|---|---|---:|
| Copilot CLI | GPT-5.5 | **0.450** |
| Codex | GPT-5.5 | **0.478** |
| OpenCode | GPT-5.5 | **0.449** |

## Source map

- Harness spec: `harbor_benchmark/HARNESS.md`
- Current dataset index: `harbor_benchmark/task_summary.json`
- Clean205 Copilot aggregate note: `conversations/260619-benchmark-runs/142134-copilot-gpt55-complete.md`
- Clean205 Codex/OpenCode resume note: `conversations/260619-benchmark-runs/040530-codex-opencode-resume.md`
- Clean205 OpenCode-after-Codex note: `conversations/260619-benchmark-runs/125236-opencode-after-codex-launch.md`
- Clean205 launch note + Claude auth failure: `conversations/260619-benchmark-runs/153200-copilot-gpt55-clean205-launch.md`

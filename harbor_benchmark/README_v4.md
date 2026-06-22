# DepBench v4

DepBench v4 is a dependency-update **breaking-change repair** benchmark. Each task is built from a real dependency-upgrade PR where the bot bumped a package, CI failed, and a human repaired the code. The agent receives the broken post-upgrade repository state and must edit source code so the hidden post-upgrade tests pass.

This README is the compact reference for the **current v4 benchmark baseline**, the **current dataset distribution**, and the **results that use the current dataset**.

## Current baseline

- **Authoritative dataset path:** `harbor_benchmark/tasks_v4/`
- **Current benchmark baseline:** **205 clean witnessed tasks**
- **Index file:** `harbor_benchmark/task_summary.json`
- **Harness spec:** `harbor_benchmark/HARNESS.md`
- **Important launch rule:** long-running Harbor jobs should use a **frozen snapshot path**, not the mutable working-tree dataset path.

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

| Agent | Model | Snapshot | Result | Notes | Source |
|---|---|---|---|---|---|
| Copilot CLI | GPT-5.5 | clean205 | **91 pass / 111 fail / 3 no reward** over 205 task results; **45.0%** over 202 reward-bearing tasks | Final aggregate merged across 3 job segments | `conversations/260619-benchmark-runs/142134-copilot-gpt55-complete.md` |
| Codex | GPT-5.5 | clean205 | **98 pass / 107 fail** over 205 reward-bearing tasks; approx **47.8%** pass rate | 1 reward-bearing task from initial launch + 204-task clean resume | `harbor_jobs/codex_cloudgpt_gpt55_clean205_nopreapply_conc5_2026-06-19__15-16-03/result.json`, `harbor_jobs/codex_cloudgpt_gpt55_clean205_resume204_clean_conc5_2026-06-21__04-12-00/result.json`, `conversations/260619-benchmark-runs/125236-opencode-after-codex-launch.md` |
| OpenCode | GPT-5.5 | clean205 | **92 pass / 113 fail** over 205 reward-bearing tasks; approx **44.9%** pass rate | 1 reward-bearing task from initial launch + 204-task resume after Codex | `harbor_jobs/opencode_cloudgpt_gpt55_clean205_nopreapply_conc5_2026-06-19__15-16-03/result.json`, `harbor_jobs/opencode_gpt55_clean205_resume_after_codex_conc5_2026-06-21/result.json`, `conversations/260619-benchmark-runs/125236-opencode-after-codex-launch.md` |
| Claude Code | GPT-5.5 | clean205 | **No valid benchmark result** | Blocked by auth (`Not logged in`) on both attempted launches | `conversations/260619-benchmark-runs/153200-copilot-gpt55-clean205-launch.md` |

#### Current in-progress clean205 run

| Agent | Model | Snapshot | Current state | Notes | Source |
|---|---|---|---|---|---|
| OpenCode | Gemini 3.5 Flash | clean205 frozen | **22 completed / 22 exception-marked / 6 running / 177 pending**, mean reward **0.273** | Frozen-snapshot launch is valid, but current finished trials are all `AgentTimeoutError`; some still pass verifier | `harbor_jobs/opencode_gemini35flash_clean205_frozen_conc6_2026-06-22__03-11-12/result.json` |
## Recommended comparison baseline

For any new v4 comparison table, use:

1. the **205-task clean witnessed snapshot**
2. a **frozen dataset snapshot path** for long-running runs
3. clearly labeled agent/model pairs

The most meaningful completed clean205 comparison already documented in-repo is:

| Agent | Model | Valid clean205 result |
|---|---|
| Copilot CLI | GPT-5.5 | 91 / 202 reward-bearing passes = **45.0%** |
| Codex | GPT-5.5 | 98 / 205 passes = **47.8%** |
| OpenCode | GPT-5.5 | 92 / 205 passes = **44.9%** |

## Source map

- Harness spec: `harbor_benchmark/HARNESS.md`
- Current dataset index: `harbor_benchmark/task_summary.json`
- Clean205 Copilot aggregate note: `conversations/260619-benchmark-runs/142134-copilot-gpt55-complete.md`
- Clean205 Codex/OpenCode resume note: `conversations/260619-benchmark-runs/040530-codex-opencode-resume.md`
- Clean205 OpenCode-after-Codex note: `conversations/260619-benchmark-runs/125236-opencode-after-codex-launch.md`
- Clean205 launch note + Claude auth failure: `conversations/260619-benchmark-runs/153200-copilot-gpt55-clean205-launch.md`

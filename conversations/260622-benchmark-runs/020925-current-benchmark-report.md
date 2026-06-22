# Historical report — invalid 228-task Harbor snapshot

Snapshot time: 2026-06-22T02:09Z

> **Superseded on 2026-06-22.** This report documents the failed Gemini 3.5 Flash run family that still targeted the old 228-task mutable `tasks_v4` path. The benchmark baseline has since been frozen to the clean witnessed **205-task** snapshot, so do **not** use this report as the current comparison baseline.

## Scope

- This report covers the **228-task `tasks_v4` snapshot** used by the active Gemini 3.5 Flash benchmark runs.
- The task metadata is taken from `harbor_benchmark/task_summary.json` at git commit `a95f48e5`, which has **228 rows**.
- The current branch HEAD now contains the later **205-task pruned snapshot**, so the 228-task distribution below is reconstructed from git history plus the checked-in Harbor artifacts.
- I scanned the checked-in `harbor_jobs/` tree for top-level `v4_228` jobs; **only 3 runs are present in this checkout**, so this report includes all currently available results for this dataset, including anything already pushed from another device.

## Dataset distribution

| Ecosystem | Tasks | Share |
|---|---:|---:|
| npm_and_yarn | 95 | 41.7% |
| maven | 67 | 29.4% |
| go_modules | 31 | 13.6% |
| cargo | 22 | 9.6% |
| pip | 13 | 5.7% |

**Most common upgraded libraries**

| Library | Tasks |
|---|---:|
| `version` | 13 |
| `sqlglot` | 8 |
| `typescript` | 6 |
| `@octokit/types` | 4 |
| `github.com/cloudflare/cloudflare-go` | 3 |
| `unknown` | 3 |
| `glob` | 3 |
| `org.maplibre:mlt` | 3 |
| `@babel/parser` | 3 |
| `protobuf-java.version` | 3 |

## Run summary

| Run | Agent | Model | Finished | Completed | Errored | Running | Pending | Mean reward | Exception mix |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| Broken Copilot launch | Copilot CLI | `gemini-3.5-flash` | running | 214 | 214 | 0 | 14 | 0.196 | NonZeroAgentExitCodeError=209, RuntimeError=1, CancelledError=4 |
| Fixed Copilot run | Copilot CLI | `gemini-3.5-flash` | 2026-06-22T00:54:22.781408 | 228 | 4 | 0 | 0 | 0.303 | AgentTimeoutError=4 |
| OpenCode run (live) | OpenCode | `gemini-3.5-flash` | running | 16 | 16 | 1 | 211 | 0.250 | AgentTimeoutError=11, CancelledError=5 |

## Notes on the three runs

- **Broken Copilot launch**: infrastructure-invalid. It mounted the whole Copilot home read-only, causing widespread `NonZeroAgentExitCodeError` before real work. Treat this as a failed launch, not a fair model result.
- **Fixed Copilot run**: the valid completed Copilot benchmark. This is the result to compare against other agents on the 228-task snapshot.
- **OpenCode run (live)**: still in progress. The numbers below are an early-progress snapshot, not a final score.

## Broken Copilot launch

- Job: `copilot_cli_gemini35flash_v4_228_nopreapply_conc6_2026-06-21__10-00-03`
- Overall status mix: **pass 42 · fail 0 · error 172 · pending/running 14**
- Mean reward: **0.196**

| Ecosystem | Pass | Fail | Error | Pending/running |
|---|---:|---:|---:|---:|
| npm_and_yarn | 16 | 0 | 75 | 4 |
| maven | 14 | 0 | 47 | 6 |
| go_modules | 6 | 0 | 22 | 3 |
| cargo | 2 | 0 | 20 | 0 |
| pip | 4 | 0 | 8 | 1 |

## Fixed Copilot run

- Job: `copilot_cli_gemini35flash_v4_228_nopreapply_conc6_2026-06-21__15-15-42`
- Overall status mix: **pass 69 · fail 156 · error 3 · pending/running 0**
- Mean reward: **0.303**

| Ecosystem | Pass | Fail | Error | Pending/running |
|---|---:|---:|---:|---:|
| npm_and_yarn | 21 | 74 | 0 | 0 |
| maven | 31 | 34 | 2 | 0 |
| go_modules | 10 | 21 | 0 | 0 |
| cargo | 1 | 20 | 1 | 0 |
| pip | 6 | 7 | 0 | 0 |

## OpenCode run (live)

- Job: `opencode_gemini35flash_v4_228_nopreapply_conc6_2026-06-21__12-37-23`
- Overall status mix: **pass 4 · fail 0 · error 12 · pending/running 212**
- Mean reward: **0.250**

| Ecosystem | Pass | Fail | Error | Pending/running |
|---|---:|---:|---:|---:|
| npm_and_yarn | 3 | 0 | 4 | 88 |
| maven | 0 | 0 | 4 | 63 |
| go_modules | 0 | 0 | 0 | 31 |
| cargo | 0 | 0 | 1 | 21 |
| pip | 1 | 0 | 3 | 9 |

## Key takeaways

- The **valid Copilot Gemini 3.5 Flash result** is **69 / 228 passed** with mean reward **0.303**.
- The **live OpenCode Gemini 3.5 Flash run** is still very early: **4 passes**, **12 errors**, and **212 tasks not finished yet** at this snapshot.
- The 228-task dataset is heavily weighted toward **npm/yarn (95 tasks, 41.7%)** and **Maven (67 tasks, 29.4%)**; together they account for **71.1%** of the benchmark.
- There are **no additional checked-in 228-task benchmark runs** in this checkout beyond the three listed above.

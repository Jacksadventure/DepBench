# DepBench v4-with-test219 release

This branch is a clean release snapshot of the DepBench dependency-upgrade benchmark. It contains the benchmark dataset, agent trajectories, verifier logs, result summaries, and analysis tables for the reported run.

The release is updated live as final artifacts are refreshed. For reproducible experiments, pin the exact commit SHA of this branch.

## Contents

| Path | Description |
|---|---|
| `dataset/tasks/` | 219 task directories. Each task contains the agent-facing instruction, task metadata, environment metadata, oracle source patch, and hidden verifier test patch. |
| `dataset/task_summary.json` | Task-level metadata: ecosystem, dependency/library, old version, and new version. |
| `trajectories/` | Trajectory exports as gzip JSONL, one file per harness/model configuration. |
| `verify_logs/` | Verifier logs as gzip JSONL, aligned with the trajectory rows. Each row includes verifier stdout and CTRF JSON when available. |
| `results/` | Configuration-level summary and per-trial reward metadata. |
| `analysis/` | Aggregate result and coverage tables. |
| `MANIFEST.json` | Machine-readable release manifest and source commit metadata. |

## Dataset layout

Each task lives under `dataset/tasks/<owner>__<repo>__<pr>/`:

| File | Purpose |
|---|---|
| `instruction.md` | The instruction shown to the coding agent. |
| `task.toml` | Task metadata, resource limits, verifier timeout, and Docker image tag. |
| `environment/docker-compose.yaml` | Container environment definition. |
| `environment/patches/manifest.patch` | Dependency manifest upgrade patch applied to the base repo. |
| `solution/code.patch` | Oracle source-code repair patch. |
| `solution/manifest.patch` | Oracle dependency manifest patch. |
| `solution/solve.sh` | Oracle patch application helper. |
| `tests/test.patch` | Hidden verifier test patch. Do not expose this to agents during benchmark runs. |
| `tests/test.sh` | Hidden verifier command. |
| `tests/test_state.py` | Verifier state helper. |

Docker images are referenced in each `task.toml` as `idk233333/depbench-task-images:<task-folder>`.

## Basic usage

1. Select a task from `dataset/task_summary.json`.
2. Read `dataset/tasks/<task>/instruction.md` and provide it to the agent.
3. Run the agent in the task Docker image from `task.toml`, after applying the dependency manifest upgrade from `environment/patches/manifest.patch`.
4. Keep `solution/` and `tests/` hidden from the agent.
5. After the agent finishes, apply `tests/test.patch` and run `tests/test.sh`.
6. Score reward as `1.0` if the verifier passes and `0.0` if it fails. Rows with no valid reward are reported as `no_reward`.

The release also includes trajectories and verifier logs, so you can analyze the reported experiments directly.

## Agent results

All rows below are over 219 tasks. `Pass rate (total)` uses 219 as the denominator. `Pass rate (reward-bearing)` excludes `no_reward` rows.

| Harness | Model | Pass | Fail | No reward | Pass rate (total) | Pass rate (reward-bearing) | Trajectories |
|---|---|---:|---:|---:|---:|---:|---:|
| Claude Code | Claude Opus 4.8 | 71 | 146 | 2 | 32.4% | 32.7% | 219/219 |
| Copilot CLI | Claude Opus 4.8 | 76 | 141 | 2 | 34.7% | 35.0% | 219/219 |
| OpenCode | Claude Opus 4.8 | 74 | 145 | 0 | 33.8% | 33.8% | 171/219 |
| Claude Code | Gemini 3.5 Flash | 41 | 175 | 3 | 18.7% | 19.0% | 219/219 |
| Copilot CLI | Gemini 3.5 Flash | 45 | 174 | 0 | 20.5% | 20.5% | 219/219 |
| OpenCode | Gemini 3.5 Flash | 49 | 169 | 1 | 22.4% | 22.5% | 79/219 |
| Claude Code | GPT-5.5 | 61 | 158 | 0 | 27.9% | 27.9% | 219/219 |
| Codex | GPT-5.5 | 84 | 135 | 0 | 38.4% | 38.4% | 219/219 |
| Copilot CLI | GPT-5.5 | 88 | 128 | 3 | 40.2% | 40.7% | 216/219 |
| OpenCode | GPT-5.5 | 68 | 150 | 1 | 31.1% | 31.2% | 218/219 |

The best total pass rate in this snapshot is Copilot CLI + GPT-5.5 with 88/219 tasks solved. No configuration solves a majority of the benchmark, and all configurations show substantial failures on hidden dependency-upgrade tests.

## Trajectories

`trajectories/*.jsonl.gz` files are gzip-compressed JSONL. Each row is one reported trial and includes:

- `task`, `trial`, `harness`, `llm`, `model`
- `reward`, `exception_type`
- `has_trajectory`
- `trajectory`: an ATIF-like trajectory object when available

Some rows intentionally have `has_trajectory=false`: the reward and verifier log are included, but the agent log did not contain a recoverable trajectory.

## Verifier logs

`verify_logs/*.jsonl.gz` files are gzip-compressed JSONL and use the same file naming as `trajectories/`. Each row includes:

- trial metadata and reward
- verifier reward text
- verifier stdout as `verifier_test_stdout`
- CTRF JSON as `verifier_ctrf` when available

Use `verify_logs/index.csv` or `verify_logs/index.json` to check coverage.

## Results and analysis

- `results/summary.csv` and `results/summary.json` contain the configuration-level result table.
- `results/per_trial_results.jsonl.gz` contains one compact metadata row per trial, without embedding the full trajectory or verifier stdout.
- `analysis/ecosystem_results.csv` contains result counts by configuration and ecosystem.
- `analysis/coverage.csv` contains trajectory and verifier-log coverage by configuration.

## Release policy

This branch is for consumption and archival use. It contains only release artifacts for the reported benchmark snapshot.

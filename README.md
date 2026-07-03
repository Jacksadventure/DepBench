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
| `analysis/` | Aggregate result, coverage, and trajectory-scan tables. |
| `repro/` | Helper scripts and schema notes for pulling task images, verifying oracle solutions, verifying candidate patches, validating this release, and scanning trajectories. |
| `custom_agents/` | Harbor agent adapters referenced by the provided Harbor config templates. |
| `pyproject.toml` | Python package metadata declaring the Harbor dependency for local execution. |
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

For runnable helper scripts, see `repro/README.md`. For Harbor-based execution, see `repro/HARBOR.md`.

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
- `analysis/trajectory_scan_summary.csv` and `analysis/trajectory_scan_detail.csv` contain rule-based trajectory scan outputs.

## Release policy

This branch is for consumption and archival use. It contains only release artifacts for the reported benchmark snapshot.

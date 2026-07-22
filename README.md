# DepBench v4-with-test203 contract-clean release

DepBench is the first repository-level benchmark for evaluating code agents on dependency-upgrade repair. The original dataset was built from 219 real merged Dependabot and Renovate pull requests across five software ecosystems. This contract-clean release contains the 203 tasks that remain after removing 16 invalid test contracts. DepBench separates dependency upgrades, developer repairs, and test patches, and uses executable oracle checks to ensure that each retained task's failure is caused by the dependency upgrade and that the repair is causally validated. On this filtered benchmark, the strongest historical configuration solves 95/203 tasks (46.8%), highlighting persistent gaps in handling hidden breaking changes and repository-level consistency repairs.

This branch is a clean release snapshot of the DepBench dependency-upgrade benchmark. It contains the benchmark dataset, agent trajectories, verifier logs, result summaries, and analysis tables for the reported run.

The release is updated live as final artifacts are refreshed. For reproducible experiments, pin the exact commit SHA of this branch.

## Maintenance update: Maven verifier environments

On 2026-07-13, 57 Maven task verifiers were hardened after an audit found
guarded task images whose config had lost `JAVA_HOME` and Java on `PATH`.
The verifiers now restore the JDK/Maven environment explicitly and avoid login
shell environment resets.

The corresponding DockerHub task-image tags received config-only updates that
restore `JAVA_HOME`, `PATH`, `MAVEN_HOME`, and `MAVEN_CONFIG`; existing
filesystem layers were reused. Old/new image digests are recorded in
`repro/java_home_image_repair_2026-07-13.csv`.

The retained historical trajectory and verifier rows preserve their original
observations. Any retained verifier cell that failed because of missing
`JAVA_HOME` remains an invalid historical observation and must be replayed
before interpreting cross-configuration Maven results.

## Maintenance update: test contracts

On 2026-07-14, 37 semantic or mixed test-contract findings were reviewed
individually. Eight contracts were repaired, 13 were repackaged around a clean
dependency witness, and 16 were found invalid because no dependency-caused
source-repair witness existed.

The full decision table is available in
`analysis/test_contract_repair_decisions_2026-07-14.{md,csv}`. The 16 invalid
tasks have been removed from `dataset/tasks`, task metadata, all 10 trajectory
and verifier-log files, per-trial results, analysis tables, and Harbor example
configs.

The remaining historical reward values were not changed; aggregate counts and
rates were recomputed over the 203 retained tasks.

## Contents

| Path | Description |
|---|---|
| `dataset/tasks/` | 203 contract-valid task directories. Each task contains the agent-facing instruction, task metadata, environment metadata, oracle source patch, and verifier files. |
| `dataset/task_summary.json` | Task-level metadata: ecosystem, dependency/library, old version, and new version. |
| `trajectories/` | Trajectory exports as gzip JSONL, one file per harness/model configuration. |
| `verify_logs/` | Verifier logs as gzip JSONL, aligned with the trajectory rows. Each row includes verifier stdout and CTRF JSON when available. |
| `results/` | Configuration-level summary and per-trial reward metadata. |
| `analysis/` | Aggregate result, coverage, and trajectory-scan tables. |
| `analysis/repository_metadata.{csv,json}` | Unique repository URLs, licenses, primary languages, archive status, and task mappings. |
| `analysis/task_repository_metadata.csv` | Task-level mapping to repository URL, license, and primary language. |
| `analysis/test_contract_repair_decisions_2026-07-14.{md,csv}` | Per-task decisions for the 37 reviewed semantic/mixed contracts. |
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
| `tests/test.patch` | Optional hidden verifier test patch. Build/compile-only witnesses may omit it. Do not expose it to agents during benchmark runs. |
| `tests/test.sh` | Hidden verifier command. |
| `tests/test_state.py` | Verifier state helper. |

Docker images are referenced in each `task.toml` as `idk233333/depbench-task-images:<task-folder>`.

## Basic usage

1. Select a task from `dataset/task_summary.json`.
2. Read `dataset/tasks/<task>/instruction.md` and provide it to the agent.
3. Run the agent in the task Docker image from `task.toml`, after applying the dependency manifest upgrade from `environment/patches/manifest.patch`.
4. Keep `solution/` and `tests/` hidden from the agent.
5. After the agent finishes, apply `tests/test.patch` when present and run `tests/test.sh`.
6. Score reward as `1.0` if the verifier passes and `0.0` if it fails. Rows with no valid reward are reported as `no_reward`.

The release also includes trajectories and verifier logs, so you can analyze the reported experiments directly.

For runnable helper scripts, see `repro/README.md`. For Harbor-based execution, see `repro/HARBOR.md`.

## Reproduce

All reproduction helpers are in the top-level `repro/` folder:

- `repro/README.md`: reproduction entry point.
- `repro/HARBOR.md`: Harbor-based execution instructions.
- `repro/examples/`: Harbor config templates for the reported configurations.
- `repro/pull_task_images.sh`: pull task Docker images.
- `repro/run_oracle_solution.sh`: verify an oracle solution for one task.
- `repro/run_patch_verifier.sh`: verify a candidate patch for one task.
- `repro/scan_trajectories.py`: scan the released trajectory files.
- `repro/validate_release.py`: validate the release layout and row counts.

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
- `results/final_per_task_outcomes.csv` applies the 111 targeted rerun outcomes to the original full-run result cells.
- `results/targeted_runtime_exception_reruns_203.csv` contains the targeted rerun result records.
- `results/per_trial_results.jsonl.gz` contains one compact metadata row per trial, without embedding the full trajectory or verifier stdout.
- `analysis/ecosystem_results.csv` contains result counts by configuration and ecosystem.
- `analysis/coverage.csv` contains trajectory and verifier-log coverage by configuration.
- `analysis/trajectory_scan_summary.csv` and `analysis/trajectory_scan_detail.csv` contain rule-based trajectory scan outputs.

## Release policy

This branch is for consumption and archival use. It contains only release artifacts for the reported benchmark snapshot.

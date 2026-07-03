# Reproducing DepBench v4-with-test219

This directory contains the minimal helper files for using the release snapshot.

## Requirements

- Docker with access to the task images listed in `dataset/tasks/*/task.toml`
- Bash
- Python 3.10+ for the JSONL helper scripts
- Harbor, if you want to execute benchmark jobs through the benchmark harness
- Network access when a task verifier installs test dependencies

## Task contract

For each task, the agent-facing input is:

- `/app`: the project checkout inside the task Docker image
- `dataset/tasks/<task>/instruction.md`: the prompt text

The following files are for scoring and must not be shown to the agent:

- `dataset/tasks/<task>/solution/*`
- `dataset/tasks/<task>/tests/*`
- `dataset/tasks/<task>/environment/patches/manifest.patch`

After the agent finishes, the verifier applies `tests/test.patch` and runs `tests/test.sh`. The score is read from `/logs/verifier/reward.txt`.

## Harbor execution

For Harbor-based execution, see `repro/HARBOR.md`.

## Pull task images

Pull all task images:

```bash
bash repro/pull_task_images.sh
```

Pull selected tasks:

```bash
bash repro/pull_task_images.sh 29ki__29k__3418 ArcadeData__arcadedb__2808
```

## Verify the oracle solution for one task

```bash
bash repro/run_oracle_solution.sh 29ki__29k__3418
```

The script starts the task image, applies the oracle solution, runs the verifier, and prints the reward path.

## Verify a candidate patch

If you have a patch produced by an agent, verify it with:

```bash
bash repro/run_patch_verifier.sh 29ki__29k__3418 /path/to/agent.patch
```

If the patch needs an additional setup command before scoring, pass it through `DEPBENCH_PRE_VERIFY_CMD`:

```bash
DEPBENCH_PRE_VERIFY_CMD="npm install" \
  bash repro/run_patch_verifier.sh 29ki__29k__3418 /path/to/agent.patch
```

## Inspect reported artifacts

Validate the release layout:

```bash
python3 repro/validate_release.py
```

Read one reported trajectory and verifier row:

```bash
python3 repro/read_trial.py --configuration gpt55__codex --task 29ki__29k__3418 --show-verifier
```

Configuration names match the gzip JSONL filenames under `trajectories/` and `verify_logs/` without the `.jsonl.gz` suffix.

## Scan trajectories

Run the trajectory scanner:

```bash
python3 repro/scan_trajectories.py
```

By default, this reads `trajectories/*.jsonl.gz` and writes:

- `analysis/trajectory_scan_detail.csv`
- `analysis/trajectory_scan_summary.csv`
- `analysis/trajectory_scan_summary.json`

The scanner uses one rule set across all configurations and only scans agent-authored trajectory steps.

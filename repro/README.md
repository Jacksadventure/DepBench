# Reproducing DepBench

This directory contains the minimal helper files for using the release snapshot.

## Download the benchmark

The directory-format task contracts are hosted at
[ZijiantheJack/DepBench](https://huggingface.co/datasets/ZijiantheJack/DepBench).
From the release root, install the package and download the pinned snapshot:

```bash
python3 -m pip install .
python3 repro/download_benchmark.py
```

This creates the ignored local paths `dataset/tasks/` and
`dataset/task_summary.json`.

## Requirements

- The benchmark downloaded from Hugging Face with the command above
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

After the agent finishes, the verifier applies `tests/test.patch` when present and runs `tests/test.sh`. The score is read from `/logs/verifier/reward.txt`.

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

The 57 Maven image tags repaired on 2026-07-13 are listed with their old and
new manifest digests in `repro/java_home_image_repair_2026-07-13.csv`.
Maintainers can use `repro/repair_task_image_toolchain_paths.py` to rebuild
selected Rust, Java, or Go task images with toolchain entry points that remain
available under login shells. The command verifies each staging image before
an optional canonical-tag push and writes old/new image provenance to JSON.

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

## Validate the benchmark

Validate the downloaded task contracts and repository layout:

```bash
python3 repro/audit_release_compliance.py
python3 repro/validate_release.py
```

The compliance audit checks repository governance files, source headers,
license-category accounting, known internal path markers, and high-confidence
credential patterns. It also scans the downloaded dataset when
`dataset/tasks/` is present. External Microsoft approval steps are tracked in
`OPEN_SOURCE_RELEASE_CHECKLIST.md`.

Run results, trajectories, verifier logs, failure annotations, and Harbor job
archives are intentionally not distributed from the `main` branch. Maintainer
scripts for processing private experiment outputs remain under `repro/`, but
they require the corresponding external inputs.

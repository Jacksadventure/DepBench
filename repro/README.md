# Reproducing DepBench

This directory contains the minimal helper files for using the release snapshot.

## Failure-root-cause annotation

For the committed paper-review evidence, use
[`run_multilabel_annotation.py`](run_multilabel_annotation.py). It defaults to
all 10 configurations and all 1,262 non-passes (including missing rewards) in
`paper_review/results/final_per_task_outcomes.csv`. It does not default to the
historical 150-case Gemini + OpenCode subset.

Prepare the evidence without calling any models:

```bash
python3 repro/run_multilabel_annotation.py \
  --output results/failure_multilabel \
  --prepare-only
```

See the [annotation protocol and runtime commands](../paper_review/README.md#failure-root-cause-annotation)
for independent multi-label annotation, Astra adjudication, credentials, resume,
and agreement metrics. `--limit` is only for a global smoke-test subset; omit it
for the complete cohort.

To export compact evidence packets only, without starting annotation:

```bash
python3 repro/build_failure_annotation_packets.py \
  --output results/failure_annotation_packets.json
```

This also defaults to all configurations under `paper_review`. Use
`--configuration <name>` (repeatable) or `--manifest <path>` only for an
intentional subset, and `--artifact-root <path>` for another artifact layout.
The historical `package_paper_review_supplements.py` and
`validate_paper_review_supplements.py` preserve the original single-label
supplement; they are not the entry points for the new all-configuration study.

## Download the benchmark

The directory-format task contracts are hosted at
[Depbench/build_from_source](https://huggingface.co/datasets/Depbench/build_from_source/tree/3eef955c222baa310ef039153755ec9d7cdb03f3).
From the release root, install the package and download the pinned snapshot:

```bash
python3 -m pip install .
python3 repro/download_benchmark.py
```

This creates the ignored local paths `dataset/tasks/` and
`dataset/task_summary.json`. The pinned archive directly contains the
201-task `main` dataset; the two license-excluded tasks documented in the root
README are not packaged.

## Requirements

- The benchmark downloaded from Hugging Face with the command above
- Docker with network access to the source repositories, base-image registry,
  and package registries used during local builds
- Bash
- Python 3.12+ for the release helpers and Harbor
- Harbor, if you want to execute benchmark jobs through the benchmark harness
- Network access while task images and verifier dependencies are built

## Task contract

For each task, the agent-facing input is:

- `/app`: the project checkout created by `environment/Dockerfile`
- `dataset/tasks/<task>/instruction.md`: the prompt text

The following files are for scoring and must not be shown to the agent:

- `dataset/tasks/<task>/solution/*`
- `dataset/tasks/<task>/tests/*`
- `dataset/tasks/<task>/environment/patches/manifest.patch`

After the agent finishes, the verifier applies `tests/test.patch` when present and runs `tests/test.sh`. The score is read from `/logs/verifier/reward.txt`.

## Harbor execution

For Harbor-based execution, see `repro/HARBOR.md`.

## Build task images

Build all task images locally from their upstream source repositories:

```bash
bash repro/build_task_images.sh
```

Build selected tasks:

```bash
bash repro/build_task_images.sh 29ki__29k__3418 ArcadeData__arcadedb__2808
```

Each Dockerfile installs the required build tools, clones the repository,
checks out its fixed base commit, bootstraps dependencies, restores a clean Git
worktree, and exposes language toolchains to Harbor login shells. Source pins
are listed in `analysis/task_source_builds.{csv,json}`.

The release audit rebuilt every Dockerfile and checked the runtime toolchain,
Git HEAD, and clean worktree. Results are in
`analysis/source_build_audit_201.{csv,json}`.

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

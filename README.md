<div align="center">

# DepBench

**A repository-level benchmark for dependency-upgrade repair by coding agents**

<p>
  <a href="https://huggingface.co/datasets/ZijiantheJack/DepBench">
    <img alt="Hugging Face dataset" src="https://img.shields.io/badge/Hugging%20Face-Dataset-FFD21E?style=flat-square">
  </a>
  <img alt="203 tasks" src="https://img.shields.io/badge/tasks-203-2E8B57?style=flat-square">
  <img alt="159 repositories" src="https://img.shields.io/badge/repositories-159-3B82F6?style=flat-square">
  <img alt="5 ecosystems" src="https://img.shields.io/badge/ecosystems-5-8B5CF6?style=flat-square">
  <img alt="contract-clean release" src="https://img.shields.io/badge/release-v4--with--test203-343A40?style=flat-square">
</p>

[Quick Start](#quick-start) &middot;
[Benchmark Design](#benchmark-design) &middot;
[Evaluation Protocol](#evaluation-protocol) &middot;
[Artifacts](#release-artifacts) &middot;
[Reproduction](#reproduction)

</div>

---

DepBench evaluates whether coding agents can repair repository-level breakages
caused by dependency upgrades. Its tasks originate from real merged Dependabot
and Renovate pull requests and span npm/yarn, Maven, Go modules, Cargo, and pip.

This contract-clean release retains **203 valid tasks** from the original
219-task snapshot. Each task separates the dependency upgrade, the developer
repair, and the hidden verifier so that the causal effect of the upgrade can be
checked directly.

> [!IMPORTANT]
> `solution/` and `tests/` are published for reproducibility. Keep both
> directories hidden from agents during evaluation.

## At a glance

| Tasks | Source repositories | Ecosystems | Evaluated configurations | Reported trials |
|---:|---:|---:|---:|---:|
| **203** | **159** | **5** | **10** | **2,030** |

The strongest historical configuration in this snapshot solves **95/203 tasks
(46.8%)**. Complete configuration-level results are available in
[`results/summary.csv`](results/summary.csv).

## Quick start

Install the release helpers, download the pinned benchmark snapshot from
Hugging Face, and validate the complete release:

```bash
python3 -m pip install -e .
python3 repro/download_benchmark.py
python3 repro/validate_release.py
```

The downloader verifies the archive checksum and creates:

```text
dataset/
|-- task_summary.json
`-- tasks/
    `-- <owner>__<repo>__<pull-request>/
```

The Hugging Face revision and archive SHA-256 are pinned in
[`MANIFEST.json`](MANIFEST.json). The downloaded `dataset/` directory is
excluded from Git.

## Benchmark design

```text
Repository state
      |
      v
Dependency manifest upgrade
      |
      v
Agent-authored repository repair
      |
      v
Hidden test patch + verifier
      |
      v
Pass / non-pass outcome
```

Each task under `dataset/tasks/<task>/` contains:

| Path | Role | Agent visibility |
|---|---|---|
| `instruction.md` | Task prompt | Visible |
| `task.toml` | Docker image, resources, and verifier timeout | Harness |
| `environment/patches/manifest.patch` | Dependency upgrade applied during setup | Hidden |
| `solution/code.patch` | Oracle source repair | Hidden |
| `solution/manifest.patch` | Oracle dependency manifest patch | Hidden |
| `solution/solve.sh` | Oracle application helper | Hidden |
| `tests/test.patch` | Optional held-out test patch | Hidden |
| `tests/test.sh` | Verifier command | Hidden |
| `tests/test_state.py` | Verifier state helper | Hidden |

Some build- or compile-only witnesses do not require `tests/test.patch`.
Task Docker images are referenced from `task.toml` as
`idk233333/depbench-task-images:<task-folder>`.

## Evaluation protocol

1. Select a task from `dataset/task_summary.json`.
2. Start the repository state provided by the task Docker image.
3. Apply `environment/patches/manifest.patch`.
4. Give the agent only the working repository and `instruction.md`.
5. Keep `solution/` and `tests/` unavailable to the agent.
6. Apply `tests/test.patch` when present, then run `tests/test.sh`.
7. Record `1.0` for pass and `0.0` for non-pass. Rows without a valid reward
   remain `no_reward`.

## Release artifacts

| Path | Contents |
|---|---|
| [`trajectories/`](trajectories/) | Gzip JSONL trajectory exports for the 10 harness/model configurations |
| [`verify_logs/`](verify_logs/) | Verifier stdout and CTRF exports aligned with trajectory rows |
| [`results/`](results/) | Configuration summaries, final per-task outcomes, and targeted reruns |
| [`analysis/`](analysis/) | Ecosystem results, coverage, repository metadata, and trajectory scans |
| [`repro/`](repro/) | Download, validation, image, verifier, Harbor, and analysis helpers |
| [`custom_agents/`](custom_agents/) | Harbor adapters used by the example configurations |
| [`MANIFEST.json`](MANIFEST.json) | Machine-readable release and dataset provenance |

### Result files

| File | Purpose |
|---|---|
| `results/summary.{csv,json}` | Configuration-level pass, fail, and no-reward counts |
| `results/final_per_task_outcomes.csv` | Final outcomes after applying 111 targeted reruns |
| `results/targeted_runtime_exception_reruns_203.csv` | Targeted runtime-exception rerun records |
| `results/per_trial_results.jsonl.gz` | Compact metadata for all 2,030 reported trials |
| `analysis/ecosystem_results.csv` | Results by configuration and ecosystem |
| `analysis/coverage.csv` | Trajectory and verifier-log coverage |
| `analysis/trajectory_scan_*` | Rule-based trajectory scan outputs |

### Repository metadata

`analysis/repository_metadata.{csv,json}` records repository URLs, licenses,
primary languages, archive status, and task counts for the 159 source
repositories. `analysis/task_repository_metadata.csv` provides the corresponding
task-level mapping.

The source repositories use different licenses, including open-source,
source-available, custom, and undeclared terms. Review the license recorded for
each source repository before redistribution or other use.

## Reproduction

Common workflows are available as focused helpers:

| Goal | Command or guide |
|---|---|
| Download the benchmark | `python3 repro/download_benchmark.py` |
| Validate the release | `python3 repro/validate_release.py` |
| Pull all task images | `bash repro/pull_task_images.sh` |
| Verify one oracle solution | `bash repro/run_oracle_solution.sh <task>` |
| Verify a candidate patch | `bash repro/run_patch_verifier.sh <task> <patch>` |
| Scan released trajectories | `python3 repro/scan_trajectories.py` |
| Run with Harbor | [`repro/HARBOR.md`](repro/HARBOR.md) |
| Read the full reproduction guide | [`repro/README.md`](repro/README.md) |

Harbor configuration templates for every reported configuration are under
[`repro/examples/`](repro/examples/).

## Artifact formats

<details>
<summary><strong>Trajectory rows</strong></summary>

`trajectories/*.jsonl.gz` contains one row per reported trial with:

- `task`, `trial`, `harness`, `llm`, and `model`
- `reward` and `exception_type`
- `has_trajectory`
- an ATIF-like `trajectory` object when available

Some rows intentionally use `has_trajectory=false`: their reward and verifier
log are retained, but no recoverable agent trajectory was available.

</details>

<details>
<summary><strong>Verifier rows</strong></summary>

`verify_logs/*.jsonl.gz` follows the same configuration naming and row alignment
as `trajectories/`. Each row includes trial metadata, reward text, verifier
stdout as `verifier_test_stdout`, and CTRF JSON as `verifier_ctrf` when
available.

Coverage is summarized in `verify_logs/index.{csv,json}`.

</details>

## Release integrity

<details>
<summary><strong>Test-contract audit (July 14, 2026)</strong></summary>

Thirty-seven semantic or mixed test-contract findings were reviewed
individually:

| Decision | Tasks |
|---|---:|
| Repaired | 8 |
| Repackaged around a clean dependency witness | 13 |
| Removed as invalid | 16 |

The decision table is available in
`analysis/test_contract_repair_decisions_2026-07-14.{md,csv}`. The 16 invalid
tasks were removed from the benchmark, all 10 trajectory and verifier-log
files, per-trial results, analysis tables, and Harbor example configurations.
Historical rewards for retained observations were not changed; aggregate
counts and rates were recomputed over the 203 retained tasks.

</details>

<details>
<summary><strong>Maven verifier environments (July 13, 2026)</strong></summary>

Fifty-seven Maven task verifiers were hardened after an audit found guarded
task images whose configuration had lost `JAVA_HOME` and Java on `PATH`. The
verifiers now restore `JAVA_HOME`, `PATH`, `MAVEN_HOME`, and `MAVEN_CONFIG`
explicitly without changing existing filesystem layers.

Old and new image digests are recorded in
`repro/java_home_image_repair_2026-07-13.csv`. Historical rows preserve their
original observations; cells affected by the missing Java environment must be
replayed before interpreting cross-configuration Maven results.

</details>

## Release policy

The `main` branch contains reported artifacts and reproduction helpers.
Directory-format benchmark contracts are versioned on
[Hugging Face](https://huggingface.co/datasets/ZijiantheJack/DepBench) and
downloaded on demand. Pin both the Git commit and the Hugging Face revision for
reproducible experiments.

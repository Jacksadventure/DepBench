> [!IMPORTANT]
> **Paper-review branch.** The self-contained [paper-review artifact](paper_review/README.md)
> contains the paper's **203 tasks and 2,030 matching trajectories** from 10
> configurations, with outcomes and verifier logs. It preserves historical runs;
> it is not a new evaluation of the source-build release. 
> `paper_review/dataset/` with `paper_review/trajectories/` for paper review.
>
> New [failure-root-cause annotation](paper_review/README.md#failure-root-cause-annotation)
> defaults to **all 10 configurations**, not only Gemini + OpenCode.

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/depbench-logo-dark.svg">
  <img alt="DepBench" src="assets/depbench-logo.svg" width="460">
</picture>

**A repository-level benchmark for dependency-upgrade repair by coding agents**

<p>
  <a href="https://huggingface.co/datasets/Depbench/build_from_source/tree/3eef955c222baa310ef039153755ec9d7cdb03f3">
    <img alt="Hugging Face dataset" src="https://img.shields.io/badge/Hugging%20Face-Dataset-FFD21E?style=flat-square">
  </a>
  <img alt="201 tasks" src="https://img.shields.io/badge/tasks-201-2E8B57?style=flat-square">
  <img alt="157 repositories" src="https://img.shields.io/badge/repositories-157-3B82F6?style=flat-square">
  <img alt="5 ecosystems" src="https://img.shields.io/badge/ecosystems-5-8B5CF6?style=flat-square">
  <img alt="contract-clean release" src="https://img.shields.io/badge/release-contract--clean-343A40?style=flat-square">
</p>

[Quick Start](#quick-start) &middot;
[Benchmark Design](#benchmark-design) &middot;
[Evaluation Protocol](#evaluation-protocol) &middot;
[Artifacts](#release-artifacts) &middot;
[Reproduction](#reproduction) &middot;
[Governance](#project-governance)

</div>

---

DepBench evaluates whether coding agents can repair repository-level breakages
caused by dependency upgrades. Its tasks originate from real merged Dependabot
and Renovate pull requests and span npm/yarn, Maven, Go modules, Cargo, and pip.
DepBench uses the
[Harbor framework](https://github.com/harbor-framework/harbor) as its evaluation
harness for running agents, building isolated task environments, invoking
verifiers, and collecting trial results.

The contract-clean source snapshot retains 203 valid tasks from the original
219-task snapshot.

> [!IMPORTANT]
> `solution/` and `tests/` are published for reproducibility. Keep both
> directories hidden from agents during evaluation.

## At a glance

| Tasks | Source repositories | Ecosystems |
|---:|---:|---:|
| **201** | **157** | **5** |

## Quick start

DepBench release helpers require Python 3.12 or newer.

Install the release helpers, download the pinned 201-task snapshot from
Hugging Face, and validate the benchmark:

```bash
python3 -m pip install .
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
[`MANIFEST.json`](MANIFEST.json). The archive directly contains the 201-task
`main` dataset; the two license-excluded tasks listed below are not packaged.
The downloaded `dataset/` directory is excluded from Git.

### License-excluded tasks

The `main` branch does not directly distribute the following task packages
because of their upstream repository licensing status:

| Repository | Dependency upgrade | Upstream pull request |
|---|---|---|
| `databricks/cli` | `github.com/databricks/databricks-sdk-go` 0.36.0 to 0.37.0 | [databricks/cli#1326](https://github.com/databricks/cli/pull/1326) |
| `nearform/brokeneck` | `react-router-dom` 5.2.0 to 6.4.1 | [nearform/brokeneck#820](https://github.com/nearform/brokeneck/pull/820) |

Users may inspect those upstream pull requests and independently reconstruct
or attempt the upgrades, subject to the upstream repositories' terms. Neither
task is included in the 201-task dataset materialized by the `main` branch.

## Benchmark design

<picture>
  <source media="(prefers-color-scheme: dark) and (max-width: 640px)" srcset="assets/benchmark-flow-mobile-dark.svg">
  <source media="(max-width: 640px)" srcset="assets/benchmark-flow-mobile.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/benchmark-flow-dark.svg">
  <img alt="Repository state flows through dependency manifest upgrade, agent-authored repository repair, hidden test patch and verifier, and a pass or non-pass outcome." src="assets/benchmark-flow.svg" width="1120">
</picture>

Each task under `dataset/tasks/<task>/` contains:

| Path | Role | Agent visibility |
|---|---|---|
| `instruction.md` | Task prompt | Visible |
| `task.toml` | Resources and verifier timeout | Harness |
| `environment/Dockerfile` | Clone the upstream repository, checkout the fixed base commit, and bootstrap dependencies | Harness |
| `environment/patches/manifest.patch` | Dependency upgrade applied during setup | Hidden |
| `solution/code.patch` | Oracle source repair | Hidden |
| `solution/manifest.patch` | Oracle dependency manifest patch | Hidden |
| `solution/solve.sh` | Oracle application helper | Hidden |
| `tests/test.patch` | Optional held-out test patch | Hidden |
| `tests/test.sh` | Verifier command | Hidden |
| `tests/test_state.py` | Verifier state helper | Hidden |

Some build- or compile-only witnesses do not require `tests/test.patch`.
There are no prebuilt task-image references in the release. Harbor builds each
task locally from `environment/Dockerfile`; each Dockerfile clones the
repository URL and checks out the immutable commit recorded in
`analysis/task_source_builds.{csv,json}`.

## Evaluation protocol

1. Select a task from `dataset/task_summary.json`.
2. Build `environment/Dockerfile`, which clones and checks out the task's fixed
   base commit.
3. Apply `environment/patches/manifest.patch`.
4. Give the agent only the working repository and `instruction.md`.
5. Keep `solution/` and `tests/` unavailable to the agent.
6. Apply `tests/test.patch` when present, then run `tests/test.sh`.
7. Record `1.0` for pass and `0.0` for non-pass. Rows without a valid reward
   remain `no_reward`.

## Release artifacts

| Path | Contents |
|---|---|
| [`analysis/`](analysis/) | Task-contract audits, dependency metadata, repository metadata, and static task classifications |
| [`repro/`](repro/) | Download, validation, image, verifier, Harbor, and benchmark-audit helpers |
| [`custom_agents/`](custom_agents/) | Harbor adapters used by the example configurations |
| [`assets/`](assets/) | DepBench brand assets and responsive benchmark flow diagrams |
| [`MANIFEST.json`](MANIFEST.json) | Machine-readable release and dataset provenance |
| [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) | Third-party data, software, and exceptional-license inventory |
| [`NOTICE.txt`](NOTICE.txt) | Distribution-level third-party notice and attribution pointers |
| [`OPEN_SOURCE_RELEASE_CHECKLIST.md`](OPEN_SOURCE_RELEASE_CHECKLIST.md) | Repository checks and outstanding Microsoft approval steps |

### Audit files

| File | Purpose |
|---|---|
| `analysis/dependency_metadata_corrections_2026-07-26.{md,csv}` | Human-readable and machine-readable audit of 44 corrected package/version metadata rows |
| `analysis/bot_pr_dependency_audit_2026-07-26.{md,csv}` | Cross-check of those 44 rows against merged Dependabot/Renovate PR declarations and final diffs |
| `analysis/instruction_bump_audit_201.{md,csv,json}` | Per-task audit of all 201 distributed Bump instructions against packaged manifests and upstream PR metadata |
| `analysis/task_source_builds.{csv,json}` | Repository URL, fixed base commit, base-image reference, Dockerfile path, and Dockerfile checksum for every task |
| `analysis/base_image_digests.json` | Immutable manifest digest for all 41 language base images |
| `analysis/source_build_audit_201.{csv,json}` | Per-task local build, runtime toolchain, checkout, and clean-worktree validation |
| `analysis/source_build_audit_201.md` | Source-build audit method, adjustments, and result summary |
| `analysis/source_commit_audit_201.{csv,json}` | Per-task Git fetch validation for every canonical repository URL and base commit |
| `analysis/test_patch_behavior_classification_201.csv` | Static held-out test-patch behavior labels and size metrics for the 201 distributed tasks |
| `analysis/task_change_mechanism_*` | Direct/indirect dependency-upgrade mechanism labels and taxonomy for all 201 distributed tasks |
| `analysis/test_contract_repair_decisions_2026-07-14.{md,csv}` | Contract-audit decisions for the 36 reviewed tasks retained in main metadata |

### Repository metadata

`analysis/repository_metadata.{csv,json}` records repository URLs, licenses,
primary languages, archive status, and task counts for the 157 distributed
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
| Build all task images locally | `bash repro/build_task_images.sh` |
| Verify one oracle solution | `bash repro/run_oracle_solution.sh <task>` |
| Verify a candidate patch | `bash repro/run_patch_verifier.sh <task> <patch>` |
| Run with Harbor | [`repro/HARBOR.md`](repro/HARBOR.md) |
| Read the full reproduction guide | [`repro/README.md`](repro/README.md) |

Harbor configuration templates for every reported configuration are under
[`repro/examples/`](repro/examples/).

## Licensing and third-party content

Microsoft-authored source code, documentation, and DepBench brand assets in
this repository are licensed under the [MIT License](LICENSE.txt). Benchmark
tasks, source excerpts, patches, and other material originating from
third-party repositories are not relicensed under
that MIT license. The MIT license does not grant trademark rights.

The complete source-repository and detected-license mapping is available in
`analysis/repository_metadata.{csv,json}` and
`analysis/task_repository_metadata.csv`. Of the 201 distributed tasks, 192 are
classified as originating from open-source repositories and 9 use
source-available or custom terms. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) before redistribution or use.

## Data, privacy, and network notice

DepBench-owned helper code does not implement telemetry collection. Commands
in this repository can make outbound requests to Hugging Face, GitHub, Docker
registries, package registries, task-selected dependency sources, and
configured model providers. Third-party tools may have their own telemetry and
privacy behavior.

Authentication values must be supplied at runtime through environment
variables or another approved secret-injection mechanism. Generated example
configs intentionally contain an empty `env` object and must not be committed
after credentials are added.

## Project governance

- Contributions: [CONTRIBUTING.md](CONTRIBUTING.md)
- Security reporting: [SECURITY.md](SECURITY.md)
- Code of Conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Support: [SUPPORT.md](SUPPORT.md)
- Release review: [OPEN_SOURCE_RELEASE_CHECKLIST.md](OPEN_SOURCE_RELEASE_CHECKLIST.md)

The repository includes technical release preparation, but does not itself
prove completion of Open Source Portal, OSSOM CELA, Open Data, privacy, SDL,
Responsible AI, trademark, or supply-chain approvals.


## Release policy

The `main` branch contains benchmark metadata and reproduction helpers.
Directory-format benchmark contracts are versioned on
[Hugging Face](https://huggingface.co/datasets/Depbench/build_from_source/tree/3eef955c222baa310ef039153755ec9d7cdb03f3) and
downloaded on demand; the `main` downloader enforces the license exclusions
documented above. Pin both the Git commit and the Hugging Face revision for
reproducible experiments.

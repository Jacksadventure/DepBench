---
license: other
task_categories:
  - text-generation
language:
  - code
tags:
  - software-engineering
  - code-agents
  - dependency-upgrade
  - repository-level
  - benchmark
pretty_name: DepBench
size_categories:
  - n<1K
---

# DepBench

DepBench is a repository-level benchmark for dependency-upgrade repair by
coding agents. This source-build snapshot contains **201 tasks** from **157
repositories** across npm/yarn, Maven, Go modules, Cargo, and pip.

## Source-Build Tasks

Every task includes `environment/Dockerfile`. The Dockerfile:

1. pulls an ecosystem base image pinned by manifest digest;
2. clones the task's upstream repository;
3. checks out a fixed 40-character Git commit;
4. bootstraps project dependencies;
5. restores a clean Git worktree; and
6. exposes the compiler and package manager to Harbor login shells.

The dataset does not depend on prebuilt task images.

## Directory Layout

```text
dataset/
  task_summary.json
  tasks/
    <owner>__<repo>__<pull-request>/
      instruction.md
      task.toml
      environment/
        Dockerfile
        patches/
          manifest.patch
      solution/
        code.patch
        manifest.patch
        solve.sh
      tests/
        test.patch
        test.sh
        test_state.py
analysis/
  base_image_digests.json
  task_source_builds.csv
  task_source_builds.json
  source_build_audit_201.csv
  source_build_audit_201.json
  source_commit_audit_201.csv
  source_commit_audit_201.json
```

`analysis/task_source_builds.*` records the repository URL, base commit,
base-image reference, and Dockerfile checksum for every task.
`analysis/source_build_audit_201.*` records the individual local-build,
toolchain, checkout, and clean-worktree checks.
`analysis/source_commit_audit_201.*` independently verifies that every recorded
base commit remains fetchable from its canonical repository URL.

## Evaluation Use

For each task:

1. Build `environment/Dockerfile`.
2. Apply `environment/patches/manifest.patch`.
3. Give only the working repository and `instruction.md` to the agent.
4. Keep `solution/` and `tests/` hidden from the agent.
5. Apply `tests/test.patch` when present and run `tests/test.sh`.

The `solution/` and `tests/` directories are published for reproducibility.
Exposing either directory to the agent invalidates the evaluation protocol.

## License Exclusions

This snapshot does not package `databricks__cli__1326` or
`nearform__brokeneck__820`. Their upstream pull requests remain available for
users who independently reconstruct those tasks subject to the repositories'
terms.

## Licenses

The source repositories use different licenses. Review
`analysis/repository_metadata.*` and `analysis/task_repository_metadata.csv`
before redistribution or use. Source code cloned while building a task remains
subject to its upstream repository's license.

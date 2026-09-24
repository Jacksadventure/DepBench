# DepBench paper-review artifact

This directory contains **203 tasks and 2,030 matching final selected
trajectories**, covering 10 model-harness configurations. All trajectory,
outcome, and verifier-log files use the same 203-task cohort.

The branch is based on `main` at
`c320122f1f76645cd348150a2839e973f36764fa`. The latest main implementation,
source-build helpers, and 201-task distribution metadata remain unchanged;
this directory is a separate artifact for reviewing the paper's experiments.

## Contents

| Path | Contents |
|---|---|
| `dataset/task_summary.json` | Index of the 203 review tasks |
| `dataset/tasks/` | Instructions, task metadata, hidden patches, and verifiers |
| `trajectories/` | Ten gzip JSONL files, each with 203 final selected trajectories |
| `results/final_per_task_outcomes.csv` | 2,030 final configuration-task outcomes |
| `results/summary.csv` | Per-configuration results with the 203-task denominator |
| `results/*reruns_203.csv` | Historical rerun records and replacement provenance |
| `verify_logs/` | Ten gzip JSONL files aligned with the selected trajectories |
| `analysis/release_redactions_2026-07-23.csv` | Historical trajectory redaction record |
| `MANIFEST.json` | Source commits, pinned dataset revision, and cohort boundaries |

## Provenance and interpretation

The experiment artifacts come from
`5db2628a0f43fc81b67e4eb0ca289241748c1cc7` (2026-08-02), immediately before
experimental artifacts were removed from main. The task snapshot comes from
`9750bc95f5d0830059346fb1b3f6c947e40cb7d9`, with its archive and Hugging Face
revision pinned in this directory's manifest.

These are **historical runs, not new agent executions**. Original and rerun
trials are distinguished by `outcome_source`, `source_job`, `trajectory_source`,
and the per-task outcome table. The final selected trial, task, and reward must
match across trajectory, result, and verifier-log records.

Task instructions in the packaged review snapshot use the normalized template.
Historical trajectories retain the instructions actually shown during each run;
some earlier runs predate prompt normalization. Do not infer that every stored
trajectory was generated with the latest prompt or the main source-build
environment. Matching task IDs establishes cohort alignment, not identical
execution environments or proof of a complete normalized-prompt rerun.

## Review

Run these commands from the repository root:

```bash
python3 repro/validate_paper_review.py

python3 repro/read_trial.py \
  --artifact-root paper_review \
  --configuration gpt55__codex \
  --task harvard-lil__js-wacz__41
```

Add `--show-trajectory` or `--show-verifier` to inspect the corresponding record.
The files are ordinary gzip-compressed JSONL and can also be read with Python's
`gzip` and `json` modules.

The paper-review dataset is committed in this directory; it does not require
downloading the separate 201-task main dataset. The normal
`repro/download_benchmark.py` and `repro/validate_release.py` commands continue
to refer to that main distribution, not to this historical review cohort.

## Task membership and licensing

The 203-task paper cohort includes `databricks__cli__1326` and
`nearform__brokeneck__820`. Main's later 201-task distribution excluded these
because the former has a custom repository license and the latter has no
declared repository-level license. They and their run records are retained here
to preserve the paper's original denominator and exact task-trajectory alignment.

This review branch does not grant new redistribution rights or change upstream
terms. Review and sharing must comply with the original repositories' terms;
this is not a replacement for the 201-task redistributable release.

Keep `solution/` and `tests/` hidden from agents in any new evaluation. Published
trajectories may expose repairs and must never be supplied as agent input.

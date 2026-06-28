# Handoff Note — 261322 · gpt · complete-grid-jobs

## Inherited context

Continued `conversations/260626-harbor-job-retrieval/`. Prior note
`261304-gpt-complete-harbor-jobs.md` recorded that `harbor-jobs-useful.7z` had
been extracted into local `harbor_jobs/`, adding many trajectory/result
artifacts while preserving the project convention that `harbor_jobs/` remains
uncommitted run output.

## Work done this session

- [x] Located the paper's benchmark grid in `paper/conference_101719.tex`.
- [x] Identified the grid source summary:
  `harbor_benchmark/reports/v4_with_test219_summary_2026-06-23.json`.
- [x] Joined reported job names from the summary to local
  `harbor_jobs/<job>/result.json` UUIDs where available.
- [x] Checked the relevant per-task CSVs that preserve trial ids for rows whose
  full local job directory is not present.
- [x] Wrote a provenance note:
  `harbor_benchmark/reports/paper_benchmark_grid_harbor_jobs_2026-06-26.md`.
- [x] Verified that all UUIDs written in the note match local result JSON files.

## Current state

One new report file was added:

| File | Change |
| --- | --- |
| `harbor_benchmark/reports/paper_benchmark_grid_harbor_jobs_2026-06-26.md` | Maps each completed paper grid cell to Harbor job name(s), local result UUIDs when present, and per-task CSV evidence sources. |

Important findings:

- The paper grid is the current curated v4-with-test219 grid: 8 completed
  agent/model cells, each over 219 tasks.
- Several cells are composites of clean205 plus hard14 jobs; this is intentional
  and recorded in `source_segments` in the summary JSON.
- Some job directories referenced by the paper summary are not present under
  local `harbor_jobs/` and were not found inside `harbor-jobs-useful.7z`.
  Their retained provenance is the checked-in summary/per-task CSV rows.
- Local UUIDs were available for 10 job names and were verified against
  `harbor_jobs/<job>/result.json`.

Commands/checks run:

- `rg` over `paper/` to locate benchmark tables.
- `jq` over `harbor_benchmark/reports/v4_with_test219_summary_2026-06-23.json`
  and local job `result.json` files.
- Python join from summary job names to local result UUIDs.
- `find` searches under `/home/v-runzhihe`, `/data/hrz`, and `/tmp` for missing
  `result.json` paths.
- `7z l harbor-jobs-useful.7z` grep for missing job names.
- A final Python check comparing UUIDs in the note to local job result ids.

## Open tasks for the next agent

1. If exact Harbor UUIDs are needed for missing job directories, retrieve those
   original job folders from the remote machine/archive source. Missing names
   are listed in the "Local Search Notes" section of the new report.
2. If the paper needs an appendix footnote, cite the new provenance report and
   the per-task CSVs rather than embedding long job lists in the LaTeX body.

## Key decisions

| Decision | Rationale |
| --- | --- |
| Added a separate provenance note instead of editing the paper | The user asked to locate job ids; a report artifact is easier to audit and avoids disturbing paper prose/tables. |
| Recorded "not present locally" explicitly | The checked-in summaries contain job names and trial ids, but local UUIDs require the original `result.json`; inventing UUIDs would corrupt provenance. |
| Left unrelated untracked files alone | The worktree already contains many untracked artifacts from earlier sessions; project convention says not to revert unrelated changes. |

## Blockers

- Some reported Harbor job directories are absent locally, so their Harbor
  result UUIDs could not be recovered from `result.json`.

## Suggested next step

Use `harbor_benchmark/reports/paper_benchmark_grid_harbor_jobs_2026-06-26.md`
as the source map; retrieve the missing job directories only if reviewers need
Harbor result UUIDs rather than job names plus per-task trial ids.

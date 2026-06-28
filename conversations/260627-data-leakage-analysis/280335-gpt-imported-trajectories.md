# Handoff Note — 280335 · gpt · imported-trajectories

## Inherited context

Read `conversations/260627-data-leakage-analysis/271034-claude-planned-leakage-analysis.md` and `271117-claude-drafted-annotation-protocol.md`.

Locked decisions inherited:

- Trajectory analysis supports leakage, RQ4 discovery behavior, pass-alignment, and failure-mode analysis.
- `harbor_benchmark/trajectory_exports/v4_withtest219_20260627/*.jsonl.gz` is the current trajectory corpus.
- `gemini35flash__opencode` has no analyzable trajectories and should be reported as missing/not analyzable.
- Do not conflate dependency-doc access with leakage; only own-project PR/repo/fix access is leakage.

Important correction from this session:

- The export files are containers, not proof that every embedded trajectory is canonical Harbor ATIF. `trajectory_source="existing"` rows preserve source `agent/trajectory.json`; `trajectory_source="converted"` rows are lightweight ATIF-compatible conversions produced by `scripts/export_llm_harness_trajectories.py`.

## Work done this session

- [x] Inspected `harbor_benchmark/trajectory_exports/v4_withtest219_20260627/` and confirmed the archive-to-job mapping is row-local: `source_job` + `trial` + `task`.
- [x] Read `scripts/traj_export.py`; it uses Harbor agent parser classes and `format_trajectory_json`, but the current Python environment cannot assume the `harbor` package is importable and the raw logs referenced in exports are not local.
- [x] Read `scripts/export_llm_harness_trajectories.py`; it preserves existing Harbor trajectories when present and otherwise emits lightweight ATIF-compatible conversions for raw logs.
- [x] Added `scripts/import_trajectory_exports_to_harbor_jobs.py`, a cautious importer that skips missing trajectories, writes only embedded trajectory objects, and adds provenance sidecars.
- [x] Ran the importer with `--write`, placing available trajectories at `harbor_jobs/<source_job>/<trial>/agent/trajectory.json`.
- [x] Verified counts against `index.csv`.

## Current state

| File / path | Change |
| --- | --- |
| `scripts/import_trajectory_exports_to_harbor_jobs.py` | New importer. Dry-run by default; `--write` imports; `--overwrite` required to replace existing files. |
| `harbor_jobs/<source_job>/<trial>/agent/trajectory.json` | 2,403 ignored artifact files written from embedded trajectories. |
| `harbor_jobs/<source_job>/<trial>/agent/trajectory_export_meta.json` | 2,403 ignored provenance sidecars written. |

Import totals:

| Classification | Count | Meaning |
| --- | ---: | --- |
| `existing` | 1,093 | Preserved from source Harbor `agent/trajectory.json`. |
| `converted` | 1,310 | Lightweight converter output from `scripts/export_llm_harness_trajectories.py`. |
| `missing` | 225 | No embedded trajectory; no placeholder was written. |

Per-group verification matched `index.csv`:

- `gpt55/codex`: 219 imported, all existing.
- `gpt55/copilot_cli`: 216 imported, all converted; 3 missing.
- `gpt55/opencode`: 219 imported, all existing.
- `gpt55/claude_code`: 219 imported, all converted.
- `gemini35flash/codex`: 219 imported, all existing.
- `gemini35flash/copilot_cli`: 219 imported, all converted.
- `gemini35flash/opencode`: 0 imported; 219 missing.
- `gemini35flash/claude_code`: 219 imported, all converted.
- `claude48/codex`: 217 imported, all existing; 2 missing.
- `claude48/copilot_cli`: 219 imported, all converted.
- `claude48/opencode`: 219 imported, all existing.
- `claude48/claude_code`: 218 imported, all converted; 1 missing.

Validation commands run:

- `python scripts/import_trajectory_exports_to_harbor_jobs.py`
- `python scripts/import_trajectory_exports_to_harbor_jobs.py --write`
- `python -m py_compile scripts/import_trajectory_exports_to_harbor_jobs.py`
- Count checks comparing `harbor_jobs/<source_job>/*/agent/trajectory.json` against `index.csv`.
- Sample sidecar checks for one `existing` row and one `converted` row.

## Open tasks for the next agent

1. Decide whether downstream annotation should accept `converted` rows as analyzable, or restrict stricter claims to `existing` rows only. The sidecar field `import_classification` supports this filter.
2. If truly canonical Harbor parser output is required for `converted` rows, recover the original raw log directories from `/Data2/v-zijianluo/depbot_v4_with_tests/harbor_jobs/...` or another source machine; they are not present locally.
3. If `harbor view` compatibility is required, add a second importer mode that synthesizes or restores `config.json` / `result.json`. The current importer intentionally writes only trajectory paths and provenance, not full Harbor job metadata.
4. Build the annotation-bundle generator around `harbor_jobs/<source_job>/<trial>/agent/trajectory.json` plus `trajectory_export_meta.json`, `task`, `reward`, and oracle patches.

## Key decisions

| Decision | Rationale |
| --- | --- |
| Preserve `existing` vs `converted` in sidecar metadata | User warned that not all JSONL data is ATIF; provenance prevents accidental overclaiming. |
| Skip `missing` rows entirely | A placeholder `trajectory.json` would be misleading for leakage and RQ4 annotation. |
| Do not synthesize full Harbor job/trial `config.json` and `result.json` | The exports contain enough for trajectory analysis, but not enough to recreate authoritative Harbor run metadata honestly. |
| Use `source_job` as the import job id | This is the stable mapping in each export row; older `raw_log_path` job names are provenance only. |

## Blockers

- Raw logs are not local: every sampled `raw_log_path` points under `/Data2/v-zijianluo/...` and does not exist on this machine.
- `gemini35flash__opencode` has no embedded trajectories.

## Suggested next step

Use `trajectory_export_meta.json` to filter/analyze `existing` and `converted` rows separately while building the per-trial annotation bundles.

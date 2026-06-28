# Handoff Note — 280353 · gpt · removed-export-meta

## Inherited context

Continued reconstructed trajectory/job viewer work from:

- `conversations/260627-data-leakage-analysis/280344-gpt-reconstructed-viewer-metadata.md`
- `conversations/260627-data-leakage-analysis/280347-gpt-fixed-viewer-datetimes.md`
- `conversations/260627-data-leakage-analysis/280350-gpt-fixed-exception-schema.md`

The user noticed `trajectory_export_meta.json` files had reappeared after the importer was rerun with `--overwrite`.

## Work done this session

- [x] Confirmed 2,403 `harbor_jobs/<job>/<trial>/agent/trajectory_export_meta.json` files existed.
- [x] Deleted all of them with a depth-limited `find`.
- [x] Patched `scripts/import_trajectory_exports_to_harbor_jobs.py` so it no longer writes sidecar `trajectory_export_meta.json` files.
- [x] Removed the now-unused `meta_for()` helper from the importer.
- [x] Re-ran the importer with `--write --write-metadata --overwrite` to confirm sidecars are not recreated.
- [x] Validated all 12 exported job roots and all 2,628 trial results with Harbor's installed Pydantic models.

## Current state

| Path | State |
| --- | --- |
| `harbor_jobs/**/agent/trajectory_export_meta.json` | Count is `0`. |
| `scripts/import_trajectory_exports_to_harbor_jobs.py` | No longer writes export-meta sidecars. |
| `result.json.agent_result.metadata` | Still contains provenance (`llm`, `harness`, `trajectory_source`, `has_trajectory`, `source_job`, source/raw paths). |

Validation:

- `find harbor_jobs -maxdepth 4 -path '*/agent/trajectory_export_meta.json' -type f | wc -l` -> `0`
- `python -m py_compile scripts/import_trajectory_exports_to_harbor_jobs.py`
- Re-run importer once after patch; sidecar count stayed `0`.
- Harbor-model validation:
  - `roots = 12`
  - `trials = 2628`
  - `bad = 0`

## Open tasks for the next agent

1. Do not reintroduce `trajectory_export_meta.json`; the user explicitly does not want these files.
2. Use `result.json.agent_result.metadata` for trajectory provenance instead.

## Key decisions

| Decision | Rationale |
| --- | --- |
| Delete sidecars and stop generating them | User requested no export-meta files; provenance is already embedded in trial result metadata. |
| Keep provenance in `result.json` | Needed to distinguish `existing` vs lightweight `converted` trajectories without extra files. |

## Blockers

- None.

## Suggested next step

Use Harbor viewer normally; provenance remains visible in the trial result JSON without sidecar files.

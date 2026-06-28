# Handoff Note — 280344 · gpt · reconstructed-viewer-metadata

## Inherited context

Read the earlier trajectory-analysis notes in this thread, especially:

- `conversations/260627-data-leakage-analysis/271034-claude-planned-leakage-analysis.md`
- `conversations/260627-data-leakage-analysis/271117-claude-drafted-annotation-protocol.md`
- `conversations/260627-data-leakage-analysis/280335-gpt-imported-trajectories.md`

The user then asked to convert imported trajectory metadata into real Harbor job-style `config.json` / `result.json` files so the jobs can be inspected with `harbor view`, and to recover root job summaries from the summary JSON previously noticed.

## Work done this session

- [x] Compared real Harbor job files at `harbor_jobs/2026-06-25__13-51-04/config.json`, root `result.json`, and `actix__actix__554__jBoaznY/{config,result}.json`.
- [x] Located the summary sources:
  - `harbor_benchmark/trajectory_exports/v4_withtest219_20260627/index.json`
  - `harbor_benchmark/reports/v4_with_test219_summary_2026-06-23.json`
  - `harbor_benchmark/reports/v4_withtest219_result_directory_map_20260627.json`
- [x] Extended `scripts/import_trajectory_exports_to_harbor_jobs.py` with `--write-metadata`.
- [x] Wrote Harbor-shaped `config.json` and `result.json` at every reconstructed job root and trial directory.
- [x] Preserved the trajectory provenance distinction: `existing` vs `converted` remains in `agent/trajectory_export_meta.json` and trial `result.json.agent_result.metadata`.
- [x] Ran a Harbor viewer smoke test on `harbor_jobs/v4_withtest219__codex__gpt55__full219_20260627`.

## Current state

| Path | State |
| --- | --- |
| `scripts/import_trajectory_exports_to_harbor_jobs.py` | Now imports trajectories and can reconstruct viewer metadata with `--write --write-metadata`. |
| `harbor_jobs/<source_job>/config.json` | Reconstructed for all 12 trajectory-export jobs. |
| `harbor_jobs/<source_job>/result.json` | Reconstructed for all 12 trajectory-export jobs, with pass/fail/no-reward matching `index.csv`. |
| `harbor_jobs/<source_job>/<trial>/config.json` | Reconstructed for all 2,628 trial rows. |
| `harbor_jobs/<source_job>/<trial>/result.json` | Reconstructed for all 2,628 trial rows. |
| `harbor_jobs/<source_job>/<trial>/agent/trajectory.json` | Still only present where the export embedded a trajectory: 2,403 files. Missing-trajectory rows do not get fake trajectories. |

Important caveat:

- The new metadata is viewer-compatible reconstruction, not original Harbor runtime metadata. Timing, token counts, costs, exact agent versions, and full exception tracebacks were not present in the compact exports and are therefore `null`, `unknown`, or explicitly marked as recovered from export metadata.

Validation:

- `python -m py_compile scripts/import_trajectory_exports_to_harbor_jobs.py`
- `python scripts/import_trajectory_exports_to_harbor_jobs.py --write --write-metadata`
- `timeout 10s ~/.local/bin/harbor view harbor_jobs/v4_withtest219__codex__gpt55__full219_20260627 --port 8899 --host 127.0.0.1 --no-build`
  - Viewer started and shut down cleanly after timeout.
- Checked all 12 root `result.json` files against `index.csv`; pass/fail/no-reward counts match exactly.
- Parsed 5,280 reconstructed JSON files with `json.loads`; `bad_json = 0`.

Per-group metadata counts:

- All 12 job roots have root `config.json` and `result.json`.
- All 12 groups have 219 trial `config.json` and 219 trial `result.json`.
- Trajectory files remain at original availability:
  - 2,403 present.
  - 225 missing, including all 219 `gemini35flash__opencode` rows.

## Open tasks for the next agent

1. If exact original configs are needed, copy them from the original source job directories where they exist locally. Current reconstructed configs are enough for `harbor view`, but do not preserve every custom agent env/kwarg.
2. If exact exception messages/tracebacks are needed, recover original trial `result.json` from the source paths. The compact export only retained `exception_type`.
3. Start `harbor view harbor_jobs/<source_job>` for whichever group the annotators need to inspect interactively.
4. For annotation, continue to filter by `agent_result.metadata.trajectory_source` or `agent/trajectory_export_meta.json.import_classification` so lightweight converted trajectories are not mistaken for preserved Harbor ATIF.

## Key decisions

| Decision | Rationale |
| --- | --- |
| Reconstruct metadata instead of pretending it is original | The compact trajectory exports omit runtime details. |
| Write trial metadata for missing-trajectory rows too | Harbor viewer and denominator checks need the complete 219-row job shape. |
| Do not create placeholder `agent/trajectory.json` for missing rows | Would mislead trajectory/leakage analysis. |
| Store provenance inside `agent_result.metadata` | Makes the viewer metadata useful without requiring sidecar-only inspection. |

## Blockers

- No blocker for viewer inspection.
- Exact runtime configs/results still require original source job directories if stricter provenance is needed.

## Suggested next step

Open the desired reconstructed job with `harbor view harbor_jobs/<source_job> --port 8899 --no-build` and inspect trial trajectories, using provenance metadata to separate `existing` from `converted`.

# Handoff — 154520 · copilot · drop-list-prune

## Context

User asked to remove all tasks in the drop list from the dataset and push the change. The current authoritative task tree had 228 directories. The current drop list was the 23-task non-clean set from `_run_configs/gpt55_clean205_20260619/drop_current23.json`, matching the non-`WITNESSES_BREAKING_CHANGE` current-task intersection from the 2026-06-18 audit.

## Work done

- Removed 23 drop-list task directories from `harbor_benchmark/tasks_v4/`.
- Regenerated `harbor_benchmark/task_summary.json` from 228 rows to 205 rows by filtering the removed folders.
- Updated `harbor_benchmark/HARNESS.md` top-level snapshot and variant log to describe the new 205-task clean witnessed dataset.
- Validated:
  - `tasks_v4` directory count is 205.
  - `task_summary.json` row count is 205.
  - `task_summary.json` folders exactly match the remaining task directories.
  - All 23 drop-list folders are absent.

## New dataset counts

| Ecosystem | Count |
|---|---:|
| npm/yarn | 79 |
| Maven/Java | 66 |
| Go | 28 |
| Cargo/Rust | 20 |
| Python | 12 |

Metadata schemas: 96 `schema_version = "1.1"` tasks and 109 legacy `version = "1.0"` tasks.

## Notes

- Existing Harbor run outputs and logs remain untracked and should not be committed.
- The earlier GPT-5.5 codex/OpenCode jobs were launched with an explicit 205-task allowlist, so removing the 23 drop-list directories should not remove any task they are scheduled to run.

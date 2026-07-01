# Leakage findings (guarded-synchronized metadata)

Generated: 2026-07-01T00:48:52.496307+00:00

Original annotation files were backed up before guarded synchronization.

- Backup directory: `harbor_benchmark/annotations/v4_withtest219_20260630/backup_before_guarded_sync_20260701`
- Confirmed+both rows: 355
- Confirmed+one-only rows: 15
- Rows with guarded replacement metadata: 330
- Rows marked skipped: 32

Guarded synchronization updates reward/trial provenance for replaced pairs but does not claim the original annotation labels were re-annotated. The leakage labels and findings remain the original annotator judgments unless a future annotation run replaces them.

## Guarded status counts

| Status | Rows |
|---|---:|
| unmodified | 111 |
| replaced | 330 |
| skipped | 32 |

Placeholder rows added to annotation JSONL for guarded replacement pairs that were present in `leakage_findings.csv` but absent from the original annotator JSONL: {"codex.jsonl": 7, "opencode.jsonl": 7}

# Handoff Note — 131619 · gpt · expanded-inventory

## Inherited context

- Continued the harness-quality investigation from `conversations/260713-test-harness-quality/131554-gpt-diagnosed-harness.md`.
- The original note established 44 directly questioned zero-pass tasks but distributed broader task lists across several findings.
- User requested that all problematic cases be listed explicitly in the report.

## Work done this session

- [x] Added `conversations/260713-test-harness-quality/REPORT.md` as the consolidated case inventory.
- [x] Listed all 44 immediately questioned zero-pass tasks with ecosystem, finding, and required action.
- [x] Added the two additional adversarial zero-pass tasks (`nearform__brokeneck__820` and `solana-labs__solana-program-library__4301`) that are not part of the 44-task non-witness/infra/structural union.
- [x] Listed all 122 unique tasks flagged by any evidence screen, including pass count and every applicable flag.
- [x] Preserved category boundaries: oracle-quality problem, no-op exploit, invalid guarded Java verification, structural/scaffolding defect, and adversarial visible/hidden tests.
- [x] Verified the full inventory table contains exactly 122 task rows and `git diff --check` passes.

## Current state

| File | Change |
| --- | --- |
| `conversations/260713-test-harness-quality/REPORT.md` | New consolidated 122-task problem inventory; includes the P0 44-task zero-pass table |
| `conversations/260713-test-harness-quality/131619-gpt-expanded-inventory.md` | This continuation handoff |

No benchmark task, verifier, run configuration, result file, or `HARNESS.md` setting was changed.

## Open tasks for the next agent

1. Use `REPORT.md` as the task queue for remediation; do not treat all 122 rows as deletion candidates.
2. Reverify all 166 `JAVA_HOME`-invalid cells across the 57 listed Maven tasks.
3. Dynamically adjudicate the 50 oracle candidates, starting with the 33 zero-pass rows.
4. Run NOP over all 219 after manifest enforcement; the listed 37 no-op passes are only a lower bound.
5. Repackage nuts-node and actix before including them in further evaluation.

## Key decisions

| Decision | Rationale |
| --- | --- |
| Created `REPORT.md` instead of modifying the prior handoff | Handoff notes are append-only; the user requested a report-level inventory. |
| Included 122 unique tasks | “All problematic cases” includes every task flagged by oracle, NOP, `JAVA_HOME`, structural, or adversarial evidence, not only the 44 zero-pass priority rows. |
| Kept flags separate | A `JAVA_HOME` task has invalid trials but is not automatically a bad task; a NOP-pass task is a harness exploit; an oracle task is a quarantine candidate. |

## Blockers

- None for the inventory itself.
- Final removal/retention decisions still require the dynamic reruns and adjudications described in `REPORT.md`.

## Suggested next step

Fix the guarded Java environment first, then work down the 44-task zero-pass table in `REPORT.md` using the action column.

# Test-patch audit — liquibase__liquibase__2285

## 1. Task summary
- Folder: liquibase__liquibase__2285
- Ecosystem: maven
- Upgrade: h2 1.4.200 -> 2.0.202
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE`

## 2. What is the breaking change?
H2 2.0 changed metadata tables, reserved keywords, type names, and behavior around sequences/indexes/constraints compared with H2 1.4. Liquibase's H2 support must account for new reserved words, `INFORMATION_SCHEMA` differences, `CHARACTER VARYING` type names, `BINARY/CHARACTER LARGE OBJECT`, `DOUBLE PRECISION`, and unique-constraint/index metadata changes.

## 3. What does Δt (test.patch) actually do?
- Updates Ant integration resources for `DatabaseRollbackTaskTest` and `DropAllTaskTest`.
- Renames the test table from `users` to `TEST_USERS` in affected Ant XML/changelog/SQL resources, avoiding an H2 2 keyword-sensitive identifier.
- The verifier runs `-pl liquibase-core -am -Dtest=DatabaseRollbackTaskTest,DropAllTaskTest test` after applying the hidden resources.

## 4. Does Δt directly exercise the breaking change?
Yes. The hidden tests run Liquibase's Ant rollback/drop flows against H2 2.0-era changelog resources. Without Δc, Liquibase still has H2 1.4 assumptions for keywords, type names, and metadata queries; with Δc, H2 2 metadata/type handling is repaired and the targeted tests pass.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt updates the H2-backed integration resources for the post-upgrade database behavior, and the selected Liquibase tests exercise the H2 compatibility repairs in Δc.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc mainly updates Liquibase core H2 handling in production Java code. The two `liquibase-dist` example launcher updates are ancillary.

## 7. Soundness concerns / notes
- Δt is mostly fixture/resource migration rather than new assertions, but it is run by the verifier and exercises real H2 integration paths.
- `test_cmd` is not extracted in batch metadata; `test_state.py` shows the targeted Maven command.

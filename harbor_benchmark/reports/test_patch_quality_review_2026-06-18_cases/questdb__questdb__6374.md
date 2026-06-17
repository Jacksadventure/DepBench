# Test-patch audit — questdb__questdb__6374

## 1. Task summary
- Folder: questdb__questdb__6374
- Ecosystem: maven
- Upgrade: org.postgresql:postgresql 42.7.4 -> 42.7.7
- test_cmd: `mvn ... -pl core -am -Dtest=PGJobContextTest test` (extracted from verifier)

## 2. What is the breaking change?
The newer PostgreSQL JDBC driver expects catalog metadata to be available from the server. QuestDB's PGWire path already had `current_database()`, but not the `current_catalog()` function used by newer catalog/metadata queries. The human source repair adds `CurrentCatalogFunctionFactory`, returning the same constant database name as `current_database()`, and exposes the shared `CurrentDatabaseFunctionFactory.INSTANCE`.

## 3. What does Δt (test.patch) actually do?
`PGJobContextTest` is broadened substantially: many `skipOnWalRun()` / `Assume.assumeFalse(walEnabled)` guards are removed so the PGWire JDBC tests run in more modes. The patch also updates metadata expectations in `testSchemasCall` from null catalog values to `qdb` catalog values for schemas, tables, and columns.

## 4. Does Δt directly exercise the breaking change?
Yes. The verifier runs `PGJobContextTest`, including JDBC metadata paths whose expected output now contains catalog `qdb`. Without the source repair, the upgraded driver/server combination lacks the `current_catalog()` implementation needed to satisfy those catalog queries and metadata expectations.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden test suite exercises PGWire/JDBC catalog metadata after the pgjdbc upgrade; the source repair supplies the missing `current_catalog()` compatibility function.

## 6. Δc nature
REAL_SOURCE_REPAIR — the patch adds a production function factory for `current_catalog()` and adjusts visibility of the existing `current_database()` constant.

## 7. Soundness concerns / notes
- Δt is broad and noisy because it removes many WAL skips, but the catalog expectation changes are directly tied to the new source function.
- The verifier command targets only `PGJobContextTest`, so the witness is concentrated in PGWire metadata behavior rather than the whole QuestDB suite.


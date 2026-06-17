# Test-patch audit — eakmanrq__sqlframe__137

## 1. Task summary
- Folder: eakmanrq__sqlframe__137
- Ecosystem: pip
- Upgrade: `sqlglot` >=24.0.0,<25.10 -> >=24.0.0,<25.11
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `/usr/local/bin/python -m pip install pytest-xdist databricks-sql-connector && /usr/local/bin/python -m pytest "tests/integration/engines/test_int_functions.py::test_convert_timezone[duckdb]" tests/unit/standalone/test_functions.py::test_convert_timezone -x -q`

## 2. What is the breaking change?
The newer sqlglot range provides a native `ConvertTimezone` expression / rendering path. sqlframe’s old `convert_timezone` implementation was marked unsupported for all engines and emitted anonymous `CONVERT_TIMEZONE(...)` calls without casting the timestamp argument, which no longer matches the desired sqlglot output.

## 3. What does Δt (test.patch) actually do?
It expands `test_convert_timezone` expectations. The integration test now accounts for engine-specific timezone-aware datetime results, especially DuckDB. The standalone unit test changes expected SQL from `CONVERT_TIMEZONE(cola, colb)` to `CONVERT_TIMEZONE(cola, CAST(colb AS TIMESTAMP))` and similarly for the three-argument form.

## 4. Does Δt directly exercise the breaking change?
Yes. Even if the DuckDB integration case can be skipped while `convert_timezone` is still marked unsupported, the standalone unit test calls `SF.convert_timezone` directly and expects the new sqlglot native rendering with timestamp casts. Without Δc, the old anonymous-function implementation emits the old SQL and fails the hidden unit assertion.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt distinguishes the old anonymous SQL rendering from the new `expression.ConvertTimezone` implementation, and Δc is required for the targeted unit test to pass.

## 6. Δc nature
MIXED — real source repair in `sqlframe/base/functions.py` plus documentation support-list updates in `docs/duckdb.md` and `docs/snowflake.md`.

## 7. Soundness concerns / notes
- The integration portion is weaker because unsupported-engine metadata can cause skips in unfixed states.
- The standalone SQL-rendering assertion is the strong witness and directly targets the changed implementation.

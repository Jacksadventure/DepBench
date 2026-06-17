# Test-patch audit — eakmanrq__sqlframe__466

## 1. Task summary
- Folder: eakmanrq__sqlframe__466
- Ecosystem: pip
- Upgrade: sqlglot >=24.0.0,<27.7 -> >=24.0.0,<27.8
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `/usr/local/bin/python -m pip install pytest-xdist databricks-sql-connector && /usr/local/bin/python -m pytest "tests/integration/engines/test_int_functions.py::test_date_from_unix_date[duckdb]" tests/unit/standalone/test_functions.py::test_invoke_anonymous -x -q`

## 2. What is the breaking change?
sqlglot 27.8 added native expression support for functions that SQLFrame previously emitted through anonymous calls, notably `DateFromUnixDate`, `Reverse`, `UnixMicros`, and `UnixMillis`. SQLFrame needed to route these helpers through sqlglot expression nodes and enable `date_from_unix_date` for engines where it is now supported.

## 3. What does Δt (test.patch) actually do?
- Relaxes `test_date_from_unix_date` to accept either `datetime.date(1970, 1, 2)` or `datetime.datetime(1970, 1, 2, 0, 0)` for DuckDB.
- Updates `test_invoke_anonymous` comments and ignore list to account for `unix_micros`, then runs the anonymous-function audit over standalone functions.

## 4. Does Δt directly exercise the breaking change?
Yes. The integration test is nominally aimed at `date_from_unix_date`, and the standalone `test_invoke_anonymous` is the stronger discriminator: on P⊕Δm, functions like `date_from_unix_date` still use `invoke_anonymous_function` even though sqlglot can now parse native expressions; with Δc they are converted to `expression.DateFromUnixDate`, `expression.Reverse`, `expression.UnixMicros`, and `expression.UnixMillis`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the verifier includes the anonymous-function audit that fails on the old SQLFrame mappings under sqlglot 27.8 and passes after the source mappings are updated.

## 6. Δc nature
REAL_SOURCE_REPAIR — `sqlframe/base/functions.py` replaces anonymous calls with native sqlglot expression nodes and enables `date_from_unix_date`; docs are also updated to list the newly supported function.

## 7. Soundness concerns / notes
- The `date_from_unix_date[duckdb]` integration assertion alone would be weaker because unsupported-function skip logic can mask failures in SQLFrame tasks.
- Including `test_invoke_anonymous` makes this task materially stronger than similar SQLFrame cases where only a skipped integration test is selected.

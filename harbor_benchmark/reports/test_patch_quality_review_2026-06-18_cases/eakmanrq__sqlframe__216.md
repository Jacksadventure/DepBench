# Test-patch audit — eakmanrq__sqlframe__216

## 1. Task summary
- Folder: eakmanrq__sqlframe__216
- Ecosystem: pip
- Upgrade: sqlglot >=24.0.0,<25.33 -> >=24.0.0,<25.35
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `/usr/local/bin/python -m pip install pytest-xdist databricks-sql-connector && /usr/local/bin/python -m pytest ... -k duckdb -x -q && /usr/local/bin/python -m pytest tests/unit/standalone/test_functions.py::test_to_timestamp tests/unit/standalone/test_functions.py::test_convert_timezone -x -q`

## 2. What is the breaking change?
sqlglot 25.35 changed timestamp/time-zone typing and rendering enough that SQLFrame needed to normalize timestamp casts and returned Python datetime values. The repair switches generic `to_timestamp` to `TIMESTAMP_LTZ`, adds engine-specific timestamp alternatives, and normalizes timezone-aware datetimes before converting Python values into SQLFrame rows.

## 3. What does Δt (test.patch) actually do?
- Forces tests to run under `TZ=UTC`.
- Updates many DuckDB integration expectations for timestamp/date/timezone functions (`to_timestamp`, `date_trunc`, `from_unixtime`, `unix_timestamp`, `current_timezone`, `make_timestamp`, `timestamp_micros`, `unix_seconds`, etc.).
- Updates standalone SQL rendering expectations from `CAST(... AS TIMESTAMP)` to `CAST(... AS TIMESTAMP_LTZ)` for `to_timestamp` and `convert_timezone`.

## 4. Does Δt directly exercise the breaking change?
Yes. The verifier selects the changed DuckDB timestamp tests and the standalone SQL-generation tests. On P⊕Δm, `to_timestamp` still casts to plain `timestamp`, timezone-aware literals keep old semantics, and several new UTC/TIMESTAMP_LTZ expectations fail. With Δc, the source emits the updated sqlglot types and normalizes datetime values as expected.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt directly checks the timestamp/timezone behavior and SQL rendering that Δc changes for the upgraded sqlglot range.

## 6. Δc nature
REAL_SOURCE_REPAIR — the patch adds timestamp alternatives in `function_alternatives.py`, changes `to_timestamp` to `timestampltz`, strips timezone info in `_to_value`, and wires engine-specific `to_timestamp` implementations for BigQuery, DuckDB, and Postgres.

## 7. Soundness concerns / notes
- The verifier is broad but still focused on timestamp behavior.
- It does not exercise every changed engine path, but the DuckDB and standalone checks are enough to distinguish P⊕Δm from P⊕Δm⊕Δc.

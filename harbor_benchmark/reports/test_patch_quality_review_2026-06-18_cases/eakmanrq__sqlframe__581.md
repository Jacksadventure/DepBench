# Test-patch audit — eakmanrq__sqlframe__581

## 1. Task summary
- Folder: eakmanrq__sqlframe__581
- Ecosystem: pip
- Upgrade: sqlglot >=28.0.0,<28.7 -> >=28.0.0,<28.8
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `/usr/local/bin/python -m pip install pytest-xdist databricks-sql-connector && /usr/local/bin/python -m pytest "tests/integration/engines/test_int_functions.py::test_try_element_at[duckdb]" tests/unit/standalone/test_functions.py::test_array_append tests/unit/standalone/test_functions.py::test_array_prepend -x -q`

## 2. What is the breaking change?
sqlglot 28.7 changes expression generation for array functions and negative numeric literals. sqlframe must invoke new expression classes such as `ArrayCompact`, `ArrayInsert`, and `ArraysZip`, and `try_element_at` must recognize `expression.Neg` as numeric for DuckDB index adjustment.

## 3. What does Δt (test.patch) actually do?
It updates `tests/unit/standalone/test_functions.py` expectations for `array_append` and `array_prepend` to include `COALESCE(cola, ARRAY())`, and removes a stale commented DuckDB assertion in `tests/integration/engines/test_int_functions.py`. The verifier targets `test_try_element_at[duckdb]`, `test_array_append`, and `test_array_prepend`.

## 4. Does Δt directly exercise the breaking change?
Yes for the unit tests: representative expectations change to `ARRAY_APPEND(COALESCE(cola, ARRAY()), 'val')` and `ARRAY_PREPEND(COALESCE(cola, ARRAY()), '-')`, which require sqlframe to emit the new sqlglot 28.7 expression output. The targeted DuckDB integration test exercises the `expression.Neg` handling in Δc.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the selected tests assert the new sqlglot-generated SQL and DuckDB indexing behavior, which old source does not satisfy under the widened dependency range.

## 6. Δc nature
MIXED — the main repair is production code in `sqlframe/base/functions.py` and `sqlframe/base/group.py`, with a small docs capability-list update in `docs/duckdb.md`.

## 7. Soundness concerns / notes
Good witnessed task. The only minor concern is that one Δt hunk removes a comment, but the targeted assertions are real output checks.


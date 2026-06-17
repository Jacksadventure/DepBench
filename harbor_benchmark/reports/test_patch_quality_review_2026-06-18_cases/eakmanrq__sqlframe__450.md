# Test-patch audit — eakmanrq__sqlframe__450

## 1. Task summary
- Folder: eakmanrq__sqlframe__450
- Ecosystem: pip
- Upgrade: sqlglot >=24.0.0,<27.1 -> >=24.0.0,<27.2
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `/usr/local/bin/python -m pip install pytest-xdist databricks-sql-connector && /usr/local/bin/python -m pytest "tests/integration/engines/test_int_functions.py::test_timestamp_add[duckdb]" tests/unit/standalone/test_functions.py::test_dayofweek tests/unit/standalone/test_functions.py::test_dayofmonth tests/unit/standalone/test_functions.py::test_dayofyear tests/unit/standalone/test_functions.py::test_weekofyear -x -q`

## 2. What is the breaking change?
sqlglot 27.1→27.2 (a) changed rendering of `dayofweek`/`dayofmonth`/`dayofyear`/`weekofyear` so they no longer wrap their argument in `TO_DATE(...)`, and (b) introduced native expression classes (`BitwiseAndAgg`, `BitwiseOrAgg`, `BitwiseXorAgg`, `BitwiseCountAgg`) for `bit_and`/`bit_or`/`bit_xor`/`bit_count`, which sqlframe had been emitting as `invoke_anonymous_function("BIT_AND", ...)`.

## 3. What does Δt (test.patch) actually do?
- `tests/integration/engines/test_int_functions.py`: appends a new "Test adding quarters" block to `test_timestamp_add` calling `timestamp_add("quarter", lit(2), "ts")` with hardcoded expected datetimes.
- `tests/unit/standalone/test_functions.py`: rewrites the parametrized expected strings for `test_dayofweek`/`test_dayofmonth`/`test_dayofyear`/`test_weekofyear` from e.g. `"DAYOFWEEK(TO_DATE(cola))"` to `"DAYOFWEEK(cola)"` (drops the `TO_DATE` wrapper).
- No tests for `bit_and`/`bit_or`/`bit_xor`/`bit_count` are added or modified.

## 4. Does Δt directly exercise the breaking change?
No. The dayof* expected-value edits align with sqlglot 27.2's new rendering, but Δc never touches the `dayofweek`/`dayofmonth`/`dayofyear`/`weekofyear` functions — so on P⊕Δm sqlframe already emits `DAYOFWEEK(cola)` (sqlglot changed, not sqlframe) and the new Δt expectations match without Δc. The `test_timestamp_add` quarter block is likewise unrelated to Δc (Δc does not touch `timestamp_add`). The actual Δc repair (bit_* anonymous→native expression classes) is not exercised by any test in Δt.

## 5. Coverage verdict
UNWITNESSED — Δt updates dayof* expectations to match the new sqlglot rendering (which holds with or without Δc) and adds an unrelated `timestamp_add` quarter case; the bit_* source repairs in Δc are never tested, so the hidden test passes on P⊕Δm without Δc.

## 6. Δc nature
MIXED — real source repair in `sqlframe/base/functions.py` (`bit_and`/`bit_or`/`bit_xor`/`bit_count` switch from `invoke_anonymous_function` to `invoke_expression_over_column` with native `expression.Bitwise*Agg`, plus `unsupported_engines` tweaks) plus drive-by docs additions in `docs/bigquery.md`, `docs/duckdb.md`, `docs/postgres.md`.

## 7. Soundness concerns / notes
- Confirmed by the 2026-06-10 review: "Exclude from witnessed main set. Contains real source edit, but hidden tests pass without it."
- The Δc bit_* repair is genuinely motivated by sqlglot 27.2 but Δt provides no assertion that distinguishes `invoke_anonymous_function` from `invoke_expression_over_column` — coverage gap.
- Sister task `eakmanrq__sqlframe__200` is witnessed (via `test_invoke_anonymous`'s `inspect.getsource` + `exp.Anonymous` check); `__450` lacks any analogous probe.

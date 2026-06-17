# Test-patch audit — eakmanrq__sqlframe__200

## 1. Task summary
- Folder: eakmanrq__sqlframe__200
- Ecosystem: pip
- Upgrade: sqlglot >=24.0.0,<25.29 -> >=24.0.0,<25.32
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `/usr/local/bin/python -m pip install pytest-xdist databricks-sql-connector && /usr/local/bin/python -m pytest tests/unit/standalone/test_functions.py::test_invoke_anonymous tests/unit/standalone/test_functions.py::test_regexp_extract_all -x -q`

## 2. What is the breaking change?
sqlglot 25.29→25.32 introduced/changed native expression classes for `Median` and `UnixSeconds` (so `invoke_anonymous_function` no longer round-trips as `exp.Anonymous`), changed `regexp_extract_all` limit handling, and changed `DataType.build` for the `regtype` case. sqlframe's `functions.py` / `function_alternatives.py` had to switch `median`/`unix_seconds` from `invoke_anonymous_function` to `invoke_expression_over_column` and adjust `unsupported_engines`.

## 3. What does Δt (test.patch) actually do?
- `tests/unit/standalone/test_functions.py`:
  - `test_invoke_anonymous`: expands `ignore_funcs` from `{"array_size","to_char","ltrim","rtrim"}` to add `"contains"`, `"exists"`, `"make_interval"`, `"regexp_extract_all"`.
  - `test_regexp_extract_all`: changes one parametrized row from `(SF.regexp_extract_all("cola","colb",1), "REGEXP_EXTRACT_ALL(cola, colb, 1)")` to `(SF.regexp_extract_all("cola","colb",2), "REGEXP_EXTRACT_ALL(cola, colb, 2)")`.
- No new tests/fixtures; two targeted edits to keep the suite aligned with sqlglot 25.3x.

## 4. Does Δt directly exercise the breaking change?
Yes, via `test_invoke_anonymous`. The test checks: `if "invoke_anonymous_function" in inspect.getsource(func) and name not in ignore_funcs: assert isinstance(parse_one(f"{name}()", read="spark", ...), exp.Anonymous)`. `median`/`unix_seconds` are NOT in the ignore set. On P⊕Δm (new sqlglot, no Δc) their source still contains `invoke_anonymous_function`, so the test parses them and asserts `exp.Anonymous` — but sqlglot 25.3x now resolves them to `exp.Median`/`exp.UnixSeconds`, so the assertion fails. On P⊕Δm⊕Δc their source uses `invoke_expression_over_column` (so the `if` is False and they are skipped), and the test passes. The `test_regexp_extract_all` row edit is a drive-by alignment for the new sqlglot (Δc does not touch `regexp_extract_all`), so it does not itself witness Δc, but the combined `-x` run is driven to failure by `test_invoke_anonymous`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — `test_invoke_anonymous` fails on P⊕Δm (median/unix_seconds no longer anonymous in new sqlglot) and passes on P⊕Δm⊕Δc (Δc switches them to `invoke_expression_over_column`).

## 6. Δc nature
MIXED — real source repairs in `sqlframe/base/functions.py` (`median`→`expression.Median`, `unix_seconds`→`expression.UnixSeconds`, `contains` unsupported_engines) and `sqlframe/base/function_alternatives.py` (`DataType.build` regtype), plus drive-by docs additions in `docs/bigquery.md`, `docs/duckdb.md`, `docs/snowflake.md`.

## 7. Soundness concerns / notes
- The `test_regexp_extract_all` row change (1→2) is unrelated to Δc (Δc never edits `regexp_extract_all`) and is purely a sqlglot-version alignment; harmless but adds noise.
- Witness is somewhat indirect (relies on `inspect.getsource` string check + sqlglot's class resolution), but it does genuinely distinguish P⊕Δm from P⊕Δm⊕Δc.
- Sister tasks `eakmanrq__sqlframe__450` and `__533` ARE flagged `no_code_pass` in the 2026-06-10 review; this one is not, consistent with `__200` being genuinely witnessed.

# Test-patch audit — eakmanrq__sqlframe__533

## 1. Task summary
- Folder: eakmanrq__sqlframe__533
- Ecosystem: pip
- Upgrade: sqlglot >=24.0.0,<27.26 -> >=24.0.0,<27.27
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `/usr/local/bin/python -m pip install pytest-xdist databricks-sql-connector && /usr/local/bin/python -m pytest "tests/integration/engines/test_int_functions.py::test_pi[duckdb]" -x -q`

## 2. What is the breaking change?
sqlglot 27.27 (a) added a native `expression.Tanh` AST node so `tanh()` should be emitted via `invoke_expression_over_column(col, expression.Tanh)` rather than the anonymous `TANH` function, and (b) extended native support so `pi()` is now usable on more engines (the project widens `unsupported_engines` from `"*"` to `["bigquery","snowflake"]`, enabling duckdb). Neither is a callers-facing API signature change; both are internal mapping updates.

## 3. What does Δt (test.patch) actually do?
- `tests/integration/engines/test_int_functions.py`: a single one-line assertion relaxation in `test_pi`:
  `assert session.range(1).select(pi()).first()[0] == math.pi` -> `assert ... in (math.pi, 3.141592654)`.
No new test, no new fixture, no test for `tanh`. The `tanh` repair in Δc is not exercised by Δt at all (test_cmd runs only `test_pi[duckdb]`).

## 4. Does Δt directly exercise the breaking change?
No. With the un-fixed source (P⊕Δm), `pi` still carries `@meta(unsupported_engines="*")`, so on the `duckdb` engine the `get_session_and_func("pi")` harness treats `pi` as unsupported and the `test_pi[duckdb]` case is **skipped** (pytest skip → exit 0 → reward 1). Once Δc narrows `unsupported_engines` to `["bigquery","snowflake"]`, `pi` runs on duckdb and returns `3.141592654`, which the relaxed `in (math.pi, 3.141592654)` assertion accepts. So both P⊕Δm⊕Δt and P⊕Δm⊕Δc⊕Δt pass — the assertion relaxation is permissive enough that it does not discriminate Δc, and the skip path makes the un-fixed state pass anyway.

## 5. Coverage verdict
UNWITNESSED — `flagged_in_problematic_review: True`; `test_pi[duckdb]` is skipped on P⊕Δm (pi marked unsupported on all engines) and passes on P⊕Δm⊕Δc via the relaxed assertion, so P⊕Δm⊕Δt already passes without Δc.

## 6. Δc nature
REAL_SOURCE_REPAIR — `sqlframe/base/functions.py` makes two genuine sqlglot-27.27 mappings: `tanh` switches from `invoke_anonymous_function(col, "TANH")` to `invoke_expression_over_column(col, expression.Tanh)`, and `pi`'s `@meta(unsupported_engines="*")` is narrowed to `["bigquery","snowflake"]`. `docs/duckdb.md` adds a `tanh` doc entry. Real source edit, but only the `pi` engine-narrowing is even nominally reachable by the verifier, and it is not needed because of the skip.

## 7. Soundness concerns / notes
- The verifier runs a **single test case** (`test_pi[duckdb]`), and Δt only relaxes that case's assertion — it does not add any test that would fail on the un-fixed `tanh` mapping. So the `tanh` half of Δc is completely untested by the oracle.
- The relaxation `in (math.pi, 3.141592654)` is permissive on purpose to accept duckdb's float result, but combined with the `unsupported_engines="*"` skip on P⊕Δm it produces a symmetric PASS/PASS (no_code_pass).
- A witnessing version of this task would need a test that (a) runs `tanh` on an engine where the anonymous `TANH` call now fails under sqlglot 27.27, or (b) runs `pi` on duckdb and asserts the exact duckdb value while also removing the `unsupported_engines="*"` skip — neither is present.

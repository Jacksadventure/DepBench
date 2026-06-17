# Test-patch audit — eakmanrq__sqlframe__492

## 1. Task summary
- Folder: eakmanrq__sqlframe__492
- Ecosystem: pip
- Upgrade: sqlglot >=24.0.0,<27.11 -> >=24.0.0,<27.12
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `/usr/local/bin/python -m pip install pytest-xdist databricks-sql-connector && /usr/local/bin/python -m pytest tests/unit/standalone/test_functions.py::test_invoke_anonymous -x -q`

## 2. What is the breaking change?
Newer sqlglot exposes native expression classes for functions that sqlframe previously emitted through generic anonymous function calls. `ntile` and `regexp_instr` need to move from `Column.invoke_anonymous_function(...)` to sqlglot expression-backed calls.

## 3. What does Δt (test.patch) actually do?
`tests/unit/standalone/test_functions.py` adds `format_string` to the `ignore_funcs` set in `test_invoke_anonymous`, with a comment that it has complex overrides. The existing test continues scanning functions that call `invoke_anonymous_function` and checking whether they should instead map to known sqlglot expressions.

## 4. Does Δt directly exercise the breaking change?
Yes, through the existing `test_invoke_anonymous` oracle. With the sqlglot bound widened and `format_string` ignored, the remaining offending anonymous functions include the source-level cases fixed by Δc (`ntile` and `regexp_instr`); P⊕Δm⊕Δt fails until those functions stop using anonymous invocation.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt retargets the existing oracle for sqlglot 27.11-era behavior, and the source repair removes anonymous invocation for functions now represented by sqlglot expressions.

## 6. Δc nature
REAL_SOURCE_REPAIR — `sqlframe/base/functions.py` changes `ntile` to `expression.Ntile` and `regexp_instr` to `expression.RegexpInstr` with updated engine support metadata.

## 7. Soundness concerns / notes
The test patch itself is an ignore-list adjustment rather than a newly added assertion. The witness depends on the pre-existing `test_invoke_anonymous` behavior and is credible, but a dynamic run would be useful if this case needs especially high confidence.

# Test-patch audit — eakmanrq__sqlframe__589

## 1. Task summary
- Folder: eakmanrq__sqlframe__589
- Ecosystem: pip
- Upgrade: sqlglot >=28.0.0,<28.10 -> >=28.0.0,<29.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `/app/.venv/bin/python -m pytest "tests/integration/engines/test_int_functions.py::test_to_binary[duckdb]" tests/unit/standalone/test_functions.py::test_bit_get tests/unit/standalone/test_functions.py::test_curdate -x -q`

## 2. What is the breaking change?
sqlglot 29 changes helper/API availability and expression rendering. SQLFrame must stop importing `classproperty` from `sqlglot.helper`, guard reserved-word parsing changes, and switch some functions from anonymous SQL calls to typed sqlglot expressions such as `Getbit` and `CurrentDate`.

## 3. What does Δt (test.patch) actually do?
The hidden tests update expected behavior for three targeted cases: DuckDB `to_binary` now expects `b"abc"` instead of a bit string, standalone `bit_get` now expects `GETBIT(...)`, and standalone `curdate` now expects `CURRENT_DATE`.

## 4. Does Δt directly exercise the breaking change?
Yes. Without Δc, `test_bit_get` and `test_curdate` still render the old anonymous forms `BIT_GET(...)` and `CURDATE()`, failing the updated assertions. Δc changes those functions to sqlglot expression classes. The wider source patch also handles sqlglot 29 helper removal and parsing changes that can surface during import/session setup.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the targeted unit tests discriminate the old source from the repaired sqlglot-29-compatible source.

## 6. Δc nature
MIXED — Δc contains real production repairs in `sqlframe/base/*.py` and `sqlframe/spark/session.py`, but also adds a `.claude` skill file, docs updates, Makefile churn, and lockfile updates.

## 7. Soundness concerns / notes
The verifier only runs three focused tests while Δc contains many broader function and documentation changes. The `bit_get` and `curdate` portions are well witnessed; the rest of the repair is only indirectly covered or not covered by this command.

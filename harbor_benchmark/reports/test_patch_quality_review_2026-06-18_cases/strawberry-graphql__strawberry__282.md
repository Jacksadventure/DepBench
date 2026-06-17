# Test-patch audit - strawberry-graphql__strawberry__282

## 1. Task summary
- Folder: strawberry-graphql__strawberry__282
- Ecosystem: pip
- Upgrade: flask 3.1.0b0 -> 3.1.0b2 (bundle manifest actually updates graphql-core 3.1.0b0 -> 3.1.0b2)
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `PYTHONPATH=/work pytest tests/flask -v -p no:cacheprovider --tb=short -o addopts=`

## 2. What is the breaking change?
The effective dependency break in the manifest is `graphql-core` 3.1.0b0 -> 3.1.0b2, not Flask. The GraphQL schema-printer utilities moved from `graphql.utilities.schema_printer` to `graphql.utilities.print_schema`. Δc updates imports in `strawberry/printer.py` and `strawberry/schema.py`.

## 3. What does Δt (test.patch) actually do?
Refactors Flask tests by moving Flask app/client setup into a new `tests/flask/conftest.py`, renaming the fixture from `client` to `flask_client`, and importing `url_for` directly. It does not add assertions for schema printing.

## 4. Does Δt directly exercise the breaking change?
Indirectly. The Flask test suite imports Strawberry schema/view code, which imports `strawberry.schema`; with graphql-core 3.1.0b2 and no Δc, that import path is broken and the tests fail during collection/import. With Δc, the schema module imports the new `print_schema` location and the Flask tests can run.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the selected Flask tests import the repaired schema module and expose the graphql-core import-path break, even though the test edits themselves are fixture cleanup rather than new schema-printer assertions.

## 6. Δc nature
MIXED - real source repair in `strawberry/printer.py` and `strawberry/schema.py`, plus a new `RELEASE.md` note.

## 7. Soundness concerns / notes
- The batch metadata labels the library as Flask, but the manifest hunk that matches the version numbers is `graphql-core`.
- Δt is weakly targeted; the witness is primarily import/collection failure from the existing Flask test path.

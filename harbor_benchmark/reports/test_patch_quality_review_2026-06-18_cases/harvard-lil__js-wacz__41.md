# Test-patch audit - harvard-lil__js-wacz__41

## 1. Task summary
- Folder: harvard-lil__js-wacz__41
- Ecosystem: npm_and_yarn
- Upgrade: glob 8.1.0 -> 10.3.3
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `node --test`

## 2. What is the breaking change?
`glob` 10 no longer supports the old default import plus `.sync` usage used by the project. Production code imports `glob from 'glob'` and calls `glob.sync(...)`; Δc changes this to the named `globSync` export.

## 3. What does Δt (test.patch) actually do?
Updates `index.test.js` the same way: `import { globSync } from 'glob'` and `globSync(FIXTURE_INPUT)` instead of `glob.sync(FIXTURE_INPUT)`.

## 4. Does Δt directly exercise the breaking change?
Yes. The hidden test file itself must be migrated to the new `glob` API, and the test command imports/runs production `index.js`, which also needs the same migration. On P+Δm+Δt, production still uses the old default import/`.sync` call and fails under glob 10. With Δc, both production and tests use `globSync`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the verifier exercises the glob 10 import/API migration and fails without the production change.

## 6. Δc nature
REAL_SOURCE_REPAIR - a production import and callsite are migrated from `glob.sync` to `globSync`.

## 7. Soundness concerns / notes
- Δt mirrors the same import migration in tests; it does not add new behavioral coverage, but the existing end-to-end WACZ process test still imports and runs the repaired production path.

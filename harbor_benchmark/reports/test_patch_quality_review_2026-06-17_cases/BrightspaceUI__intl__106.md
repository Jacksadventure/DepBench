# Test-patch audit — BrightspaceUI__intl__106

## 1. Task summary
- Folder: BrightspaceUI__intl__106
- Ecosystem: npm_and_yarn
- Upgrade: eslint-config-brightspace 0.17 -> 0.18 (and Δm also widens the lint script from `eslint lib test --ext .js` to `eslint . --ext .js`, and adds `eslint-plugin-import`).
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npm run lint`

## 2. What is the breaking change?
eslint-config-brightspace 0.18 turns on stricter rules (prefer-const / no-var, arrow callbacks over `function`, template literals over string concatenation, import/order). Combined with Δm widening the lint target from `eslint lib test` to `eslint .` (everything) and adding `eslint-plugin-import`, `npm run lint` now flags style violations across both `lib/` and `test/`. No functional/runtime change to the internationalization library.

## 3. What does Δt (test.patch) actually do?
Touches 4 test files (`test/common.js`, `test/dateTime.js`, `test/fileSize.js`, `test/number.js`). Every hunk is style compliance: `var expect` -> `const expect`; `function(input)` -> `(input)`; string concatenation in `it(...)` titles -> template literals; and import-order reordering (e.g. `getDocumentLocaleSettings` moved after the local module imports). No new test cases, no modified behavioral assertions, no fixtures.

## 4. Does Δt directly exercise the breaking change?
No behavioral assertion is involved. Δt merely makes the test files lint-clean under the 0.18 config + `eslint .` scope. The "failure" it helps produce on P⊕Δm⊕Δt is `npm run lint` exiting non-zero on the still-non-compliant `lib/` source (which Δc fixes) — i.e. a style-check failure, not a functional test.

## 5. Coverage verdict
TESTS_OTHER_THING — the verifier "test" is `npm run lint` (a style check), which the locked breaking-change definition explicitly excludes ("not ... lint"); Δt is pure style churn with no functional assertion.

## 6. Δc nature
FORMATTER_LINT_CHURN — `lib/common.js` (`var`->`const`), `lib/dateTime.js` (`var`->`let`/`const`, `function`->arrow), `lib/fileSize.js` (import reorder), `lib/number.js` (string concat -> template literals). All style-only; zero logic change.

## 7. Soundness concerns / notes
- This is a lint-only task whose test_cmd is `npm run lint`; per the locked definition lint failures are excluded from Level 1, so it should not be in the witnessed main set — yet it is NOT flagged in `problematic_prs_review_2026-06-10.md` (same gap as cloudant__nodejs-cloudant__400).
- Part of the "breaking change" is actually in Δm itself (the script widening `eslint lib test` -> `eslint .` and the `eslint-plugin-import` addition), so the manifest is doing the breaking, not the dependency bump per se.
- An agent can pass by running `eslint --fix`; the task measures style-rule compliance, not dependency-repair skill.
- Δt and Δc are symmetric style churn; trivially reproducible, low benchmark value.

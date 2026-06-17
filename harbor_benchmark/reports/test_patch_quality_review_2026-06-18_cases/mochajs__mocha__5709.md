# Test-patch audit — mochajs__mocha__5709

## 1. Task summary
- Folder: mochajs__mocha__5709
- Ecosystem: npm_and_yarn
- Upgrade: prettier 3.6.2 -> 3.8.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npm run format:check`

## 2. What is the breaking change?
The only observed change is Prettier formatting output changing between 3.6.2 and 3.8.1 for certain `require.resolve(...)` and assertion-call line wraps.

## 3. What does Δt (test.patch) actually do?
Δt reformats several test files (`multiple-runs.spec.js`, `root-hooks.spec.js`, `test/node-unit/mocha.spec.js`, `test/unit/mocha.spec.js`) to the newer Prettier output. It changes line wrapping only; no assertions or runtime behavior change.

## 4. Does Δt directly exercise the breaking change?
Only as a formatter check. The verifier is `npm run format:check`, so the oracle is style conformance rather than functional behavior.

## 5. Coverage verdict
TESTS_OTHER_THING — lint/format-only `test_cmd` is always outside the witnessed-breaking-change definition, and this task tests Prettier output churn rather than a functional dependency break.

## 6. Δc nature
FORMATTER_LINT_CHURN — `lib/nodejs/parallel-buffered-runner.js` is reformatted by Prettier with no semantic code change.

## 7. Soundness concerns / notes
- The pre-phase failure is a format failure, explicitly excluded by the benchmark definition.
- Δt and Δc are both pure formatting.

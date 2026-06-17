# Test-patch audit — onthegomap__maplibre-contour__34

## 1. Task summary
- Folder: onthegomap__maplibre-contour__34
- Ecosystem: npm_and_yarn
- Upgrade: prettier 2.8.8 -> 3.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npm test`

## 2. What is the breaking change?
This is a Prettier formatting upgrade. Δc and Δt are dominated by Prettier 3 style changes, especially trailing commas and argument/list wrapping. No runtime or type-level API migration is visible in the source patch.

## 3. What does Δt (test.patch) actually do?
Δt reformats test files (`actor.test.ts`, `e2e.test.ts`, `height-tile.test.ts`, `isolines.test.ts`, `utils.test.ts`, `vtpbf.test.ts`) with Prettier 3 output. It does not alter assertions or tested behavior.

## 4. Does Δt directly exercise the breaking change?
It exercises formatter conformance only. The visible hidden-test changes are all formatting, and Δc applies the same formatting style to production TypeScript files. Any FAIL -> PASS signal comes from formatting checks within `npm test`, not from application behavior.

## 5. Coverage verdict
TESTS_OTHER_THING — the task tests Prettier-format compliance, and format/lint failures are excluded from witnessed breaking-change evidence.

## 6. Δc nature
FORMATTER_LINT_CHURN — source files are reformatted for Prettier 3 with no semantic changes.

## 7. Soundness concerns / notes
- If `npm test` only ran unit tests, this would be unwitnessed because formatting does not affect runtime assertions. The only plausible discriminating signal is a format check, which is excluded.
- This task is useful for formatter-upgrade repair, not dependency API repair.

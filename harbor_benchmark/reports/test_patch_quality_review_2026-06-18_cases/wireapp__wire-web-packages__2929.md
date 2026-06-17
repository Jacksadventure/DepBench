# Test-patch audit - wireapp__wire-web-packages__2929

## 1. Task summary
- Folder: wireapp__wire-web-packages__2929
- Ecosystem: npm_and_yarn
- Upgrade: prettier 1.19.1 -> 2.0.4
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `yarn run lint`

## 2. What is the breaking change?
This is a Prettier formatting update. The patch rewrites line wrapping and function spacing across source, docs, and tests. No runtime or compile dependency API break is visible.

## 3. What does test.patch actually do?
The hidden patch reformats test files such as `packages/cbor/spec/EncoderSpec.ts`, `AccountHelper.js`, and `PriorityQueue.test.js`, mostly collapsing chained calls and adding spaces around function declarations.

## 4. Does test.patch directly exercise the breaking change?
It only exercises the formatter/lint pipeline. The verifier command is `yarn run lint`, so a pass/fail result is lint evidence, not valid witnessed breaking-change evidence.

## 5. Coverage verdict
TESTS_OTHER_THING - lint/format-only `test_cmd` is explicitly excluded from witnessed evidence.

## 6. Delta_c nature
FORMATTER_LINT_CHURN - source, README, and test hunks are mechanical Prettier 2 formatting changes with no semantic repair.

## 7. Soundness concerns / notes
This task may be operationally useful as a formatter-update task, but it should not be counted in the Level-1 breaking-change benchmark.

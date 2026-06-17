# Test-patch audit - option-t__option-t__1911

## 1. Task summary
- Folder: option-t__option-t__1911
- Ecosystem: npm_and_yarn
- Upgrade: prettier 2.8.8 -> 3.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `./node_modules/.bin/prettier --check .`

## 2. What is the breaking change?
Prettier 3 changes formatting defaults and this project also changes `.prettierrc.toml` from `trailingComma = 'es5'` to `trailingComma = 'all'`. The observed failures are formatting/check failures, not runtime, compile, or dependency API failures.

## 3. What does test.patch actually do?
The hidden patch is a large mechanical Prettier reprint of test files under `packages/api_tests/__tests__/...`, mainly adding trailing commas and reflowing long expressions to match the Prettier 3 configuration.

## 4. Does test.patch directly exercise the breaking change?
It only exercises formatting. The verifier command is itself `prettier --check .`, so the task is a formatter oracle rather than a source behavior oracle.

## 5. Coverage verdict
TESTS_OTHER_THING - lint/format-only `test_cmd` is explicitly excluded from witnessed breaking-change evidence.

## 6. Delta_c nature
FORMATTER_LINT_CHURN - `.prettierrc.toml` changes the trailing-comma rule and the many source hunks are mechanical Prettier 3 formatting, not semantic repair.

## 7. Soundness concerns / notes
This task should be excluded from the witnessed main set despite operationally requiring source files to be reformatted.

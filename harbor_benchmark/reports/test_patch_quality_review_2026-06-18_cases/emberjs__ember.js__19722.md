# Test-patch audit — emberjs__ember.js__19722

## 1. Task summary
- Folder: emberjs__ember.js__19722
- Ecosystem: npm_and_yarn
- Upgrade: eslint-plugin-qunit 4.0.0 -> 6.2.0
- test_cmd: `yarn lint:eslint`

## 2. What is the breaking change?
The upgraded dependency is an ESLint plugin, and the verifier command is lint-only. The human source change adds an inline disable for `qunit/no-qunit-stop` around a legacy QUnit compatibility call.

## 3. What does Δt (test.patch) actually do?
The hidden patch is entirely lint accommodation in test files: it adds `eslint-disable qunit/no-test-expect-argument`, rewrites arrow callbacks to function callbacks, and changes some assertions to lint-preferred forms.

## 4. Does Δt directly exercise the breaking change?
It exercises only lint-rule compatibility, not source behavior. Per the audit instructions, lint-only `test_cmd` is always `TESTS_OTHER_THING`.

## 5. Coverage verdict
TESTS_OTHER_THING — the verifier is `yarn lint:eslint`, so the evidence is lint compliance rather than a witnessed dependency breaking-change repair.

## 6. Δc nature
FORMATTER_LINT_CHURN — Δc is an ESLint suppression comment for a new lint rule.

## 7. Soundness concerns / notes
- This may be a legitimate repository maintenance patch, but it is not suitable as a behavioral breaking-change task.
- Dependency-resolution, lint, formatting, and style-rule failures are excluded as witnessed evidence by the report criteria.


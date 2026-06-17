# Test-patch audit — laconiajs__laconia__178

## 1. Task summary
- Folder: laconiajs__laconia__178
- Ecosystem: npm_and_yarn
- Upgrade: eslint-config-standard 12.0.0 -> 13.0.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npm run test:jslint`

## 2. What is the breaking change?
eslint-config-standard 13 tightens lint rules, producing style failures such as `prefer-const` and safer `hasOwnProperty` usage. There is no runtime dependency API behavior under test.

## 3. What does Δt (test.patch) actually do?
Four test files receive lint-only edits: `let` to `const` in several specs, `inputHeaders.hasOwnProperty(...)` to `expect(inputHeaders).toHaveProperty(...)`, and similar style-rule compliance changes. No behavioral test coverage is added.

## 4. Does Δt directly exercise the breaking change?
No. The verifier is `npm run test:jslint`, so Δt and Δc are both just making files satisfy the new lint rules.

## 5. Coverage verdict
TESTS_OTHER_THING — lint-only `test_cmd` is excluded from witnessed breaking-change evidence by the locked classification rule.

## 6. Δc nature
FORMATTER_LINT_CHURN — production files are changed for lint compliance in `ApiGatewayNameMappingErrorConverter.js`, `SecretsManagerConfigConverter.js`, and `laconia-test-helper/src/index.js`.

## 7. Soundness concerns / notes
This should be treated as a lint-rule migration, not a source repair benchmark. The prior problematic review did not flag it, but the command makes the classification unambiguous.

# Test-patch audit — ktsn__vue-auto-routing__103

## 1. Task summary
- Folder: ktsn__vue-auto-routing__103
- Ecosystem: npm_and_yarn
- Upgrade: prettier 1.19.1 -> 2.0.5
- test_cmd: `npm test`

## 2. What is the breaking change?
The dependency bump is a Prettier major-version formatting change. The captured source repair changes only formatting (`compilation =>` -> `(compilation) =>`), and the hidden test patch is entirely Prettier 2 formatting churn in a spec file.

## 3. What does Δt (test.patch) actually do?
Δt reformats `test/webpack-plugin.spec.ts`: adds trailing commas and wraps single-argument arrow callbacks in parentheses. It adds no assertions and changes no test behavior.

## 4. Does Δt directly exercise the breaking change?
No functional behavior is exercised. The only observable difference is formatter/lint conformance under the upgraded Prettier style. Per the audit rule, lint/format-only evidence is not a witnessed breaking change.

## 5. Coverage verdict
TESTS_OTHER_THING — Δt and Δc are formatter churn for a Prettier upgrade, not source behavior repair.

## 6. Δc nature
FORMATTER_LINT_CHURN — Δc changes a single arrow function's formatting in `src/webpack-plugin.ts`.

## 7. Soundness concerns / notes
Even if `npm test` includes a formatting check and produces a fail/pass, that is explicitly outside the witnessed dependency-breaking definition for this report.

# Test-patch audit — fb55__css-what__1184

## 1. Task summary
- Folder: fb55__css-what__1184
- Ecosystem: npm_and_yarn
- Upgrade: prettier 2.8.8 -> 3.1.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npm test`

## 2. What is the breaking change?
prettier 3.1.1 reformats TypeScript code differently, especially trailing commas and ternary indentation. The accompanying `.eslintrc.json` change disables an ESLint syntax rule; there is no functional parser/stringifier behavior change in `css-what`.

## 3. What does Δt (test.patch) actually do?
It reformats test files only: `src/parse.spec.ts`, `src/stringify.spec.ts`, `src/wpt.spec.ts`, and `src/__fixtures__/tests.ts` gain prettier-style trailing commas and formatting. No test case or assertion semantics change.

## 4. Does Δt directly exercise the breaking change?
No behavioral assertion is involved. A representative hunk is `expect(parse(selector)).toStrictEqual(expected)` -> `expect(parse(selector)).toStrictEqual(expected),`, which is syntactic formatting only and should not affect Jest/runtime test outcomes.

## 5. Coverage verdict
TESTS_OTHER_THING — the hidden patch and Δc are formatter/lint churn for a Prettier upgrade; even though the command is `npm test`, the evidence is not a functional dependency break.

## 6. Δc nature
FORMATTER_LINT_CHURN — `.eslintrc.json`, `src/parse.ts`, and `src/stringify.ts` are changed for Prettier/ESLint formatting and rule compatibility, not runtime behavior.

## 7. Soundness concerns / notes
This is low benchmark value. If `npm test` includes lint/format checks, the task is tooling-style only; if it only runs Jest, the formatting changes are likely unwitnessed at runtime.


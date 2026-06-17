# Test-patch audit — codemod-js__codemod__387

## 1. Task summary
- Folder: codemod-js__codemod__387
- Ecosystem: npm_and_yarn
- Upgrade: @typescript-eslint/eslint-plugin 2.9.0 -> 2.11.0 (also @typescript-eslint/parser)
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `for p in parser core matchers cli; do (cd packages/$p && ./node_modules/.bin/tsc); done; ./node_modules/.bin/eslint packages/cli --ext .ts; (cd packages/cli && ./node_modules/.bin/mocha 'test/**/*Test.js'); ./node_modules/.bin/eslint packages/matchers --ext .ts; (cd packages/matchers && ./node_modules/.bin/jest --ci)`

## 2. What is the breaking change?
@typescript-eslint/eslint-plugin 2.11 tightened / newly enforced `no-empty-function` (or an equivalent empty-arrow rule), so `() => {}` arrow/function bodies without a comment are now lint failures. The repair pattern across Δc and Δt is to either add a `// do nothing` comment inside the empty body or replace the empty arrow with a non-empty reference (e.g. `Number`).

## 3. What does Δt (test.patch) actually do?
- `packages/cli/test/unit/ProcessSnapshotTest.ts` (7 sites): `() => {}` -> `() => { // do nothing }` for `fakeRequire.extensions['.omg']` assignments, `const originalLoader = (): void => {}`, `const listener = (): void => {}`, `const existingListener = (): void => {}`. Pure lint compliance; no assertion changes.
- `packages/matchers/src/__tests__/matchers.test.ts` (2 sites): `expect(m.anything().match(() => {})).toBeTruthy()` -> `expect(m.anything().match(Number)).toBeTruthy()` and the corresponding `toBeFalsy()` for `arrayOf`. The empty arrow passed as a matcher argument is replaced with `Number` (a non-empty function) — semantically still "a function," so the `anything()` and `arrayOf(anything())` behaviors are unchanged, but it's a real edit to the test input, not just a comment.

## 4. Does Δt directly exercise the breaking change?
Only in the lint-compliance sense. The `eslint packages/cli --ext .ts` and `eslint packages/matchers --ext .ts` steps in test_cmd lint the test files too; Δt makes those test files lint-clean under the new `no-empty-function` enforcement. But Δt does **not** exercise Δc: Δc only touches `CLIEngine.ts` (`onTransform` default param `= () => {}`) and `ProcessSnapshot.ts` (`log` default param `= () => {}`), both **default-parameter** empty arrows. `no-empty-function` typically allows empty default-parameter functions (or the project config doesn't flag them), so Δc is not required for `eslint packages/cli` to pass once the test files are fixed.

## 5. Coverage verdict
UNWITNESSED — `flagged_in_problematic_review: True` indicates P⊕Δm⊕Δt passes without Δc: Δt clears the lint violations in the test files (assignments/arguments), and the source-file `() => {}` sites Δc modifies are default parameters that the rule does not flag, so `eslint packages/cli` passes without Δc.

## 6. Δc nature
FORMATTER_LINT_CHURN — `packages/cli/src/CLIEngine.ts` and `packages/cli/src/ProcessSnapshot.ts` only add `// do nothing by default` / `// no logging by default` comments inside empty default-parameter arrow bodies; no semantic change, no API migration, no behavior difference. Almost certainly defensive cleanup that the lint rule does not actually require.

## 7. Soundness concerns / notes
- Asymmetry: Δt edits empty arrows in **assignment / call-argument** positions (which `no-empty-function` flags), Δc edits empty arrows in **default-parameter** position (which it typically does not). That asymmetry is the mechanism by which P⊕Δm⊕Δt passes without Δc — the canonical no_code_pass signature.
- The `matchers.test.ts` edit (`() => {}` -> `Number`) is a semantic test-input change, but because `m.anything()` matches any value and `m.arrayOf(m.anything())` rejects any non-array, swapping one function for another (both functions, neither an array) preserves the expected truthy/falsy results, so it does not introduce a new behavioral probe.
- Task would only be witnessed if `no-empty-function` (or the project's config) also flagged default-parameter empty arrows; the flagged status shows it does not.

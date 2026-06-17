# Test-patch audit — inrupt__solid-client-authn-js__279

## 1. Task summary
- Folder: inrupt__solid-client-authn-js__279
- Ecosystem: npm_and_yarn
- Upgrade: prettier 1.19.1 -> 2.1.0
- Flagged in problematic_prs_review_2026-06-10.md: NO (in the 31-row "random" control sample, not the 34 flagged rows)
- test_cmd: `npm run lint`

## 2. What is the breaking change?
Prettier 2.0 changed its default formatting — most visibly trailing commas (`trailingComma: "all"` became the default in 2.x vs `"es5"` in 1.x), plus quote/spacing/markdown tweaks. Because the repo runs `eslint-plugin-prettier` (prettier as an ESLint rule), every file formatted under prettier 1.19 now fails `npm run lint` until re-formatted with prettier 2.x. There is **no semantic/behavioral source change** — only formatting.

## 3. What does Δt (test.patch) actually do?
Touches ~52 files, ALL under `__tests__/**/*.spec.ts` and `src/**/__mocks__/*.ts`. Every hunk is mechanical prettier-2 reformatting: adding trailing commas after the last object/array element and last function argument (e.g. `RedirectHandlerResponse` → `RedirectHandlerResponse,`, `type: "dpop"` → `type: "dpop",`, `storageUtility: StorageUtilityMock` → `storageUtility: StorageUtilityMock,`). No new test cases, no new assertions, no fixtures, no snapshot changes, no test-infra logic — purely formatter churn on test/mock files.

## 4. Does Δt directly exercise the breaking change?
No. Δt does not exercise any dependency breaking change — it only re-formats test/mock files to satisfy prettier 2.x. The verifier (`npm run lint`) does fail on P⊕Δm⊕Δt (because the un-reformatted `src/**/*.ts` production files still violate the prettier-2 rule) and passes on P⊕Δm⊕Δc⊕Δt (once Δc reformats source), so the operational FAIL→PASS holds — but the "break" is a **lint/format failure**, not a runtime or compile break caused by an API change.

## 5. Coverage verdict
TESTS_OTHER_THING — Δt (and the whole task) exercises prettier-2 formatting conformance via a linter, not a dependency breaking change; the pre-phase FAIL is a lint failure, which the locked definition explicitly excludes ("not ... lint").

## 6. Δc nature
FORMATTER_LINT_CHURN — Δc spans 54 files (`src/**/*.ts`, `examples/**`, `webpack.*.js`, `jest.config.js`, `README.md`, `.github/**`, `.prettierrc.json`, `.gitattributes`) and every hunk is prettier-2 reformatting (trailing commas, `"`, markdown spacing, EOF newlines); zero semantic source edits (e.g. `src/dependencies.ts` only gains trailing commas).

## 7. Soundness concerns / notes
This task is a soundness liability for a *witnessed breaking-change* benchmark and should be quarantined:
- **test_cmd is `npm run lint`** — a linter, not a test suite; there are no behavioral assertions whatsoever.
- The witnessed definition (AGENTS.md / `2026-06-06-breaking-change-definition`) excludes lint failures; the entire FAIL here is a lint failure.
- Both Δc and Δt are 100% formatter churn with no production-source repair — an agent "passes" by running `prettier --write`, which is unrelated to dependency-update breaking-change repair.
- It evaded the `no_code_pass` flag (it is in the random control set, not the 34 flagged) because operationally it *does* need Δc (source files must be re-formatted); the CSV audit's pass/fail check cannot detect that the underlying failure mode is a disallowed lint failure. A format/lint filter on test_cmd would catch it.

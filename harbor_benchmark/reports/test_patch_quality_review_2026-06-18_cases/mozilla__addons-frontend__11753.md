# Test-patch audit — mozilla__addons-frontend__11753

## 1. Task summary
- Folder: mozilla__addons-frontend__11753
- Ecosystem: npm_and_yarn
- Upgrade: flow-bin 0.176.0 -> 0.183.0
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `npx jest tests/unit/amo/api/test_reviews.js tests/unit/amo/reducers/test_errorPage.js tests/unit/amo/reducers/test_languageTools.js tests/unit/amo/test_tracking.js --no-coverage --passWithNoTests`

## 2. What is the breaking change?
flow-bin 0.183.0 is a Flow typechecker upgrade that tightened checks / changed behavior, prompting a sweep of `.flowconfig` and ~29 source files (per the 2026-06-10 review, 109+/115-) to add/adjust Flow type annotations and, notably, drop runtime parameter-validation guards (`requires a user or addon`, `requires an error`, `errorHandlerId is required`, `languageTools are required`, etc.) in favor of type-level enforcement.

## 3. What does Δt (test.patch) actually do?
- `tests/unit/amo/api/test_reviews.js`: DELETES the `it('requires a user or addon', …)` case from the `getReviews` describe block.
- `tests/unit/amo/reducers/test_errorPage.js`: DELETES the `it('requires an error', …)` case from `loadErrorPage`.
- `tests/unit/amo/reducers/test_languageTools.js`: drops the `fetchLanguageTools` import and DELETES the `describe('fetchLanguageTools', …)` (`requires an errorHandlerId`) and `describe('loadLanguageTools', …)` (`requires language tools`) blocks.
- `tests/unit/amo/test_tracking.js`: changes `tracking.sendEvent()` → `tracking.sendEvent({ action: 'whatever' })` while keeping the `toThrowError(/category is required/)` expectation.
- No new assertions are added; the patch is almost entirely test deletions plus one signature-compatibility edit.

## 4. Does Δt directly exercise the breaking change?
No. The Δt removes the very "requires X" runtime-validation tests that would have detected Δc's removal of those guards, and the lone modified assertion (`sendEvent({ action: 'whatever' })` still expecting `category is required`) does not distinguish P⊕Δm from P⊕Δm⊕Δc — the category guard is retained, so the test passes with or without Δc. Critically, the verifier runs `jest` (unit tests), not `flow check`, so the flow-bin 0.183.0 typechecker migration itself is never exercised by the test command; the deleted runtime-validation tests were the only candidates for a witness and they are gone.

## 5. Coverage verdict
UNWITNESSED — Δt deletes the "requires X" runtime-validation cases (the would-be witnesses for Δc's removal of those guards) and makes one signature-compat edit; the verifier runs jest not flow, so the hidden tests pass on P⊕Δm without Δc.

## 6. Δc nature
MIXED — `.flowconfig` config edit (removes `log.file=./flow/logs/flow.log`) plus a large sweep of `src/amo/**` source files (actions/reviews.js, addonManager.js, api/addonInfo.js, api/index.js, api/reviews.js, components/GetFirefoxButton, RatingManager, Routes, Search, i18n/utils.js, localState.js, middleware/requestId.js, reducers/addons.js, reducers/collections.js, reducers/errorPage.js, reducers/languageTools.js, …) carrying Flow type-annotation and runtime-guard changes for flow-bin 0.183.0.

## 7. Soundness concerns / notes
- Confirmed by the 2026-06-10 review: "Typechecker/tooling migration and no hidden-test witness."
- flow-bin is a dev typechecker; the verifier command runs `jest`, not `flow`, so the typechecker break is structurally not testable by the oracle.
- The Δt is dominated by test deletions — the textbook unwitnessed pattern where the witnessing assertions are removed rather than added, so the residual suite is green with or without the source repair.

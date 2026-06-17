# Test-patch audit — mozilla__addons-frontend__10931

## 1. Task summary
- Folder: mozilla__addons-frontend__10931
- Ecosystem: npm_and_yarn
- Upgrade: redux-saga 0.16.2 -> 1.1.3
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `yarn jest tests/unit/amo/sagas/test_site.js`

## 2. What is the breaking change?
redux-saga 0.16 -> 1.1.3 is a major rewrite: the `Task` API dropped `.done` in favor of `.toPromise()`; `delay` and `takeEvery` moved from `redux-saga`/`redux-saga/lib/internal/utils` to `redux-saga/effects`; the `Token`/internal import paths were removed.

## 3. What does Δt (test.patch) actually do?
- `tests/unit/amo/sagas/test_site.js`: changes `rootTask.done.then(...)` to `(rootTask.toPromise ? rootTask.toPromise() : rootTask.done).then(...)` — a compatibility shim so the test itself runs under v1.
- `tests/unit/amo/sagas/test_utils.js`: moves `takeEvery` import from `redux-saga` to `redux-saga/effects` (v1 layout). NOTE: this file is NOT run by the test_cmd.

## 4. Does Δt directly exercise the breaking change?
No. The test_cmd runs only `test_site.js`, which tests the **site** saga. The two Δc changes are in `src/amo/sagas/reviews.js` (import migration) and `src/amo/server/base.js` (`runningSagas.done` -> `runningSagas.toPromise()`, server-side SSR) — neither is exercised by the site-saga test. The Δt change in `test_site.js` is a test-infra shim (toPromise fallback), not an assertion that catches a source break; `test_utils.js` (the only Δt file that touches the import migration) is not executed.

## 5. Coverage verdict
UNWITNESSED — TEST(P⊕Δm⊕Δt) already PASS: the single executed test (site saga) does not touch the Δc-modified source (`reviews.js`, `base.js`), and Δt is a test-compatibility shim rather than a break-witnessing assertion.

## 6. Δc nature
REAL_SOURCE_REPAIR — `src/amo/sagas/reviews.js` (`delay` import moved to `redux-saga/effects`) and `src/amo/server/base.js` (`await runningSagas.done` -> `await runningSagas.toPromise()`) are genuine v1 migration fixes; they are simply not covered by Δt.

## 7. Soundness concerns / notes
Confirmed unwitnessed (matches the problematic-review flag). The test_cmd targets only `test_site.js`; the Δc repair sites (`reviews.js`, server `base.js`) lie outside its scope. `test_utils.js` (the Δt file most relevant to the import break) is not run. A correct v1 migration in source is not required for the hidden test to pass — the test passes on P⊕Δm alone. Quarantine/exclude from the witnessed main set.

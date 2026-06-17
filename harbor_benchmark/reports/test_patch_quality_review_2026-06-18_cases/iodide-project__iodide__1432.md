# Test-patch audit — iodide-project__iodide__1432

## 1. Task summary
- Folder: iodide-project__iodide__1432
- Ecosystem: npm_and_yarn
- Upgrade: babel-jest 23.6.0 -> 24.7.1 (plus jest 23.6.0 -> 24.7.1 and jest-cli 23.6.0 -> 24.7.1; manifest also renames the jest 23 `setupTestFrameworkScriptFile` option to the jest 24 `setupFilesAfterEnv` array)
- Flagged in problematic_prs_review_2026-06-10.md: YES (row 61 — "Packaged npm task. Δc: `.babelrc` and `__test_helpers__/reps-test-value-cases.js`; Δt: 1 saga test. Exclude. Both unwitnessed and classified as test config/helper only.")
- test_cmd: `npx jest src/editor/actions/sagas/__tests__/eval-queue-saga.test.js --no-coverage --passWithNoTests`

## 2. What is the breaking change?
Jest 24 forbids passing an `async` function to `describe()` (it throws at load time — describe blocks must be synchronous). The graded test file `eval-queue-saga.test.js` has `describe("loadKnownLanguage test", async () => {...})`, which errors under jest 24. (The manifest's `setupTestFrameworkScriptFile`→`setupFilesAfterEnv` rename is the other jest-24 config change, but it is part of Δm, not Δc.)

## 3. What does Δt (test.patch) actually do?
Touches exactly one file: `src/editor/actions/sagas/__tests__/eval-queue-saga.test.js`. A single one-token edit — `describe("loadKnownLanguage test", async () => {` → `describe("loadKnownLanguage test", () => {` (drops the `async` keyword from the describe callback). No new test cases, no assertion changes, no fixtures — this *is* the jest-24 compatibility fix.

## 4. Does Δt directly exercise the breaking change?
No — Δt **is** the fix for the only break that affects the graded test. With Δt applied (async removed), `eval-queue-saga.test.js` loads and runs under jest 24 without Δc: Δc's two changes (`.babelrc` `targets: node: current`, and commenting out `promise_reject` in `__test_helpers__/reps-test-value-cases.js`) do not touch this saga test or its imports, so the test passes on P⊕Δm⊕Δt already. There is no assertion that fails-without-Δc and passes-with-Δc.

## 5. Coverage verdict
UNWITNESSED — TEST(P⊕Δm⊕Δt) = PASS without Δc: removing `async` from `describe` (Δt itself) is what resolves the jest-24 failure for this graded test, and Δc's `.babelrc`/test-helper edits are irrelevant to `eval-queue-saga.test.js`. Matches the problematic-review flag (no_code_pass / latent).

## 6. Δc nature
MIXED — `.babelrc` (build/test config: wraps `@babel/preset-env` with `{ targets: { node: "current" } }` and reformats plugins) and `src/eval-frame/components/reps/__test_helpers__/reps-test-value-cases.js` (a **test helper**, not production source: comments out the `promise_reject` case). Neither file is production consumer code, and neither is exercised by the graded saga test — consistent with the review's "test config/helper only" classification.

## 7. Soundness concerns / notes
- Correctly flagged for exclusion. This is a textbook Level-2 / `no_code_pass` case: Δt carries the actual repair (async-removal) so the oracle test passes before any source fix is applied.
- The Δc is not production code at all — it is babel config + a test helper — so even if it were needed it would not represent a "dependency-update breaking-change repair" of consumer source.
- If kept anywhere, it belongs in the latent/Level-2 reporting set, not the main witnessed benchmark. The graded test should be re-pointed at a test that actually depends on `reps-test-value-cases.js` (or Δc) if a witnessed variant is desired, but as packaged it is unsalvageable as a witnessed item.

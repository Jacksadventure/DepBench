# Test-patch audit — cawa-93__vite-electron-builder__662

## 1. Task summary
- Folder: cawa-93__vite-electron-builder__662
- Ecosystem: npm_and_yarn
- Upgrade: vitest 0.0.136 -> 0.0.137
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `npm run test:main`

## 2. What is the breaking change?
vitest 0.0.137 changed mock lifecycle / `mock.instances` reset semantics such that the original tests (which relied on `mock.instances` persisting across tests) became order-dependent. The human response was to restructure the tests to be self-contained and to refactor the source from a module-level `mainWindow` variable to querying `BrowserWindow.getAllWindows()`.

## 3. What does Δt (test.patch) actually do?
Rewrites `packages/main/tests/unit.spec.ts`: adds `bw.getAllWindows = vi.fn(() => bw.mock.instances)` to the electron mock, switches `expect(mock.instances.length).toBe(n)` → `expect(mock.instances).toHaveLength(n)`, and restructures the "restore existing window" and "destroyed window" tests to create their own window first (instead of relying on state carried over from the first test). No new behavioral assertion is added — the tests still check `mock.instances` length and `restore`/`focus` calls.

## 4. Does Δt directly exercise the breaking change?
No assertion in Δt verifies the new `getAllWindows()` code path. The tests check the same observable behavior (instance count, `restore` called once) that both the original module-variable implementation and the new `getAllWindows()` implementation satisfy when mock state is reset between tests. Per the project's 2026-06-10 oracle run, TEST(P⊕Δm⊕Δt)=PASS — the restructured tests pass on the un-patched source, so there is no fail→pass transition attributable to Δc.

## 5. Coverage verdict
UNWITNESSED — Δt restructures the vitest tests for mock-isolation compatibility but asserts the same window-restore semantics satisfied by both the original and Δc source; the project review confirms "Source-looking but unwitnessed."

## 6. Δc nature
REAL_SOURCE_REPAIR — `packages/main/src/mainWindow.ts` removes the `restoreWindowOrThrow`/`canRestoreWindow` helpers and the module-level `mainWindow` variable, rewriting `restoreOrCreateWindow` to discover windows via `BrowserWindow.getAllWindows()`. A genuine source refactor, but one the run tests do not require.

## 7. Soundness concerns / notes
The Δt adds a `getAllWindows` mock that is only exercised by the Δc source; the original source never calls `getAllWindows()`, yet the tests still pass on it. This is the signature of an unwitnessed task: Δc is a real but unnecessary refactor, and Δt is a test-harness adaptation to the vitest mock-reset change rather than a behavioral oracle for the source change.

# Test-patch audit — marp-team__marp-vscode__176

## 1. Task summary
- Folder: marp-team__marp-vscode__176
- Ecosystem: npm_and_yarn
- Upgrade: @marp-team/marp-cli 0.21.1 -> 0.22.0
- Flagged in problematic_prs_review_2026-06-10.md: NO (random control)
- test_cmd: `npx jest src/marp-cli.test.ts --no-coverage`

## 2. What is the breaking change?
Strictly speaking there is **no dependency-induced break**: marp-cli 0.22.0 is API-compatible with the wrapper's existing usage (`CLIError`/`CLIErrorCode.NOT_FOUND_CHROMIUM` are unchanged) and the old source compiles and the old test passes on P⊕Δm. What changed is that marp-cli 0.22.0 *added* Microsoft Edge as a supported export browser, and the maintainer adapted the "browser not found" error message in `src/marp-cli.ts` to list Edge (on win32/darwin) — a feature adaptation, not a repair of a failure.

## 3. What does Δt (test.patch) actually do?
Touches one file: `src/marp-cli.test.ts`. It replaces the old single test (`'throws error with helpful message when outputed error about Chrome'`, asserting `rejects.toThrow(/Google Chrome/)`) with a parameterized `it.each` table over `win32 | darwin | linux` that asserts the error message contains the expected browser fragments — win32/darwin expect both `/Google Chrome/` and `/Microsoft Edge/`; linux expects `/Google Chrome/` and `/Chromium/`. Each iteration stubs `process.platform` and re-throws the mocked `NOT_FOUND_CHROMIUM` CLIError. No fixtures/snapshots; it is a behavior assertion on the error-message construction.

## 4. Does Δt directly exercise the breaking change?
Yes, in the operational sense. Representative assertion: on `win32`/`darwin`, `await expect(runMarpCli('--version')).rejects.toThrow(/Microsoft Edge/)`. On P⊕Δm⊕Δt the old `src/marp-cli.ts` only ever emits "Google Chrome" (+"Chromium" on linux), so the `/Microsoft Edge/` assertion fails; on P⊕Δm⊕Δc⊕Δt Δc's rewritten `browsers` array emits "Google Chrome or Microsoft Edge" on non-linux → passes. (The linux row passes either way because Chromium was already in the old message.)

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the formal condition holds: Δt's `/Microsoft Edge/` assertion fails on P⊕Δm (old source omits Edge) and passes on P⊕Δm⊕Δc (Δc adds Edge to the message). Caveated below: the "break" is test-manufactured rather than dependency-induced.

## 6. Δc nature
MIXED — `src/marp-cli.ts` (real source: rewrites the not-found-browser error message to build a platform-aware `browsers` array including Microsoft Edge) plus documentation drive-bys `CHANGELOG.md` and `README.md` describing the Edge-support/Chrome-regression change; only `src/marp-cli.ts` is load-bearing for the test.

## 7. Soundness concerns / notes
- **Feature-adaptation dressed as a breaking-change repair.** The dependency did not break the existing source or the existing test — the old test (`/Google Chrome/`) passes on P⊕Δm. Δt *introduces* a stricter assertion (Edge must appear) that the old source does not satisfy, manufacturing the FAIL-without-Δc. This is the inverse of the iodide pattern (where Δt is the fix itself); here Δt is the new requirement and Δc implements it.
- It evaded the `no_code_pass` flag because operationally it does require Δc (Edge missing → fail). But by the spirit of "witnessed breaking change" (a real upgrade-induced failure), this is borderline: there is no failure until Δt asserts new feature behavior.
- Not a quarantine candidate on pure operational grounds, but reviewers may want to tag it as "feature-adaptation" rather than "breaking-change repair" to avoid inflating the benchmark's apparent difficulty.

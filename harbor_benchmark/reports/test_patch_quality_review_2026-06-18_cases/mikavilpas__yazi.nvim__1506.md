# Test-patch audit — mikavilpas__yazi.nvim__1506

## 1. Task summary
- Folder: mikavilpas__yazi.nvim__1506
- Ecosystem: npm_and_yarn
- Upgrade: @tui-sandbox/library 12.1.0 -> 12.2.2 (also transitively bumps @xterm/xterm 5.5 -> 6.0, addon-fit 0.10 -> 0.11, addon-unicode11 0.8 -> 0.9, nan 2.23 -> 2.24)
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `pnpm --dir /app/integration-tests exec tsc --noEmit -p tsconfig.json`

## 2. What is the breaking change?
Δc adds a new `clipboard: { system(), primary() }` accessor to the cypress test-application context (`TerminalTestApplicationContext` / `NeovimContext`), delegating to `underlyingNeovim.clipboard` / `terminal.clipboard` newly exposed by @tui-sandbox/library 12.2.x. There is no other source repair; the yazi binary version bump in `.github/workflows/test.yml` is CI config only.

## 3. What does Δt (test.patch) actually do?
- `cypress/e2e/lsp.cy.ts`: reorders `cy.typeIntoTerminal("q")` to *after* `waitForRenameToHaveBeenConfirmed(nvim)` (timing tweak).
- `cypress/e2e/mouse.cy.ts`: adds `{ force: true }` to an outside-click `.click()`.
- `cypress/e2e/reading-events.cy.ts`: adds `cy.contains("changed")` waits and `cy.contains("changed").should("not.exist")` guards around delete/trash events.
All three are **flaky-test timing/retry fixes** in cypress e2e tests. None reference the new `clipboard` API. None introduce type usage that would exercise the `clipboard` property added by Δc.

## 4. Does Δt directly exercise the breaking change?
No. The test_cmd is `tsc --noEmit` (type-check only); it does not execute the cypress e2e tests at all. Δt's changes are type-valid cypress calls (`{force: true}`, `cy.contains(...)`, statement reorder) that do not introduce any new type dependency on the @tui-sandbox/library 12.2.x surface. There is no assertion in Δt that fails on P⊕Δm and passes on P⊕Δm⊕Δc — Δt is structurally a no-op for the `tsc` verifier.

## 5. Coverage verdict
UNWITNESSED — the verifier (`tsc --noEmit`) does not run the cypress e2e logic Δt touches, and Δt does not add any `clipboard` usage that would require Δc's type/implementation to compile; P⊕Δm⊕Δt passes without Δc (matches `flagged_in_problematic_review: True`).

## 6. Δc nature
MIXED — `integration-tests/cypress/support/tui-sandbox.ts` adds a real `clipboard` accessor (type + implementation) to the test context (REAL source feature wiring for the new library surface), and `.github/workflows/test.yml` bumps the yazi binary `version: v25.5.31 -> v25.12.29` (CI config, not source). The clipboard wiring is plausibly needed for the *library* upgrade but is not exercised by the verifier.

## 7. Soundness concerns / notes
- The test_cmd (`tsc`) and the Δt content (cypress runtime timing fixes) are disjoint: Δt cannot influence the verifier outcome, so the task reduces to "does `tsc --noEmit` pass on P⊕Δm" — and since Δc only *adds* an optional `clipboard` property (the library does not force the project's own context type to require it), tsc passes without Δc.
- The Δt hunks are clearly flaky-test fixes unrelated to the @tui-sandbox/library upgrade; they likely landed in the same PR by coincidence. They would only matter under a cypress runtime verifier, which this task does not use.
- To witness, the test_cmd would need to actually run cypress (or `tsc` would need to enforce that the context type implements a library-required `clipboard` member, which the bundle does not show).

# Test-patch audit — ledgersmb__LedgerSMB__8904

## 1. Task summary
- Folder: ledgersmb__LedgerSMB__8904
- Ecosystem: npm_and_yarn
- Upgrade: babel-jest 29.7.0 -> 30.0.2 (manifest also bumps jest and jest-environment-jsdom to 30.x)
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `yarn jest tests/specs/LoginPage.spec.js --runInBand`

## 2. What is the breaking change?
The Jest 30/jsdom test environment no longer supports the old `window.location` monkeypatch used by the test setup. The repair makes login success behavior injectable: `LoginPage` accepts a `successFn` prop, the login state machine calls `ctx.successFn(e.data)`, and the real app passes a callback that performs the delayed `window.location.assign(...)`.

## 3. What does Δt (test.patch) actually do?
Δt removes the global `window.location.assign = jest.fn()` setup, changes the login mock to return JSON `{ "target": "erp.pl?action=root" }`, mounts `LoginPage` with a `successFn` mock, and asserts that `successFn` receives the parsed target. It also updates unrelated snapshot headers/style lines for other specs, though the verifier targets `LoginPage.spec.js`.

## 4. Does Δt directly exercise the breaking change?
Yes for the executed login spec. On P⊕Δm⊕Δt, the old source still calls `window.location.assign(e.data.target)` and never calls the supplied `successFn`, so the new Jest-compatible assertion fails. With Δc, the component and state machine route success through the injected callback and the hidden test passes.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden test witnesses the source adaptation needed after the Jest/jsdom 30 test-environment change around `window.location` mocking.

## 6. Δc nature
REAL_SOURCE_REPAIR — production Vue/login state-machine code is changed to accept and invoke an injectable success callback while preserving the real app redirect path.

## 7. Soundness concerns / notes
- The break is in the upgraded test stack rather than end-user runtime behavior; it is still a source repair, but narrower than a product dependency API migration.
- The snapshot files in Δt are dead for this verifier command and add noise.

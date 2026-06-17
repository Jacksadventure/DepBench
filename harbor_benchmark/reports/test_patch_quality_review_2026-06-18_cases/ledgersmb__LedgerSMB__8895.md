# Test-patch audit - ledgersmb__LedgerSMB__8895

## 1. Task summary
- Folder: ledgersmb__LedgerSMB__8895
- Ecosystem: npm_and_yarn
- Upgrade: @eslint/js 9.28.0 -> 9.29.0, bundled with Jest/Babel/JSDOM-related updates
- test_cmd: `npx jest tests/specs/LoginPage.spec.js --no-coverage`

## 2. What is the breaking change?
The labeled package is `@eslint/js`, but the exercised break is from the bundled Jest 30/JSDOM environment: the previous test setup replaced `window.location.assign`, while the updated tests avoid mutating `window.location` and inject a login success callback instead.

## 3. What does Delta t do?
Delta t removes the global `window.location.assign` mock, changes the login mock handler to return JSON `{ target: ... }`, mounts `LoginPage` with a `successFn` prop, and asserts that callback is called. It also includes unrelated snapshot updates for other view snapshots, though the verifier only runs `LoginPage.spec.js`.

## 4. Does Delta t directly exercise the breaking change?
Yes, for the Jest/JSDOM test-environment break. Without Delta c, `LoginPage` still redirects through `window.location.assign` and ignores the injected callback expected by the hidden test. Delta c moves redirect behavior behind `successFn`, preserving production redirect in `main-vue.js` while making the component testable under the upgraded environment.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE

## 6. Delta c nature
REAL_SOURCE_REPAIR

## 7. Soundness concerns / notes
- The witnessed dependency is not `@eslint/js`; it is the bundled Jest/JSDOM upgrade. The task instruction is misleading.
- Several Delta t snapshot changes are dead for this verifier because only `LoginPage.spec.js` is executed.

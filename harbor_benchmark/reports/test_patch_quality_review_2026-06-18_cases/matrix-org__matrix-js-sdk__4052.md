# Test-patch audit - matrix-org__matrix-js-sdk__4052

## 1. Task summary
- Folder: matrix-org__matrix-js-sdk__4052
- Ecosystem: npm_and_yarn
- Upgrade: jwt-decode 3.1.2 -> 4.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `yarn jest spec/unit/oidc/validate.spec.ts --no-coverage --runInBand`

## 2. What is the breaking change?
`jwt-decode` v4 exposes `jwtDecode` as a named export instead of the old default import shape used by the source and Jest mocks. The manifest also moves `oidc-client-ts` to 3.0.1, where `SigninState.fromStorageString` becomes async.

## 3. What does Delta t (test.patch) actually do?
`validate.spec.ts` changes `import jwtDecode from "jwt-decode"` to `import { jwtDecode } from "jwt-decode"` and changes the Jest mock to return `{ jwtDecode: jest.fn() }`. `authorize.spec.ts` gets the same import/mock shape plus WebCrypto/TextEncoder setup and a realistic ID token, but that spec is not in the verifier command.

## 4. Does Delta t directly exercise the breaking change?
Yes for `validate.ts`. The verifier runs `validate.spec.ts`, whose hidden mock now matches the v4 named export. Without Delta c, source still imports the default export and calls the wrong binding under v4; with Delta c, `validate.ts` imports `{ jwtDecode }` and the test can pass.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the running hidden test covers the `jwt-decode` v4 import/mocking break in the validation code.

## 6. Delta c nature
REAL_SOURCE_REPAIR - source imports are updated in `validate.ts`, and `authorize.ts` is migrated to await the new `oidc-client-ts` async API.

## 7. Soundness concerns / notes
Only the `validate.ts` half is exercised by the verifier command. The `authorize.ts` async repair is real but mostly untested here because `authorize.spec.ts` is excluded.


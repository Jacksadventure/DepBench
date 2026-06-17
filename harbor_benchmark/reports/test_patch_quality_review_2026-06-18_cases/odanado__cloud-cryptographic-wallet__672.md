# Test-patch audit — odanado__cloud-cryptographic-wallet__672

## 1. Task summary
- Folder: odanado__cloud-cryptographic-wallet__672
- Ecosystem: npm_and_yarn
- Upgrade: @ethereumjs/common 2.6.2 -> 3.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx vitest run packages/web3-provider-adapter/src/get-common.spec.ts --reporter=verbose --threads=false`

## 2. What is the breaking change?
`@ethereumjs/common` v3 changed its module exports and chain-ID API. The old default/CJS interop import and `chainIdBN()` expectation no longer match the package; `Common.custom` also expects a numeric chain ID rather than the old BN path used here. The related `@ethereumjs/tx` v4 bump changes signature `v` handling to `BigInt`, though that path is not selected by the verifier.

## 3. What does Δt (test.patch) actually do?
- Changes the mocked chain ID from `0x1` to `0x123`.
- Updates the assertion from `common.chainIdBN().toString("hex")` to `common.chainId().toString(16)`.

## 4. Does Δt directly exercise the breaking change?
Yes. The selected test imports and runs `getCommon`. On P⊕Δm, the old `@ethereumjs/common` default import / `chainIdBN` API is incompatible with v3. With Δc, `getCommon` imports `{ Hardfork, Common }`, passes `chainId` as a number, and returns an object whose `chainId()` API satisfies the hidden test.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt checks the new `@ethereumjs/common` v3 chain-ID API on the exact source function repaired by Δc.

## 6. Δc nature
REAL_SOURCE_REPAIR — `get-common.ts` migrates imports and chain-ID handling for `@ethereumjs/common` v3; `process-signature.ts` also adapts transaction signature `v` to `BigInt` for the paired `@ethereumjs/tx` bump.

## 7. Soundness concerns / notes
- The verifier does not exercise `process-signature.ts`, so the `@ethereumjs/tx` half of Δc is uncovered.
- The selected `get-common` test is still a valid witness for the declared `@ethereumjs/common` upgrade.

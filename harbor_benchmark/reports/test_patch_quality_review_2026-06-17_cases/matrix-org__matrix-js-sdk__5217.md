# Test-patch audit — matrix-org__matrix-js-sdk__5217

## 1. Task summary
- Folder: matrix-org__matrix-js-sdk__5217
- Ecosystem: npm_and_yarn
- Upgrade: @matrix-org/matrix-sdk-crypto-wasm 17.1.0 -> 18.0.0
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `pnpm vitest run spec/unit/rust-crypto/rust-crypto.spec.ts spec/unit/rust-crypto/verification.spec.ts`

## 2. What is the breaking change?
v18 renamed the `QrCodeMode` enum to `QrCodeIntent` (runtime: old export gone) and changed `OlmMachine.getIdentity()` return type so that callers must narrow/cast to `OwnUserIdentity` / `OtherUserIdentity`. Both are real API changes — but only the enum rename has a runtime effect; the `getIdentity` change is purely type-level.

## 3. What does Δt (test.patch) actually do?
- `MSC4108SignInWithQR.spec.ts` and `MSC4108SecureChannel.spec.ts`: rename `QrCodeMode`→`QrCodeIntent` in imports and `generateCode(...)` calls (runtime-behavioral).
- `rust-crypto.spec.ts`: import `type OtherUserIdentity` and cast a mock `as unknown as OtherUserIdentity` (type-level only).
- `verification.spec.ts`: import `type OtherUserIdentity` and cast `getIdentity(...)` results `as OtherUserIdentity` in three places (type-level only).

## 4. Does Δt directly exercise the breaking change?
Not the tests that actually run. The `test_cmd` runs ONLY `rust-crypto.spec.ts` and `verification.spec.ts`, whose Δt edits are pure TypeScript `as` casts — stripped at runtime by vitest (which uses esbuild/swc and does not type-check). The `getIdentity()` runtime return is identical in v17 and v18, so those tests pass on P⊕Δm without Δc. The behavioral Δt (the `QrCodeMode`→`QrCodeIntent` rename that would throw at runtime because `QrCodeMode` is undefined in v18) lives in the MSC4108 spec files, which are NOT in the test_cmd.

## 5. Coverage verdict
UNWITNESSED — the test_cmd executes only the two spec files whose Δt changes are type-only casts with no runtime effect under vitest; the runtime-breaking Δt (enum rename) is in spec files excluded from the verifier command, so TEST(P⊕Δm⊕Δt)=PASS without Δc.

## 6. Δc nature
REAL_SOURCE_REPAIR — `MSC4108SignInWithQR.ts` and `MSC4108SecureChannel.ts` rename `QrCodeMode`→`QrCodeIntent`; `rust-crypto.ts` refactors `getIdentity` call sites to use a `getOwnIdentity()` helper with `as` casts. Real source edits, but not exercised at runtime by the run tests.

## 7. Soundness concerns / notes
This is a test_cmd / Δt mismatch bug: the behavioral witness (MSC4108 enum rename) was placed in spec files that the verifier never runs, while the run specs carry only type-level casts. Either the test_cmd should include `spec/unit/rendezvous/...` and `spec/integ/rendezvous/...`, or the type casts should be backed by runtime assertions. Matches the 2026-06-10 review: "Exclude from witnessed main set unless a stricter hidden test can be added."

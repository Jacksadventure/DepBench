# Test-patch audit — alveusgg__alveusgg__871

## 1. Task summary
- Folder: alveusgg__alveusgg__871
- Ecosystem: npm_and_yarn
- Upgrade: @eslint/js 9.15.0 -> 9.16.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `pnpm exec vitest run --reporter=verbose`

## 2. What is the breaking change?
The manifest patch is a broad frontend dev-toolchain bump around ESLint, TypeScript, Vitest, Node typings, and related packages. The observed repair is not an ESLint rule change; it updates web-push and base64 helpers to accept `BufferSource` / `ArrayBufferLike` values instead of assuming every byte payload is a `Uint8Array`.

## 3. What does Δt (test.patch) actually do?
`base64url.test.ts` and `push-content-encryption.test.ts` are rewritten to pass raw `.buffer` values in several places: `decodedBuffer`, `HKDF_expand` info, `createCipherText` payload, `encryptContent` payload, `createCipherHeader` key id, and VAPID coordinate slices. One assertion also compares `cipherSalt` through a `Uint8Array` wrapper.

## 4. Does Δt directly exercise the breaking change?
Yes. With Δt applied but without Δc, tests such as `createCipherText` and `encryptContent` pass an `ArrayBuffer` into code that still uses `payload.length` and `payload.subarray(...)`, which are `Uint8Array` assumptions. Δc changes the implementation to use `byteLength`, `slice`, `.buffer`, and `ArrayBufferLike`-compatible helper signatures, so the same tests exercise the repaired behavior.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden tests drive the post-upgrade byte-buffer contract and should fail deterministically on P⊕Δm⊕Δt, then pass after the source accepts `ArrayBufferLike` inputs.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc is production TypeScript in encryption, web-push, VAPID, array-buffer, and base64url utilities. It is not test-only or lint-only churn.

## 7. Soundness concerns / notes
The named dependency is `@eslint/js`, but the manifest patch includes multiple coupled dev-toolchain upgrades. The witnessed issue is best described as an ArrayBuffer/typed-array compatibility repair surfaced by that dependency bundle, not as an ESLint semantic break.

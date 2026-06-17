# Test-patch audit — solana-labs__solana-program-library__4301

## 1. Task summary
- Folder: solana-labs__solana-program-library__4301
- Ecosystem: npm_and_yarn
- Upgrade: @solana/spl-token 0.1.8 -> 0.3.7
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest --ci`

## 2. What is the breaking change?
@solana/spl-token 0.1.8 -> 0.3.7 is a major API rewrite: the `Token` class (with static `Token.getAssociatedTokenAddress`, `Token.createApproveInstruction`, `Token.createAssociatedTokenAccountInstruction`) and the `new Token(...)` constructor are removed; replaced by functional helpers `getAssociatedTokenAddressSync`, `createAssociatedTokenAccountIdempotentInstruction`, `createApproveInstruction`, `getAccount`. `AccountLayout` is now exported from `@solana/spl-token` (165-byte layout). `getAccount` throws `TokenAccountNotFoundError` (replacing the old "Invalid token account" `Error`). Account `amount` is now a `bigint` (not `BN`), so `.toNumber()` is gone.

## 3. What does Δt (test.patch) actually do?
- `stake-pool/js/test/instructions.test.ts`: imports `TokenAccountNotFoundError`; changes `==` to `===`; updates the `depositSol` success assertions from `getAccountInfo` calls `toBe(2)` / `instructions toHaveLength(2)` to `toBe(1)` / `toHaveLength(3)` (new idempotent-ATA flow); changes `withdrawSol`/`withdrawStake` invalid-account expectations from `Error('Invalid token account')` to `TokenAccountNotFoundError`.
- `stake-pool/js/test/mocks.ts`: imports `AccountLayout` and `TOKEN_PROGRAM_ID` from `@solana/spl-token` (instead of local `AccountLayout`); changes `poolTokenAccount` to a real base58 pubkey; rewrites `mockTokenAccount` to a 165-byte buffer with the real `AccountLayout.encode` fields (`BigInt` amounts, `delegateOption`, `state:1`, `isNativeOption`, `closeAuthorityOption`, owner = `TOKEN_PROGRAM_ID`).

## 4. Does Δt directly exercise the breaking change?
Yes. Representative assertions that fail on P⊕Δm and pass on P⊕Δm⊕Δc:
```
expect((connection.getAccountInfo as jest.Mock).mock.calls.length).toBe(1);
expect(res.instructions).toHaveLength(3);
...
await expect(withdrawSol(connection, stakePoolAddress, tokenOwner, solReceiver, 1))
  .rejects.toThrow(TokenAccountNotFoundError);
```
On P⊕Δm the original source imports the removed `Token` class and calls `Token.getAssociatedTokenAddress` / `Token.createApproveInstruction` (`Token` is undefined in 0.3.7) and the old `getTokenAccount` throws `Error('Invalid token account')`, so the above assertions (call count 1, instruction length 3, `TokenAccountNotFoundError`) fail. Δc migrates to the functional API, satisfying the assertions.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt directly pins the new spl-token 0.3.7 behavior (idempotent-ATA instruction count, single `getAccountInfo` call, `TokenAccountNotFoundError`, `bigint` amounts) that Δc's API migration produces; FAIL on P⊕Δm, PASS on P⊕Δm⊕Δc.

## 6. Δc nature
REAL_SOURCE_REPAIR — `stake-pool/js/src/index.ts` migrates from `Token.*` to `getAssociatedTokenAddressSync`/`createAssociatedTokenAccountIdempotentInstruction`/`getAccount`/`createApproveInstruction` and drops `rentFee`; `src/utils/token.ts` is DELETED; `src/layouts.ts` removes the custom `AccountLayout`; `src/utils/math.ts` adds `bigint` handling to `lamportsToSol`; `src/utils/index.ts` drops the `./token` re-export.

## 7. Soundness concerns / notes
Clean, well-witnessed task. Δt's behavioral assertions (instruction count, call count, typed error) are tied to the new API shape Δc implements, not just compile. `npx jest --ci` runs the whole crate test suite; the shared `mocks.ts` rewrite is consistent with the new `AccountLayout`. No soundness concerns.

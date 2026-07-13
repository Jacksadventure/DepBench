# Case study: solana-labs/solana-program-library #4301 — @solana/spl-token 0.1.8 → 0.3.7 (npm, /stake-pool/js)

**Task:** DepBench `solana-labs__solana-program-library__4301` — bump `@solana/spl-token` from 0.1.8 to 0.3.7 in `stake-pool/js`.
**Task PR created:** 2023-05-15T12:58:38Z (= CUTOFF) by dependabot[bot]; repaired by maintainer **Jon Cinque** with a single commit "Accommodate new update, some cleanup" (42a20a3d, 2023-05-18T12:08:40Z); merged 2023-05-18T12:36:06Z. +113/−236, 9 files. https://github.com/solana-labs/solana-program-library/pull/4301
**Upstream:** `@solana/spl-token` — which lives in **`token/js` of the very same monorepo**. 0.2.0 (the Token-class removal) published to npm 2022-02-17; 0.3.7 published 2023-01-10. Both >4 months before cutoff.
**Benchmark outcome:** solved by **0 / 10** harness×model configurations.
**Local artifacts:** `/Users/hrz/Documents/GitHub/DependAgent/DepBench/dataset/tasks/solana-labs__solana-program-library__4301/` (instruction.md, solution/code.patch, solution/manifest.patch, tests/test.patch).

---

## Step 1 — The breaking change: repair facts

spl-token 0.2.0 was a ground-up TypeScript rewrite (PR #2539) that deleted the `Token` god-class and its static methods in favor of standalone tree-shakeable functions, replaced BN amounts with native `bigint`, and exported working buffer layouts and typed errors. The stake-pool client (`stake-pool/js/src/{index,layouts}.ts`, `src/utils/token.ts`) used the old API pervasively.

Ground-truth repair facts (from solution/code.patch):

| # | Fact | Where in ground truth | Exercised by hidden tests? |
|---|------|----------------------|---------------------------|
| F1 | Named exports changed: `Token`, `AccountInfo`, `MintInfo` gone; import standalone `getAccount`, `getAssociatedTokenAddressSync`, `createApproveInstruction`, `createAssociatedTokenAccountIdempotentInstruction` | src/index.ts imports; src/layouts.ts drops `AccountInfo` import | Implicitly (compile) |
| F2 | `Token.getAssociatedTokenAddress(ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID, mint, owner)` (async, program IDs first) → `getAssociatedTokenAddressSync(mint, owner)` (sync; program IDs now optional trailing params) | withdrawStake, withdrawSol, depositStake, depositSol | Implicitly (compile + counts) |
| F3 | `Token.createApproveInstruction(TOKEN_PROGRAM_ID, acct, delegate, owner, [], amount)` → `createApproveInstruction(acct, delegate, owner, amount)` — program ID and multiSigners dropped/optional | withdrawStake, withdrawSol | Implicitly |
| F4 | Check-then-create ATA pattern (RPC `getAccountInfo` probe + `Token.createAssociatedTokenAccountInstruction`) → **unconditionally push `createAssociatedTokenAccountIdempotentInstruction(payer, ata, owner, mint)`** (new in 0.3.6) | depositStake, depositSol; deletes `addAssociatedTokenAccount` helper | **Yes, hard:** depositSol test asserts `getAccountInfo` mock called exactly **1** time and `res.instructions` has length **3** |
| F5 | Custom `getTokenAccount` wrapper (decode + mint check + `throw new Error('Invalid token account')`) → `getAccount(connection, addr)`, letting the library's **`TokenAccountNotFoundError` propagate** | withdrawStake, withdrawSol; deletes src/utils/token.ts entirely | **Yes, hard:** two tests assert `rejects.toThrow(TokenAccountNotFoundError)` |
| F6 | `account.amount` is now `bigint`, not BN — drop `.toNumber()`; `lamportsToSol` extended to accept `bigint` | src/index.ts balance checks; src/utils/math.ts | Yes (balance-check test with mocked amount) |
| F7 | spl-token's own `AccountLayout` now works (the 0.1.x one didn't — old code carried a hand-rolled copy with the comment "AccountLayout.encode from @solana/spl-token doesn't work") → delete local layout | src/layouts.ts | Yes — hidden mocks.ts imports `AccountLayout` from `@solana/spl-token`, encodes a 165-byte account with bigint fields, `owner: TOKEN_PROGRAM_ID` |
| F8 | **Discretionary:** drop the `rentFee` field from `depositStake`/`depositSol` return values (made possible by F4 removing the rent-exemption RPC round-trip) | src/index.ts | Indirectly — the call-count assertion (F4) forces removing the RPC probe, which is what computed rentFee |

**The oracle trap.** The hidden test.patch (taken verbatim from the human PR) *flips* the visible assertions:

- visible: `expect(...getAccountInfo...).toBe(2)`, `toHaveLength(2)`, `rejects.toThrow(Error('Invalid token account'))`
- hidden: `toBe(1)`, `toHaveLength(3)`, `rejects.toThrow(TokenAccountNotFoundError)`

These are **mutually exclusive**: no source change passes both. The ground-truth solution fails the visible tests; anything that passes the visible tests fails the hidden ones. The instruction ("so that the existing tests pass") actively steers agents toward the losing side.

## Step 2 — What agents actually did wrong

Trajectories/verify logs examined: `gpt55__copilot_cli` and `claude48__claude_code` (both reward 0.0; grep `solana-labs__solana-program-library__4301` in `/Users/hrz/Documents/GitHub/DependAgent/DepBench/{trajectories,verify_logs}/*.jsonl.gz`).

Both agents did the *hard part right and the "easy" part wrong*:

- **claude48__claude_code** (115 steps): read all sources, ran `npm install @solana/spl-token@0.3.7`, then greppped `node_modules/@solana/spl-token/lib/types/` for the exact new signatures (`getAssociatedTokenAddress`, `createApproveInstruction`, constants, `getMint`). It correctly mapped F1–F3 and F6-ish, then **deliberately preserved legacy semantics**: kept `src/utils/token.ts` with `getTokenAccount` still throwing `Error('Invalid token account')`, kept the check-then-create ATA + rentFee logic using non-idempotent `createAssociatedTokenAccountInstruction`, and kept a local `AccountLayout`. Result: `tsc` exit 0, **all 17 visible tests green** — agent declared victory ("All green. The upgrade is complete.").
- **gpt55__copilot_cli** (94 steps): same shape. It even read `node_modules/@solana/spl-token/src/errors.ts` (where `TokenAccountNotFoundError` is defined) and `src/state/account.ts` — i.e., it *saw* the typed-error mechanism — but wrote a compatibility shim ("added a local token account layout type to preserve existing behavior"), passing build + lint + visible tests.

Verify failures are **identical across both configs** (and per the 0/10 stat, presumably the pattern for all):

```
Expected constructor: TokenAccountNotFoundError
Received constructor: Error
Received message: "Invalid token account"        ← F5 gap
...
expect((connection.getAccountInfo as jest.Mock).mock.calls.length).toBe(1)   ← F4 gap
expect(res.instructions).toHaveLength(3)
```

**Gap statement:** not an API-knowledge gap. Both agents had (and used) the complete 0.3.7 source/typings in node_modules. The gap is **semantic modernization vs. behavior preservation**: the hidden oracle rewards the maintainer's discretionary refactor (propagate library errors, idempotent ATA creation, drop rentFee), while the visible tests — which agents used as their oracle, as the instruction told them to — reward the opposite.

## Step 3 — Upstream mining at cutoff (all evidence pre-2023-05-15)

The "upstream repository" is `token/js` **in the same monorepo** — same checkout, two directories up from the client code.

| Fact | Documented where (pre-cutoff) | Evidence |
|------|------------------------------|----------|
| F1 (Token class removed) | `token/js/README.md`, "Upgrading from 0.1.x" section — present at tag `token-js-v.0.3.6` (npm-published 2022-10-28) and **shipped inside the npm 0.3.7 tarball** (verified: `package/README.md` line 83), i.e. sitting in `node_modules/@solana/spl-token/README.md` in the task container after install | "The `@solana/spl-token` library as of version 0.2.0 does not have the `Token` class. Instead the actions are split up and exported separately." Plus an FAQ literally titled "**No export named Token**" that reproduces the exact SyntaxError a naive upgrade hits. https://github.com/solana-labs/solana-program-library/blob/token-js-v.0.3.6/token/js/README.md |
| F1 (rewrite provenance) | PR #2539 "Rewrite spl-token-js in TypeScript" (jordaaash), merged 2021-12-14, +5086/72 files; PR #2641 "Prepare Token TypeScript client for release", merged 2021-12-28 | #2641 body foresaw the whole problem: "There will be a lot of users trying to use the old Token class API from tutorials they find, so we'll probably need to provide a migration guide". https://github.com/solana-labs/solana-program-library/pull/2539 , /pull/2641 |
| F1 (official docs) | PR #2575 "Added token ts docs", merged 2022-02-19 → spl.solana.com/token gained JS/TS examples for every operation using the new function API | body: "I have provided the javascript/typescript references for all the CLI reference material found on spl.solana.com/token." https://github.com/solana-labs/solana-program-library/pull/2575 |
| F2 (getAssociatedTokenAddressSync) | `token/js/test/unit/index.test.ts` at v.0.3.6 — test `'getAssociatedTokenAddressSync matches getAssociatedTokenAddress'`; signature in `token/js/src/state/mint.ts` | in-repo unit test demonstrates both the sync variant and the new (mint, owner) arg order |
| F3 (createApproveInstruction) | `token/js/src/instructions/approve.ts` at v.0.3.6; `.d.ts` in node_modules (claude48 actually printed it) | signature `createApproveInstruction(account, delegate, owner, amount, multiSigners = [], programId = TOKEN_PROGRAM_ID)` |
| F4 (idempotent ATA) | PR #3558 "[token-js]: JS binding for CreateIdempotent instruction", merged 2022-10-06 (released in 0.3.6); on-chain instruction added in PR #2883 "associated-token-account: Add CreateIdempotent instruction", merged 2022-02-09; e2e test `token/js/test/e2e/create.test.ts` at v.0.3.6 | test comment/flow spells out the *purpose*: "creating again should cause TX error … // when creating again but with idempotent mode, TX should not throw error" — i.e., this instruction exists precisely to replace the check-then-create pattern the old stake-pool helper implemented. https://github.com/solana-labs/solana-program-library/pull/3558 |
| F5 (getAccount throws TokenAccountNotFoundError) | `token/js/src/state/account.ts` at v.0.3.6, lines 96–104 & 170–171 | `export async function getAccount(connection, address, commitment?, programId = TOKEN_PROGRAM_ID): Promise<Account>` … `if (!info) throw new TokenAccountNotFoundError(); if (!info.owner.equals(programId)) throw new TokenInvalidAccountOwnerError();` — also shipped as source in the npm tarball (gpt55 greppped exactly this file in node_modules) |
| F6 (bigint amount) | `token/js/src/state/account.ts`: `amount: bigint;` in the `Account` interface; e2e test asserts `expect(accountInfo.amount).to.eql(BigInt(0))` | in node_modules typings too |
| F7 (working AccountLayout, ACCOUNT_SIZE=165) | `token/js/src/state/account.ts` at v.0.3.6: `export const ACCOUNT_SIZE = AccountLayout.span` | gpt55's trajectory shows it read this very region |
| F8 (drop rentFee) | **Nowhere.** This is an API change of the stake-pool client itself, decided in the repair commit | undocumented anywhere pre-PR |

Also pre-cutoff: Solana Cookbook token page migrated to the new API on 2022-02-22 (solana-dev-adv/solana-cookbook#250, +644/−390, 29 files) — the exact resource the README's migration section points to.

**Bottom line for Step 3:** every mandatory fact (F1–F7) was documented *and demonstrated in executable test form* before cutoff — inside the same repository checkout (`token/js/README.md`, `token/js/test/unit`, `token/js/test/e2e`, `token/js/src/state/account.ts`), and a large subset was additionally injected into the agents' own `node_modules` the moment they ran `npm install`. Only F8 (rentFee removal) was truly unknowable.

## Step 4 — Sibling mining at cutoff (GHArchive via play.clickhouse.com)

Queries (table `github_events`; all filtered `created_at < '2023-05-15 12:58:38'`):

```sql
-- bot-style bumps
SELECT count() FROM github_events
WHERE event_type='PullRequestEvent' AND action='closed' AND merged=1
  AND created_at < '2023-05-15 12:58:38'
  AND title LIKE '%@solana/spl-token from 0.1%';
-- => 28 (all versions); full row listing with additions/deletions/changed_files/commits pulled with a second query

-- manual migrations
SELECT repo_name, number, title, created_at, additions, deletions, changed_files
FROM github_events
WHERE event_type='PullRequestEvent' AND action='closed' AND merged=1
  AND created_at BETWEEN '2022-02-01' AND '2023-05-15 12:58:38'
  AND title ILIKE '%spl-token%' AND title NOT ILIKE '%registry%' AND title NOT ILIKE '%swap%'
  AND (title ILIKE '%0.2%' OR title ILIKE '%0.3%' OR title ILIKE '%upgrad%' OR title ILIKE '%migrat%' OR title ILIKE '%new%')
ORDER BY created_at;
```

**Stratum size.** Merged PRs whose title crosses the 0.1.x → 0.2/0.3 boundary before cutoff: **14 events** (8 are `governance-ui` forks of the same Dependabot PR; others: CodeCrowCorp/cro-website #6 & #136, ecoWarriors/stake-pool-ui #16 & #52, jstarry/solana #609 fork-mirror). **Repair-signal siblings among the bot bumps (commits>1 OR changed_files>3): 0** — every one is a manifest+lockfile-only merge. The cautionary tale in the stratum is negative signal: **solana-labs/governance-ui #562** (bump 0.1.8→0.2.0, merged 2022-04-10 18:42) was **reverted two hours later by #564** ("Revert \"npm: bump @solana/spl-token from 0.1.8 to 0.2.0 (#562)\"", merged 2022-04-10 20:44) — naive merge without code repair broke the build.

**The real repair knowledge lives in manually-titled migration PRs**, which title-based bump mining misses:

- **metaplex-foundation/metaplex-program-library #299** "chore: upgrade spl-token package", merged 2022-03-11, +730/−461, 51 files. Contains the *same* repair facts, hunk-for-hunk:
  ```diff
  -  const createApproveIx = Token.createApproveInstruction(
  +  const createApproveIx = createApproveInstruction(
  -  const associatedTokenAccount = await Token.getAssociatedTokenAddress(
  +  const associatedTokenAccount = await getAssociatedTokenAddress(tokenMint, tokenOwner);
  ```
  (F1, F2, F3, F6 — also drops `.amount.toNumber()` patterns.)
- **marinade-finance/marinade-ts-sdk #35** "Update @solana/spl-token to 0.3.6", merged 2023-01-16, 5 files. Nails F1 + **F5** — replaces a wrapper *just like stake-pool's* and handles the typed error:
  ```diff
  -import { AccountInfo, ASSOCIATED_TOKEN_PROGRAM_ID, Token, TOKEN_PROGRAM_ID } from '@solana/spl-token'
  +import { createAssociatedTokenAccountInstruction, getAccount, TokenError } from '@solana/spl-token'
  -    await getTokenAccountInfo(mintClient, associatedTokenAccountAddress)
  +    await getAccount(anchorProvider.connection, associatedTokenAccountAddress)
  +    if (!(err instanceof TokenError) || err.name !== 'TokenAccountNotFoundError') {
  ```
- **solana-labs/solana #25044** "chore: update dev dep @solana/spl-token to 0.2.0", merged 2022-05-06, +435/−826: `Token.createMint` → `splToken.createMint`, `splToken.createAccount`, `splToken.mintTo`, `splToken.transfer` (F1 across the whole action surface).
- **solana-dev-adv/solana-cookbook #250** (2022-02-22, 29 files) — documentation-grade before/after for nearly every call site.
- **In-repo sibling five days before cutoff:** solana-labs/solana-program-library **#4160** (token-lending/js, 0.2.0→0.3.7, merged 2023-05-10) — manifest-only (dev-dep), no code signal.

No sibling anywhere uses `createAssociatedTokenAccountIdempotentInstruction` in a 0.1.x migration before cutoff (it was only 7 months old); F4's *unconditional-push* idiom is documented only by upstream's own e2e test and PR #3558. And no sibling can reveal F8 or the hidden tests' exact counts.

## Step 5 — Verdict

**Knowability matrix (pre-PR):**

- From upstream docs (in-repo README + spl.solana.com + cookbook): F1, F2, F3, F6 — explicit, with the README's "No export named Token" FAQ matching the first compile error verbatim.
- From upstream code+tests (token/js, same checkout; also npm tarball in node_modules): F1–F7, including the two facts the hidden tests weaponize — `getAccount` throwing `TokenAccountNotFoundError` (account.ts L170) and the idempotent-ATA-replaces-check-then-create idiom (create.test.ts).
- From siblings: F1, F2, F3, F5, F6 (metaplex #299, marinade #35, solana #25044). Not F4's idempotent variant, not F7's layout swap.
- From nowhere: F8 (rentFee API removal), and the hidden tests' concrete expectations (`toBe(1)`, `toHaveLength(3)`, the new mock pubkey, `AccountLayout` sourced from spl-token in mocks).

**Sibling stratum at cutoff:** 14 merged 0.1.x→0.2+ title-matched bump PRs, **0 with repair signal** (one high-salience revert: governance-ui #562→#564); ≥5 substantial manual-migration PRs carrying the actual repair facts.

**Minimal context artifact that would plausibly have flipped the task:** a short migration brief stating (1) replace bespoke `getTokenAccount`-style wrappers with `getAccount()` and **let `TokenAccountNotFoundError`/`TokenInvalidAccountOwnerError` propagate** — do not re-wrap in generic Errors [source: token/js/src/state/account.ts + marinade #35]; (2) replace check-then-create ATA logic (and its rent-fee RPC probe) with an **unconditionally pushed `createAssociatedTokenAccountIdempotentInstruction`** [source: PR #3558 + token/js e2e create.test.ts]; (3) `amount` is `bigint` now. Crucially it must carry the meta-instruction: *"grading uses the post-upgrade test suite; pre-upgrade assertions that encode old wrapper behavior (generic 'Invalid token account' errors, RPC-probe call counts) will be inverted — migrate semantics, don't preserve them."* Items (1)–(2) exactly close the observed agent gap; without the meta-instruction, agents will revert them the moment the visible tests go red.

**The self-dependency angle.** Yes — everything needed was already inside the repo checkout. The dependency's complete 0.3.x source, its README with a dedicated "Upgrading from 0.1.x" section, and unit/e2e tests demonstrating every replacement API sat in `token/js/`, two directories from the code being fixed; `npm install` then copied the README, full `src/`, and typings into `node_modules` as well. Agents *did* exploit the node_modules copy — both greppped `.d.ts`/`src` files and mapped F1–F3+F6 correctly, producing compiling, visible-test-green migrations. Neither ever looked at `../../token/js` (0 references in both trajectories), and neither opened the README migration guide sitting in node_modules. They failed anyway because the binding constraint was not context availability but **oracle divergence**: the hidden tests encode the maintainer's discretionary modernization (F4/F5/F8), the visible tests encode the legacy behavior, and the two are contradictory. Perfect in-repo mining narrows the gap to a judgment call ("be idiomatic, not faithful") — it cannot mechanically resolve it.

**Surprises / facts even perfect mining wouldn't surface:**
1. **The task is an oracle trap, not a knowledge test.** No patch satisfies both visible and hidden assertions (getAccountInfo call-count 2 vs 1; instruction count 2 vs 3; `Error` vs `TokenAccountNotFoundError`). 0/10 is overdetermined: any agent that runs the visible suite converges on the losing behavior — the better the agent's test discipline, the more certainly it fails. Both examined agents ended their runs at "all 17 tests green."
2. The repairer was Jon Cinque, an spl-token maintainer — the ground truth is insider-idiomatic ("some cleanup"), including the semver-relevant, wholly unknowable removal of `rentFee` from the client's own public return type.
3. The bot-bump sibling stratum is pure noise for this dependency (0 repair-signal events); all migration knowledge is in differently-titled manual PRs, arguing for API-symbol-based (e.g., `Token.createApproveInstruction` removal) rather than title-based sibling mining.
4. The npm tarball ships the library's full TypeScript source and the migration README — for this package, "upstream mining" is achievable via `ls node_modules` alone; agents used it for signatures but never for the prose that would have told them *how the ecosystem expects the migration to be done*.

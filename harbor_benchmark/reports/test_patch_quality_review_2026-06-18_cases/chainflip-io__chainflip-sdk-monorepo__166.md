# Test-patch audit — chainflip-io__chainflip-sdk-monorepo__166

## 1. Task summary
- Folder: chainflip-io__chainflip-sdk-monorepo__166
- Ecosystem: npm_and_yarn
- Upgrade: ethers 5.7.2 -> 6.7.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `pnpm --filter sdk-shared --filter sdk --filter cli test:ci`

## 2. What is the breaking change?
ethers v6 removes the v5 `providers` namespace, changes many numeric return/value types from `BigNumber` to native `bigint`, changes transaction receipts from `transactionHash` to `hash`, and changes generated TypeChain contract surfaces such as `address`/`target`, `getAddress()`, and bytes argument handling. The source has to migrate imports, transaction parameter types, receipt properties, address helpers, and regenerated ethers-v6 ABI bindings.

## 3. What does Δt (test.patch) actually do?
Δt updates CLI, SDK, shared contract, state-chain-gateway, vault, schema, and snapshot tests. Representative changes include expected CLI handler amounts from strings to `1000000000n`, mocks from `{ transactionHash: ... }` to `{ hash: ... }`, `ethers.BigNumber` mock values to `bigint`, contract address expectations from `address` to `target`, vault call bytes from `[]` to `""`, and schema fixtures from string amounts to bigint amounts.

## 4. Does Δt directly exercise the breaking change?
Yes. For example, `packages/shared/src/vault/__tests__/executeSwap.test.ts` now calls `executeSwap({ amount: 1n, ... })` and expects mocked v6 receipts with `{ hash: "hello world" }`, while the old source still accepts string amounts, passes `[]` for bytes arguments, uses v5 `ContractReceipt`/`transactionHash`, and relies on v5 `BigNumber` behavior. The CLI snapshots similarly expect bigint amounts after the command parser, which old source does not produce.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden tests encode ethers-v6 observable API and type behavior, so P⊕Δm⊕Δt would fail on old v5-shaped source and P⊕Δm⊕Δc⊕Δt is the intended repaired state.

## 6. Δc nature
MIXED — Δc contains real source migration across `packages/{cli,sdk,shared,swap}/src`, regenerated TypeChain ABI/factory files under `packages/shared/src/abis`, and lint-ignore churn.

## 7. Soundness concerns / notes
The witness is broad and realistic for an ethers major upgrade, but much of Δc is generated ABI churn; the verifier samples several high-value API surfaces rather than every generated binding.

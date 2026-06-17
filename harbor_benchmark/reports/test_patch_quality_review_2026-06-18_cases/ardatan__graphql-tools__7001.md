# Test-patch audit — ardatan__graphql-tools__7001

## 1. Task summary
- Folder: ardatan__graphql-tools__7001
- Ecosystem: npm_and_yarn
- Upgrade: `@envelop/core` 5.2.0 -> 5.2.1, with related `@envelop/live-query`, promise-helper, and Svelte patch bumps
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest packages/executor/src/execution/__tests__/stream-test.ts tests/envelop.spec.ts --no-coverage --passWithNoTests`

## 2. What is the breaking change?
The dependency bump pulls in newer promise-helper behavior and changes observable GraphQL execution/envelop integration behavior. The executor’s old code eagerly wrapped values in promises (`async` callbacks, `Promise.all`) and did not preserve the newer stream/result sequencing expected by the upgraded stack. Envelop/Yoga warning plumbing also needed to route through the host logger.

## 3. What does Δt (test.patch) actually do?
It updates stream directive expectations so incremental payloads are split differently and `hasNext` remains true until a final `{ hasNext: false }` result. It also updates the envelop subscribe test to pass `contextValue`, compare the printed document rather than raw object identity, and assert the executor receives the expected context.

## 4. Does Δt directly exercise the breaking change?
Yes. The stream tests exercise the executor changes in `execute.ts` and `promiseForObject.ts`, especially the `handleMaybePromise` path and final stream payload shape. The envelop test exercises the changed integration contract around execution request shape and context propagation under the upgraded `@envelop/core`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden Jest tests encode the new post-upgrade execution/envelop behavior and require the Δc source changes to pass.

## 6. Δc nature
MIXED — real source repairs in executor/envelop/yoga packages plus changeset metadata files.

## 7. Soundness concerns / notes
- The manifest patch includes several adjacent patch bumps (`@envelop/live-query`, Svelte), but Δt focuses on executor/envelop behavior.
- The test command uses a broad Jest path pattern with `--passWithNoTests`; here it still matches the patched executor and envelop tests.

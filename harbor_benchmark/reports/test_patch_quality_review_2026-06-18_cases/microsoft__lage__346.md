# Test-patch audit — microsoft__lage__346

## 1. Task summary
- Folder: microsoft__lage__346
- Ecosystem: npm_and_yarn
- Upgrade: jest 27.2.0 -> 29.0.3
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest packages/cache/tests/BackfillCacheProvider.test.ts ... packages/target-graph/tests/TargetGraphBuilder.test.ts --no-coverage --passWithNoTests`

## 2. What is the breaking change?
This is primarily a Jest/ts-jest 29 migration: package manifests bump Jest/@types/ts-jest, shared Jest config moves from deprecated `globals/preset` style to explicit `transform`, and Jest 29's pretty-format/snapshot output changes inline and stored snapshots.

## 3. What does Δt (test.patch) actually do?
It updates Jest-facing tests: removes one option from `BackfillCacheProvider.test.ts`, updates large snapshot outputs to Jest 29 formatting (`Array [`/`Object {` -> plain `[`/`{`, unescaped JSON strings), switches a temp cleanup helper from `fs.rmdirSync` to `fs.rmSync`, and adds TypeScript non-null/type annotations in tests.

## 4. Does Δt directly exercise the breaking change?
It exercises the Jest 29 test-runner migration, not a product behavior change. Most Δt hunks are snapshot serializer churn or TypeScript test cleanup. The only source-like Δc hunk is `writeRemoteCache?: boolean`, while the rest is Jest/ts-jest config, tsconfig cleanup, VS Code settings, and change files. The fail/pass gate is therefore about keeping the test suite runnable under Jest 29 rather than repairing dependency-broken application behavior.

## 5. Coverage verdict
TESTS_OTHER_THING — Δt is dominated by Jest 29 snapshot/formatter/type-test updates, and Δc is mostly CONFIG_INFRA_ONLY; the verifier tests the test harness migration rather than a dependency-induced source behavior break.

## 6. Δc nature
MIXED — mostly CONFIG_INFRA_ONLY (`jest.config`, `tsconfig`, removed docs Jest config, VS Code setting, change files) with one small source type relaxation in `RemoteFallbackCacheProvider.ts`.

## 7. Soundness concerns / notes
- An agent could likely satisfy most of the verifier through Jest config and snapshot-facing changes without understanding any Lage runtime behavior.
- The test command explicitly includes changed snapshot/test files, so the suite is narrow to the migration artifacts.

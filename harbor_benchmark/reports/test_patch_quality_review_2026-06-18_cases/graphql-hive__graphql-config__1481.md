# Test-patch audit — graphql-hive__graphql-config__1481

## 1. Task summary
- Folder: graphql-hive__graphql-config__1481
- Ecosystem: npm_and_yarn
- Upgrade: minimatch 4.2.3 -> 10.0.0
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `pnpm exec vitest run test/loaders.spec.ts --pool=forks`

## 2. What is the breaking change?
minimatch 10.0.0 drops the default export, so `import minimatch from 'minimatch'` must become `import { minimatch } from 'minimatch'`, and the matcher now requires forward-slash-normalized patterns (the `match` helper in `src/project-config.ts` adds `.split('\\').join('/')`). Without Δc the default import is `undefined` and calling it throws.

## 3. What does Δt (test.patch) actually do?
- `test/loaders.spec.ts`: adds three `// @ts-expect-error - we're adding a property here` comments — before `schema.isTheOne = true;`, before `expect(received.isTheOne).toEqual(true);`, and before `expect(receivedAsync.isTheOne).toEqual(true);`.
- No new test cases, no assertions, no fixtures; purely TypeScript suppression directives for the `isTheOne` ad-hoc property on a `GraphQLSchema`.

## 4. Does Δt directly exercise the breaking change?
No. The Δt changes are exclusively `@ts-expect-error` comments for the `isTheOne` property assignment in the `middlewares` schema-loading test — entirely unrelated to minimatch. The test mocks `@graphql-tools/load` and exercises schema loading, not filepath glob matching, so it never drives the `match()` function that calls `minimatch`. The `@ts-expect-error` directives are stripped by esbuild/vitest at runtime (vitest does not type-check by default), so they neither fail on P⊕Δm nor pass specifically because of Δc.

## 5. Coverage verdict
UNWITNESSED — Δt only adds `@ts-expect-error` comments for an unrelated `isTheOne` property and never exercises the minimatch default→named-export / path-normalization break; the hidden test passes on P⊕Δm without Δc.

## 6. Δc nature
MIXED — real source repair in `src/project-config.ts` (`import minimatch from` → `import { minimatch } from` plus `.split('\\').join('/')` normalization) alongside a new `.changeset/hip-badgers-thank.md` release note and `tsconfig.build.json` / `tsconfig.json` config churn.

## 7. Soundness concerns / notes
- Confirmed by the 2026-06-10 review: "Unwitnessed; `Delta c` also mixes release-note/config material with a small source edit."
- The Δt has zero relationship to the actual minimatch breaking change; it is a TypeScript-suppression drive-by on a schema-loading test.
- Because vitest (esbuild) ignores `@ts-expect-error` at runtime, the directives do not even produce a compile-time gate under the verifier command.

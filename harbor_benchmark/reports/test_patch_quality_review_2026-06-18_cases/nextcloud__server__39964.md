# Test-patch audit — nextcloud__server__39964

## 1. Task summary
- Folder: nextcloud__server__39964
- Ecosystem: npm_and_yarn
- Upgrade: camelcase 6.3.0 -> 8.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest apps/systemtags/src/utils.spec.ts --no-coverage`

## 2. What is the breaking change?
`camelcase` 8.0.0 is an ESM-only/modern-package upgrade relative to the older CommonJS-compatible 6.x line. Nextcloud's Jest setup normally ignores packages in `node_modules`, so importing `apps/systemtags/src/utils.ts` now pulls an untransformed `camelcase` package into the test runtime unless `camelcase` is explicitly allowlisted for transform. Δc also relaxes `parseTags` from `Required<FileStat>[]` to the narrower `{ props: DAVResultResponseProps }[]`, matching what the utility actually consumes and what the new focused test passes in.

## 3. What does Δt (test.patch) actually do?
Adds one new test file, `apps/systemtags/src/utils.spec.ts`, covering the system-tags utilities:
- `parseTags`: passes DAV props with keys such as `user-visible`, `user-assignable`, and `can-assign`, then expects camel-cased fields `userVisible`, `userAssignable`, and `canAssign`.
- `parseIdFromLocation`: checks simple, trailing-slash, and query-string URL forms.
- `formatTag`: checks both client `Tag` and server `ServerTag` inputs normalize to the expected output object.

## 4. Does Δt directly exercise the breaking change?
Yes. The new `parseTags` test imports `parseTags` from `./utils`, and `utils.ts` imports `camelCase from 'camelcase'`; on P⊕Δm, Jest is likely to fail while loading the upgraded ESM `camelcase` package because `jest.config.ts` still ignores it under `node_modules`. Δc's `jest.config.ts` hunk adds `'camelcase'` to the transform allowlist, and its `parseTags` signature update lets the new test's `{ props: DAVResultResponseProps }` fixture type-check against the intended utility boundary.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden test imports and executes the source path that consumes `camelcase`; without Δc the upgraded package is not transformed for Jest, while with Δc the new `parseTags` assertion exercises the camel-casing behavior and passes.

## 6. Δc nature
MIXED — load-bearing changes include source repair in `apps/systemtags/src/utils.ts` and test/build configuration in `jest.config.ts`, plus regenerated bundled artifacts under `dist/`.

## 7. Soundness concerns / notes
- The witness is partly a Jest module-loading/configuration failure for an ESM dependency, which is valid dependency-upgrade evidence but less behavior-focused than a pure assertion failure.
- The new test also drives a type-boundary relaxation in `parseTags`; that repair is real source work, but the type mismatch is introduced by the new unit-test fixture rather than by `camelcase` itself.
- Large `dist/` and source-map hunks dominate the patch size but are generated outputs, not independent repair logic.

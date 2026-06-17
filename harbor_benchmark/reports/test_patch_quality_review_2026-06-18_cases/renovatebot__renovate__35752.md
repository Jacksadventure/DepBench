# Test-patch audit — renovatebot__renovate__35752

## 1. Task summary
- Folder: renovatebot__renovate__35752
- Ecosystem: npm_and_yarn
- Upgrade: find-up 5.0.0 -> 7.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx vitest run lib/util/exec/hermit.spec.ts lib/util/fs/index.spec.ts`

## 2. What is the breaking change?
find-up v7 no longer supports the old default-import consumer shape used by Renovate. Consumers must import the named `findUp` export, so `import findUp from 'find-up'` in TypeScript source and tests becomes invalid or resolves incorrectly under the upgraded package.

## 3. What does Δt (test.patch) actually do?
Touches two Vitest files:
- `lib/util/exec/hermit.spec.ts`: changes the mock/import from `import _findUp from 'find-up'` to `import { findUp as _findUp } from 'find-up'`.
- `lib/util/fs/index.spec.ts`: makes the same named-import migration.
No assertions are added; the tests keep exercising the existing hermit and filesystem lookup behavior while compiling against find-up v7.

## 4. Does Δt directly exercise the breaking change?
Yes. The hidden tests import and mock find-up using the v7 named export, while the production repair changes `lib/util/fs/index.ts` to the same named import. On P⊕Δm, the old default import in production remains incompatible with find-up v7 and the targeted Vitest command should fail; with Δc and Δt, source and tests agree on the new export shape.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the source and test imports are directly adapted to the find-up v7 export change, producing a focused import/API witness.

## 6. Δc nature
REAL_SOURCE_REPAIR — the only code repair is `lib/util/fs/index.ts`, changing the production find-up import to `{ findUp }`.

## 7. Soundness concerns / notes
- Clean narrow case.
- Δt is mostly a test-side import compatibility migration, but the selected tests still run the production filesystem utility that uses the changed dependency.

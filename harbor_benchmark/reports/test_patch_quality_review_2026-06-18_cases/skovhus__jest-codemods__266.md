# Test-patch audit — skovhus__jest-codemods__266

## 1. Task summary
- Folder: skovhus__jest-codemods__266
- Ecosystem: npm_and_yarn
- Upgrade: execa 4.1.0 -> 6.1.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest src/cli/transformers.test.ts`

## 2. What is the breaking change?
execa 6 changed the synchronous API surface used here from a default import with `.sync` to the named `execaSync` export. The old TypeScript source imports `execa` as a default and calls `execa.sync(...)`.

## 3. What does Δt (test.patch) actually do?
`src/cli/transformers.test.ts` updates the Jest mock for `execa` from `{ sync: () => execaReturnValue }` to `{ execaSync: () => execaReturnValue }`.

## 4. Does Δt directly exercise the breaking change?
Yes. With Δt, the mocked dependency exposes the execa 6 named synchronous export. P⊕Δm source still calls `execa.sync`, so the targeted transformer test fails; Δc imports `{ execaSync }` and calls `execaSync(...)`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden mock follows the new execa API and discriminates the old source call from the repaired source call.

## 6. Δc nature
REAL_SOURCE_REPAIR — `src/cli/transformers.ts` changes the production import and call site from `execa.sync` to `execaSync`.

## 7. Soundness concerns / notes
Clean API-surface witness. The test is mock-based, but the mock shape matches the upgraded dependency API.

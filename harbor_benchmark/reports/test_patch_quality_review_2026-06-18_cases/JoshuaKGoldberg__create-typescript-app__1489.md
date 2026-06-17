# Test-patch audit - JoshuaKGoldberg__create-typescript-app__1489

## 1. Task summary
- Folder: JoshuaKGoldberg__create-typescript-app__1489
- Ecosystem: npm_and_yarn
- Upgrade: packageManager pnpm@8.15.4 -> pnpm@9.0.6
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx vitest run src/steps/writing/creation/writePackageJson.test.ts`

## 2. What is the breaking change?
The project manifest's `packageManager` field is bumped to pnpm 9.0.6, but the package generator still hardcodes `packageManager: "pnpm@8.15.4"` in generated package.json output.

## 3. What does test.patch actually do?
The hidden patch updates two snapshots/inline expected JSON outputs in `writePackageJson.test.ts`, changing the generated `packageManager` expectation from `pnpm@8.15.4` to `pnpm@9.0.6`.

## 4. Does test.patch directly exercise the breaking change?
Yes. With only Delta_m and Delta_t, the generator still emits the old pnpm version and the updated vitest expectations fail. Delta_c changes the production generator constant to `pnpm@9.0.6`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the hidden test directly checks source behavior that must track the manifest packageManager bump.

## 6. Delta_c nature
REAL_SOURCE_REPAIR - a production TypeScript constant in `writePackageJson.ts` is updated to the new package manager version.

## 7. Soundness concerns / notes
This is a metadata consistency repair rather than an API migration. It is still a direct witness for this task because the dependency-like manifest field and generated output are intentionally kept in sync.

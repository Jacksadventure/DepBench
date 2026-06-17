# Test-patch audit — decaporg__decap-cms__6305

## 1. Task summary
- Folder: decaporg__decap-cms__6305
- Ecosystem: npm_and_yarn
- Upgrade: simple-git 2.0.0 -> 3.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest packages/netlify-cms-proxy-server/src/middlewares/localGit/index.spec.ts --no-coverage --passWithNoTests`

## 2. What is the breaking change?
simple-git v3 removes the old `simple-git/promise` entry point and exposes the promise API from `simple-git`, with TypeScript types imported as named exports such as `SimpleGit`. Code importing `simple-git/promise` no longer resolves under the upgraded dependency.

## 3. What does Δt (test.patch) actually do?
Δt changes only `packages/netlify-cms-proxy-server/src/middlewares/localGit/index.spec.ts`. It rewrites the Jest mock and test require from `simple-git/promise` to `simple-git`.

## 4. Does Δt directly exercise the breaking change?
Yes. The patched test mocks the v3 entry point (`jest.mock("simple-git")` and `require("simple-git")`), while old source still imports `simple-git/promise`; under simple-git v3 that old path is unavailable or mismatched, and Δc updates both production imports and `SimpleGit` type usage.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt targets the entry-point removal introduced by simple-git 3, and the verifier runs the localGit middleware spec that imports the repaired production module.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc updates source imports in `cypress/plugins/common.js` and `packages/netlify-cms-proxy-server/src/middlewares/localGit/index.ts`, plus TypeScript `SimpleGit` type annotations.

## 7. Soundness concerns / notes
The test witness is narrow but directly tied to the removed package subpath; no unrelated test or lint command is involved.

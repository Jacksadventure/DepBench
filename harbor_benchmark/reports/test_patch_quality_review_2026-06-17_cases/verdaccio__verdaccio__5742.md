# Test-patch audit — verdaccio__verdaccio__5742

## 1. Task summary
- Folder: verdaccio__verdaccio__5742
- Ecosystem: npm_and_yarn
- Upgrade: vitest 3.2.4 -> 4.1.2 (labeled; Δm actually bumps ~15 packages)
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `pnpm vitest run test/unit/modules/api/user.spec.ts`

## 2. What is the breaking change?
A monorepo-wide upgrade: vitest 3→4 plus all `@verdaccio/*` packages to `next-9.8`, `lodash` → `lodash-es`, and `@verdaccio/utils` helpers (`buildToken`, `generateRandomHexString`, `getAuthenticatedMessage`, `addGravatarSupport`, `formatAuthor`, `generateGravatarUrl`) relocated into `@verdaccio/core` (`authUtils`/`cryptoUtils`) or inlined. `bootstrap.ts` is deleted and `startVerdaccio` renamed to `runServer`.

## 3. What does Δt (test.patch) actually do?
Touches ~18 test files: replaces `import _ from 'lodash'` with native checks (`instanceof RegExp`, `!= null`, `typeof === 'object'`), and updates helper/test calls from `@verdaccio/utils` (`buildToken`, `generateRandomHexString`) to `@verdaccio/core` (`authUtils.buildToken`, `cryptoUtils.generateRandomHexString`). In `user.spec.ts` specifically: imports `authUtils` from `@verdaccio/core` and rewrites `buildToken(TOKEN_BEARER, ...)` → `authUtils.buildToken(TOKEN_BEARER, ...)` at ~5 call sites; `_helper.ts` makes the same relocation for `buildToken`/`generateRandomHexString`.

## 4. Does Δt directly exercise the breaking change?
Yes, via the exercised path. `user.spec.ts` → `_helper.ts` → `src/api/endpoint` → `user.ts`, which (pre-Δc) still does `import _ from 'lodash'` and `import { getAuthenticatedMessage } from '@verdaccio/utils'`. Δm removes `lodash` (→ `lodash-es`) and bumps `@verdaccio/utils`; under pnpm the un-declared `lodash` is not resolvable, so `user.ts` fails to load → FAIL. With Δc (`import * as _ from 'lodash-es'`, `authUtils.getAuthenticatedMessage`) the module loads and the `authUtils.buildToken` calls in Δt match → PASS.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — P⊕Δm⊕Δt fails to load (`user.ts` imports the removed `lodash` / relocated `getAuthenticatedMessage`) and P⊕Δm⊕Δc⊕Δt passes; the witness is a load-time module-resolution / API-relocation gate on the user API path.

## 6. Δc nature
REAL_SOURCE_REPAIR (MIXED) — large migration across ~30 source files: `lodash` → `lodash-es` (`import * as _`), `@verdaccio/utils` helper relocations to `@verdaccio/core`, inlining of gravatar helpers into `src/api/web/api/package.ts`, deletion of `src/lib/bootstrap.ts`, `startVerdaccio` → `runServer` rename (`src/index.ts`, `index.js`), plus `vitest.config.mjs`/`package.json` script churn.

## 7. Soundness concerns / notes
- Mislabeled: the task is tagged "vitest 3.2.4 -> 4.1.2" but Δm bundles ~15 dependency changes (all `@verdaccio/*`, lodash→lodash-es, verdaccio-auth-memory/memory major bumps). The actual witnessed break is from the bundled ecosystem changes, not vitest 4 itself.
- Dead Δt: `test_cmd` runs only `user.spec.ts`, but Δt modifies ~18 test files; only `user.spec.ts` + its transitive `_helper.ts`/source imports are exercised. The other 15+ files' changes are never run by the verifier.
- The problematic-review flag may reflect pnpm hoisting uncertainty (if `lodash` stays resolvable, or `@verdaccio/utils` 9.8 still exports the old helpers, the source could load without Δc → no_code_pass). The witness is a load-time gate, not a behavioral vitest-4 test.

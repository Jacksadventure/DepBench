# Test-patch audit — rollup__rollup__5046

## 1. Task summary
- Folder: rollup__rollup__5046
- Ecosystem: npm_and_yarn
- Upgrade: locate-character 2.0.5 -> 3.0.0
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `npm test`

## 2. What is the breaking change?
Two facets of locate-character v3: (a) it became ESM-only / pure-ESM, so `require('locate-character')` in CJS test files throws `ERR_REQUIRE_ESM`; (b) the `locate()` function's return type widened to `Location | null`, so destructuring `{ line, column } = locate(...)` is no longer type-correct in TypeScript source. Facet (a) affects the test file; facet (b) affects `src/utils/logs.ts` and `src/ast/nodes/Program.ts`.

## 3. What does Δt (test.patch) actually do?
Touches one file, `test/misc/in-memory-sourcemaps.js`: removes the top-level `const { getLocator } = require('locate-character');` and changes `const locator = getLocator(generated.code, { offsetLine: 1 });` to `const locator = (await import('locate-character')).getLocator(generated.code, { offsetLine: 1 });` (dynamic import to satisfy ESM-only). No new assertion — the existing sourcemap assertions (`loc.source === 'main'`, `loc.line === 1`, etc.) are unchanged.

## 4. Does Δt directly exercise the breaking change?
Δt directly handles facet (a) — the ESM-only `require` break — by switching to dynamic `import()`. It does NOT assert facet (b) (the nullable `locate()` return) at all; nothing in the test observes null-return behavior. The sourcemap assertions would exercise `getLocator`/`SourceMapConsumer`, not the source-side `locate()` calls that Δc patches.

## 5. Coverage verdict
INCONCLUSIVE — Δc's only source change is a TypeScript non-null assertion (`!`) with **zero runtime effect** (erased at compile). Whether the task is witnessed depends entirely on whether `npm test` runs a type-checking build: if it does (rollup's build runs tsc), the widened `locate()` type fails to compile without Δc -> compile-error witness; if `npm test` is transpile-only/mocha-against-prebuilt-dist, runtime behavior is identical with/without Δc and Δt already fixes the ESM import, so `TEST(P⊕Δm⊕Δt)` passes -> UNWITNESSED. The bundle does not include `package.json` scripts to confirm.

## 6. Δc nature
MIXED — 2 trivial type-only source edits (`src/ast/nodes/Program.ts`, `src/utils/logs.ts`: add `!` after `locate(..., { offsetLine: 1 })`), plus non-source churn: `.eslintrc.js` (add `locate-character` to `import/no-unresolved` ignore list) and `LICENSE.md` + `browser/LICENSE.md` (update the locate-character repository URL to a gitlab URL). The dominant line count is config/license, and the only real source change is type-level.

## 7. Soundness concerns / notes
- Δc has no runtime effect (`!` is erased), so the witness can only be a compile/typecheck failure; this is fragile and depends on rollup's build pipeline type-checking, which is unconfirmed from the bundle.
- Δt addresses a *different* facet of the v3 break (ESM-only) than Δc's source edit (nullable return type), so Δt does not directly cover the line Δc changes.
- Per the problematic review: "Exclude from witnessed main set. Mixed source/config/docs and no witness." The "no witness" concern is consistent with the type-only nature of Δc.
- To resolve: confirm whether `npm test` (rollup) executes `tsc`/type-checking build. If yes -> valid compile-error witness (Level 1); if no -> no_code_pass (Level 2) and should be quarantined.

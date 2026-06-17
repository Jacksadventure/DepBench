# Test-patch audit — webhintio__hint__4027

## 1. Task summary
- Folder: webhintio__hint__4027
- Ecosystem: npm_and_yarn
- Upgrade: postcss 7.0.32 -> 8.0.5
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `cd packages/utils-types && npm run build && cd ../utils-css && npm run build && ./node_modules/.bin/ava --tap`

## 2. What is the breaking change?
PostCSS 8 changes its CommonJS/TypeScript import surface and removes the `vendor` helper API (`vendor.prefix`, `vendor.unprefixed`) that webhint production packages imported from `postcss`. The repair replaces the removed helper usage with local `@hint/utils-css` functions and updates PostCSS type/import usage.

## 3. What does Δt (test.patch) actually do?
Touches `packages/utils-css/tests/get-css-code-snippet.ts` and adds `packages/utils-css/tests/get-unprefixed.ts` plus `packages/utils-css/tests/get-vendor-prefix.ts`. It rewrites the PostCSS test import to `require`, updates type references to `import('postcss')`, and adds AVA assertions for the replacement prefix helper functions.

## 4. Does Δt directly exercise the breaking change?
Yes. The verifier builds `packages/utils-css` under PostCSS 8 and runs tests that import the new replacement helpers; without Δc, those helpers and the PostCSS 8-compatible source/type changes are absent.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — `P⊕Δm⊕Δt` should fail due missing replacement helper exports and/or PostCSS 8 compile/import incompatibilities; Δc introduces the helpers and migrates production imports and types.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc updates multiple production TypeScript files under `packages/hint-*`, `packages/parser-*`, `packages/utils-compat-data`, and `packages/utils-css` to stop using removed PostCSS APIs and to expose local replacement helpers.

## 7. Soundness concerns / notes
- The new helper tests are somewhat implementation-specific: an alternative valid repair might inline prefix handling rather than exporting `getUnprefixed`/`getVendorPrefix`.
- The build portion of the verifier still gives independent compile-level coverage of the PostCSS 8 migration.

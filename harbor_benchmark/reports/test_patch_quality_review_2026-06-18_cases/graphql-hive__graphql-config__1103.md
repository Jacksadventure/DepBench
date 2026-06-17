# Test-patch audit - graphql-hive__graphql-config__1103

## 1. Task summary
- Folder: graphql-hive__graphql-config__1103
- Ecosystem: npm_and_yarn
- Upgrade: package export/types metadata from `dist/index.d.ts` to `dist/typings/index.d.ts` with bob-the-bundler 1.7.3 -> 4.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `yarn jest test/config.spec.ts test/loaders.spec.ts --runInBand`

## 2. What is the breaking change?
The manifest rewrites the package to ESM/CJS-aware exports: `main` moves to `dist/cjs/index.js`, `module` to `dist/esm/index.js`, typings to `dist/typings/index.d.ts`, `type` becomes `module`, `bob` config changes, and bob-the-bundler is upgraded. Source imports now need explicit `.js` extensions and the Jest setup needs to resolve the package export path.

## 3. What does test.patch actually do?
The hidden tests stop importing internals via `../src` and instead import public APIs from `graphql-config`. They also add Jest globals imports, use the package-level `LoadersRegistry`, and adjust mocks/assertions so the test runs through the package resolver rather than direct TypeScript source paths.

## 4. Does test.patch directly exercise the breaking change?
Yes. The patched tests exercise the package's public export resolution under the new packaging layout. Without Delta_c, the package cannot be resolved/compiled correctly through the new export and ESM/CJS structure.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the hidden tests are targeted at the packaging/export migration introduced by the manifest change.

## 6. Delta_c nature
MIXED - it includes real source import/export migration plus Jest/Babel/bob config, workflow, gitignore, and changeset files.

## 7. Soundness concerns / notes
The "library" metadata in the batch is not a normal external dependency name; it is package export metadata. Still, within this task the manifest change is the thing that breaks package-level imports, and the test patch directly probes that surface.

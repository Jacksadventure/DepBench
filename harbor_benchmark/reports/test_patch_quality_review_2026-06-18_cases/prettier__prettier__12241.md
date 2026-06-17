# Test-patch audit — prettier__prettier__12241

## 1. Task summary
- Folder: prettier__prettier__12241
- Ecosystem: npm_and_yarn
- Upgrade: @babel/parser 7.16.12 -> 7.17.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `yarn jest tests/format/js/regex tests/format/js/babel-plugins tests/format/misc/errors/js/regex-v-u-flags tests/format/typescript/type-arguments-bit-shift-left-like tests/integration/__tests__/debug-print-comments.js tests/integration/__tests__/debug-print-ast.js --colors=false`

## 2. What is the breaking change?
@babel/parser 7.17 adds parser support that Prettier must explicitly enable through Babel parser plugins, especially the `regexpUnicodeSets` plugin for the new regular-expression `v` flag. It also changes AST location objects to include `loc.*.index`, which affects debug-print snapshots.

## 3. What does Δt (test.patch) actually do?
Δt adds regex `v` flag format/error fixtures under `tests/format/js/{babel-plugins,regex}` and `tests/format/misc/errors/js/regex-v-u-flags`, adds TypeScript parser regression fixtures, and updates snapshots for Babel AST/comment debug printing with `loc.index` fields. The key new fixtures include `/a/v;`, `/a/ugv;`, and `/a/vu;`.

## 4. Does Δt directly exercise the breaking change?
Yes. The new Babel-format snapshots expect `/a/v;` to parse and print successfully for Babel-based parsers, while non-Babel parsers report invalid flag errors. Without Δc adding `"regexpUnicodeSets"` to `src/language-js/parse/babel.js`, the Babel parser options do not enable that syntax and the new fixtures fail.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt contains concrete parser fixtures and snapshots for syntax/AST behavior introduced by the bumped @babel/parser, and Δc is the minimal source-side parser option needed to satisfy them.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc is a one-line production parser configuration change in `src/language-js/parse/babel.js`.

## 7. Soundness concerns / notes
The hidden patch is snapshot-heavy, but the main witness is not snapshot churn alone: it adds executable fixtures for the new `v` flag parser capability.

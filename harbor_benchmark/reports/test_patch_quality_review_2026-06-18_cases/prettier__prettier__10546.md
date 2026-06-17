# Test-patch audit — prettier__prettier__10546

## 1. Task summary
- Folder: prettier__prettier__10546
- Ecosystem: npm_and_yarn
- Upgrade: @babel/parser 7.13.10 -> 7.13.11
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `yarn jest tests/misc/typescript-babel-only --ci`

## 2. What is the breaking change?
The upgraded Babel TypeScript parser exposes `importKind` on `TSImportEqualsDeclaration` for `import type A = require("...")`. Prettier's TypeScript printer previously emitted `import ` unconditionally before printing the identifier/module reference, so it lost or misplaced the new `type` import kind.

## 3. What does Δt (test.patch) actually do?
It adds `tests/misc/typescript-babel-only/type-import-equals-declaration.ts` with several multiline `import type` / `export import type` cases and updates the snapshot to expect normalized output such as `import type A = require("foo");` and `export import type B = require("B");`.

## 4. Does Δt directly exercise the breaking change?
Yes. On P⊕Δm⊕Δt, the parser produces `node.importKind === "type"` but the old printer never emits it for import-equals declarations, so the snapshot fails. Δc prints `node.importKind` before the identifier when it is not `"value"`, making the new snapshot pass.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the test fixture directly targets the AST field exposed by the parser upgrade and the source printer change required to preserve it.

## 6. Δc nature
REAL_SOURCE_REPAIR — `src/language-js/print/typescript.js` adds import-kind printing for TypeScript import-equals declarations.

## 7. Soundness concerns / notes
The witness is snapshot-based, but it covers a precise parser/printer behavior and a minimal source repair.

# Test-patch audit — keystonejs__keystone__8056

## 1. Task summary
- Folder: keystonejs__keystone__8056
- Ecosystem: npm_and_yarn
- Upgrade: @markdoc/markdoc 0.1.5 -> 0.2.0
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `npx jest markdoc/index.test.ts --no-coverage --passWithNoTests`

## 2. What is the breaking change?
@markdoc/markdoc 0.2.0 widened `Markdoc.transform()`'s return type from `Tag` to the union `RenderableTreeNode` (string | number | boolean | null | array | Tag), and the runtime can now yield non-Tag nodes. Code that assumed the result is always a `Tag` (destructuring `node.name`/`node.attributes`, or asserting `!== null && typeof !== 'string'`) is no longer type-correct and may mishandle non-Tag nodes. The repair introduces an `isTag()` guard.

## 3. What does Δt (test.patch) actually do?
Touches one file, `docs/markdoc/index.test.ts`: adds `import { isTag } from './isTag';` and rewrites the test helper `renderableToReactElement` to handle the widened union — return primitives/null as-is, recurse on arrays, render only `isTag(node)` nodes via `React.createElement`, else `null`. No new `it(...)` cases, no new fixtures, no new snapshots; it mirrors Δc's `Markdoc.tsx` render logic inside the test helper used for snapshot serialization.

## 4. Does Δt directly exercise the breaking change?
Not via a new assertion. Δt only updates the test's render helper to narrow the widened `RenderableTreeNode` type (and import `isTag`). There is no new test input that forces a non-Tag node through `transformContent`. If `Markdoc.transform` still returns a `Tag` at runtime for the existing fixtures (only the TypeScript *type* widened), then `renderableToReactElement` behaves identically before and after Δt at runtime, and `transformContent`'s only real change is the `assert(isTag(...))` / `as Tag` cast.

## 5. Coverage verdict
INCONCLUSIVE — Δt adds no runtime assertion; the witness hinges on whether the jest run type-checks. If ts-jest type-checks (likely default), the widened 0.2.0 types make the source (`Markdoc.tsx`, `index.ts`) fail to compile without Δc -> compile-error witness (Level 1 allowed). If jest is configured transpile-only, `transform` returns a `Tag` at runtime and the existing tests pass without Δc -> UNWITNESSED. The bundle does not include jest/tsconfig settings to disambiguate.

## 6. Δc nature
REAL_SOURCE_REPAIR — `docs/components/Markdoc.tsx` (add `isTag` guards, handle string/number/boolean/null/array nodes before destructuring), `docs/markdoc/index.ts` (replace the `!== null && typeof !== 'string'` assertion with `assert(isTag(...))` and cast `as Tag`), and new file `docs/markdoc/isTag.ts` (`$$mdtype === 'Tag'` check). Real logic, not formatting — but all under `docs/` (documentation-site code), not product source.

## 7. Soundness concerns / notes
- Witness is type-level (compile-error) at best; no runtime-failing assertion is added by Δt. Needs confirmation that the jest config type-checks.
- Per the problematic review: "Exclude from main benchmark unless documentation site examples are intentionally considered product code." Confirmed scope concern: all of Δc lives under `docs/` (Markdoc.tsx, docs/markdoc/*), so even if witnessed it grades docs-site repair, not keystone product code.
- The test helper changes in Δt duplicate Δc's `isTag` logic, which is a reasonable test-oracle adaptation but does not by itself detect a non-Tag output — there's no fixture exercising one.
- If transpile-only: this is a latent/no_code_pass case (Level 2); if type-check: a valid but fragile compile-error witness.

# Test-patch audit — curbengh__hexo-yam__135

## 1. Task summary
- Folder: curbengh__hexo-yam__135
- Ecosystem: npm_and_yarn
- Upgrade: svgo 2.4.0 -> 3.0.0
- test_cmd: `npx jest --testPathPattern='svg'`

## 2. What is the breaking change?
svgo 3 changes option naming and error behavior. The `cleanupIDs` plugin option becomes `cleanupIds`, and `optimize()` throws on invalid input instead of returning an `{ error }` object.

## 3. What does Δt (test.patch) actually do?
`test/svg.test.js` updates the custom option to `cleanupIds` and rewrites the invalid-SVG expectation to catch the thrown svgo error before asserting that the plugin rejects with that error.

## 4. Does Δt directly exercise the breaking change?
Yes. The error-path test calls the minify function with invalid SVG under svgo 3. Without Δc, the thrown optimizer error is not converted into the expected rejected promise; with Δc, the source catches and rejects with the new error shape.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt directly covers svgo 3 option/error API changes that Δc implements.

## 6. Δc nature
MIXED — real source repair in `lib/filter.js` plus README/example option-name documentation.

## 7. Soundness concerns / notes
- The README hunk is not part of the witness, but the `lib/filter.js` hunk is directly exercised by the hidden svg test.
- The custom option rename and thrown-error handling are both dependency-specific API changes.


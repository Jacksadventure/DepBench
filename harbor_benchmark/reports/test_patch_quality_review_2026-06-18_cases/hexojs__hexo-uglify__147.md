# Test-patch audit — hexojs__hexo-uglify__147

## 1. Task summary
- Folder: hexojs__hexo-uglify__147
- Ecosystem: npm_and_yarn
- Upgrade: terser 4.3.9 -> 5.3.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx mocha test/index.js --reporter spec`

## 2. What is the breaking change?
terser 5 makes `minify()` asynchronous, returning a promise rather than the synchronous `{ code }` result that terser 4 allowed. The old Hexo filter calls `const { code } = minify(...)` inside a synchronous function, so it no longer returns minified JavaScript under the upgraded dependency.

## 3. What does Δt (test.patch) actually do?
`test/index.js` marks the terser-related Mocha tests as `async`, awaits `terserFilter.apply(...)`, and adds an `after_render` integration-style test that registers the filter in Hexo and awaits `hexo.extend.filter.exec(...)`.

## 4. Does Δt directly exercise the breaking change?
Yes. The hidden tests await the filter and assert the returned code is shorter than the input. On P⊕Δm the source function is still synchronous and destructures the unresolved terser promise, so it returns `undefined` or otherwise fails the minification assertions; Δc makes the filter `async` and awaits `minify()`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt checks the new async terser behavior through both direct filter calls and the Hexo `after_render` filter path.

## 6. Δc nature
REAL_SOURCE_REPAIR — `lib/filter-terser.js` changes the exported filter to `async` and awaits `minify(str, jsOptions)`.

## 7. Soundness concerns / notes
Clean runtime witness. The added `after_render` test broadens coverage beyond the direct unit calls and is causally tied to the async dependency API.

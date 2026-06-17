# Test-patch audit — mozilla__addons-frontend__9637

## 1. Task summary
- Folder: mozilla__addons-frontend__9637
- Ecosystem: npm_and_yarn
- Upgrade: @loadable/component and @loadable/server 5.13.1 -> 5.13.2
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `./node_modules/.bin/jest tests/unit/core/components/TestServerHtml.js --runInBand --forceExit`

## 2. What is the breaking change?
`@loadable/server` renamed/pluralized the chunk extractor API used here: `getRequiredChunksScriptElement()` is replaced by `getRequiredChunksScriptElements()`.

## 3. What does Δt (test.patch) actually do?
It updates the `TestServerHtml.js` fake chunk extractor and assertion to stub and expect `getRequiredChunksScriptElements` instead of `getRequiredChunksScriptElement`.

## 4. Does Δt directly exercise the breaking change?
Yes. The test renders `ServerHtml` with a fake extractor and asserts the new plural method is called. Without Δc, `ServerHtml` still calls the singular method, so the plural stub is never called and the assertion fails. With Δc, the component calls the new API.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt directly checks the upgraded @loadable/server method name and Δc is the corresponding source call-site repair.

## 6. Δc nature
REAL_SOURCE_REPAIR — one production call-site in `src/core/components/ServerHtml/index.js` is migrated to `getRequiredChunksScriptElements()`.

## 7. Soundness concerns / notes
- The task metadata reports library `@`, but the manifest patch clearly upgrades `@loadable/component` and `@loadable/server`.
- This is a concise, high-signal witness with no unrelated test files.

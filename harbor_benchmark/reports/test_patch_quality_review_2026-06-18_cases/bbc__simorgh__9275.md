# Test-patch audit — bbc__simorgh__9275

## 1. Task summary
- Folder: bbc__simorgh__9275
- Ecosystem: npm_and_yarn
- Upgrade: js-cookie 2.2.1 -> 3.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest src/app/lib/analyticsUtils/index.test.js --no-coverage --passWithNoTests`

## 2. What is the breaking change?
js-cookie 3 removed the `Cookie.getJSON` helper used by `getAtUserId`. Callers must use `Cookie.get` and parse the JSON string themselves.

## 3. What does Δt (test.patch) actually do?
Updates the `getAtUserId` tests to mock `Cookie.get` returning JSON strings or null instead of mocking `Cookie.getJSON` returning parsed objects.

## 4. Does Δt directly exercise the breaking change?
Yes. With Δm and Δt, the test suite expects the post-js-cookie-3 API. The old source still calls `Cookie.getJSON(cookieName)`, which no longer exists in js-cookie 3 and does not satisfy the patched mocks. Δc changes the source to call `Cookie.get(cookieName)`, parse it with `JSON.parse`, and fall back to a generated UUID.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt directly moves the unit test from the removed `getJSON` API to the js-cookie 3 `get` API, and Δc performs the corresponding source repair.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc changes production analytics utility code to use and parse `Cookie.get`.

## 7. Soundness concerns / notes
- The patch logs parse errors to console, but the core repair is the removed js-cookie API migration.

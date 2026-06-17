# Test-patch audit — fastify__fastify-http-proxy__171

## 1. Task summary
- Folder: fastify__fastify-http-proxy__171
- Ecosystem: npm_and_yarn
- Upgrade: ws 7.4.1 -> 8.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx tap test/*.js --no-coverage --reporter=tap`

## 2. What is the breaking change?
ws 8 is stricter about WebSocket URL schemes, so code and tests that pass `http://` / `https://` URLs to `WebSocket` need to use `ws://` / `wss://` instead. The source repair adds `convertUrlToWebSocket` and uses it when constructing the proxied upstream WebSocket URL.

## 3. What does Δt (test.patch) actually do?
- Adds `test/utils.js`, which imports `../utils` and unit-tests `convertUrlToWebSocket`.
- Changes WebSocket tests to use `ws://` client/upstream URLs instead of `http://`.
- In prefix-rewrite tests, converts frontend HTTP URLs to WebSocket URLs in the test code before constructing `new WebSocket(...)`.

## 4. Does Δt directly exercise the breaking change?
Only indirectly, and in an over-specified way. P⊕Δm⊕Δt fails immediately because `test/utils.js` imports a new `../utils` module that does not exist before Δc. The patched integration tests mostly avoid the ws 8 break themselves by changing test inputs to `ws://`, so they do not prove that the proxy still accepts an `http://` upstream and converts it internally. The new helper unit test checks the oracle's chosen helper shape rather than the public proxy behavior.

## 5. Coverage verdict
TESTS_OTHER_THING — the hidden test primarily requires the exact new helper module introduced by Δc. It is related to the ws 8 URL-scheme migration, but it does not directly witness the real proxy behavior that would fail under the upgraded dependency.

## 6. Δc nature
REAL_SOURCE_REPAIR — `index.js` converts source/upstream URL construction to WebSocket schemes and `utils.js` adds `convertUrlToWebSocket`.

## 7. Soundness concerns / notes
- An agent could plausibly fix the ws 8 break inline in `index.js` and still fail because the hidden test imports `../utils`.
- A stronger witness would keep or add an integration case with `upstream: "http://..."` and assert that the proxy connects successfully under ws 8.

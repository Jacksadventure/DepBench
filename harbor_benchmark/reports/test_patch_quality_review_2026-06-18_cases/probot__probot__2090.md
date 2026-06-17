# Test-patch audit — probot__probot__2090

## 1. Task summary
- Folder: probot__probot__2090
- Ecosystem: npm_and_yarn
- Upgrade: @types/express 4.17.21 -> 5.0.1 (PR also bumps express 4.21.0 -> 5.0.0, plus transitive accepts/body-parser/send/serve-static/finalhandler/type-is/etc.)
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `npx vitest run test/server.test.ts test/server/logging-middleware.test.ts`

## 2. What is the breaking change?
express 5 / @types/express 5 tightened middleware & route-handler typing: handlers now return `void | Promise<void>`, so arrow functions that `return res.end(...)`/`res.send(...)` (returning a non-void value) no longer type-check; `app.listen` callback typing also changed. The Δc wraps handlers in block bodies and routes `listen` through `node:http` `createServer` to satisfy the new types.

## 3. What does Δt (test.patch) actually do?
- `test/server.test.ts` (4 sites) and `test/server/logging-middleware.test.ts` (1 site): wraps `(_req, res) => res.end("foo")` / `res.send("OK")` arrow handlers into block bodies `(_req, res) => { res.end("foo"); }`. No new assertions, no behavioral change — purely void-return typing conformance.

## 4. Does Δt directly exercise the breaking change?
No. vitest runs tests at runtime via esbuild (strips types, no type-check). `(_req, res) => res.end("foo")` and `(_req, res) => { res.end("foo"); }` are runtime-identical; express 5 ignores the handler return value. So Δt's reformatting does not cause any runtime test to fail on P⊕Δm or pass on P⊕Δm⊕Δc. There is no assertion in Δt that plausibly fails on the broken state — the change is type-only and the verifier never type-checks.

## 5. Coverage verdict
UNWITNESSED — the test_cmd is `vitest run` (runtime only, no `tsc`), so express-5 type incompatibilities do not surface; P⊕Δm⊕Δt passes because the old source still runs correctly under express 5 at runtime.

## 6. Δc nature
MIXED — type-compatibility repairs (`src/server/server.ts`: wrap `createWebhookMiddleware` in an async handler for `void | Promise<void>`; switch `expressApp.listen` to `createServer(app).listen`; `src/apps/setup.ts`: `import type {…} from "http"` -> `from "node:http"`) plus stylistic block-body wrapping of `res.end`/`res.send` arrows. All type/style; no runtime behavior change.

## 7. Soundness concerns / notes
- Classic no_code_pass: the verifier (vitest) does not invoke `tsc`, so the express-5 type migrations in Δc are invisible to the test_cmd. Matches `flagged_in_problematic_review: True`.
- express 5 does have runtime breaking changes (path-to-regexp v8 wildcard syntax, `res.redirect` boolean arg, `req.query` getter) but none are exercised by these two test files (paths are literal `/foo`, `/ping`, `/my-app/foo`; no wildcards, no redirects, no query use). So even the runtime breakage path is not hit.
- To witness this task one would need `tsc --noEmit` (or `vitest --typecheck`) in the test_cmd; currently the verifier cannot distinguish P⊕Δm from P⊕Δm⊕Δc.

# Test-patch audit — octokit__plugin-paginate-rest.js__226

## 1. Task summary
- Folder: octokit__plugin-paginate-rest.js__226
- Ecosystem: npm_and_yarn
- Upgrade: @octokit/types 5.5.0 -> 6.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest --ci`

## 2. What is the breaking change?
@octokit/types 6 replaces the old `:param` route-key spellings with OpenAPI/RFC6570-style `{param}` route keys and changes some generated response shapes. The package's generated `PaginatingEndpoints` and public paginate overloads still referenced `Endpoints["GET /orgs/:org/repos"]`-style keys and direct `response["data"]` access, so the upgraded type package no longer matches the source typings.

## 3. What does Δt (test.patch) actually do?
- `test/compose-paginate.test.ts`, `test/issues.test.ts`, and `test/paginate.test.ts`: rewrites route strings and test names from `GET /.../:param/...` to `GET /.../{param}/...` for paginate, iterator, request, and results-namespace coverage.
- `test/validate-typescript.ts`: rewrites representative known and unknown route calls to the new `{param}` spelling.
- No new behavioral assertions are added; the test patch updates the existing runtime/type-usage corpus to the new route syntax.

## 4. Does Δt directly exercise the breaking change?
Yes. Representative calls such as `octokit.paginate("GET /orgs/{org}/repos", { org: "octorg" })` and `octokit.paginate.iterator("GET /orgs/{org}/repos", ...)` require the source's `PaginatingEndpoints` and paginate overloads to understand the new @octokit/types 6 route keys. On P⊕Δm, the generated source still indexes old keys like `Endpoints["GET /orgs/:org/repos"]`, which should fail TypeScript compilation under the upgraded dependency; with Δc, `src/generated/paginating-endpoints.ts` and `src/types.ts` are migrated to `{param}` keys and the tests compile/run.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt switches the exercised route strings to the new API spelling that @octokit/types 6 exposes, and the old source typings are incompatible with that upgraded dependency until Δc regenerates/adapts them.

## 6. Δc nature
MIXED — the dominant fix is real source/type repair in `src/generated/paginating-endpoints.ts`, `src/types.ts`, and `scripts/update-endpoints/typescript.js`, but Δc also includes README example updates and a very large regenerated endpoint JSON fixture.

## 7. Soundness concerns / notes
- The witness is primarily TypeScript/API-surface compatibility rather than a new runtime assertion; `npx jest --ci` must type-check/transpile the touched `.ts` tests for the failure to be observed.
- The large regenerated `scripts/update-endpoints/generated/endpoints.json` makes the oracle noisy, but the source-facing changes are causally tied to the @octokit/types 6 route-key migration.

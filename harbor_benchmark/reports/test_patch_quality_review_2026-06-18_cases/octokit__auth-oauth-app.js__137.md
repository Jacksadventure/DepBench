# Test-patch audit — octokit__auth-oauth-app.js__137

## 1. Task summary
- Folder: octokit__auth-oauth-app.js__137
- Ecosystem: npm_and_yarn
- Upgrade: @octokit/types 6.0.0 -> 6.0.3
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest --no-coverage --reporters=default`

## 2. What is the breaking change?
The Octokit route type/openapi surface moved OAuth application routes from legacy `:param` notation to `{param}` notation. Source helpers that recognize OAuth application token/grant routes must therefore accept brace-style route templates as well as the legacy colon form.

## 3. What does Δt (test.patch) actually do?
`test/index.test.ts` contains broad Prettier-style comma churn, but the meaningful changes rename and invoke OAuth route tests with `{client_id}` / `{access_token}` route strings, for example `POST /applications/{client_id}/tokens/{access_token}`, `POST /applications/{client_id}/token`, and `PATCH /applications/{client_id}/token`.

## 4. Does Δt directly exercise the breaking change?
Yes. The hidden route tests exercise `auth.hook` and basic-auth/token-reset detection with brace-style OAuth routes. On P⊕Δm the production regexes only understand the old colon/no-placeholder forms, so those routes are not classified correctly; Δc updates the regexes to accept `:{param}`-style and `{param}`-style routes.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the route assertions are tied to the new Octokit route notation and fail without the source regex migration.

## 6. Δc nature
REAL_SOURCE_REPAIR — `src/hook.ts` and `src/requires-basic-auth.ts` update production route detection for brace-style parameters; README edits are ancillary documentation updates.

## 7. Soundness concerns / notes
Δt contains a lot of formatting noise, but the route-template changes are real and discriminating. The benchmark is still source-repair focused rather than pure formatter churn.

# Test-patch audit — integrations__jira__293

## 1. Task summary
- Folder: integrations__jira__293
- Ecosystem: npm_and_yarn
- Upgrade: resolved http://registry.npmjs.org/resolve/-/resolve-1.1.7.tgz -> https://registry.npmjs.org/resolve/-/resolve-1.1.7.tgz
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest --forceExit test/unit/api/api.test.js`

## 2. What is the breaking change?
There is no credible breaking change from the recorded dependency bump: it changes a lockfile tarball URL from HTTP to HTTPS for `resolve` 1.1.7. The human repair instead migrates Sequelize-style application code (`findById` -> `findByPk`, `response.send(JSON.stringify(...))` -> `response.json(...)`, removal of `operatorsAliases`) and test setup mocks.

## 3. What does Δt (test.patch) actually do?
Δt modifies `test/setup/app.js`, `test/unit/api/api.test.js`, and its Jest snapshot. It adds mocked methods such as `Installation.findByPk` and `Subscription.findOrStartSync`, imports the real `Installation` model in the API spec, and adds a new `/api/jira/:installationId/verify` test expecting JSON content and the `"Installation already enabled"` message snapshot.

## 4. Does Δt directly exercise the breaking change?
No. The new test drives the `/verify` endpoint and specifically expects `Installation.findByPk` plus `response.json` behavior from Δc. None of that behavior is caused by changing the `resolve` tarball URL; old source would fail this new test because it still calls `findById` and sends a stringified JSON payload, not because the visible dependency has a breaking API.

## 5. Coverage verdict
TESTS_OTHER_THING — Δt tests unrelated Sequelize/API behavior and a drive-by endpoint repair, not the recorded dependency URL normalization.

## 6. Δc nature
MIXED — Δc combines source edits in `lib/api/index.js` and `lib/models/index.js` with database configuration changes in `db/config.json`.

## 7. Soundness concerns / notes
This appears misattributed: the manifest patch is a lockfile/protocol cleanup, while the oracle patches encode an unrelated application migration.

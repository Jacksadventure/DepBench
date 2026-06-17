# Test-patch audit — tusbar__eslint-config-xo-nextjs__163

## 1. Task summary
- Folder: tusbar__eslint-config-xo-nextjs__163
- Ecosystem: npm_and_yarn
- Upgrade: @next/eslint-plugin-next 10.2.0 -> 10.2.2
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `yarn jest`

## 2. What is the breaking change?
The upgraded Next.js ESLint plugin exposes/changes its recommended config and rule messages. The package under test is itself an ESLint config, so the repair changes `index.js` to extend `plugin:@next/next/recommended` instead of manually enabling a small set of rules.

## 3. What does Δt (test.patch) actually do?
Δt adds new fixtures for `@next/next/google-font-display`, `@next/next/google-font-preconnect`, and `@next/next/link-passhref`, adjusts existing fixtures to use `next/document`'s `Head`, and updates `__tests__/next.js` to assert new rule IDs and messages such as `@next/next/google-font-display` and `@next/next/link-passhref`.

## 4. Does Δt directly exercise the breaking change?
Yes for this package's behavior. `lintFixture('@next/next/google-font-display.incorrect.js')` expects four `@next/next/google-font-display` messages; the pre-Δc config does not extend the plugin's recommended rules, so those messages are absent, while Δc enables the recommended config and removes the stale manual rule list.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the Jest tests assert the upgraded ESLint plugin's recommended-rule behavior and fail against the old config until Δc migrates `index.js`.

## 6. Δc nature
CONFIG_INFRA_ONLY — Δc only edits the exported ESLint configuration in `index.js`; there is no application production source.

## 7. Soundness concerns / notes
This is a valid unit-test witness for an ESLint-config package, but it is lint-domain behavior. It should not be confused with a runtime application dependency break.

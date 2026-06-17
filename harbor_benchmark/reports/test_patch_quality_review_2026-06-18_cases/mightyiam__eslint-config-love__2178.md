# Test-patch audit — mightyiam__eslint-config-love__2178

## 1. Task summary
- Folder: mightyiam__eslint-config-love__2178
- Ecosystem: npm_and_yarn
- Upgrade: eslint 9.12.0 -> 9.35.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npm run compile && npx ava lib/test/export.js lib/test/resolved-config.js lib/test/rules.js`

## 2. What is the breaking change?
ESLint 9.35 exposes the new core rule `preserve-caught-error`. This config package enumerates built-in ESLint rules in its exported configuration, so the expected exported/resolved config changes with the upgraded ESLint rule set.

## 3. What does Δt (test.patch) actually do?
It updates `src/test/expected-exported-value/_eslint.ts` to include:
`'preserve-caught-error': ['error', { requireCatchParameter: true }]`.

## 4. Does Δt directly exercise the breaking change?
Yes. The AVA tests compare the package's exported/resolved ESLint rule config to the expected rule map. On P⊕Δm⊕Δt, the expected map includes the new ESLint rule but `src/plugin-usage/eslint.ts` does not, so the config tests fail. Δc adds the same rule to production config generation, making the expected export pass.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the verifier checks the source configuration surface affected by the ESLint rule-set change, not merely lint formatting.

## 6. Δc nature
REAL_SOURCE_REPAIR — one source config file adds the new `preserve-caught-error` rule with the intended options.

## 7. Soundness concerns / notes
This is a configuration-output witness rather than an application runtime witness, but it is not a lint-only `test_cmd`; the package's product is the ESLint config, and the tests validate that exported product.

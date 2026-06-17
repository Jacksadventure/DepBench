# Test-patch audit — mightyiam__eslint-config-love__2120

## 1. Task summary
- Folder: mightyiam__eslint-config-love__2120
- Ecosystem: npm_and_yarn
- Upgrade: eslint-plugin-import 2.31.0 -> 2.32.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npm run compile && npx ava lib/test/export.js lib/test/resolved-config.js lib/test/rules.js`

## 2. What is the breaking change?
eslint-plugin-import 2.32.0 adds the `enforce-node-protocol-usage` rule. The project chooses to include that new rule in its exported import-plugin configuration.

## 3. What does Δt (test.patch) actually do?
`src/test/expected-exported-value/_import.ts` adds the expected exported rule entry: `'import/enforce-node-protocol-usage': ['error', 'always']`.

## 4. Does Δt directly exercise the breaking change?
It exercises the project's "expected exported config includes all configured import rules" invariant, but not a dependency breaking change. The old config would still compile and run with eslint-plugin-import 2.32.0; Δt simply expects the newly available rule to be adopted.

## 5. Coverage verdict
TESTS_OTHER_THING — Δt tests a policy/config addition caused by a new upstream rule, not a failing API or runtime breaking change in the upgraded dependency.

## 6. Δc nature
REAL_SOURCE_REPAIR — `src/plugin-usage/import.ts` changes exported config semantics by enabling `enforce-node-protocol-usage`.

## 7. Soundness concerns / notes
- The FAIL/PASS signal is circular: Δt adds an expected config entry and Δc adds the matching actual config entry.
- This is useful project maintenance, but weak evidence for DependBench's locked breaking-change definition.

# Test-patch audit — InfluxCommunity__influxdb3-js__413

## 1. Task summary
- Folder: InfluxCommunity__influxdb3-js__413
- Ecosystem: npm_and_yarn
- Upgrade: eslint 8.43.0 -> 9.10.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `yarn run lint`

## 2. What is the breaking change?
ESLint 9 switches projects toward flat config (`eslint.config.mjs`) and changes config loading semantics. The patch adds flat-config files for the package and subdirectories.

## 3. What does Δt (test.patch) actually do?
Adds `packages/client/test/eslint.config.mjs` with globals and a rule override for test files.

## 4. Does Δt directly exercise the breaking change?
No for benchmark purposes. The verifier command is `yarn run lint`, and the user instruction for this audit states that lint/format-only `test_cmd` is always `TESTS_OTHER_THING`. Even if ESLint 9 config migration is a real toolchain compatibility issue, lint failures are excluded as witnessed breaking-change evidence.

## 5. Coverage verdict
TESTS_OTHER_THING — the only verifier is lint, and lint/format-only commands are not accepted witnessed evidence.

## 6. Δc nature
CONFIG_INFRA_ONLY — Δc only adds ESLint flat configuration files; it does not repair production runtime/source behavior.

## 7. Soundness concerns / notes
- This can remain useful as an ESLint migration case, but it should not count as a dependency-update source repair witness under the locked definition.

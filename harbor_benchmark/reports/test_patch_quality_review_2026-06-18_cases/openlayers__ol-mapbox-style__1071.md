# Test-patch audit — openlayers__ol-mapbox-style__1071

## 1. Task summary
- Folder: openlayers__ol-mapbox-style__1071
- Ecosystem: npm_and_yarn
- Upgrade: eslint-config-openlayers 18.0.0 -> 19.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx eslint test examples src`

## 2. What is the breaking change?
The dependency upgrade is an ESLint config/tooling upgrade. `eslint` is also raised to 8.56.0 and `@openlayers/eslint-plugin` is added. The observed repair is mostly conformance to the new lint/prettier rules and project lint configuration, not a runtime dependency API break.

## 3. What does Δt (test.patch) actually do?
Δt rewrites test files to satisfy the new formatter/linter style: trailing commas, callback wrapping, and line wrapping across `MapboxVectorLayer.test.js`, `apply.test.js`, `stylefunction*.test.js`, `text.test.js`, and `util.test.js`. It does not add new behavioral assertions; it reformats existing test code so the lint command accepts the test tree.

## 4. Does Δt directly exercise the breaking change?
It exercises lint-rule compliance only. Since the verifier command is `npx eslint test examples src`, failure evidence is lint/static-formatting output, which the locked definition excludes from witnessed breaking-change evidence. Δc includes `.eslintrc` changes and many source/example/doc edits needed to make the same lint command pass over non-test files.

## 5. Coverage verdict
TESTS_OTHER_THING — the verifier is a lint-only command, and lint/format failures are explicitly not witnessed dependency-breaking evidence.

## 6. Δc nature
MIXED — Δc combines lint config (`.eslintrc`, plugin/ecmaVersion), large formatter churn in `src/**/*.js`, README/example additions, and at least one source-string fix in `src/stylefunction.js`.

## 7. Soundness concerns / notes
- Useful as an ESLint-config migration task, but not as a dependency-update source-repair witness.
- The manifest upgrade is broader than the labeled package because it changes ESLint and plugin dependencies alongside `eslint-config-openlayers`.

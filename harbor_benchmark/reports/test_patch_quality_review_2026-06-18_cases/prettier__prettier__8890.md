# Test-patch audit - prettier__prettier__8890

## 1. Task summary
- Folder: prettier__prettier__8890
- Ecosystem: npm_and_yarn
- Upgrade: cosmiconfig 6.0.0 -> 7.0.0
- test_cmd: `yarn jest tests_integration/__tests__/config-resolution.js --no-colors`

## 2. What is the breaking change?
Delta c adds support for `.prettierrc.cjs` and `prettier.config.cjs` by adding those names to Prettier's `searchPlaces`. This appears to be a new feature enabled alongside the cosmiconfig upgrade, not a repair to an existing behavior that the dependency broke.

## 3. What does Delta t do?
Delta t adds an integration test that resolves `.cjs` config files across package directories with `type: module`, `type: commonjs`, and no `type`. Delta m also adds the corresponding fixture `package.json` files, while Delta c adds the actual `.cjs` config fixtures and source search-place change.

## 4. Does Delta t directly exercise the breaking change?
No. The hidden test fails on P+Delta m because `.cjs` config search support does not exist yet, then passes after Delta c adds that feature. That is feature coverage, not evidence of a dependency-induced break in existing source behavior.

## 5. Coverage verdict
TESTS_OTHER_THING

## 6. Delta c nature
MIXED

## 7. Soundness concerns / notes
- Delta c includes source, docs, changelog, and fixture additions.
- The task is useful as feature validation, but it does not satisfy the witnessed breaking-change definition.

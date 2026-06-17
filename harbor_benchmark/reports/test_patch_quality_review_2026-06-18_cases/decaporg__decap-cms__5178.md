# Test-patch audit — decaporg__decap-cms__5178

## 1. Task summary
- Folder: decaporg__decap-cms__5178
- Ecosystem: npm_and_yarn
- Upgrade: ajv ^7.0.0 -> ^8.0.0 (plus ajv-errors ^2.0.0->^3.0.0, ajv-keywords ^4.0.0->^5.0.0)
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `yarn jest packages/netlify-cms-core/src/constants/__tests__/configSchema.spec.js --no-coverage --runInBand`

## 2. What is the breaking change?
ajv 8 changed the validation-error object shape: `error.dataPath` was removed in favor of `error.instancePath`, and keyword message wording changed from "should" to "must" (ajv 8 messages natively say "must"). `ajv-errors` v3 / `ajv-keywords` v5 are the ajv-8-compatible majors. netlify-cms-core's `ConfigError` builder and `validateConfig` switch therefore had to read `instancePath` (with `dataPath` fallback) and normalize messages.

## 3. What does Δt (test.patch) actually do?
- `packages/netlify-cms-core/src/constants/__tests__/configSchema.spec.js`: rewrites ~25 `toThrowError(...)` expected strings, replacing the verb "should" with "must" throughout (e.g. `"config should have required property 'backend'"` → `"config must have required property 'backend'"`, `"'backend.name' should be string"` → `"'backend.name' must be string"`, `"'collections' should NOT have fewer than 1 items"` → `"... must NOT have fewer than 1 items"`, `"'i18n.locales[1]' should match pattern ..."` → `"... must match pattern ..."`).
- No new test cases, no fixtures; a mechanical expected-message sweep across the existing config-validation specs.

## 4. Does Δt directly exercise the breaking change?
Yes. The assertions expect correct dot-paths (e.g. `'backend.name' must be string`). On P⊕Δm (ajv 8, no Δc) the `ConfigError` constructor still reads `dataPath` (undefined in ajv 8), so `dotPath` collapses to empty and the message becomes `config must be string` rather than `'backend.name' must be string` — the `toThrowError` match fails. On P⊕Δm⊕Δc the constructor reads `instancePath` (with fallbacks) and applies `message.replace(/\bshould\b/g, 'must')`, producing the expected `'backend.name' must be string` → PASS. So Δt witnesses the `instancePath`/`dataPath` migration (the real behavioral break), with the "should"→"must" wording being a secondary alignment.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt's dot-path-specific assertions fail on P⊕Δm (broken `dataPath`→`instancePath` handling) and pass on P⊕Δm⊕Δc, exercising the ajv-8 error-shape migration.

## 6. Δc nature
REAL_SOURCE_REPAIR — `packages/netlify-cms-core/src/constants/configSchema.js`: `ConfigError` constructor now destructures `instancePath`/`dataPath`/`params` with fallback chain and applies `message.replace(/\bshould\b/g, 'must')`; `validateConfig` switch cases read `e.instancePath || e.dataPath` and update the `instanceof` message to "must be a regular expression".

## 7. Soundness concerns / notes
- Task metadata is malformed: the `library` field is `@` 2.0.1→3.0.0 (the bump is actually the ajv / ajv-errors / ajv-keywords trio). Cosmetic but the instruction reads "Dependency `@` has been upgraded".
- The "should"→"must" verb change in Δt is partly redundant with ajv 8's native wording; the load-bearing part of the witness is the `instancePath`-based dotPath, which is a genuine ajv-8 behavioral break.
- Δt is large (many assertion rewordings) but coherent and all in service of the single ajv-8 migration.

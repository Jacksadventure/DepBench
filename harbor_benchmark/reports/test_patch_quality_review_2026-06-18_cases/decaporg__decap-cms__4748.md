# Test-patch audit — decaporg__decap-cms__4748

## 1. Task summary
- Folder: decaporg__decap-cms__4748
- Ecosystem: npm_and_yarn
- Upgrade: ajv/ajv-errors/ajv-keywords unknown -> ajv 7.0.2, ajv-errors 2.0.0, ajv-keywords 4.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npm install --prefix packages/netlify-cms-core --no-save --legacy-peer-deps ajv@7.0.2 ajv-keywords@4.0.0 ajv-errors@2.0.0 && npx jest packages/netlify-cms-core/src/constants/__tests__/configSchema.spec.js --no-coverage --passWithNoTests`

## 2. What is the breaking change?
AJV 7 and ajv-keywords 4 changed import paths, strict schema behavior, recursive `$id` reuse, and error message wording/paths. The config schema needs new keyword imports, `strict: false`, and unique generated IDs for nested field schemas.

## 3. What does Δt (test.patch) actually do?
It updates `configSchema.spec.js` expected validation errors: nested relation errors now include full `collections[0]...` paths, empty object wording changes from `properties` to `items`, and min/max string length messages use `fewer/more than N characters`.

## 4. Does Δt directly exercise the breaking change?
Yes. The verifier installs the upgraded AJV packages and runs the schema tests. Without Δc, the old `ajv-keywords/keywords` import and AJV 6 schema assumptions are incompatible with AJV 7/keywords 4, and the expected error paths/messages do not match. With Δc, the schema compiles and produces the hidden test expectations.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt asserts AJV-7 validation output and P⊕Δm needs Δc's schema/import migration to pass.

## 6. Δc nature
REAL_SOURCE_REPAIR — updates production `configSchema.js` imports, AJV options, and recursive schema IDs to work with AJV 7.

## 7. Soundness concerns / notes
- The manifest metadata labels the library/version as unknown, but the patch clearly upgrades `ajv`, `ajv-errors`, and `ajv-keywords`.
- The witness is focused on config validation behavior, not unrelated CMS runtime paths.

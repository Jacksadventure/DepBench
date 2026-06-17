# Test-patch audit - operaton__operaton__1523

## 1. Task summary
- Folder: operaton__operaton__1523
- Ecosystem: maven
- Upgrade: com.networknt:json-schema-validator 1.5.9 -> 2.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `<could not extract>`; `test_state.py` runs `mvn ... -pl engine-rest/engine-rest-openapi-generator -am -Dtest=SchemaValidatorTest test`

## 2. What is the breaking change?
`json-schema-validator` 2.0 replaces the old `JsonSchemaFactory` / `JsonSchema` / `SpecVersion` / `ValidationMessage` API with `SchemaRegistry`, `Schema`, `SpecificationVersion`, and `Error`. Validation also returns the newer error type and the repair changes invalid-schema handling to throw `SchemaException`.

## 3. What does Delta t (test.patch) actually do?
It adds `SchemaValidatorTest`, with one valid JSON instance that must not throw and one invalid JSON instance that must throw `SchemaException`.

## 4. Does Delta t directly exercise the breaking change?
Yes. With only the manifest bump and hidden test, `SchemaValidator` still imports and calls classes removed or changed by validator 2.0, so the module fails to compile or run the focused test. With Delta c, the source uses `SchemaRegistry.withDefaultDialect(SpecificationVersion.DRAFT_4)`, `schema.validate(...)`, and `Error::getMessage`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the hidden test reaches the validator wrapper whose implementation must be migrated to the new networknt 2.0 API.

## 6. Delta c nature
MIXED - the core repair is real source migration in `SchemaValidator.java`, but the patch also removes obsolete build profiles.

## 7. Soundness concerns / notes
Good witness despite `test_cmd` extraction failure in metadata. The test is newly added and narrow, but it targets exactly the dependency-facing wrapper.


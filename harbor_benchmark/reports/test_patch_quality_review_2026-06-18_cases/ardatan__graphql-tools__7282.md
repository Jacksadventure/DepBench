# Test-patch audit — ardatan__graphql-tools__7282

## 1. Task summary
- Folder: ardatan__graphql-tools__7282
- Ecosystem: npm_and_yarn
- Upgrade: @babel/plugin-transform-regenerator 7.28.0 -> 7.28.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest packages/utils/tests/print-schema-with-directives.spec.ts --no-coverage --passWithNoTests`

## 2. What is the breaking change?
The source repair adds support for printing GraphQL `@oneOf` on input object types with `isOneOf`. That is a GraphQL schema-printing feature, not a behavioral break introduced by the `@babel/plugin-transform-regenerator` patch-level bump.

## 3. What does Δt (test.patch) actually do?
- Adds a `GraphQLInputObjectType` with `isOneOf: true`.
- If the installed GraphQL object exposes `isOneOf`, builds a schema and asserts `printSchemaWithDirectives(schema)` contains `input OneOfInput @oneOf`.

## 4. Does Δt directly exercise the breaking change?
No. The test exercises GraphQL `@oneOf` support in `packages/utils/src/print-schema-with-directives.ts`. It does not exercise regenerator transformation output or any Babel-runtime behavior. P⊕Δm⊕Δt would fail because the project did not yet print `@oneOf`, but that is a feature gap unrelated to the declared dependency upgrade.

## 5. Coverage verdict
TESTS_OTHER_THING — the hidden test proves `@oneOf` printing support, not a breaking change caused by `@babel/plugin-transform-regenerator` 7.28.1.

## 6. Δc nature
REAL_SOURCE_REPAIR — the patch updates directive-node handling to filter all native GraphQL directives via `specifiedDirectives`, synthesize `@oneOf` when `entity.isOneOf` is true, and preserve native `deprecated`/`specifiedBy`/`oneOf` directives. It also adds a changeset.

## 7. Soundness concerns / notes
- The test is legitimate for the `@graphql-tools/utils` feature, but the task metadata points at an unrelated Babel dependency.
- An agent repairing an actual Babel/regenerator issue would receive no useful signal from this verifier.

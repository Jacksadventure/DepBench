# Test-patch audit — graphql-java-kickstart__graphql-java-tools__560

## 1. Task summary
- Folder: graphql-java-kickstart__graphql-java-tools__560
- Ecosystem: maven
- Upgrade: graphql-java.version 16.2 -> 17.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `<could not extract>`

## 2. What is the breaking change?
graphql-java 17 renamed `SchemaGeneratorHelper.buildDirective(...)` to `buildAppliedDirective(...)` with a new `BuildContext`-bearing signature, and made the `Coercing` interface methods non-nullable (`Any?` → `Any` in Kotlin, throwing instead of returning null). The SDL parser also moved interface lists from `,` to `&` syntax.

## 3. What does Δt (test.patch) actually do?
- `EndToEndSpecHelper.kt`: rewrites three `Coercing` impls (`customScalarId`, `customScalarUUID`, `customScalarMap`) to non-nullable `Any` signatures that throw `CoercingParseLiteralException` instead of returning null.
- `MethodFieldResolverTest.kt`: same `Coercing` signature migration for the `CustomScalar` coercing (+ imports `CoercingParseLiteralException`/`CoercingSerializeException`), and `CustomScalar.of(input: Any)` throws instead of returning null.
- `SchemaClassScannerTest.kt`: same `Coercing` signature migration on two scalar helpers.
- `src/test/resources/Place.graphqls`: changes `type Place1 implements Entity, Place, OtherPlace` → `implements Entity & Place & OtherPlace` (graphql-java 17 SDL syntax).

## 4. Does Δt directly exercise the breaking change?
Yes. The `Coercing` signature changes and the `Place.graphqls` `&` syntax are exactly the graphql-java 17 contract. Without Δc, `SchemaGeneratorHelperExt.kt` still calls `super.buildDirective(null, ...)` which no longer exists in graphql-java 17 (renamed to `buildAppliedDirective` with a `BuildContext`) → compile failure; with Δc the source calls `super.buildAppliedDirective(context, ...)` and the updated tests compile and pass.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt migrates test Coercing impls and SDL syntax to the graphql-java 17 contract; P⊕Δm⊕Δt fails to compile (source still calls removed `buildDirective`) and P⊕Δm⊕Δc⊕Δt passes.

## 6. Δc nature
REAL_SOURCE_REPAIR — `SchemaParser.kt` and `SchemaGeneratorHelperExt.kt` migrate to `buildAppliedDirective` with a `BuildContext`; the two vendored `directive/` Java files are re-synced from graphql-java 17.0 (one adds the new `schemaDirectiveWiringIsRequired` method). MIXED with VENDOR_ONLY on the two copied files.

## 7. Soundness concerns / notes
- `test_cmd` could not be extracted from `test_state.py`; the actual Maven test invocation is missing, threatening runnability.
- Several Δt hunks are pure signature adaptations (compile-level witness), but the `Place.graphqls` `&` change is a genuine behavioral test of the 17 SDL parser, giving decent coverage.

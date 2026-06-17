# Test-patch audit — graphql-java-kickstart__graphql-java-tools__800

## 1. Task summary
- Folder: graphql-java-kickstart__graphql-java-tools__800
- Ecosystem: maven
- Upgrade: graphql-java 23.1 -> 25.0 plus project groupId/version metadata
- test_cmd: `mvn ... -Dtest=EndToEndSpecHelper,MethodFieldResolverDataFetcherTest,MethodFieldResolverTest,SchemaClassScannerDirectiveTest,SchemaParserTest test` (extracted from verifier)

## 2. What is the breaking change?
graphql-java 25 tightens or changes nullability in several APIs. The production Kotlin code must accept nullable source locations and nullable relay directive type names, and must avoid direct dereferences of possibly-null `FieldDefinition.sourceLocation`.

## 3. What does Δt (test.patch) actually do?
The hidden tests are updated for the graphql-java 25 nullability/API surface: scalar maps and custom values become nullable, `DataFetchingEnvironment` construction always supplies a `GraphQLContext`, and source-location assertions use safe calls.

## 4. Does Δt directly exercise the breaking change?
Yes. The verifier compiles and runs the affected test classes under graphql-java 25. Without Δc, production Kotlin code still treats now-nullable values as non-null and directly dereferences `field.sourceLocation`, which is a compile/runtime compatibility break under the new API.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden tests update the project to graphql-java 25 expectations and force compilation/execution through the nullable API surface that Δc repairs.

## 6. Δc nature
REAL_SOURCE_REPAIR — production Kotlin source is updated for nullable API types in `RelayConnectionFactory` and `FieldResolverScanner`.

## 7. Soundness concerns / notes
- The manifest patch includes publishing metadata churn in addition to the dependency bump, but the source/test witness concerns graphql-java 25 nullability.
- Δt mostly adapts existing tests rather than adding a new behavioral assertion, but the compile-time API witness is still legitimate for a compiled language task.


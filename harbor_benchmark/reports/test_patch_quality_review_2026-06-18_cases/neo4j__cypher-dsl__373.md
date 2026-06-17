# Test-patch audit — neo4j__cypher-dsl__373

## 1. Task summary
- Folder: neo4j__cypher-dsl__373
- Ecosystem: maven
- Upgrade: neo4j-cypher-javacc-parser 4.4.6 -> 4.4.7
- test_cmd: `mvn ... -pl neo4j-cypher-dsl-parser -am -Dtest=CypherDslASTFactoryTest test` (extracted from verifier)

## 2. What is the breaking change?
The parser AST factory interface changed in Neo4j 4.4.7: the previous database-alias methods were replaced or split into methods such as `showAliases`, `createLocalDatabaseAlias`, `createRemoteDatabaseAlias`, `alterLocalDatabaseAlias`, and `alterRemoteDatabaseAlias`. `CypherDslASTFactory` must implement the new interface shape to compile and to preserve the existing unsupported-operation behavior.

## 3. What does Δt (test.patch) actually do?
`CypherDslASTFactoryTest` adds a nested parameterized test that reflects over the factory and verifies each new method exists and throws `UnsupportedOperationException` when invoked.

## 4. Does Δt directly exercise the breaking change?
Yes. The hidden test directly names the new methods introduced by the dependency update. Without Δc the project is expected to fail compilation because `CypherDslASTFactory` no longer satisfies the upgraded parser interface; if it did compile, the reflection test would still fail if the new methods were absent or did not preserve unsupported behavior.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt checks the new 4.4.7 AST-factory surface, and Δc is the corresponding source adaptation.

## 6. Δc nature
REAL_SOURCE_REPAIR — one production parser factory is updated to implement the new dependency interface methods.

## 7. Soundness concerns / notes
- `manifest.patch` also excludes shaded parser internals from japicmp, but that is part of Δm, not Δc.
- The hidden test is narrow but appropriate: it directly targets the interface drift.


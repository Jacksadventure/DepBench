# Test-patch audit — graphql-java-kickstart__graphql-java-tools__645

## 1. Task summary
- Folder: graphql-java-kickstart__graphql-java-tools__645
- Ecosystem: maven
- Upgrade: graphql-java.version 17.3 -> 18.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `<could not extract>` (test_state runs Maven test-compile / Maven tests)

## 2. What is the breaking change?
graphql-java 18 introduces the applied-directive model (`GraphQLAppliedDirective`, `getAppliedDirectives()`) and tighter nullable definition types. The project must build SDL directive definitions and applied directives explicitly, include directive definitions in scanned schema objects, and pass applied directives through directive wiring environments.

## 3. What does Δt (test.patch) actually do?
- `SchemaClassScannerTest.kt`: adds Apollo federation directive definitions (`@key`, `@extends`, `@external`) and the `_FieldSet` scalar, then registers that scalar.
- `SchemaParserTest.kt`: updates assertions to dereference nullable `.definition!!`.
- `RelayConnection.graphqls`: declares `directive @connection(for: String!) on FIELD` and reformats the SDL.

## 4. Does Δt directly exercise the breaking change?
Yes. The new directive definitions and applied directive usage require Δc's schema-parser changes to create directives, applied directives, and directive arguments under graphql-java 18. Without Δc the upgraded source either fails compilation/API compatibility or cannot build the expected directive metadata; with Δc the parser/wiring path handles the graphql-java 18 contract.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt exercises graphql-java 18 applied-directive and nullable-definition behavior; P⊕Δm⊕Δt fails without the schema parser / wiring migration and passes with Δc.

## 6. Δc nature
REAL_SOURCE_REPAIR — Kotlin/Java source migrates schema scanning, schema construction, directive creation, directive arguments, applied directives, and directive wiring environment plumbing for graphql-java 18.

## 7. Soundness concerns / notes
- `test_cmd` is not cleanly extracted, but the verifier command in `test_state.py` does run Maven tests after applying Δt.
- Some Δt hunks are Kotlin nullability adaptations, but the directive-definition additions are substantive witnesses.

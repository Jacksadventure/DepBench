# Test-patch audit — OpenRefine__OpenRefine__7503

## 1. Task summary
- Folder: OpenRefine__OpenRefine__7503
- Ecosystem: maven
- Upgrade: jena.version 4.10.0 -> 5.6.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE`

## 2. What is the breaking change?
Jena 5 changes RDF parsing output for literals and blank-node ordering, while the upgraded dependency tree also appears to remove the old `org.apache.http.HttpHeaders` type that OpenRefine imported transitively. Δc repairs the compile break by switching to `org.apache.hc.core5.http.HttpHeaders`.

## 3. What does Δt (test.patch) actually do?
Δt touches `main/tests/server/src/com/google/refine/importers/RdfTripleImporterTests.java`. It replaces string charset lookup with `StandardCharsets.UTF_8`, updates expected RDF literal values to keep quotes such as `"Robert Zimmerman"@en`, and makes the blank-node test insensitive to row and column ordering.

## 4. Does Δt directly exercise the breaking change?
It exercises Jena 5 parser behavior, especially quoted language-tagged literals and nondeterministic blank-node row placement. It does not directly execute `HttpHeadersSupport.java`; the Δc witness is instead a compile/import failure in main sources before the RDF tests can run.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the Maven verifier compiles `main`, so P⊕Δm⊕Δt should fail on the removed/relocated HttpComponents header import, and P⊕Δm⊕Δc⊕Δt compiles and runs the updated Jena RDF parser expectations.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc updates production source `main/src/com/google/refine/commands/HttpHeadersSupport.java` from the old Apache HttpComponents 4 header class to the core5 header class.

## 7. Soundness concerns / notes
- `test_cmd` is marked `TEST_CMD_UNEXTRACTABLE`; the bundle shows a generated Maven command targeting `RdfTripleImporterTests`, but the summary metadata could not extract it cleanly.
- Δt and Δc cover different facets of the dependency upgrade: Δt checks Jena parser behavior, while Δc fixes a transitive compile break.

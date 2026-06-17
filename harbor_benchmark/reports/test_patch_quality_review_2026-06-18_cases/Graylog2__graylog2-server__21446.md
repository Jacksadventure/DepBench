# Test-patch audit — Graylog2__graylog2-server__21446

## 1. Task summary
- Folder: Graylog2__graylog2-server__21446
- Ecosystem: maven
- Upgrade: com.google.protobuf:protobuf-bom 3.25.5 -> 3.25.6
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: Maven `RawMessageTest` command extracted in `tests/test_state.py`

## 2. What is the breaking change?
The protobuf runtime/generator API changed enough that previously generated Java protobuf classes no longer match the upgraded protobuf runtime. Δc largely regenerates protobuf Java code and updates generated-code comments/proto regeneration notes.

## 3. What does Δt (test.patch) actually do?
`RawMessageTest.java` removes the unused `java.io.IOException` import and drops `throws IOException` from `minimalEncodeDecode()`.

## 4. Does Δt directly exercise the breaking change?
The test edit itself is small, but the verifier compiles and runs `RawMessageTest` through Maven. Without the regenerated protobuf sources in Δc, the old generated code still references APIs/shapes from the prior protobuf generation/runtime and should fail during compilation under the upgraded BOM. With Δc, the generated source is compatible and the raw-message roundtrip test can compile/run.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the decisive evidence is a deterministic compile witness from stale generated protobuf Java code against protobuf 3.25.6.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc updates production generated Java sources and proto regeneration metadata, plus one production exception-wrapping call. It is not merely tests or formatting.

## 7. Soundness concerns / notes
The hidden test patch does not add a new protobuf assertion; it relies on the Maven test compile to expose the generated-code/runtime mismatch. That is still a valid compile-level dependency break, but the behavioral coverage is narrow.

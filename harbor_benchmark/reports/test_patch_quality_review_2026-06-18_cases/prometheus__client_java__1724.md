# Test-patch audit — prometheus__client_java__1724

## 1. Task summary
- Folder: prometheus__client_java__1724
- Ecosystem: maven
- Upgrade: protobuf-java.version 4.33.1 -> 4.33.2
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE`

## 2. What is the breaking change?
The project vendors/generated protobuf Java classes into versioned packages. Bumping protobuf from 4.33.1 to 4.33.2 changes the generated package path from `generated.com_google_protobuf_4_33_1` to `generated.com_google_protobuf_4_33_2`, so all imports of the old generated package stop compiling.

## 3. What does Δt (test.patch) actually do?
Δt updates seven test files, including exporter integration tests and core metric tests, to import `io.prometheus.metrics.expositionformats.generated.com_google_protobuf_4_33_2.Metrics` instead of the 4.33.1 package.

## 4. Does Δt directly exercise the breaking change?
Yes. The patched tests import and use the new generated `Metrics` package; without Δc, production `PrometheusProtobufWriterImpl.java` still imports the old generated package and the Maven compile/test phase fails.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — P⊕Δm⊕Δt fails on stale generated protobuf imports in production code, and P⊕Δm⊕Δc⊕Δt passes once source and tests agree on the 4.33.2 generated package.

## 6. Δc nature
MIXED — Δc updates production source `PrometheusProtobufWriterImpl.java` and also changes `mise.toml` from `protoc` 33.1 to 33.2.

## 7. Soundness concerns / notes
- `test_cmd` is marked `TEST_CMD_UNEXTRACTABLE`; the embedded test_state contains a generated Maven command targeting the affected tests, but the metadata could not extract a compact command.
- The task is primarily generated-code package churn, not a semantic protobuf runtime behavior assertion.

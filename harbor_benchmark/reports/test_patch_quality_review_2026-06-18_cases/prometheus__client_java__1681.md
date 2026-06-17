# Test-patch audit — prometheus__client_java__1681

## 1. Task summary
- Folder: prometheus__client_java__1681
- Ecosystem: maven
- Upgrade: protobuf-java.version 4.33.0 -> 4.33.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE`

## 2. What is the breaking change?
The project encodes the protobuf Java version into the generated metrics package name. Moving protobuf/protoc from 4.33.0 to 4.33.1 changes references from `generated.com_google_protobuf_4_33_0.Metrics` to `generated.com_google_protobuf_4_33_1.Metrics`, so source and tests must import the regenerated package.

## 3. What does Δt (test.patch) actually do?
Seven test files update only their generated protobuf import, including `ExporterTest`, `ExporterIT`, `ApplicationTest`, `CounterTest`, `HistogramTest`, `InfoTest`, and `ProtobufExpositionFormatsTest`, replacing `com_google_protobuf_4_33_0.Metrics` with `com_google_protobuf_4_33_1.Metrics`.

## 4. Does Δt directly exercise the breaking change?
Yes. The hidden tests compile against the 4.33.1-generated protobuf package. On P⊕Δm the production writer still imports `com_google_protobuf_4_33_0.Metrics`, so the Maven compile/test path is inconsistent with the regenerated protobuf package; Δc changes `PrometheusProtobufWriterImpl` to the 4.33.1 package.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt expects the new versioned generated protobuf package, and the old source import fails the upgraded compile/test path until Δc updates it.

## 6. Δc nature
MIXED — Δc includes real source adaptation in `PrometheusProtobufWriterImpl.java`, plus config/infra changes in `mise.toml`, `.github/workflows/lint-rest.yml`, `.mise/tasks/lint/bom.py`, and `generate-protobuf.sh`.

## 7. Soundness concerns / notes
The human summary says "lint scripts", and much of Δc is infrastructure churn. The discriminating verifier evidence is still the Java import migration, not lint; the compact `test_cmd` is unextractable, but the generated command targets Maven compile/tests for the affected protobuf users.

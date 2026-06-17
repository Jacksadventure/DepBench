# Test-patch audit - prometheus__client_java__1402

## 1. Task summary
- Folder: prometheus__client_java__1402
- Ecosystem: maven
- Upgrade: protobuf-java.version 4.31.0 -> 4.31.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `mvn ... -Dtest=ExporterTest,ExporterIT,ApplicationTest,CounterTest,HistogramTest,InfoTest,ProtobufExpositionFormatsTest test`

## 2. What is the breaking change?
This project versions generated protobuf Java packages by protobuf version. After upgrading protobuf from 4.31.0 to 4.31.1, generated classes move from `generated.com_google_protobuf_4_31_0` to `generated.com_google_protobuf_4_31_1`. Imports that reference the old generated package no longer match the regenerated sources.

## 3. What does test.patch actually do?
The hidden patch updates test imports across integration and unit tests from `io.prometheus.metrics.expositionformats.generated.com_google_protobuf_4_31_0.Metrics` to `...com_google_protobuf_4_31_1.Metrics`.

## 4. Does test.patch directly exercise the breaking change?
Yes. The patched tests compile against the 4.31.1 generated package name. Without Delta_c, production `PrometheusProtobufWriterImpl` still imports the 4.31.0 generated package, so the upgraded build/test compile is inconsistent.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the hidden tests witness the generated protobuf package-name migration caused by the protobuf-java version bump.

## 6. Delta_c nature
MIXED - it includes the real production import repair plus protobuf generation tooling/config changes in `mise.toml` and `generate-protobuf.sh`.

## 7. Soundness concerns / notes
The repair is partly generated-code workflow maintenance rather than hand logic, but the failing surface is still compile-time source compatibility with the upgraded protobuf package.

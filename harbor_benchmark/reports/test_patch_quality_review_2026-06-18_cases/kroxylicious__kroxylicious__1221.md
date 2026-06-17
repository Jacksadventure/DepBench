# Test-patch audit - kroxylicious__kroxylicious__1221

## 1. Task summary
- Folder: kroxylicious__kroxylicious__1221
- Ecosystem: maven
- Upgrade: io.micrometer:micrometer-bom 1.12.5 -> 1.13.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE` (test_state.py runs Maven against `kroxylicious-integration-tests`, including `MetricsIT`)

## 2. What is the breaking change?
Micrometer 1.13 moves the Prometheus registry classes from `io.micrometer.prometheus` to `io.micrometer.prometheusmetrics`, and the Prometheus 1.x text output no longer emits a trailing comma for a single label. Old source imports no longer compile and old metric regexes expect the old label shape.

## 3. What does test.patch actually do?
`MetricsIT.assertResponseBodyContainsMeterWithTag` changes the expected label regex from `\{tag="value",\}` to `\{tag="value"\}`.

## 4. Does test.patch directly exercise the breaking change?
Yes. The verifier targets the integration-test module. On P+Delta_m+Delta_t, production code still imports the old Prometheus package and fails to compile; after Delta_c updates the imports and metric regex helpers, the patched `MetricsIT` expectation matches the new single-label output.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the hidden test is on the metrics/Prometheus path affected by the Micrometer upgrade, and the Maven compile/test gate fails without the source migration.

## 6. Delta_c nature
REAL_SOURCE_REPAIR - runtime/admin source imports are migrated to `io.micrometer.prometheusmetrics`, and metric collection utilities are adjusted for the new Prometheus label/value format.

## 7. Soundness concerns / notes
The extracted command is not concise because the Maven harness generates a long fallback command, but it clearly runs the `MetricsIT` path. The source patch also contains a logging improvement and system-test utility cleanup, but the core is a real dependency API/output migration.

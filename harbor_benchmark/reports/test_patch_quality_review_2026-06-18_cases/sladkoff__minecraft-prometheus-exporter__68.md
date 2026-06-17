# Test-patch audit — sladkoff__minecraft-prometheus-exporter__68

## 1. Task summary
- Folder: sladkoff__minecraft-prometheus-exporter__68
- Ecosystem: maven
- Upgrade: jetty.version 9.4.38.v20210224 -> 11.0.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `mvn ... -Dtest=PrometheusExporterTest test`

## 2. What is the breaking change?
Jetty 11 moves from `javax.servlet` to `jakarta.servlet`, changes handler signatures/status constants, and requires source code using Jetty server/handler APIs to be updated. The old `MetricsController` imports `javax.servlet.http.*` and uses the older handler parameter naming/API style.

## 3. What does Δt (test.patch) actually do?
Δt adds `PrometheusExporterTest`, which starts a new `MetricsServer`, makes HTTP requests with RestAssured, and asserts `/metrics` returns Prometheus text with `HttpStatus.OK_200` while unknown paths return `HttpStatus.NOT_FOUND_404`. It also adds Mockito inline mock-maker config for final Bukkit methods.

## 4. Does Δt directly exercise the breaking change?
Yes. The hidden test imports and instantiates `MetricsServer`, a class added by Δc around the Jetty 11 server setup. Without Δc, there is no `MetricsServer`, and the old `MetricsController` still uses `javax.servlet` imports incompatible with Jetty 11. With Δc, the code uses `jakarta.servlet`, Jetty `HttpStatus`, and the extracted `MetricsServer` abstraction that the hidden tests drive.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the verifier covers the migrated Jetty 11 server path and fails/pass around the source API migration.

## 6. Δc nature
REAL_SOURCE_REPAIR — production server/controller code is migrated to Jetty 11 APIs and refactored into `MetricsServer`.

## 7. Soundness concerns / notes
Clean witness. The test is partly new coverage rather than a minimal compile check, but it directly exercises the upgraded Jetty server behavior.

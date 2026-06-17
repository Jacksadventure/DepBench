# Test-patch audit — sourcenetwork__defradb__1577

## 1. Task summary
- Folder: sourcenetwork__defradb__1577
- Ecosystem: go_modules
- Upgrade: go.opentelemetry.io/otel/metric 0.36.0 -> 1.16.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test ./metric/... -v`

## 2. What is the breaking change?
OpenTelemetry metrics API changed between the pre-1.0 metric package and 1.16: `instrument`/`unit` packages are gone, instrument types live under `metric`, `metric.WithUnit` takes strings, and manual reader collection now fills `metricdata.ResourceMetrics` via an output parameter.

## 3. What does Δt (test.patch) actually do?
It updates `metric_test.go` for the new API: unit constants become strings (`"ms"`, `"1"`), `Dump` returns `*metricdata.ResourceMetrics` directly, histogram data uses generic `metricdata.Histogram[int64]`, and sums are asserted as `int64`.

## 4. Does Δt directly exercise the breaking change?
Yes. The tests call `GetSyncHistogram`, `GetSyncCounter`, and `Dump`. Without Δc, the metric package still imports removed packages and exposes old types/signatures, so P⊕Δm⊕Δt fails to compile. With Δc, the source API matches OTel 1.16 and the assertions pass.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — compile-level and API-level OpenTelemetry metric changes are directly covered by Δt.

## 6. Δc nature
REAL_SOURCE_REPAIR — production `metric/metric.go` is migrated to the OTel 1.16 metric and `metricdata` APIs.

## 7. Soundness concerns / notes
- The witness is narrow but clean: one source file and one matching test file under `metric/`.
- The sdk metric version in Δm is 0.39.0 while metric is 1.16.0; Δc handles that mixed OTel API surface.

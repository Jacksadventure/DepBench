# Test-patch audit — open-telemetry__opentelemetry-go__1872

## 1. Task summary
- Folder: open-telemetry__opentelemetry-go__1872
- Ecosystem: go_modules
- Upgrade: go.opentelemetry.io/proto/otlp 0.7.0 -> 0.8.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test ./...`

## 2. What is the breaking change?
OTLP proto 0.8 collapses the old split metric data-point types (`IntGauge`, `DoubleGauge`, `IntSum`, `DoubleSum`, `IntHistogram`, `DoubleHistogram`) into unified `Gauge`, `Sum`, `Histogram`, and `Summary` forms using `NumberDataPoint` with `AsInt` / `AsDouble` oneofs.

## 3. What does Δt do?
Δt rewrites metric expectations in `exporters/otlp/internal/transform/metric_test.go` and `exporters/otlp/otlp_metric_test.go` to expect `metricpb.Sum`, `metricpb.Gauge`, `metricpb.Histogram`, `metricpb.Summary`, and `NumberDataPoint_{AsInt,AsDouble}` values instead of the removed int/double-specific message types.

## 4. Does Δt directly exercise the dependency break?
Yes. On P⊕Δm, the old transform code still constructs removed proto fields/types such as `Metric_IntGauge`, `IntDataPoint`, and `DoubleSum`, causing compile failure. With Δc, the transform code emits the new unified proto shapes and the Δt expectations match them.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the upgraded OTLP proto API breaks the old source at compile time and Δt directly asserts the new metric representation after Δc.

## 6. Δc nature
REAL_SOURCE_REPAIR — OTLP metric transformation and test helpers are migrated to the 0.8 unified metric proto model.

## 7. Soundness concerns / notes
Clean witnessed case. This is the same family as the later OTLP 0.8 -> 0.9 task, but here the break is the unified metric-type migration rather than the labels-to-attributes migration.

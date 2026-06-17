# Test-patch audit — open-telemetry__opentelemetry-go__1943

## 1. Task summary
- Folder: open-telemetry__opentelemetry-go__1943
- Ecosystem: go_modules
- Upgrade: go.opentelemetry.io/proto/otlp 0.8.0 -> 0.9.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test ./...`

## 2. What is the breaking change?
OTLP proto 0.9.0 renamed the `Labels` field to `Attributes` on `NumberDataPoint`/`SummaryDataPoint`/`HistogramDataPoint`, and replaced `[]*commonpb.StringKeyValue` (string-only value) with `[]*commonpb.KeyValue` whose `Value` is a typed `*commonpb.AnyValue` (`BoolValue`/`IntValue`/`DoubleValue`/`StringValue`/`ArrayValue`). The old `StringKeyValue` type and `Labels` field are removed.

## 3. What does Δt (test.patch) actually do?
- `exporters/otlp/internal/transform/metric_test.go`: rewrites `TestStringKeyValues` expected table from `{Key, Value: "8"}` (`StringKeyValue`) to `{Key, Value: &commonpb.AnyValue{Value: &commonpb.AnyValue_IntValue{IntValue: 8}}}` (`KeyValue`/`AnyValue`), asserting `keyValues(labels.Iter())`; updates `TestMinMaxSumCountDatapoints`, `TestSumIntDataPoints`, `TestSumFloatDataPoints`, `TestLastValueIntDataPoints`, `TestExactIntDataPoints`, `TestExactFloatDataPoints` to use `Attributes: []*commonpb.KeyValue{...}` with `AnyValue` values.
- `exporters/otlp/otlp_metric_test.go`: retypes `cpu1Labels`/`cpu2Labels` from `[]*commonpb.StringKeyValue` to `[]*commonpb.KeyValue` with `AnyValue` (`IntValue` for CPU, `StringValue` for host), and switches every `Labels:` expectation to `Attributes:` across all grouping-export tests.

## 4. Does Δt directly exercise the breaking change?
Yes. A representative assertion:
```
assert.Equal(t, test.expected, keyValues(labels.Iter()))
// expected: []*commonpb.KeyValue{{Key: "eight", Value: &commonpb.AnyValue{Value: &commonpb.AnyValue_IntValue{IntValue: 8}}}, ...}
```
On P⊕Δm the original source `metric.go` still references the removed `Labels` field and `stringKeyValues` returning `[]*commonpb.StringKeyValue` -> compile error -> `go test ./...` FAILS. With Δc (`Attributes`, `keyValues` returning `[]*commonpb.KeyValue`, plus new `value()`/`arrayValue()` helpers) it compiles and the Δt typed-attribute expectations pass.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the proto 0.9.0 `Labels`->`Attributes` + `StringKeyValue`->`KeyValue`/`AnyValue` rename forces a compile failure on P⊕Δm that Δc repairs, and Δt directly asserts the new typed-attribute serialization (`AnyValue` Int/Bool/Double/String).

## 6. Δc nature
REAL_SOURCE_REPAIR — `exporters/otlp/internal/transform/metric.go`: renames `stringKeyValues` -> `keyValues` returning `[]*commonpb.KeyValue`, switches all data-point builders from `Labels: pbLabels` to `Attributes: pbAttrs`, and adds `value()` (attribute.Value -> `AnyValue` for BOOL/INT64/FLOAT64/ARRAY/default) and `arrayValue()` helpers.

## 7. Soundness concerns / notes
Clean, well-witnessed task. Δt's typed expectations (`AnyValue` variants) genuinely pin the new serialization behavior Δc implements, not just the compile. No soundness concerns.

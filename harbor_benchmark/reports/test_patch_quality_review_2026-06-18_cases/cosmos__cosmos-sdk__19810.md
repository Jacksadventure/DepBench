# Test-patch audit — cosmos__cosmos-sdk__19810

## 1. Task summary
- Folder: cosmos__cosmos-sdk__19810
- Ecosystem: go_modules
- Upgrade: cosmossdk.io/store 1.0.2 -> 1.1.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test ./telemetry/... -run TestMetrics -count=1 -v`

## 2. What is the breaking change?
The store bump pulls a newer Prometheus stack where `github.com/prometheus/common/expfmt` no longer exposes the old text format constant in the same way. Production telemetry code must create the encoder with `expfmt.NewFormat(expfmt.TypeTextPlain)` and return the explicit Prometheus text content type string instead of `string(expfmt.FmtText)`.

## 3. What does Δt (test.patch) actually do?
- `telemetry/metrics_test.go`: removes the direct `expfmt` import.
- Updates `TestMetrics_Prom` from expecting `string(expfmt.FmtText)` to expecting the package-level `ContentTypeText` constant.
- Keeps the existing metrics-content assertion (`test_dummy_counter 30`) unchanged.

## 4. Does Δt directly exercise the breaking change?
Yes. The verifier runs the telemetry test that calls `m.Gather(FormatPrometheus)`. On P⊕Δm, `telemetry/metrics.go` still uses the old `expfmt.FmtText` path and old content-type value, so the upgraded Prometheus API/content-type expectation is not satisfied. Δc adds `ContentTypeText`, switches encoder construction to `expfmt.NewFormat(expfmt.TypeTextPlain)`, and returns that new content type.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden test asserts the post-upgrade Prometheus text content type through the real telemetry gather path, and Δc repairs the upgraded expfmt API/content-type behavior.

## 6. Δc nature
MIXED — `telemetry/metrics.go` is a real source repair, but the patch also contains multiple `CHANGELOG.md` updates for the root and module changelogs.

## 7. Soundness concerns / notes
The core witness is clean, but Δc is not source-only because of changelog churn. The task is still a valid witnessed dependency API repair for the telemetry package.

# Test-patch audit — ymtdzzz__otel-tui__153

## 1. Task summary
- Folder: ymtdzzz__otel-tui__153
- Ecosystem: go_modules
- Upgrade: github.com/open-telemetry/opentelemetry-collector-contrib/receiver/zipkinreceiver 0.107.0 -> 0.108.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test ./tuiexporter/internal/sharedcomponent/... -v`

## 2. What is the breaking change?
OpenTelemetry Collector 0.108 moved component status reporting away from `component.TelemetrySettings.ReportStatus` / `component.StatusEvent` toward the `componentstatus` reporter/host mechanism. Shared components now need to report status through a host-side `componentstatus.Reporter` and replay prior status events to later component instances.

## 3. What does Δt (test.patch) actually do?
- Rewrites shared-component tests to import `go.opentelemetry.io/collector/component/componentstatus`.
- Replaces `component.Status` / `StatusEvent` expectations with `componentstatus.Status` / `Event`.
- Adds a `testHost` implementing `componentstatus.Reporter` and verifies that multiple starts receive replayed status events, with different expected reporter counts for start-error and shutdown-error cases.

## 4. Does Δt directly exercise the breaking change?
Yes. P⊕Δm still uses the old `TelemetrySettings.ReportStatus` design and old component status event types. Against the upgraded Collector APIs and hidden tests, it either fails to compile or fails the new reporter/replay expectations. Δc adds a `hostWrapper` implementing `componentstatus.Reporter`, reports start/stop/error events through it, and replays previous events to additional reporter hosts.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden tests directly target the Collector 0.108 status-reporting API migration and the shared-component semantics implemented by Δc.

## 6. Δc nature
REAL_SOURCE_REPAIR — `sharedcomponent.go` migrates status reporting to `componentstatus`, introduces `hostWrapper`, preserves event replay for multiple shared instances, and updates shutdown/error reporting.

## 7. Soundness concerns / notes
Clean, focused witness. The test covers both API adaptation and the multi-instance status replay behavior that the old implementation no longer provides under the new API.

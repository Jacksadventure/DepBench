# Test-patch audit - influxdata__telegraf__14250

## 1. Task summary
- Folder: influxdata__telegraf__14250
- Ecosystem: go_modules
- Upgrade: github.com/showwin/speedtest-go 1.6.6 -> 1.6.7
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test -v -count=1 -timeout 300s ./...`

## 2. What is the breaking change?
`speedtest-go` changes `speedtest.UserConfig`: the old boolean `ICMP` field is replaced by a `PingMode` enum such as `speedtest.HTTP` or `speedtest.ICMP`. The old Telegraf source no longer compiles against the upgraded dependency.

## 3. What does test.patch actually do?
`internet_speed_test.go` calls `internetSpeed.Init()` before `Gather` in both tests and simplifies the final accumulator assertion to use `metric.Fields` and `metric.Tags` directly.

## 4. Does test.patch directly exercise the breaking change?
Yes at compile level. The verifier runs Go tests for the `internet_speed` package. On P+Delta_m+Delta_t, `internet_speed.go` still sets the removed `ICMP` field and fails to compile. Delta_c selects `speedtest.HTTP` or `speedtest.ICMP` and assigns `PingMode`, allowing the tests to build and run.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the Go compile/test gate directly catches the speedtest-go `UserConfig` API change.

## 6. Delta_c nature
REAL_SOURCE_REPAIR - production Go code migrates from the removed `ICMP` boolean to the new `PingMode` enum.

## 7. Soundness concerns / notes
The added `Init()` calls are mostly test setup hygiene; the actual witness is the package compile failure against the changed dependency API.

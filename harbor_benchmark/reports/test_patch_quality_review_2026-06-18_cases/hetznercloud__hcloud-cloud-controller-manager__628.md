# Test-patch audit — hetznercloud__hcloud-cloud-controller-manager__628

## 1. Task summary
- Folder: hetznercloud__hcloud-cloud-controller-manager__628
- Ecosystem: go_modules
- Upgrade: github.com/hetznercloud/hcloud-go/v2 2.6.0 -> 2.13.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `export PATH=/usr/local/go/bin:$PATH && go test ./... -count=1 -timeout=300s`

## 2. What is the breaking change?
hcloud-go changed several client APIs: polling/retry backoff moved into `PollOpts`/`RetryOpts`, action watching moved from `WatchProgress`/local `WatchAction` wrapping to `Action.WaitFor`, and `IsError` now accepts multiple error codes in one call. The project also adopts the new `envutil.LookupEnvWithFile` helper.

## 3. What does Δt (test.patch) actually do?
Δt touches `tests/e2e/cloud_test.go` and `tests/e2e/testing.go`. It replaces `hcops.WatchAction(ctx, &testCluster.hcloud.Action, action)` with `testCluster.hcloud.Action.WaitFor(ctx, action)` and migrates `WithPollBackoffFunc` to `WithPollOpts` plus `ExponentialBackoffWithOpts`.

## 4. Does Δt directly exercise the breaking change?
Yes. The hidden e2e test sources compile against the new hcloud-go API, and the full `go test ./...` also compiles production packages that had to migrate all action-wait and backoff call sites.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — P⊕Δm⊕Δt fails to compile because old `WatchAction`/`WatchProgress`/backoff APIs remain in source, while P⊕Δm⊕Δc⊕Δt passes after the hcloud-go API migration.

## 6. Δc nature
MIXED — Δc includes real production repairs in `hcloud/routes.go`, `internal/config/config.go`, and `internal/hcops/*.go`, plus extensive test and mock updates in `*_test.go` and `internal/mocks`.

## 7. Soundness concerns / notes
- The witness is mostly compile-time API compatibility; the e2e tests changed by Δt may not be meaningfully runnable without external Hetzner credentials, but `go test ./...` still compiles them.
- Because Δc includes tests/mocks, agents constrained away from tests may be graded on a narrower subset than the full human patch.

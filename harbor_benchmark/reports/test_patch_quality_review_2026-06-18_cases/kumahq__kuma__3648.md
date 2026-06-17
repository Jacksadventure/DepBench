# Test-patch audit — kumahq__kuma__3648

## 1. Task summary
- Folder: kumahq__kuma__3648
- Ecosystem: go_modules
- Upgrade: github.com/sethvargo/go-retry 0.1.0 -> 0.2.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test ./app/kuma-dp/pkg/dataplane/envoy/... ./pkg/hds/authn/... -count=1`

## 2. What is the breaking change?
go-retry 0.2 changes constructor ergonomics: `retry.NewConstant` and `retry.NewExponential` are used directly as backoff values rather than returning `(Backoff, error)`. It also changes error propagation so the final errors in these retry paths no longer include the old `"retryable: "` prefix expected by Kuma's tests.

## 3. What does Δt (test.patch) actually do?
Touches two test files:
- `app/kuma-dp/pkg/dataplane/envoy/remote_bootstrap_test.go`: updates the expected missing-Dataplane error string by removing the `"retryable: "` prefix.
- `pkg/hds/authn/callbacks_test.go`: updates the expected HDS authentication missing-Dataplane error string by removing the same prefix.

## 4. Does Δt directly exercise the breaking change?
Yes. The hidden assertions target the changed error text from go-retry 0.2 retryable-error handling. On P⊕Δm, the selected packages also still contain old two-value constructor calls such as `backoff, err := retry.NewConstant(...)`, so they should fail to compile; with Δc, the constructor calls are migrated and the updated error-string assertions pass.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — both compile-time constructor changes and runtime error-string expectations are tied to the go-retry upgrade and are covered by the selected Go test packages.

## 6. Δc nature
REAL_SOURCE_REPAIR — production Go files in dataplane bootstrap, HDS/XDS auth, defaults, resource manager, tokens, and admin-token bootstrap are migrated to the new go-retry constructor and composition style.

## 7. Soundness concerns / notes
- Solid witness, though part of the failure is compile-time API churn rather than only the changed error assertions.
- The test command runs only the packages containing the hidden assertion updates, which keeps the witness focused.

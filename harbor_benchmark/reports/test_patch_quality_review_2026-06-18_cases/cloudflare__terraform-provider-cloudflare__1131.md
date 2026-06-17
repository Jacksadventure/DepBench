# Test-patch audit — cloudflare__terraform-provider-cloudflare__1131

## 1. Task summary
- Folder: cloudflare__terraform-provider-cloudflare__1131
- Ecosystem: go_modules
- Upgrade: github.com/cloudflare/cloudflare-go 0.18.0 -> 0.19.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test -count=1 ./cloudflare/...`

## 2. What is the breaking change?
cloudflare-go 0.19.0 changed `CustomHostname.SSL` from a value type `CustomHostnameSSL` to a pointer `*CustomHostnameSSL` (so SSL becomes optional/nullable). The provider code that assigned `SSL: cloudflare.CustomHostnameSSL{...}` (value) and dereferenced `customHostname.SSL.Type` without a nil-check no longer compiles / would panic.

## 3. What does Δt (test.patch) actually do?
- `cloudflare/resource_cloudflare_custom_hostname_test.go`: adds a new acceptance test `TestAccCloudflareCustomHostnameWithNoSSL` + helper `testAccCheckCloudflareCustomHostnameWithNoSSL` that creates a `cloudflare_custom_hostname` resource with NO `ssl` block and asserts `resource.TestCheckNoResourceAttr(resourceName, "ssl")`.

## 4. Does Δt directly exercise the breaking change?
No Δt assertion actually executes in the verifier. The new test is a Terraform acceptance test (`TestAcc...`) gated on `CLOUDFLARE_ZONE_ID`/`CLOUDFLARE_DOMAIN` env vars and `testAccPreCheck`; with no credentials/network in the verifier it is SKIPPED. The real witness is the compile error: on P⊕Δm the original `SSL: cloudflare.CustomHostnameSSL{...}` value assignment to the now-pointer field fails to compile, so `go test ./cloudflare/...` fails; Δc switches to `&cloudflare.CustomHostnameSSL{...}` + nil-checks, so it compiles and passes.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the cloudflare-go 0.19.0 SSL value->pointer type change is witnessed via a deterministic compile error that Δc repairs (FAIL on P⊕Δm, PASS on P⊕Δm⊕Δc).

## 6. Δc nature
REAL_SOURCE_REPAIR — `cloudflare/resource_cloudflare_custom_hostname.go`: `ssl` schema `Required`->`Optional`, Read wrapped in `if customHostname.SSL != nil`, and `buildCustomHostname` assigns `ch.SSL = &cloudflare.CustomHostnameSSL{...}` guarded by `d.GetOk("ssl")`.

## 7. Soundness concerns / notes
Weak oracle: the witness is purely the compile error; Δt's only assertion (`TestAccCloudflareCustomHostnameWithNoSSL`) is a skipped acceptance test that never runs in the resource-constrained verifier, so no runtime assertion of the no-SSL behavior is actually exercised. The task is technically witnessed but the hidden test adds no runtime verification — an agent that merely fixes the compile (as Δc does) passes. Consider whether a non-acceptance unit test could be added to genuinely exercise the nil-SSL path.

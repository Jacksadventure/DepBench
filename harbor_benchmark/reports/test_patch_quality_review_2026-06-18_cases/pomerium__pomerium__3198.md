# Test-patch audit — pomerium__pomerium__3198

## 1. Task summary
- Folder: pomerium__pomerium__3198
- Ecosystem: go_modules
- Upgrade: github.com/caddyserver/certmagic 0.15.4 -> 0.16.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test ./internal/autocert/... -count=1 -timeout 300s`

## 2. What is the breaking change?
certmagic 0.16 renamed/reworked the ACME manager type and methods: `ACMEManager` becomes `ACMEIssuer`, `NewACMEManager` becomes `NewACMEIssuer`, and certificate-cache methods such as `CacheManagedCertificate` / `CacheUnmanagedTLSCertificate` now take a `context.Context`.

## 3. What does Δt (test.patch) actually do?
It updates `internal/autocert/manager_test.go` to use `certmagic.ACMEIssuer`, rename the helper `newACMEManager()` to `newACMEIssuer()`, and compare expected structs while ignoring unexported fields on `certmagic.ACMEIssuer`.

## 4. Does Δt directly exercise the breaking change?
Yes. Test code now constructs and compares `certmagic.ACMEIssuer` values, for example `expected: &certmagic.ACMEIssuer{...}`. P⊕Δm production code still refers to `certmagic.ACMEManager` and old cache method signatures, so it fails to compile until Δc migrates the production manager.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden tests and production code both compile only after the certmagic 0.16 type/method migration.

## 6. Δc nature
REAL_SOURCE_REPAIR — `internal/autocert/manager.go` updates production types, constructors, context arguments, and helper signatures to the certmagic 0.16 API.

## 7. Soundness concerns / notes
Clean compile-level Go API witness. No major concerns.


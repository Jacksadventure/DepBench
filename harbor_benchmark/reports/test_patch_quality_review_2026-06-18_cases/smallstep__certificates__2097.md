# Test-patch audit — smallstep__certificates__2097

## 1. Task summary
- Folder: smallstep__certificates__2097
- Ecosystem: go_modules
- Upgrade: github.com/slackhq/nebula 1.9.4 -> 1.9.5
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test ./authority/provisioner/ -run '^TestNebula' -v -count=1 -timeout=300s`

## 2. What is the breaking change?
nebula 1.9.5 changes `nebula.NewCAPoolFromBytes` from returning `(pool, err)` to returning `(pool, certErrors, err)`, separating parse errors from certificate validation errors. The old provisioner code assigns only two return values and therefore no longer compiles; it also would ignore the new per-certificate validation errors such as expired CA roots.

## 3. What does Δt (test.patch) actually do?
Touches `authority/provisioner/nebula_test.go`. It adds `mustExpiredNebulaCA`, builds an expired CA PEM, appends a valid CA PEM so the input is otherwise parseable, and adds a `TestNebula_Init` table case named `"fail expired root"` expecting provisioner initialization to fail.

## 4. Does Δt directly exercise the breaking change?
Yes. The new table case targets the newly exposed `certErrors` path from `NewCAPoolFromBytes`: expired roots must now be detected and converted into an initialization error. On P⊕Δm, the provisioner code still uses the two-result assignment and should fail to compile; with Δc, it handles `certErrors` and the expired-root test passes.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt adds a focused expired-root case for the new nebula return contract and the selected Go test package compiles/runs only after the production adaptation.

## 6. Δc nature
REAL_SOURCE_REPAIR — `authority/provisioner/nebula.go` is updated to receive `certErrors`, normalize the CA-pool error message, and fail initialization when validation errors are returned.

## 7. Soundness concerns / notes
- Clean witnessed case with both compile-time and behavioral evidence.
- The hidden test is stronger than a pure compile witness because it checks that the new validation-error return is not silently ignored.

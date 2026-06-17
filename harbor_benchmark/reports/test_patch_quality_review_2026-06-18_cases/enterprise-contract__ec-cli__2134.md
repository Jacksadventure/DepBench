# Test-patch audit — enterprise-contract__ec-cli__2134

## 1. Task summary
- Folder: enterprise-contract__ec-cli__2134
- Ecosystem: go_modules
- Upgrade: github.com/open-policy-agent/opa 0.69.0 -> 0.70.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test -count=1 -tags=unit -v ./internal/opa/rule/...`

## 2. What is the breaking change?
OPA 0.70 parses YAML metadata custom fields that look like timestamps as `time.Time` values rather than strings. The existing `customAnnotationString` helper only returned values whose dynamic type was `string`, so `effective_on: 2022-01-01T00:00:00Z` became invisible after the upgrade.

## 3. What does Δt (test.patch) actually do?
- `internal/opa/rule/rule_test.go`: adds a `TestEffectiveOn` case where the `effective_on` custom metadata value is an unquoted timestamp.
- Keeps the existing string-valued `effective_on` case and labels it as `"with effective_on annotation as string"`.
- Expects the timestamp case to return the RFC3339 string `2022-01-01T00:00:00Z`.

## 4. Does Δt directly exercise the breaking change?
Yes. The new test drives `customAnnotationString` through `EffectiveOn` with a metadata value that OPA now materializes as `time.Time`. On P⊕Δm⊕Δt, the helper ignores non-string custom values and returns an empty string. Δc handles `time.Time` and formats it with `time.RFC3339`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden test directly captures the OPA metadata timestamp type change and fails without the source repair.

## 6. Δc nature
MIXED — `internal/opa/rule/rule.go` contains a real source repair, while the same patch also updates generated/user documentation for a new OPA CLI flag.

## 7. Soundness concerns / notes
The core test is focused and strong. The only concern is Δc purity: docs updates are bundled with the source fix.

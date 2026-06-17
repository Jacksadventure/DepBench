# Test-patch audit — golangci__golangci-lint__4718

## 1. Task summary
- Folder: golangci__golangci-lint__4718
- Ecosystem: go_modules
- Upgrade: go-simpler.org/sloglint 0.6.0 -> 0.7.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test -count=1 -run TestFromTestdata ./pkg/golinters/sloglint/... -v`

## 2. What is the breaking change?
sloglint 0.7 adds support for a `ForbiddenKeys` setting. golangci-lint's wrapper/config layer must expose that setting, include it in config decoding/schema/reference config, and pass it through to the upstream analyzer.

## 3. What does Δt (test.patch) actually do?
It adds `pkg/golinters/sloglint/testdata/sloglint_forbidden_keys.go` and `.yml`. The fixture enables `forbidden-keys: [foo_bar]` and expects diagnostics for direct string keys, constants, `slog.Int`, and `slog.Attr` forms using `foo_bar`.

## 4. Does Δt directly exercise the breaking change?
Yes. Without Δc, the `forbidden-keys` config key is not represented in `SlogLintSettings` and is not passed into `sloglint.Options`, so the new fixture does not produce the expected diagnostics. With Δc, the setting is decoded and forwarded to the analyzer, and the testdata expectations pass.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the verifier directly tests the new upstream analyzer option through golangci-lint's wrapper.

## 6. Δc nature
REAL_SOURCE_REPAIR — source config structs/defaults and the sloglint wrapper gain `ForbiddenKeys`, with matching schema/reference config updates.

## 7. Soundness concerns / notes
Strong witness for a wrapper integration change. The reference YAML/jsonschema edits are supporting config artifacts, but the source pass-through is the discriminating repair.

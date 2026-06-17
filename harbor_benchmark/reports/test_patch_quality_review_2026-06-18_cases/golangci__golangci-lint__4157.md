# Test-patch audit — golangci__golangci-lint__4157

## 1. Task summary
- Folder: golangci__golangci-lint__4157
- Ecosystem: go_modules
- Upgrade: github.com/catenacyber/perfsprint 0.2.0 -> 0.2.2
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `GOFLAGS=-buildvcs=false go test -count=1 -run 'TestSourcesFromTestdata/perfsprint' ./test/ -v`

## 2. What is the breaking change?
The upgraded `perfsprint` analyzer now supports configuration via a constructed analyzer and an `int-conversion` option. golangci-lint must pass that option through its linter settings instead of using the old package-level analyzer value with no configuration.

## 3. What does Δt (test.patch) actually do?
Adds `test/testdata/configs/perfsprint_int_conversion.yml` and `test/testdata/perfsprint_int_conversion.go`, and extends `test/testdata/perfsprint.go`. The new fixture verifies normal new perfsprint diagnostics and verifies that `linters-settings.perfsprint.int-conversion: false` suppresses uint conversion diagnostics while keeping other diagnostics.

## 4. Does Δt directly exercise the breaking change?
Yes. The targeted `TestSourcesFromTestdata/perfsprint` test reads the perfsprint config fixture and compares expected `// want` diagnostics; without Δc, the new config option is not wired into golangci-lint and the analyzer behavior does not match the fixture.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — `P⊕Δm⊕Δt` should fail on the perfsprint fixture expectations because the upgraded analyzer configuration is not propagated; Δc adds the `PerfSprintSettings` plumbing and passes it to `analyzer.New()`.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc updates `pkg/config/linters_settings.go`, `pkg/golinters/perfsprint.go`, and `pkg/lint/lintersdb/manager.go` to add production configuration support, with an accompanying reference config entry.

## 7. Soundness concerns / notes
- The repair includes a reference YAML update, but the decisive behavior is production linter configuration plumbing.
- This is a linter product test, but the verifier is testing golangci-lint's own supported analyzer behavior rather than a generic formatting/lint-only cleanup command.

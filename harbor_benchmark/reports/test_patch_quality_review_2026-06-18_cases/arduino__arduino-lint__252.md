# Test-patch audit — arduino__arduino-lint__252

## 1. Task summary
- Folder: arduino__arduino-lint__252
- Ecosystem: go_modules
- Upgrade: github.com/arduino/go-paths-helper 1.4.0 -> 1.6.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test ./internal/rule/rulefunction/ -run TestMissingExamples -v`

## 2. What is the breaking change?
The repaired code stops using `Path.IsDirCheck()` as a combined existence-and-directory predicate. With the upgraded go-paths-helper, the code first calls `ExistCheck()` and then separately calls `IsDirCheck()` before recursively reading examples.

## 3. What does Δt do?
Δt adds a `TestMissingExamples` table case named `File name collision`, plus a fixture where `examples` exists as a regular file rather than a directory. The expected result is `Fail`, not a panic or a false `Pass`.

## 4. Does Δt directly exercise the dependency break?
Yes. The new fixture targets the precise path-helper semantics Δc addresses: a path can exist but not be a directory, and the rule must not treat that as an examples folder. On P⊕Δm the old single `IsDirCheck()` flow is vulnerable to the changed helper behavior; with Δc, file existence and directory-ness are handled explicitly.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden test exercises the upgraded path-helper semantics around existing non-directory paths, and Δc provides the required source repair.

## 6. Δc nature
REAL_SOURCE_REPAIR — `MissingExamples()` is changed to use `ExistCheck()` followed by `IsDirCheck()` and to skip non-directories before recursive reads.

## 7. Soundness concerns / notes
The witness is narrow but well-targeted to the dependency API/behavior change. It validates a single edge case in `MissingExamples` rather than broad path-helper use across the codebase.

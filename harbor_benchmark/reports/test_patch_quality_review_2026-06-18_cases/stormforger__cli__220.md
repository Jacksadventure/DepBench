# Test-patch audit - stormforger__cli__220

## 1. Task summary
- Folder: stormforger__cli__220
- Ecosystem: go_modules
- Upgrade: github.com/evanw/esbuild 0.9.2 -> 0.11.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test -v -count=1 ./cmd/ -run TestTestcaseBuild`

## 2. What is the breaking change?
The manifest bumps esbuild, but Delta_c does not change esbuild API usage. It refactors the CLI command so the bundling path is exposed as `MainTestcaseBuild(w, file, defines)` and the Cobra command delegates to that helper.

## 3. What does test.patch actually do?
The hidden patch adds a new Go unit test plus JS fixtures. The test calls `MainTestcaseBuild` directly, feeds it `TestTestcaseBuild_main.mjs`, and asserts the bundled output equals a checked-in fixture.

## 4. Does test.patch directly exercise the breaking change?
No. On P+Delta_m+Delta_t, the immediate failure is that `MainTestcaseBuild` does not exist. That symbol is introduced by Delta_c specifically to make the new test call possible. The test does not isolate an esbuild API migration in existing production code.

## 5. Coverage verdict
TESTS_OTHER_THING - Delta_t is primarily a new testability/behavioral probe for a newly exported helper, not witnessed evidence of an esbuild dependency break.

## 6. Delta_c nature
REAL_SOURCE_REPAIR - the change is production Go source refactoring of command execution into an exported helper, although it is not clearly dependency-repair work.

## 7. Soundness concerns / notes
The new fixture may incidentally validate esbuild 0.11 output, but the hidden test is coupled to a helper introduced by Delta_c. That makes the witness self-referential rather than a direct break caused by the dependency bump.

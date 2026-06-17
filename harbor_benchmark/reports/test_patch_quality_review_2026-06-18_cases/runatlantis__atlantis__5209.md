# Test-patch audit — runatlantis__atlantis__5209

## 1. Task summary
- Folder: runatlantis__atlantis__5209
- Ecosystem: go_modules
- Upgrade: github.com/google/go-github/v66 v66.0.0 -> v68.0.0
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `cd /app && export PATH=/usr/local/go/bin:$PATH && go get github.com/google/go-github/v68/github && go test ./server/controllers/events -run TestGithubPullRequestParsed -count=1`

## 2. What is the breaking change?
go-github v68 is a new major version on a new module path (`/v68` vs `/v66`), so every `import "github.com/google/go-github/v66/github"` must become `/v68`. Additionally the pointer-helper API was migrated: `github.String / github.Int / github.Bool` are replaced by `github.Ptr`. Both the import path and the helper rename are compile-breaking.

## 3. What does Δt (test.patch) actually do?
Touches a single file, `e2e/github.go`, in the **`e2e` submodule** (rooted at `e2e/go.mod`): rewrites the import `/v66` -> `/v68` and two helper calls `github.Bool(true)` / `github.String("closed")` -> `github.Ptr(...)`. No new test cases or assertions — just the same mechanical migration applied to one e2e helper file.

## 4. Does Δt directly exercise the breaking change?
No. The `test_cmd` runs `go test ./server/controllers/events -run TestGithubPullRequestParsed` in the **main `/app` module**. `e2e/github.go` (the only file Δt touches) lives in the separate `e2e` module and is never compiled or executed by that command. So Δt has no effect on the verifier outcome whatsoever. The real witness is the main-module compile failure of `./server/controllers/events` (and its `_test.go` files, which still import `/v66`), repaired by Δc — not by Δt.

## 5. Coverage verdict
TESTS_OTHER_THING — Δt modifies `e2e/github.go`, which is outside the package/module exercised by `test_cmd`; it does not witness the breaking change, and the actual fail/pass is driven entirely by Δc editing main-module source AND test files.

## 6. Δc nature
MIXED — 19 files: real source migration (`server/controllers/events/events_controller.go`, `server/events/event_parser.go`, `server/events/command_runner.go`, `server/events/vcs/github_client.go`, `testdrive/*.go`) for the import-path + `String/Int/Bool`->`Ptr` rename, BUT also 7 test/testdata/mock files (`events_controller_e2e_test.go`, `events_controller_test.go`, `apply_command_runner_test.go`, `command_runner_test.go`, `event_parser_test.go`, `plan_command_runner_test.go`, `server/events/vcs/testdata/fixtures.go`, `mocks/mock_*.go`). The repair is real but heavily contaminated with test/testdata edits.

## 7. Soundness concerns / notes
- Δc edits test files (`*_test.go`, `testdata/fixtures.go`) that the agent is forbidden to touch; the verifier applies only Δt, which targets the wrong module. Since `go test ./server/controllers/events` compiles the whole package including `*_test.go` still importing `/v66`, the package will not compile without Δc's test-file edits — so the agent **cannot pass this task** without violating the "do not modify tests" constraint. This is a hard soundness defect.
- Δt is dead weight (e2e module not run); the hidden test patch fails to cover the actual breaking change in the graded package.
- Per the problematic review: "Exclude from witnessed main set. Potentially real source migration, but no hidden-test witness." Confirmed: Δt provides no witness for the main-module migration.
- The `go get .../v68` in `test_cmd` plus the `replace` directive for `ghinstallation` in `go.mod` (Δm) are infrastructure needed to make v68 resolve; not part of the code repair.

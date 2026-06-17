# Test-patch audit — determined-ai__determined__8316

## 1. Task summary
- Folder: determined-ai__determined__8316
- Ecosystem: go_modules
- Upgrade: github.com/docker/docker 20.10.24+incompatible -> 24.0.7+incompatible
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test ./agent/pkg/docker/... ./agent/pkg/singularity/... ./master/internal/config/... ./master/pkg/model/... ./master/pkg/cproto/...`

## 2. What is the breaking change?
docker/docker v24 reorganized its Go API types: `types.AuthConfig` was moved to `types/registry.AuthConfig`, and `container.ContainerWaitOKBody` was renamed to `container.WaitResponse` with `ContainerWaitOKBodyError` → `WaitExitError`. These are compile-breaking renames for any consumer of the old symbols.

## 3. What does Δt (test.patch) actually do?
Mechanically mirrors the Δc import/type migration across 5 test files:
- `agent/pkg/docker/docker_test.go`: `types.AuthConfig` → `registry.AuthConfig` in `TestGetDockerAuths` and `TestRegistryToString` (all local vars, table cases, and `map[string]...AuthConfig`).
- `agent/pkg/singularity/singularity_api_test.go`: `&types.AuthConfig{}` → `&registry.AuthConfig{}` in `TestSingularity`.
- `master/internal/config/config_test.go`: `&types.AuthConfig{...}` → `&registry.AuthConfig{...}`.
- `master/pkg/model/experiment_config_test.go`: `&types.AuthConfig{...}` → `&registry.AuthConfig{...}` (3 sites).
- `master/pkg/model/task_container_defaults_test.go`: `&types.AuthConfig{...}` → `&registry.AuthConfig{...}` (3 sites).
No new assertions; all changes keep the existing tests compiling against the v24 API.

## 4. Does Δt directly exercise the breaking change?
Yes. On P⊕Δm (docker v24, no Δc) the production packages (`agent/pkg/docker`, `master/pkg/cproto`, `master/pkg/model`, `master/pkg/schemas/expconf`) still reference the removed `types.AuthConfig` / `container.ContainerWaitOKBody`, so `go test` fails to compile the package → FAIL. On P⊕Δm⊕Δc the source is migrated to `registry.AuthConfig` / `WaitResponse`, the test files (Δt) compile against the same new symbols, and the existing auth/config tests pass → PASS. The tests exercise the migrated auth-config and container-wait code paths.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — compile failure without Δc, pass with Δc; Δt's test-side type migration is the necessary counterpart that lets the verifier run the existing auth tests against v24.

## 6. Δc nature
REAL_SOURCE_REPAIR — broad API-rename migration across 9 production files: `agent/pkg/docker/docker.go` + `docker_credential_store.go`, `agent/pkg/podman/podman.go`, `agent/pkg/singularity/singularity.go`, `master/pkg/cproto/spec.go`, `master/pkg/model/environment_config.go` + `task_container_defaults.go`, `master/pkg/schemas/expconf/environment_config.go` + `zgen_environment_config_v0.go`.

## 7. Soundness concerns / notes
- Clean case; the witness is primarily the compile-time API rename (production code won't build against v24 without Δc), which is a legitimate witnessed breaking change.
- Δt adds no new behavioral assertions — it only keeps existing tests compilable. That is appropriate here because the breaking change is a type/import rename, not a behavior change.
- Note `task_container_defaults.go` Δc also reorders imports (drops `types`, adds `registry`) — purely mechanical, no concern.

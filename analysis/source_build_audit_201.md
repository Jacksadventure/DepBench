# Source-build audit

Date: 2026-08-05

The `main` dataset was converted from prebuilt task images to local source
builds and checked task by task.

## Result

| Check | Result |
|---|---:|
| Distributed tasks | 201 |
| Canonical repository URL + exact commit fetch | 201 / 201 pass |
| Dockerfile build | 201 / 201 pass |
| Login-shell toolchain check | 201 / 201 pass |
| Exact Git HEAD check | 201 / 201 pass |
| Clean worktree check | 201 / 201 pass |
| Pinned base-image manifests | 41 / 41 |
| Prebuilt task-image references | 0 |
| Placeholder compose files | 0 |

Every Dockerfile clones an upstream repository, checks out a fixed
40-character commit, bootstraps dependencies, restores a clean worktree, and
uses a language base image pinned by registry manifest digest.

## Adjustments

- Replaced redirected repository URLs with the current canonical locations for
  `ashutoshgngwr__noice__673`, `enterprise-contract__ec-cli__2134`, and
  `iterative__dvc__7899`.
- Preserved login-shell-stable compiler entry points for Go, Rust, and Java.
- Installed `libx11-dev` for `ymtdzzz__otel-tui__153`.
- Raised source-build timeouts to 1800 seconds for
  `MystenLabs__fastcrypto__460`, `bbc__simorgh__9275`, and
  `oxidecomputer__dropshot__501`.
- Removed the global 8192 MB Harbor override so each task uses the memory limit
  declared in its own `task.toml`.

## Longest builds

| Task | Seconds | Build timeout |
|---|---:|---:|
| `oxidecomputer__dropshot__501` | 1101.3 | 1800 |
| `bbc__simorgh__9275` | 1051.4 | 1800 |
| `MystenLabs__fastcrypto__460` | 1050.2 | 1800 |
| `oxidecomputer__dropshot__630` | 1027.6 | 2400 |
| `mitre__heimdall2__2276` | 317.0 | 900 |
| `huridocs__uwazi__4579` | 312.5 | 900 |

The machine-readable per-task evidence is in
`source_build_audit_201.{csv,json}` and
`source_commit_audit_201.{csv,json}`.

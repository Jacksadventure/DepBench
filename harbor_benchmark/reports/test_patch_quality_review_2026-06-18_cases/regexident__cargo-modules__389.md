# Test-patch audit — regexident__cargo-modules__389

## 1. Task summary
- Folder: regexident__cargo-modules__389
- Ecosystem: cargo
- Upgrade: rust-analyzer dependency stack previous versions -> v0.0.328
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `cargo test --release`

## 2. What is the breaking change?
The rust-analyzer crate stack changed several HIR/project-model APIs. The old code uses `RootDatabase` where the new APIs expect `dyn HirDatabase`, calls methods whose signatures now take a database parameter (`module.krate(db)`, `is_crate_root(db)`, `root_module(db)`), refers to renamed variants (`Variant` -> `EnumVariant`), and uses low-level `hir_ty` inference internals no longer exposed the same way. The cargo/load configuration also needs new fields such as `target_dir_config`, `metadata_extra_args`, and proc-macro worker counts.

## 3. What does Δt (test.patch) actually do?
It updates many `insta` snapshots under `tests/snapshots/dependencies__*.snap` and makes a small `tests/util.rs` helper change to forward `RUST_BACKTRACE`. The snapshot updates remove the `snapshot_kind: text` header, drop many builtin/body-level dependency nodes and edges (`bool`, `i32`, `str`, inferred body uses), and update visibility labels such as derived `clone` methods becoming `pub fn`.

## 4. Does Δt directly exercise the breaking change?
Yes. The verifier runs the cargo test suite, so P⊕Δm without Δc should fail to compile against the new rust-analyzer APIs. After Δc, the dependency graph generation runs, and the hidden snapshots check the new output shape caused by the dependency/API migration and the corresponding source adaptation. The `RUST_BACKTRACE` helper edit is incidental; the snapshots are the meaningful oracle.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the upgraded rust-analyzer APIs deterministically break compilation until the source is adapted, and the hidden snapshot suite distinguishes the post-upgrade generated graph output.

## 6. Δc nature
REAL_SOURCE_REPAIR — `src/analyzer.rs`, command runners, graph/tree builders, item handling, filters, and printers are updated for the new rust-analyzer HIR APIs and resulting graph-building behavior.

## 7. Soundness concerns / notes
- The behavioral part of Δt is snapshot-heavy, so it is a coarse oracle over graph output rather than focused assertions.
- The primary witness is still strong because compile failure precedes any snapshot comparison on the unfixed upgraded source.

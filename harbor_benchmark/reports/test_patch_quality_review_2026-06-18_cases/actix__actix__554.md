# Test-patch audit — actix__actix__554

## 1. Task summary
- Folder: actix__actix__554
- Ecosystem: cargo
- Upgrade: syn 1 -> 2
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `cargo test -p actix_derive && cargo test -p actix --test test_arbiter`

## 2. What is the breaking change?
syn 2 removes/changes macro parsing APIs used by `actix-derive`, including `Attribute::parse_meta`, `NestedMeta`, and `MetaNameValue` literal access patterns. The derive macros must be rewritten for syn 2 parsing.

## 3. What does Δt (test.patch) actually do?
Δt adds trybuild coverage for the proc macros, including `#[actix::main]`, `MessageResponse`, valid `#[rtype(...)]` forms, and one compile-fail bare `rtype` form. It also changes `test_arbiter` to await a sent message instead of fire-and-forget `do_send`.

## 4. Does Δt directly exercise the breaking change?
Yes. The verifier first runs `cargo test -p actix_derive`; with syn 2 and the old macro implementation, the crate should fail to compile because the old syn APIs are gone. Δc rewrites macro parsing and delegates `main`/`test` attributes through `actix_macros`, allowing the new trybuild tests to compile.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — this is a direct proc-macro compile witness for the syn 1 -> 2 API migration.

## 6. Δc nature
MIXED — Δc contains real Rust source repair in `actix-derive` and `actix/src/lib.rs`, but also includes GitHub Actions, VS Code settings, and changelog churn.

## 7. Soundness concerns / notes
The `test_arbiter` change is unrelated to syn and appears to address a flaky/buggy runtime test. The syn migration is still witnessed by the `actix_derive` compile/test phase.

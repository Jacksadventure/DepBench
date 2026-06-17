# Test-patch audit — omjadas__hudsucker__88

## 1. Task summary
- Folder: omjadas__hudsucker__88
- Ecosystem: cargo
- Upgrade: rustls-pemfile 1.0.0 -> 2.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `cargo test --lib --no-run --no-default-features --features rcgen-ca,rustls-client`

## 2. What is the breaking change?
rustls-pemfile 2 changes PEM parsing helpers from returning vectors directly to returning iterators over parsed items. Existing code that calls `.expect(...).remove(0)` no longer type-checks and must consume the iterator with `.next()` and unwrap the inner parse result.

## 3. What does Δt (test.patch) actually do?
Integration-test helpers in `tests/common/mod.rs`, `tests/rcgen_ca.rs`, and `tests/websocket.rs` are updated to use `.next().unwrap().expect(...).to_vec()` for certificates and private keys.

## 4. Does Δt directly exercise the breaking change?
Partially. The verifier command is `cargo test --lib --no-run`, so the patched integration tests are not the main runtime oracle. However, the library itself contains the same rustls-pemfile usage in source examples and unit-test helpers under `src/certificate_authority/rcgen_authority.rs`; with Δm and without Δc, the library test target should fail to compile. Δc applies the same iterator-based migration to production/library code.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the compile-only verifier still witnesses the rustls-pemfile 2 API change through library compilation, even though Δt's integration-test edits are not executed by the selected command.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc updates Rust source and doctest/example snippets in production modules to the new rustls-pemfile iterator API.

## 7. Soundness concerns / notes
The verifier is compile-only (`--no-run`) and does not run the integration tests modified by Δt. The witness is therefore an API compile witness, not behavioral coverage of certificate loading.

# Test-patch audit — mike-engel__jwt-cli__224

## 1. Task summary
- Folder: mike-engel__jwt-cli__224
- Ecosystem: cargo
- Upgrade: jsonwebtoken 7.2.0 -> 8.2.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE`

## 2. What is the breaking change?
jsonwebtoken 8 changes key and validation APIs: `DecodingKey` no longer carries the old lifetime/static pattern, `dangerous_insecure_decode` is removed, validation is constructed/mutated differently, `required_spec_claims` uses a set, and some `ErrorKind` variants change shape. The old Rust source imports removed symbols and uses v7-only methods such as `into_static()`.

## 3. What does Δt (test.patch) actually do?
Δt modifies only `tests/main_test.rs`. It removes direct test imports for `decoding_key_from_secret`, `encoding_key_from_secret`, base64 helpers, `DecodingKey`, and `EncodingKey`, then comments out four key-equality tests because `EncodingKey`/`DecodingKey` no longer implement the needed `Debug`/`Eq` comparison surface.

## 4. Does Δt directly exercise the breaking change?
Yes, mostly through compilation. Even after Δt removes tests that cannot be expressed against jsonwebtoken 8 key types, `cargo test` still compiles the production translators; old source still references removed v7 APIs (`dangerous_insecure_decode`, `DecodingKey<'static>`, `.into_static()`, old `ErrorKind::InvalidRsaKey`) and should fail to compile until Δc migrates those uses.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the verifier builds and tests the crate against jsonwebtoken 8, and P⊕Δm⊕Δt should fail on source-level API incompatibilities that Δc repairs.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc updates production Rust files `src/translators/decode.rs` and `src/translators/encode.rs` for jsonwebtoken 8 decoding, validation, key, algorithm, and error APIs.

## 7. Soundness concerns / notes
Δt weakens part of the original test suite by commenting out key equality tests, so it is a compile/API witness rather than a strong behavioral regression suite for the helper functions.

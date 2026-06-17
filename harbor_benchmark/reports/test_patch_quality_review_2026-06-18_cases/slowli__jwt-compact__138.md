# Test-patch audit — slowli__jwt-compact__138

## 1. Task summary
- Folder: slowli__jwt-compact__138
- Ecosystem: cargo
- Upgrade: rsa 0.8 -> 0.9
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `cargo test --test jwk --features rsa`

## 2. What is the breaking change?
rsa 0.9 moves key-part traits under `rsa::traits` and removes the public `algorithms::generate_multi_prime_key` helper used by the test suite. Source imports must use `traits::{PrivateKeyParts, PublicKeyParts}`.

## 3. What does Δt (test.patch) actually do?
`tests/jwk.rs` stops importing `rsa::algorithms::generate_multi_prime_key`, adds `num_bigint::{ModInverse, RandPrime}` and `rand::Rng`, copies a local multi-prime RSA key generator into the test, and updates the call site because the local helper returns `RsaPrivateKey` directly instead of `Result`.

## 4. Does Δt directly exercise the breaking change?
Yes. Δt makes the test compile under rsa 0.9 after the helper was made private. The production crate still fails without Δc because `src/alg/rsa.rs` imports removed/relocated rsa traits; Δc updates those imports to the rsa 0.9 API.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — P⊕Δm⊕Δt fails to compile without the rsa 0.9 source import migration, and passes with Δc.

## 6. Δc nature
REAL_SOURCE_REPAIR — `src/alg/rsa.rs` migrates to `rsa::traits::{PrivateKeyParts, PublicKeyParts}` and removes the old `PublicKey` import. Other CI/changelog/no-std edits are drive-by maintenance.

## 7. Soundness concerns / notes
- Δt contains a large copied helper from rsa internals, but its purpose is directly tied to the rsa 0.9 visibility change.

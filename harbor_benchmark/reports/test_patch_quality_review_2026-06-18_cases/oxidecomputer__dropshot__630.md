# Test-patch audit — oxidecomputer__dropshot__630

## 1. Task summary
- Folder: oxidecomputer__dropshot__630
- Ecosystem: cargo
- Upgrade: hyper-rustls 0.23.2 -> 0.24.0
- test_cmd: `cargo test --no-fail-fast`

## 2. What is the breaking change?
The hyper-rustls/rustls upgrade changes server TLS API expectations. `rustls::server::NoClientAuth::new()` is no longer the right verifier value for `with_client_cert_verifier`; the source must pass the boxed verifier via `NoClientAuth::boxed()`.

## 3. What does Δt (test.patch) actually do?
The TLS tests are updated for new rustls/hyper behavior: HTTP-to-TLS failure now expects a parse error, certificate verifier errors use `rustls::Error::InvalidCertificate(CertificateError::BadEncoding)`, and copyrights/comments are refreshed.

## 4. Does Δt directly exercise the breaking change?
Yes. `cargo test` compiles the crate and TLS tests against the upgraded rustls stack. Without Δc, the server configuration code does not compile against the new verifier API; with Δc, the updated tests cover the revised TLS error behavior.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the compile-time rustls verifier API break is directly repaired by Δc and covered by the cargo test build.

## 6. Δc nature
REAL_SOURCE_REPAIR — one production TLS configuration call is updated to the new rustls API.

## 7. Soundness concerns / notes
- Some Δt changes are expectation updates for adjacent dependency behavior, but the source repair itself is a concrete compile/API fix.
- The verifier runs the whole test suite, not only the touched TLS tests.


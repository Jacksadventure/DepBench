# Test-patch audit - oxidecomputer__dropshot__501

## 1. Task summary
- Folder: oxidecomputer__dropshot__501
- Ecosystem: cargo
- Upgrade: tungstenite 0.17.3 -> 0.18.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `<could not extract>`; `test_state.py` runs `cargo test --locked --verbose`

## 2. What is the breaking change?
The manifest removes the direct `tungstenite` dev dependency and upgrades `tokio-tungstenite` to 0.18.0, so code that imported `tungstenite::...` directly must use the re-exported `tokio_tungstenite::tungstenite::...` path. The repair also updates a Chrono timestamp helper in an example.

## 3. What does Delta t (test.patch) actually do?
`dropshot/tests/test_demo.rs` changes test imports from `tungstenite::protocol::Role` and `tungstenite::Message` to `tokio_tungstenite::tungstenite::protocol::Role` and `tokio_tungstenite::tungstenite::Message`.

## 4. Does Delta t directly exercise the breaking change?
Yes. With Delta m, the direct `tungstenite` crate is no longer available to the package. Hidden tests fix their own imports, but production code in `dropshot/src/websocket.rs` and examples still reference `tungstenite::...` until Delta c is applied, causing compilation failure under `cargo test`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the upgraded dependency graph requires source imports to use the `tokio_tungstenite` re-export, and the full cargo test compile catches the old paths.

## 6. Delta c nature
REAL_SOURCE_REPAIR - production websocket source is updated, with parallel example import fixes and a Chrono helper adjustment.

## 7. Soundness concerns / notes
The witness is primarily compile-time. The hidden test patch is small but aligned with the same import-path break seen in source.


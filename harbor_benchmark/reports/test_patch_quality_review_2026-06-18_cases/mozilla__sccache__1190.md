# Test-patch audit - mozilla__sccache__1190

## 1. Task summary
- Folder: mozilla__sccache__1190
- Ecosystem: cargo
- Upgrade: uuid 0.8.2 -> 1.1.2
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `cargo test --no-fail-fast`

## 2. What is the breaking change?
uuid 1.x renamed formatting adapter methods used by sccache. Calls such as `Uuid::new_v4().to_simple_ref()` and `to_hyphenated_ref()` no longer compile and must become `as_simple()` / `hyphenated()`.

## 3. What does test.patch actually do?
The hidden patch updates `tests/harness/mod.rs` so test container names use `Uuid::new_v4().hyphenated()` instead of `to_hyphenated_ref()`.

## 4. Does test.patch directly exercise the breaking change?
Yes. The patched test harness compiles against uuid 1.x. Without Delta_c, production files still call removed uuid 0.8 formatting methods in `commands.rs` and `dist/client_auth.rs`, so the full cargo test compile fails.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the hidden patch and production repair both target the uuid 1.x method rename.

## 6. Delta_c nature
MIXED - it includes real uuid API repairs, but also unrelated Rust cleanup/style changes such as `metadata(...).is_err()`, borrow simplifications, char replacement, and a private-key split change.

## 7. Soundness concerns / notes
The extra non-uuid cleanup broadens Delta_c, but the core compile failure remains a genuine dependency API break witnessed by the hidden test harness migration.

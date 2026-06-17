# Test-patch audit — imsnif__bandwhich__430

## 1. Task summary
- Folder: imsnif__bandwhich__430
- Ecosystem: cargo
- Upgrade: dependencies group previous versions -> updated versions
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `cargo test --no-fail-fast` (bundle metadata marked TEST_CMD_UNEXTRACTABLE)

## 2. What is the breaking change?
The grouped Cargo update includes ratatui 0.27.0 -> 0.28.1, which changes public terminal/backend APIs: `Frame` is imported from the crate root, `Frame::size()` becomes `Frame::area()`, `Backend::get_cursor`/`set_cursor` become `get_cursor_position`/`set_cursor_position`, and `Backend::size()` returns `layout::Size` rather than `Rect`. Existing UI code and the test fake backend no longer compile against the upgraded trait and type signatures.

## 3. What does Δt (test.patch) actually do?
Touches `src/tests/fakes/fake_output.rs`. It updates the fake `Backend` implementation to import `Position`, rename `get_cursor` to `get_cursor_position`, rename `set_cursor` to `set_cursor_position<P: Into<Position>>`, and return `Size::new(width, height)` from `size()` instead of `Rect::new(...)`.

## 4. Does Δt directly exercise the breaking change?
Yes. The fake backend is part of the Cargo test build, so with ratatui 0.28.1 it must implement the new `Backend` trait. On P⊕Δm, production UI files still use old ratatui APIs such as `terminal::Frame`, `Backend::get_cursor`, and `frame.size()`, so the test build should fail to compile; with Δc plus the test fake migration in Δt, `cargo test --no-fail-fast` can compile and run.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the verifier compiles the application and tests against ratatui 0.28.1, and both Δc and Δt are direct API-signature migrations required for that compile to succeed.

## 6. Δc nature
REAL_SOURCE_REPAIR — source files under `src/display/` are updated for ratatui's new `Frame`, `Backend`, `Position`, `Size`, and `area()` APIs.

## 7. Soundness concerns / notes
- The bundle metadata could not extract the command, but `tests/test_state.py` defines `TEST_CMD = 'cargo test --no-fail-fast'`.
- The dependency group is broad, but the observed code/test repair is specifically ratatui API churn.

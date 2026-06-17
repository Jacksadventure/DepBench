# Test-patch audit — smol-rs__async-lock__69

## 1. Task summary
- Folder: smol-rs__async-lock__69
- Ecosystem: cargo
- Upgrade: event-listener 3.0.0 -> 4.0.0; event-listener-strategy 0.3.0 -> 0.4.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `cargo test --all`

## 2. What is the breaking change?
event-listener 4 changes listener construction and registration: `EventListener::new(&event)` becomes `EventListener::new()`, and the event is supplied later via `listener.listen(&event)`.

## 3. What does Δt do?
Δt updates `tests/rwlock.rs` to bind returned task handles (`let _spawned = spawn(...)`) in several async tests. This is test-side cleanup for the upgraded tool/dependency stack, not the main event-listener API migration.

## 4. Does Δt directly exercise the dependency break?
Yes, through `cargo test --all` compiling the crate. On P⊕Δm, source files in `barrier`, `mutex`, `once_cell`, `rwlock`, and `semaphore` still call `EventListener::new(&event)` / zero-arg `listen()`, which no longer match event-listener 4. With Δc, all listener sites use the new two-step API and the patched tests compile.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the upgraded event-listener API produces deterministic Rust compile failures without Δc and passes after the source migration.

## 6. Δc nature
REAL_SOURCE_REPAIR — async-lock primitives are migrated to the event-listener 4 construction/listen API.

## 7. Soundness concerns / notes
The hidden test patch itself is mostly test hygiene, but the verifier compiles all source and therefore witnesses the actual API break.

# Test-patch audit — oxidecomputer__dropshot__1556

## 1. Task summary
- Folder: oxidecomputer__dropshot__1556
- Ecosystem: cargo
- Upgrade: serde_tokenstream 0.2.2 -> 0.2.3
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE`

## 2. What is the breaking change?
The upgraded `serde_tokenstream`/token handling changes the span available for a parsed version-range diagnostic. Dropshot's derive-macro metadata parser must capture a broader token stream span so the compile-fail diagnostic highlights the complete invalid range instead of only the first literal.

## 3. What does Δt (test.patch) actually do?
Touches only `dropshot/tests/fail/bad_version_backwards.stderr`. It updates the trybuild stderr snapshot underline from `^^^^^^^` under `"1.2.3"` to `^^^^^^^^^^^^^^^^` under the full `"1.2.3".."1.2.2"` range.

## 4. Does Δt directly exercise the breaking change?
Yes, but only through a compile-fail diagnostic snapshot. The failing fixture checks the proc-macro error span; without Δc, the old span selection should produce the old underline and mismatch the patched stderr.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — `P⊕Δm⊕Δt` should fail the trybuild stderr comparison because the diagnostic span is not adapted to the new token handling; Δc changes production metadata parsing to emit the expected span.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc edits `dropshot_endpoint/src/metadata.rs` to capture `input.cursor().token_stream()` and use that span for the backwards-version error, plus an incidental copyright-year update.

## 7. Soundness concerns / notes
- The witness is a snapshot/golden-file assertion over diagnostics, not a runtime behavior test.
- The extracted command is unavailable in metadata, although `test_state.py` shows `cargo test --no-fail-fast`.

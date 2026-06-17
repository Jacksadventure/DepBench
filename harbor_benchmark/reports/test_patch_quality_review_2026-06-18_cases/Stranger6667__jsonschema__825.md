# Test-patch audit — Stranger6667__jsonschema__825

## 1. Task summary
- Folder: Stranger6667__jsonschema__825
- Ecosystem: cargo
- Upgrade: crates/jsonschema/tests/suite 15e4505 -> be58fa9
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE` (test_state runs `cargo test --no-fail-fast --all-features`)

## 2. What is the breaking change?
The JSON Schema test suite submodule advances to cases that validate stricter IDN/punycode hostname handling. The old validator accepted or rejected several punycode labels incorrectly because ASCII hostname validation did not decode punycode labels and apply Unicode contextual/category checks.

## 3. What does Δt (test.patch) actually do?
Δt changes the `crates/jsonschema/tests/suite` submodule pointer from `e524505b8ac4a61c5dc162b51d68c2385a134706` to `8fd4fcec8ffc2294958818e05326a37fcf2b6c5c`, bringing in newer upstream JSON Schema conformance cases.

## 4. Does Δt directly exercise the breaking change?
Yes. The newer suite is expected to include hostname/punycode format cases that fail the old `is_valid_hostname`/`is_valid_idn_hostname` behavior. Δc implements punycode decoding and `validate_unicode_label`, with representative added internal cases such as `xn--l-fda`, `xn--02b508i`, and valid virama/middle-dot punycode labels.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the advanced suite pointer supplies post-upgrade conformance tests that fail without the hostname validation repair and pass after Δc.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc modifies `crates/jsonschema/src/keywords/format.rs` to implement the new punycode/Unicode hostname validation behavior; added inline unit cases support that repair.

## 7. Soundness concerns / notes
The exact upstream submodule diff is not expanded in the bundle, so the static audit infers the hidden witness from Δc's focused hostname changes and the suite pointer bump. A dynamic failure log would confirm which upstream cases trigger.

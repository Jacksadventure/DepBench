# Test-patch audit - adoptoposs__mjml_nif__13

## 1. Task summary
- Folder: adoptoposs__mjml_nif__13
- Ecosystem: cargo
- Upgrade: version 0.7.13 -> 1.0.0 (actual native dependency: mrml 0.5.0 -> 1.0.0)
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `MIX_ENV=test mix test`

## 2. What is the breaking change?
The visible metadata is misleading: the substantive native upgrade is `mrml` 0.5.0 -> 1.0.0. The old Rust NIF calls `mrml::to_html(&mjml, mrml::Options::default())`; the repair uses `mrml::parse`, then `root.render(&mrml::prelude::render::Options::default())`, and returns the new parse/render error messages.

## 3. What does test.patch actually do?
`test/mjml_test.exs` replaces one generic invalid-MJML assertion with three parse-error assertions that check message prefixes: `unexpected element`, `parsing error: unknown token`, and `parsing error: invalid element`.

## 4. Does test.patch directly exercise the breaking change?
Yes. Under the upgraded native dependency, the old `mrml::to_html`/`Options` API is no longer the repaired API path, and it only returned a generic error string. The patched tests require the new parse/render flow and the propagated mrml error messages.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the hidden tests assert the new mrml 1.0 parse-error behavior exposed by Delta_c.

## 6. Delta_c nature
MIXED - the essential Rust NIF repair is real source code, but the patch also updates README and CHANGELOG release documentation.

## 7. Soundness concerns / notes
The library label `version` is stale/misleading; this should be described as an `mrml` native dependency/API migration.

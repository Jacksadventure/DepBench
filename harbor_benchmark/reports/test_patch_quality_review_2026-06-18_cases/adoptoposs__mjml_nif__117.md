# Test-patch audit - adoptoposs__mjml_nif__117

## 1. Task summary
- Folder: adoptoposs__mjml_nif__117
- Ecosystem: cargo
- Upgrade: version 1.1.0 -> 0.11.4; manifest patch upgrades the Rust `mrml` crate from 1.2 to 2.1
- test_cmd: `MJML_BUILD=true mix test --seed 0`

## 2. What is the breaking change?
The `mrml` render API changes from `mrml::prelude::render::Options` to `RenderOptions`, with different option fields/types such as `social_icon_origin` as `Cow` and a `fonts` map. The parser also changes error strings for invalid MJML input.

## 3. What does Delta t (test.patch) actually do?
It updates expected invalid-input error prefixes to `unable to load included template` and adds tests for a new `fonts` render option, including custom font URLs and default Open Sans font output.

## 4. Does Delta t directly exercise the breaking change?
Yes. The new tests call `Mjml.to_html(..., fonts: fonts)` and assert default font behavior, which requires the Delta c changes to the Elixir render-options struct and Rust NIF conversion into `mrml::prelude::render::RenderOptions`. The old NIF source would also fail to compile against the upgraded `mrml` API.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the verifier exercises the upgraded render-option API through `mix test`, with compile and behavior evidence.

## 6. Delta c nature
MIXED - real Elixir/Rust source repair plus README and changelog documentation updates.

## 7. Soundness concerns / notes
- Delta t includes both compatibility checks and user-visible feature assertions for fonts, so it covers more than a minimal breaking-change repair.

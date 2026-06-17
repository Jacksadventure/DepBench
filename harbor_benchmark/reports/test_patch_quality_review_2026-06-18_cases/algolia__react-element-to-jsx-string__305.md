# Test-patch audit — algolia__react-element-to-jsx-string__305

## 1. Task summary
- Folder: algolia__react-element-to-jsx-string__305
- Ecosystem: npm_and_yarn
- Upgrade: `babel-jest` 22.2.2 -> 23.6.0, with matching Jest/Expect bumps
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `yarn test`

## 2. What is the breaking change?
The Jest/Babel upgrade changes how function source strings surface in tests/build output and exposes CommonJS default-export behavior in the smoke test. The old default `functionValue` was raw `fn.toString()`, which preserved line breaks/indentation and no longer matched the intended post-upgrade output.

## 3. What does Δt (test.patch) actually do?
It changes function-formatting expectations from multiline source to compact inline strings, adds a test for an exported `preserveFunctionLineBreak` formatter, imports that formatter from `src/index.js`, and updates the CommonJS smoke helper to read `require('./../../dist/cjs').default`.

## 4. Does Δt directly exercise the breaking change?
Yes. The hidden tests exercise the public formatter behavior under the upgraded Jest/Babel toolchain and the generated CJS bundle shape. Δc adds `inlineFunction` as the default, exports `preserveFunctionLineBreak`, and keeps the old multiline behavior available as an explicit option.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the upgraded test/build stack changes observable function-string/default-export expectations, and Δc is needed for the hidden formatter and smoke tests to pass.

## 6. Δc nature
REAL_SOURCE_REPAIR — source exports and formatter behavior change in `src/formatter/formatFunction.js` and `src/index.js`.

## 7. Soundness concerns / notes
- The dependency is a dev/test dependency, so the break is in the project’s tested formatting/build behavior rather than a runtime dependency API.
- The hidden tests are focused and not lint/format-only.

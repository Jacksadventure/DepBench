# Test-patch audit — frctl__fractal__763

## 1. Task summary
- Folder: frctl__fractal__763
- Ecosystem: npm_and_yarn
- Upgrade: `@allmarkedup/fang` 1.0.0 -> 2.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx mocha --require test/support/env --reporter spec test/core.utils.js`

## 2. What is the breaking change?
`@allmarkedup/fang` 2.0.0 changed the language metadata shape returned by `fang(filePath)`: Fractal can no longer pass the object through directly and must map `ace_mode` to `mode`, `tm_scope` to `scope`, and preserve fallback/default values itself. The extension handling also changes from a no-dot uppercase name to `Path.extname(filePath).toUpperCase()`.

## 3. What does Δt (test.patch) actually do?
It adds one focused unit test for `utils.lang('file.scss')`, expecting `name: 'SCSS'`, `mode: 'scss'`, and `scope: 'source.scss'`.

## 4. Does Δt directly exercise the breaking change?
Yes. The old code returns the raw Fang v2 object, whose properties do not line up with Fractal’s expected `mode` and `scope` fields. Δc maps the new Fang v2 fields into Fractal’s stable language-info shape, making the new SCSS test pass.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden unit test directly targets the API-shape change introduced by `@allmarkedup/fang` 2.0.0.

## 6. Δc nature
REAL_SOURCE_REPAIR — `packages/core/src/utils.js` adapts the language metadata mapping for Fang v2.

## 7. Soundness concerns / notes
- The witness is narrow but precise: one unit test over the exact compatibility wrapper affected by the dependency update.

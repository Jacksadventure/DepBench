# Test-patch audit — asciidoctor__asciidoctor-cli.js__96

## 1. Task summary
- Folder: asciidoctor__asciidoctor-cli.js__96
- Ecosystem: npm_and_yarn
- Upgrade: fast-deep-equal 2.0.1 -> 3.1.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npm run lint`

## 2. What is the breaking change?
No dependency breaking change is witnessed by the verifier. The repair and hidden tests mostly convert bracket property access to dot property access, prefer plain strings over templates, and change `let` to `const`, which is lint/style cleanup unrelated to `fast-deep-equal` behavior.

## 3. What does Δt (test.patch) actually do?
Touches `test/test.js`. It rewrites assertions such as `result['files']` to `result.files`, `options['backend']` to `options.backend`, removes a template literal around static HTML strings, and changes several local variables from `let` to `const`.

## 4. Does Δt directly exercise the breaking change?
No. The verifier command is `npm run lint`, and the patched tests are style rewrites rather than assertions that expose a `fast-deep-equal` API or semantic incompatibility.

## 5. Coverage verdict
TESTS_OTHER_THING — lint/format-only `test_cmd` is excluded by the locked rules, and the observed patch intent is lint cleanup rather than dependency-break evidence.

## 6. Δc nature
FORMATTER_LINT_CHURN — Δc edits `lib/invoker.js` and `lib/options.js` for style/lint concerns such as dot notation, static string literals, and related standard-js preferences.

## 7. Soundness concerns / notes
- The manifest bump changes `fast-deep-equal`, but neither Δc nor Δt shows use of that package.
- This should not be counted in the witnessed benchmark even if the lint command fails before Δc.

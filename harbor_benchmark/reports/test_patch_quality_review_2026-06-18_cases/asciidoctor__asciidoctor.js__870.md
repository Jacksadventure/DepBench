# Test-patch audit — asciidoctor__asciidoctor.js__870

## 1. Task summary
- Folder: asciidoctor__asciidoctor.js__870
- Ecosystem: npm_and_yarn
- Upgrade: ignore 3.0.9 -> 5.0.0 (PR was actually a `standard` linter upgrade 12.0.1 -> 14.3.3; `ignore` is a transitive dep)
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `npm run code:lint`

## 2. What is the breaking change?
There is no behavioral/runtime breaking change. The underlying PR upgraded the `standard` JS linter, whose new rules reject quoted property keys, bracket member access (`obj['x']`), `let` where `const` suffices, direct `obj.hasOwnProperty(...)`, and template literals for plain strings. The "fix" is purely reformatting source to satisfy the new linter.

## 3. What does Δt (test.patch) actually do?
Touches 5 spec files (`spec/browser/asciidoctor-spec.js`, `spec/browser/run.js`, `spec/node/asciidoctor.spec.js`, `spec/share/asciidoctor-spec.js`, `spec/share/semver.js`). Every hunk is a linter auto-fix: `'stylesheet'`→`stylesheet`, `defaultFormatter['$$class']['$$name']`→`defaultFormatter.$$class.$$name`, `message['text']`→`message.text`, `` `paragraph` ``→`'paragraph'`, `let`→`const`, `defs.hasOwnProperty(key)`→`Object.prototype.hasOwnProperty.call(defs, key)`. No new test cases, no modified assertions, no fixtures — only stylistic rewrites of existing tests.

## 4. Does Δt directly exercise the breaking change?
No. Every Δt change is semantically a no-op (bracket vs dot access, quoted vs unquoted keys, `let` vs `const` are runtime-identical). The assertions test the exact same behavior before and after. Nothing in Δt would plausibly fail on P⊕Δm and pass on P⊕Δm⊕Δc on behavioral grounds.

## 5. Coverage verdict
UNWITNESSED — the verifier command is `npm run code:lint` (a lint command, explicitly excluded by the DependBench witnessed definition: "not ... lint"), and both Δc and Δt are `standard`-14 auto-fixes with zero runtime/behavioral effect.

## 6. Δc nature
FORMATTER_LINT_CHURN — `asciidoctor-core-api.js`, `asciidoctor-extensions-api.js`, `benchmark/*.js`, `tasks/module/*.js` are all rewritten with the identical linter rules (quoted-key removal, bracket→dot, `let`→`const`, `Object.prototype.hasOwnProperty.call`); no logic changes.

## 7. Soundness concerns / notes
This is the most clearly invalid task of the eight. The "test command" is a linter, not a test suite, so the FAIL→PASS transition is a lint failure→lint pass — exactly the failure mode the witnessed definition excludes. The `ignore 3.0.9->5.0.0` library label is also misleading: the real driver is the `standard` linter upgrade. Should be quarantined from the witnessed main set (matches the 2026-06-10 review: "Linter/style upgrade with no observed failure").

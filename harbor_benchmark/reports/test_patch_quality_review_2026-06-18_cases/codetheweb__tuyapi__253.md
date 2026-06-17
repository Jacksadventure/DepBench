# Test-patch audit — codetheweb__tuyapi__253

## 1. Task summary
- Folder: codetheweb__tuyapi__253
- Ecosystem: npm_and_yarn
- Upgrade: string-width 2.0.0 -> 3.0.0 (actual upstream PR is a Renovate `xo` linter bump to v0.25.3; string-width is a transitive dep)
- Flagged in problematic_prs_review_2026-06-10.md: YES (`no_code_pass` / exclude_candidate)
- test_cmd: `npm test`

## 2. What is the breaking change?
No runtime breaking change is exercised. The PR is a dev/lint tooling update (`xo`); the only "source" changes are xo-rule-driven cleanups (`no-unused-vars` on catch bindings, `prefer-slice` over the deprecated `substr`, `prefer-includes` over `indexOf`). None of these alter runtime behavior, and none relate to `string-width`.

## 3. What does Δt (test.patch) actually do?
- `test/parser.js`: changes 4 primitive assertions from `t.deepEqual(x, primitive)` to `t.is(x, primitive)` — two on `parsed.sequenceN` (===2) and two on `parsed.commandByte` (===10).
- No new tests, no fixtures, no infra. Pure ava assertion-style swap for primitives.

## 4. Does Δt directly exercise the breaking change?
No. `t.deepEqual(2, 2)` and `t.is(2, 2)` both pass for primitives, so the Δt assertions pass regardless of Δc. Δc is itself behavior-preserving (`substr(8,16)` ≡ `slice(8,24)`; `indexOf(x)===-1` ≡ `!includes(x)`; `catch(error)` ≡ `catch(_)`), so `TEST(P⊕Δm⊕Δt)=PASS` without Δc — the canonical `no_code_pass` pattern. There is no assertion that would plausibly fail on P⊕Δm and pass on P⊕Δm⊕Δc.

## 5. Coverage verdict
UNWITNESSED — confirmed `no_code_pass`: Δt passes on P⊕Δm without Δc; Δc is behavior-preserving lint churn and Δt's `deepEqual`→`is` swap is also behavior-preserving for primitives.

## 6. Δc nature
FORMATTER_LINT_CHURN — `lib/cipher.js`: `catch(error)`→`catch(_)` (3x), `md5hash.substr(8,16)`→`md5hash.slice(8,24)`; `lib/message-parser.js`: `catch(error)`→`catch(_)` (2x), `Object.values(...).indexOf(...)===-1`→`!Object.values(...).includes(...)`. All xo-rule-driven, no runtime semantics change.

## 7. Soundness concerns / notes
- Confirmed unwitnessed; should be excluded from the witnessed main benchmark (matches the 2026-06-10 review recommendation).
- The dependency is a dev/lint tool (xo / string-width transitively), not a runtime dependency — there is no consumer-code runtime repair to witness.
- The instruction mis-labels the upgrade as `string-width 2.0.0→3.0.0`, hiding that the real driver is an xo bump; an agent has no meaningful runtime fix to make.

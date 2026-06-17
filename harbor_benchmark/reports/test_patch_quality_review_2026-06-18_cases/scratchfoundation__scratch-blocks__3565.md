# Test-patch audit — scratchfoundation__scratch-blocks__3565

## 1. Task summary
- Folder: scratchfoundation__scratch-blocks__3565
- Ecosystem: npm_and_yarn
- Upgrade: eslint-config-scratch 14.1.12 -> 14.1.14
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `npm run test:lint`

## 2. What is the breaking change?
eslint-config-scratch 14.1.14 pulls typescript-eslint 8.58.2 → 8.59.0 (and eslint-plugin-formatjs 6.4.5 → 6.4.6, @formatjs parsers). The newer typescript-eslint flags the project's `as unknown as X` / `as X` type assertions as lint errors, so `npm run test:lint` (eslint) fails on the existing source.

## 3. What does Δt (test.patch) actually do?
- `tests/browser/scratch_field_dropdown.test.ts`: removes an `as | (new (...args) => Blockly.Field) | null` cast on a `registry.getClass` call.
- `tests/unit/block_input_serialization.test.ts`: removes `as Element` on `new XMLSerializer().serializeToString(dom)`.
- `tests/unit/connections.test.ts`: removes two `as unknown as Blockly.RenderedConnection` casts on `previousConnection`/`nextConnection` args to `doDragChecks`.
All hunks are cast removals so the test files satisfy the stricter linter.

## 4. Does Δt directly exercise the breaking change?
It exercises lint-rule compliance, not a functional dependency behavior. The breaking change is a lint rule; Δt removes the now-flagged casts from test files. Without Δc the source files still contain the flagged `as` casts, so `npm run test:lint` fails; with Δc the casts are removed from source too and lint passes.

## 5. Coverage verdict
TESTS_OTHER_THING — the entire task is a lint-rule churn (typescript-eslint 8.59 flagging `as` casts) and the verifier runs `npm run test:lint`; lint failures are explicitly excluded from the witnessed-breaking-change definition, so Δt tests lint compliance rather than a functional breaking change.

## 6. Δc nature
FORMATTER_LINT_CHURN — every hunk in `src/fields/scratch_field_variable.ts`, `src/index.ts`, `src/renderer/{constants,drawer,renderer}.ts`, `src/scratch_c_block_wrap.ts`, `src/scratch_comment_bubble.ts`, `src/scratch_connection_checker.ts` either removes an `as`/`as unknown as` cast or rewrites `x as T` into a typed `const t: T = x`; zero runtime effect.

## 7. Soundness concerns / notes
- This is a lint-only task: test_cmd is `npm run test:lint` and both Δc and Δt are pure cast removals. Per AGENTS.md, lint failures are not valid witnessed breaking changes, so this task should not be in the main (Level-1) benchmark. The problematic-review flag is consistent with this.
- Δc being entirely type/lint churn with no runtime effect also makes it a likely no_code_pass if the verifier ever runs the functional test suite instead of lint.

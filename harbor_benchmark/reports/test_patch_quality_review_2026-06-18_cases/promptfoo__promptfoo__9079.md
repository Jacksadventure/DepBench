# Test-patch audit — promptfoo__promptfoo__9079

## 1. Task summary
- Folder: promptfoo__promptfoo__9079
- Ecosystem: npm_and_yarn
- Upgrade: @opencode-ai/sdk 1.14.22 -> 1.14.33
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx vitest run test/providers/opencode-sdk.test.ts`

## 2. What is the breaking change?
The bundle does not show a dependency break in existing provider behavior. Δc adds new provider capabilities around `parent_session_id`, a warning for no-op `enable_streaming`, and v2 `session.abort` handling.

## 3. What does Δt (test.patch) actually do?
`opencode-sdk.test.ts` adds mocks for `session.abort`, resets session mocks more aggressively, and adds new test groups for forked sessions, streaming warning behavior, and abort-signal cancellation.

## 4. Does Δt directly exercise the breaking change?
No. The tests assert new product/provider behavior implemented by Δc. They do not demonstrate that P⊕Δm broke an existing path due to the `@opencode-ai/sdk` bump. Without Δc the new tests fail because the feature does not exist, not because an upgraded dependency invalidated existing source.

## 5. Coverage verdict
TESTS_OTHER_THING — Δt is a feature/regression test for newly added provider semantics, not witnessed evidence of a dependency-update breaking change.

## 6. Δc nature
MIXED — Δc includes real source changes in `src/providers/opencode-sdk.ts` plus documentation changes in `site/docs/providers/opencode-sdk.md`.

## 7. Soundness concerns / notes
This task may still be useful as a feature-evolution benchmark, but it should not count as Level 1 witnessed breaking-change repair without separate evidence that the SDK bump caused a pre-existing test or compile path to fail.

# Test-patch audit - promptfoo__promptfoo__9078

## 1. Task summary
- Folder: promptfoo__promptfoo__9078
- Ecosystem: npm_and_yarn
- Upgrade: @anthropic-ai/claude-agent-sdk 0.2.123 -> 0.2.126
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx vitest run test/providers/claude-agent-sdk.test.ts`

## 2. What is the breaking change?
Claude Agent SDK 0.2.126 adds `origin.kind` on `result` messages. The old provider used a position heuristic: keep the last `result` in the stream. With background sub-agents, a trailing `task-notification` result can arrive after the main human-origin result, causing promptfoo to return a sub-agent summary or emit a false truncation warning. Δc tracks both `lastResultMsg` and `lastMainResultMsg`, preferring non-`task-notification` results while retaining the older fallback.

## 3. What does Δt (test.patch) actually do?
Adds four provider tests covering the new result-selection behavior: choose a human-origin result even when a task notification follows it, suppress truncation warnings when origin identifies the main result, fall back if every result is a task notification, and return an error when no result arrives.

## 4. Does Δt directly exercise the breaking change?
Yes. The new tests explicitly construct SDK result-message streams with `origin.kind` values introduced by the upgraded SDK. On P+Δm+Δt, the old last-result-wins logic selects the wrong task-notification result and/or warns incorrectly. With Δc, the provider selects the human-origin result and the assertions pass.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - Δt directly covers the SDK 0.2.126 stream-shape change and fails without the production result-selection repair.

## 6. Δc nature
REAL_SOURCE_REPAIR - the production Claude Agent SDK provider is adapted to the new `origin.kind` semantics.

## 7. Soundness concerns / notes
- The tests use mocked SDK streams, which is appropriate here because the breaking behavior is provider interpretation of stream messages.
- The manifest patch also removes `hono` from package metadata, but the relevant Δc/Δt pair is focused on `@anthropic-ai/claude-agent-sdk`.

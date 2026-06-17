# Test-patch audit - promptfoo__promptfoo__8918

## 1. Task summary
- Folder: promptfoo__promptfoo__8918
- Ecosystem: npm_and_yarn
- Upgrade: @opencode-ai/sdk 1.2.19 -> 1.14.22
- test_cmd: `npx vitest run test/providers/opencode-sdk.test.ts`

## 2. What is the breaking change?
The newer OpenCode SDK exposes richer token metadata: `tokens.total`, `tokens.reasoning`, and `tokens.cache` may be either a number or an object with `read`/`write` counts. The old provider only mapped input/output and computed total as input plus output.

## 3. What does Delta t (test.patch) actually do?
It extends the OpenCode SDK test mock token shape and adds a test named `should preserve reasoning and cache token details`, expecting `tokenUsage.total`, `cached`, and `completionDetails` to reflect the new SDK token payload.

## 4. Does Delta t directly exercise the breaking change?
Yes. Without Delta c, `provider.callApi()` returns only prompt/completion/computed-total token usage, so the new expectation for total `42`, cached `3`, reasoning `7`, and cache creation/read details fails. Delta c adds the token conversion helper that makes this pass.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the hidden test directly asserts the new SDK response-shape handling under Vitest.

## 6. Delta c nature
REAL_SOURCE_REPAIR - a focused TypeScript provider-source change.

## 7. Soundness concerns / notes
- The witness is unit-test/mocked rather than an end-to-end SDK call, but it is targeted to the changed SDK response contract.

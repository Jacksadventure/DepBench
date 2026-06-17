# Test-patch audit — promptfoo__promptfoo__8808

## 1. Task summary
- Folder: promptfoo__promptfoo__8808
- Ecosystem: npm_and_yarn
- Upgrade: @opencode-ai/sdk 1.4.3 -> 1.4.7
- test_cmd: `npx vitest run test/providers/opencode-sdk.test.ts`

## 2. What is the breaking change?
The upgraded OpenCode SDK v2 expects session permissions as a `PermissionRuleset` array at `session.create`, while promptfoo exposed a friendlier object-shaped permission config. The provider must convert string and pattern-object entries into rule objects before calling the SDK.

## 3. What does Δt (test.patch) actually do?
Δt imports `convertPermissionConfigToRuleset`, adds unit tests for undefined/empty/simple/pattern/mixed configs, and changes existing OpenCode SDK provider tests to expect `session.create` permission arrays rather than object-shaped permissions. It also checks that empty permissions omit the field.

## 4. Does Δt directly exercise the breaking change?
Yes. Without Δc, the conversion helper does not exist and the provider still sends object-shaped permissions, so the modified tests fail. With Δc, the helper exists and `OpenCodeSDKProvider.callApi()` sends the v2 rule-array shape.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt directly asserts the new OpenCode SDK permission contract that Δc implements.

## 6. Δc nature
MIXED — Δc includes real provider source repair plus docs and an example `permissions/promptfooconfig.yaml`.

## 7. Soundness concerns / notes
The witness is focused and appropriate. The only caveat is that the oracle patch contains documentation/example material in Δc beyond the minimal source repair.

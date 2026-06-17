# Test-patch audit - promptfoo__promptfoo__8946

## 1. Task summary
- Folder: promptfoo__promptfoo__8946
- Ecosystem: npm_and_yarn
- Upgrade: @anthropic-ai/claude-agent-sdk 0.2.119 -> 0.2.120
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx vitest run test/providers/claude-agent-sdk.test.ts`

## 2. What is the breaking change?
The patch set is about adding support for new Claude Agent SDK 0.2.120 configuration options: `skills`, `forward_subagent_text`, `managed_settings`, and `plan_mode_instructions`. These are new option pass-throughs and documentation/examples, not an observed break in existing provider behavior.

## 3. What does test.patch actually do?
The hidden test patch adds new vitest cases that instantiate `ClaudeCodeSDKProvider` with those new config keys and assert that `mockQuery` receives the corresponding SDK option names (`skills`, `forwardSubagentText`, `managedSettings`, `planModeInstructions`).

## 4. Does test.patch directly exercise the breaking change?
No. The tests require newly implemented feature pass-throughs. On P+Delta_m+Delta_t, they fail because the old provider does not know about these newly asserted options, not because an existing call path broke under 0.2.120.

## 5. Coverage verdict
TESTS_OTHER_THING - Delta_t tests new provider feature support and documentation-driven behavior, not a dependency-induced break in existing source.

## 6. Delta_c nature
MIXED - source option plumbing is bundled with documentation and example updates.

## 7. Soundness concerns / notes
This looks like a feature/update PR attached to a dependency bump. The hidden tests are meaningful for promptfoo's new SDK option support, but they do not establish witnessed breaking-change repair for the dependency upgrade.

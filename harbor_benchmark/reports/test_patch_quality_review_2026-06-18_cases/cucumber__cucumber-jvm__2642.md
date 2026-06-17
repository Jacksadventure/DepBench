# Test-patch audit - cucumber__cucumber-jvm__2642

## 1. Task summary
- Folder: cucumber__cucumber-jvm__2642
- Ecosystem: maven
- Upgrade: messages.version 19.1.4 -> 21.0.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `mvn ... -pl cucumber-core -am ... -Dtest=HtmlFormatterTest,MessageFormatterTest,NoPublishFormatterTest test` (extracted from `test_state.py`; batch metadata could not extract it)

## 2. What is the breaking change?
`io.cucumber:messages` 21 changes the generated message constructors and conversion helpers. Production code can no longer use `TimeConversion.javaInstantToTimestamp` / `javaDurationToDuration`, and message types such as `TestCaseStarted`, `TestStepResult`, and `TestRunFinished` require additional fields. Δc migrates to `io.cucumber.messages.Convertor.toMessage(...)` and supplies new thread/origin/error fields.

## 3. What does Δt (test.patch) actually do?
Updates three cucumber-core formatter tests to match the new `TestRunFinished` constructor shape by adding the trailing `null` argument. It also removes an unused `Disabled` import in `HtmlFormatterTest`.

## 4. Does Δt directly exercise the breaking change?
Yes, at compile/API level. The patched tests construct messages with the new generated API, while the repaired production emitters also need the same messages-version migration. On P+Δm+Δt, cucumber-core still references removed conversion helpers and old constructor signatures, so Maven test compilation fails. With Δc, the production message emission code compiles and the formatter tests run.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the hidden tests use the post-upgrade generated message API and the module fails to compile without the production migration.

## 6. Δc nature
REAL_SOURCE_REPAIR - production Java emitters in `TestCase`, `TestStep`, and `CucumberExecutionContext` are updated to the new messages API. No config-only or test-only repair.

## 7. Soundness concerns / notes
- Δt mainly mirrors constructor changes in tests; it is not adding new behavioral assertions.
- The witness is still valid because the verifier compiles the affected module and the break is a real API/constructor break, not dependency resolution or lint.

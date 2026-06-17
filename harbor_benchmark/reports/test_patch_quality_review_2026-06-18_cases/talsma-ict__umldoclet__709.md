# Test-patch audit — talsma-ict__umldoclet__709

## 1. Task summary
- Folder: talsma-ict__umldoclet__709
- Ecosystem: maven
- Upgrade: net.sourceforge.plantuml:plantuml-asl 1.2025.7 -> 1.2025.8
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE` (test_state runs `mvn ... -Dtest=UMLOptionsTest test`)

## 2. What is the breaking change?
PlantUML moved timeout configuration away from `net.sourceforge.plantuml.OptionFlags` to the new `net.sourceforge.plantuml.cli.GlobalConfig` / `GlobalConfigKey` API. The old `OptionFlags` import and timeout setter no longer match the upgraded dependency.

## 3. What does Δt (test.patch) actually do?
`UMLOptionsTest` imports `GlobalConfig` and `GlobalConfigKey` instead of `OptionFlags`, then verifies `GlobalConfig.getInstance().value(GlobalConfigKey.TIMEOUT_MS)` after processing `--uml-timeout`.

## 4. Does Δt directly exercise the breaking change?
Yes. On P⊕Δm, production `UMLOptions` still imports `OptionFlags` and calls `setTimeoutMs`; that fails compilation or writes to the wrong removed/obsolete API. With Δc, the source writes `GlobalConfigKey.TIMEOUT_MS`, and Δt asserts the new PlantUML configuration location.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the test targets the PlantUML API migration directly and passes only after the source moves from `OptionFlags` to `GlobalConfig`.

## 6. Δc nature
REAL_SOURCE_REPAIR — one production file (`UMLOptions.java`) changes imports and writes the timeout through `GlobalConfig.getInstance().put(GlobalConfigKey.TIMEOUT_MS, ...)`.

## 7. Soundness concerns / notes
Clean, narrow witness. The extracted command is unavailable in metadata, but `test_state.py` targets the relevant `UMLOptionsTest`.

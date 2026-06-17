# Test-patch audit — cucumber__cucumber-jvm__3162

## 1. Task summary
- Folder: cucumber__cucumber-jvm__3162
- Ecosystem: maven
- Upgrade: junit-jupiter.version 5.14.2 -> 6.0.2
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE`

## 2. What is the breaking change?
JUnit Platform 6 moves resource APIs from `org.junit.platform.commons.support.Resource` to `org.junit.platform.commons.io.Resource` and changes the classpath-resource selector path. The old production code still calls deprecated/removed selector and resource APIs, so `cucumber-junit-platform-engine` no longer compiles cleanly against the upgraded JUnit stack.

## 3. What does Δt (test.patch) actually do?
Touches `cucumber-junit-platform-engine/src/test/java/io/cucumber/junit/platform/engine/CucumberTestEngineTest.java`. It updates the test import to `org.junit.platform.commons.io.Resource`, removes the deprecation suppression, and changes the duplicate-resource selector call from `selectClasspathResource(resources)` to `selectClasspathResourceByName(resources)`.

## 4. Does Δt directly exercise the breaking change?
Yes. The patched `classpathResourceSelectorThrowIfDuplicateResources` test compiles against the new JUnit Platform selector/resource API, while `P⊕Δm` production code still imports the old resource type and calls the old classpath-resource methods.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — on `P⊕Δm⊕Δt`, the test module should fail at compile/build time because production selectors still use removed JUnit Platform APIs; Δc migrates those production call sites and the targeted engine test can pass.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc updates production Java files under `cucumber-junit-platform-engine/src/main/java/io/cucumber/junit/platform/engine/` to the new `Resource`, `ResourceFilter`, `getResources()`, and non-null `DiscoveryIssue` APIs.

## 7. Soundness concerns / notes
- The extracted command is unavailable in metadata, but `test_state.py` clearly targets Maven tests for `CucumberTestEngineTest`.
- This is a compile-level witness rather than a runtime assertion witness, which is appropriate for a Java API migration.

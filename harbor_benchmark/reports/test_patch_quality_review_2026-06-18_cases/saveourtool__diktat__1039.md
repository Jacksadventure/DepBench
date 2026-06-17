# Test-patch audit — saveourtool__diktat__1039

## 1. Task summary
- Folder: saveourtool__diktat__1039
- Ecosystem: maven
- Upgrade: kotlin.version 1.5.21 -> 1.5.30
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `mvn ... -pl diktat-test-framework -am -Dtest=TestArgumentsReader,TestConfigReader test`

## 2. What is the breaking change?
Kotlin 1.5.30 exposes source compatibility issues: `kotlinx.serialization.decodeFromString` requires opting into `ExperimentalSerializationApi` at these call sites, and the old internal helper `org.jetbrains.kotlin.utils.addToStdlib.firstNotNullResult` is replaced by standard `firstNotNullOfOrNull`.

## 3. What does Δt (test.patch) actually do?
Δt applies the same serialization opt-in fix to test-framework readers: `TestArgumentsReader.kt` and `TestConfigReader.kt` import `ExperimentalSerializationApi` and annotate `parseResource()` with `@OptIn(ExperimentalSerializationApi::class)`.

## 4. Does Δt directly exercise the breaking change?
Yes, as a compile-level witness. The hidden test patch fixes the test-framework compilation surface for Kotlin 1.5.30, and the verifier builds `diktat-test-framework -am`, so production modules touched by Δc are compiled too. Without Δc, `RulesConfigReader.kt` still lacks the serialization opt-in and `IndentationRule.kt` still imports/uses the removed internal helper, producing compile failures before the selected tests can pass. With Δc, those source compile errors are repaired.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the upgraded Kotlin toolchain/library surface causes source compile failures that Δc repairs, and Δt keeps the test-side code compatible with the same post-upgrade surface.

## 6. Δc nature
REAL_SOURCE_REPAIR — production Kotlin code is updated for the new serialization opt-in requirement and the removed Kotlin internal helper.

## 7. Soundness concerns / notes
This is a compile-level witness rather than a new runtime assertion, but compiled-language/toolchain API breaks are valid under the locked definition.

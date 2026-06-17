# Test-patch audit — saveourtool__diktat__1529

## 1. Task summary
- Folder: saveourtool__diktat__1529
- Ecosystem: maven
- Upgrade: io.github.microutils:kotlin-logging-jvm 2.1.23 -> 3.0.3 (task labels it `version ${log4j.version} -> ${mu-logging.version}`)
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `<could not extract>` (test_state.py could not extract a verifier command)

## 2. What is the breaking change?
kotlin-logging-jvm v3 dropped the slf4j-`Logger` integration / `LoggerFactory`-based constructors; `KotlinLogging.logger(...)` now returns `mu.KLogger` and the `logger(LoggerFactory.getLogger(...))` overload is gone. The project's diktat `EmptyBlock` lint rule also needs a new exemption because the v3 logging idiom `KotlinLogging.logger {}` uses an empty lambda that the rule would otherwise flag.

## 3. What does Δt (test.patch) actually do?
Adds exactly one new test to `diktat-rules/src/test/kotlin/org/cqfn/diktat/ruleset/chapter3/EmptyBlockWarnTest.kt`:
```kotlin
@Test @Tag(WarningNames.EMPTY_BLOCK_STRUCTURE_ERROR)
fun `should not trigger on KotlinLogging logger`() {
    lintMethod("""
        |import mu.KotlinLogging
        |fun some() {
        |    val log = KotlinLogging.logger {}
        |    log.info { "test" }
        |}""".trimMargin())
}
```
`lintMethod` with no warning assertions asserts that NO `EMPTY_BLOCK_STRUCTURE_ERROR` is emitted for `KotlinLogging.logger {}`.

## 4. Does Δt directly exercise the breaking change?
Yes. The new test feeds `KotlinLogging.logger {}` (an empty lambda block) to the `EmptyBlock` rule. On P⊕Δm the original `EmptyBlock.kt` has no `isKotlinLogging` exemption, so the rule would warn on the empty block → test fails. On P⊕Δm⊕Δc the `isKotlinLogging` guard (added in `EmptyBlock.kt`) short-circuits `checkEmptyBlock` → no warning → test passes. (Additionally the project must compile, which forces the slf4j→mu.KotlinLogging migration in Δc.)

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt adds a focused behavioral test (`should not trigger on KotlinLogging logger`) that fails on the un-patched `EmptyBlock` rule and passes once Δc adds the `isKotlinLogging` exemption, with the compile-level slf4j removal as a necessary prerequisite.

## 6. Δc nature
REAL_SOURCE_REPAIR — slf4j→mu.KotlinLogging migration across `JsonResourceConfigReader.kt`, `RulesConfigReader.kt`, `LoggingUtils.kt`, `StreamGobbler.java`, `LocalCommandExecutor.kt`, `TestArgumentsReader.kt`, `FileComparator.kt`, `TestCheckWarn.kt`, `TestComparatorUnit.kt`, `TestCompare.kt`, `TestProcessingFactory.kt`, plus the behavioral `EmptyBlock.kt` rule change adding `isKotlinLogging`.

## 7. Soundness concerns / notes
Two concerns. (1) `test_cmd` could not be extracted from test_state.py — the verifier command is unknown, so it is unclear whether this single `EmptyBlockWarnTest` test is actually the one executed; if the verifier runs the whole module the slf4j migration must compile for any test to run. (2) Δt is narrow (one test) and only exercises the `EmptyBlock` behavioral change, not the broader logging-API migration — but that is acceptable since the migration is a compile prerequisite the agent must satisfy regardless.

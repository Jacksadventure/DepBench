# Test-patch audit — camunda-community-hub__spring-zeebe__642

## 1. Task summary
- Folder: camunda-community-hub__spring-zeebe__642
- Ecosystem: maven
- Upgrade: zeebe.version 8.4.1 -> 8.4.3
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE` (test_state runs Maven test-compile plus `PropertyBasedZeebeWorkerValueCustomizerTest`)

## 2. What is the breaking change?
The repair adjusts Spring Zeebe worker variable filtering. If a worker method injects an `ActivatedJob`, the customizer must not recompute and narrow `fetchVariables`, because the activated job path needs the configured variable set preserved. The source patch also starts honoring explicit `@Variable(name=...)` values instead of always using the Java parameter name.

## 3. What does Δt (test.patch) actually do?
- Adds an `activatedJobWorker(@Variable String var1, ActivatedJob activatedJob)` sample worker.
- Adds `shouldNotAdjustVariableFilterVariablesAsActivatedJobIsInjected`, which initializes `fetchVariables` to `["a", "var1", "b"]`, runs `PropertyBasedZeebeWorkerValueCustomizer.customize`, and asserts the same array remains.

## 4. Does Δt directly exercise the breaking change?
Yes. On P⊕Δm, the old `applyFetchVariables` path ignores the `ActivatedJob` parameter and resets `fetchVariables` to the annotation-derived list, so the new assertion fails. With Δc, `hasActivatedJobInjected` short-circuits the recomputation and the hidden test passes.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden test is narrowly targeted at the worker-value customizer behavior changed by the repair and fails on the un-fixed upgraded source for a source-level behavioral reason.

## 6. Δc nature
REAL_SOURCE_REPAIR — `PropertyBasedZeebeWorkerValueCustomizer.java` adds `ActivatedJob` detection, preserves existing fetch-variable configuration when an activated job is injected, and extracts explicit `@Variable.name()` values.

## 7. Soundness concerns / notes
- The hidden test covers the `ActivatedJob` branch but not the explicit `@Variable(name=...)` extraction branch.
- The verifier command is large Maven harness plumbing, but the effective targeted test is appropriate.

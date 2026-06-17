# Test-patch audit — matsim-org__matsim-libs__2586

## 1. Task summary
- Folder: matsim-org__matsim-libs__2586
- Ecosystem: maven
- Upgrade: guice.version 5.1.0 -> 7.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE`

## 2. What is the breaking change?
Guice 7 moves the JSR-330 integration used by this project from `javax.inject` to `jakarta.inject`. Existing MATSim modules and providers still import or instantiate `javax.inject.Inject`, `javax.inject.Provider`, `javax.inject.Singleton`, and `javax.inject.Named`, which no longer match the Guice 7 binding/provider API and fail during Java compilation.

## 3. What does Δt (test.patch) actually do?
- Updates many test and integration-test files from `javax.inject.*` imports and inline `new javax.inject.Provider<...>()` usages to `jakarta.inject.*`.
- Representative files include `CadytsCarIT.java`, `CadytsPtIT.java`, `BetaTravelTest66IT.java`, `LinkSpeedCalculatorIntegrationTest.java`, `AgentNotificationTest.java`, `QSimComponentsTest.java`, and `ActivityReplanningMapTest.java`.
- Also includes substantial whitespace cleanup in the touched tests, but no new behavioral assertions.

## 4. Does Δt directly exercise the breaking change?
Yes, as a compile-level witness. For example, Δt changes `addPlanStrategyBinding(...).toProvider(new javax.inject.Provider<PlanStrategy>() { ... })` to `new jakarta.inject.Provider<PlanStrategy>()` in `CadytsCarIT.java` and `CadytsPtIT.java`, and changes test imports such as `import javax.inject.Inject;` to `import jakarta.inject.Inject;`. On P⊕Δm⊕Δt the patched tests compile against Guice 7/Jakarta injection while production code still exposes or consumes `javax.inject` providers and annotations, so Maven compilation fails; Δc migrates the production source to the same `jakarta.inject` namespace and the selected Maven tests can compile and run.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt puts the hidden tests on the post-Guice-7 Jakarta injection API, causing a Java compile failure until Δc performs the corresponding production-source migration.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc mass-migrates production Java files under `contribs/**/src/main/java` and `matsim/src/main/java` from `javax.inject` to `jakarta.inject`, including providers, annotations, and fully qualified inline provider usages; incidental whitespace churn is secondary.

## 7. Soundness concerns / notes
- The hidden test patch is broad namespace migration plus formatting, not new behavioral coverage. The evidence is nevertheless valid for a compiled-language dependency break because the verifier compiles the patched tests and source together.
- The batch metadata marks `test_cmd` as `TEST_CMD_UNEXTRACTABLE`; manual inspection of `test_state.py` shows a long Maven verifier command selecting many affected tests after applying `test.patch`.

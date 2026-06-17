# Test-patch audit — opentripplanner__OpenTripPlanner__5232

## 1. Task summary
- Folder: opentripplanner__OpenTripPlanner__5232
- Ecosystem: maven
- Upgrade: version 20.4 -> 21.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `mvn ... -Dtest=GraphQLIntegrationTest test`

## 2. What is the breaking change?
The bumped version is the GraphQL Java line. In 21.0, `AsyncExecutionStrategy.handleFetchingException(...)` no longer takes an `ExecutionContext`; Δc removes that parameter from `AbortOnTimeoutExecutionStrategy` and calls `super.handleFetchingException(environment, e)`.

## 3. What does Δt do?
Δt changes `GraphQLIntegrationTest` by removing concurrent JUnit execution and moving static context initialization into a `@BeforeAll` method. It does not assert the timeout strategy directly.

## 4. Does Δt directly exercise the dependency break?
Partially, via compilation of the extension source. The patched verifier builds the project while selecting `GraphQLIntegrationTest`; on P⊕Δm, `AbortOnTimeoutExecutionStrategy` still overrides the old GraphQL Java method signature and fails to compile. With Δc, the production override matches GraphQL Java 21.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the fail/pass gate is a compile-level GraphQL Java API migration in production code, even though Δt itself is mostly a test scheduling/setup adjustment.

## 6. Δc nature
REAL_SOURCE_REPAIR — `AbortOnTimeoutExecutionStrategy` is migrated to the new GraphQL Java method signature.

## 7. Soundness concerns / notes
The hidden test patch is not semantically focused on the breaking API. The case is still witnessed because the selected Maven test path compiles the repaired source and fails before running tests without Δc.

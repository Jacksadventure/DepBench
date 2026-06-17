# Test-patch audit — Graylog2__graylog2-server__25652

## 1. Task summary
- Folder: Graylog2__graylog2-server__25652
- Ecosystem: maven
- Upgrade: com.google.errorprone:error_prone_core 2.48.0 -> 2.49.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE`

## 2. What is the breaking change?
The upgraded dependency is Error Prone, and the patch responds to new static-analysis findings rather than an application dependency API/runtime incompatibility. The changes include replacing equivalent Java idioms, closing a stream in a test, and expanding wildcard imports.

## 3. What does Δt (test.patch) actually do?
Touches `graylog2-server/src/test/java/org/graylog/collectors/FleetServiceTest.java` and `graylog2-server/src/test/java/org/graylog2/lookup/ServiceListenerCleanupTest.java`. It wraps `sourceService.streamAllByFleet(...)` in try-with-resources and replaces a wildcard lookup import with explicit imports.

## 4. Does Δt directly exercise the breaking change?
No. Δt updates tests to satisfy static-analysis/style checks from the Error Prone bump; it does not add or alter an assertion that exercises Graylog runtime behavior against a changed library API.

## 5. Coverage verdict
TESTS_OTHER_THING — the failure evidence is lint/static-analysis cleanup from an Error Prone upgrade, and lint-style failures are excluded from witnessed breaking-change evidence.

## 6. Δc nature
FORMATTER_LINT_CHURN — Δc changes production Java code for Error Prone/style findings, including `Duration.toSeconds()`, `Optional.isEmpty()`, wildcard import expansion, and indentation-only churn.

## 7. Soundness concerns / notes
- The underlying Maven command compiles/tests `graylog2-server`, but the causal signal is the static analyzer, not a product dependency behavior.
- This task may be useful for toolchain-upgrade repair evaluation, but it should not count as a witnessed dependency breaking-change case.

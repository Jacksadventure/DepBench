# Test-patch audit — gruelbox__transaction-outbox__519

## 1. Task summary
- Folder: gruelbox__transaction-outbox__519
- Ecosystem: maven
- Upgrade: junit.jupiter.version 5.9.3 -> 5.10.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `mvn ... -Dtest=ApplicationConfig,BusinessService,BusinessServiceTest,DaoImpl,RemoteCallService,EventuallyConsistentController test` (extracted bundle label was `TEST_CMD_UNEXTRACTABLE`)

## 2. What is the breaking change?
Although the task label is the JUnit Jupiter bump, Δm also upgrades the Quarkus module from `quarkus.version` 2.16.5.Final to 3.6.4 and removes a Quarkus test dependency. Quarkus 3 is the Jakarta EE migration: application and test code must import `jakarta.enterprise`, `jakarta.inject`, `jakarta.transaction`, and `jakarta.ws.rs` rather than the old `javax.*` packages.

## 3. What does Δt (test.patch) actually do?
- Rewrites Quarkus acceptance test/support classes from `javax.*` imports to `jakarta.*`.
- Updates `BusinessService` to constructor-inject `TransactionOutbox` alongside `DaoImpl`.
- Applies small cleanup/suppression changes in acceptance-test support code, including removing extra semicolons and adding `@SuppressWarnings`.
- The verifier compiles and runs the Quarkus acceptance-test class set.

## 4. Does Δt directly exercise the breaking change?
Yes, but the witnessed break is the Quarkus 3/Jakarta break bundled into Δm, not JUnit 5.10 itself. On P⊕Δm⊕Δt, the main Quarkus source still imports `javax.enterprise`, `javax.inject`, and `javax.transaction`, which fail against the Quarkus 3/Jakarta dependency set. Δc rewrites the production Quarkus classes to `jakarta.*` and adjusts minor source compatibility issues.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the verifier compiles/runs Quarkus acceptance tests after the hidden Jakarta test migration, and Δc is required to make production Quarkus integration code compile against the upgraded dependency set.

## 6. Δc nature
REAL_SOURCE_REPAIR — the oracle patch edits production Java source in the Quarkus module, migrating imports from `javax.*` to `jakarta.*` and making small source compatibility changes.

## 7. Soundness concerns / notes
The task is metadata-contaminated: the nominal library is `junit.jupiter.version`, while the actual witnessed break comes from the concurrent Quarkus 2 -> 3 upgrade inside Δm. It is still a real source/API witness for the packaged Δm, but not a clean JUnit breaking-change case.

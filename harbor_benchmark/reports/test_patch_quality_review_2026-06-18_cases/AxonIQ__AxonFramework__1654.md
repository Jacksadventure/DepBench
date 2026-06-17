# Test-patch audit — AxonIQ__AxonFramework__1654

## 1. Task summary
- Folder: AxonIQ__AxonFramework__1654
- Ecosystem: maven
- Upgrade: hibernate-validator 6.1.7.Final -> 7.0.0.Final
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: Maven `BeanValidationInterceptorTest` command extracted in `tests/test_state.py`

## 2. What is the breaking change?
Hibernate Validator 7 moves from the `javax.validation` namespace to `jakarta.validation`. Production classes still importing `javax.validation.*` no longer compile against the upgraded validation API.

## 3. What does Δt (test.patch) actually do?
`BeanValidationInterceptorTest.java` changes its validation imports from `javax.validation.*` to `jakarta.validation.*`, broadens JUnit and assertion imports, and adds a suppression annotation on the local annotated test field.

## 4. Does Δt directly exercise the breaking change?
Yes. The verifier runs `BeanValidationInterceptorTest`. With Δm and Δt but without Δc, the test source is already on `jakarta.validation`, while production `BeanValidationInterceptor` and `JSR303ViolationException` still import `javax.validation`, yielding a deterministic compile failure. Δc updates the production imports and related Javadocs.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — this is a direct namespace-migration compile witness for the hibernate-validator 7 upgrade.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc updates production Java validation imports in `BeanValidationInterceptor` and `JSR303ViolationException`; the formatting/Javadoc churn is incidental.

## 7. Soundness concerns / notes
The evidence is compile-level rather than a runtime behavioral assertion, but compile failures from dependency API migration are valid witnessed failures for this benchmark.

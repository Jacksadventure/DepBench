# Test-patch audit — piomin__spring-boot-logging__41

## 1. Task summary
- Folder: piomin__spring-boot-logging__41
- Ecosystem: maven
- Upgrade: Spring Boot 2.1.4.RELEASE -> 2.7.13
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: targeted Maven test run for `MainControllerTests`, `LogstashAutoConfigurationTest`, and `ReactiveLogstashAutoConfigurationTest`

## 2. What is the breaking change?
Spring Boot 2.7 changes the test/runtime environment enough that the old auto-configuration pattern is no longer acceptable: `SpringLoggingAutoConfiguration` both creates a `RestTemplate` bean and field-injects an optional `RestTemplate`, then mutates it in `@PostConstruct`. The human repair removes that circular dependency pattern and installs the interceptor through conditional bean methods.

## 3. What does Δt (test.patch) actually do?
It migrates four tests from JUnit 4 to JUnit Jupiter imports/assertions and removes `@RunWith(SpringRunner.class)` from the Spring Boot tests. The assertions remain the same: context startup plus non-null beans and simple controller responses.

## 4. Does Δt directly exercise the breaking change?
Yes. The hidden tests are Spring context tests against the upgraded Boot stack. With the old source, the logstash auto-configuration can fail during context creation because of the `RestTemplate` circular dependency/mutation pattern. Δc replaces that with `@ConditionalOnMissingBean` and `@ConditionalOnBean` bean methods, so the same context tests can start and pass. The JUnit migration part of Δt is test-framework alignment for the upgraded Boot starter.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the upgraded Spring Boot/JUnit stack plus context tests expose the auto-configuration break, and Δc is a real source change needed for the targeted tests to pass.

## 6. Δc nature
REAL_SOURCE_REPAIR — `SpringLoggingAutoConfiguration.java` removes optional field injection and `@PostConstruct`, creates a missing `RestTemplate` bean separately, and decorates an existing `RestTemplate` through a conditional bean.

## 7. Soundness concerns / notes
- Δt is partly mechanical JUnit 4 -> Jupiter migration, but the targeted Spring context tests still exercise the repaired auto-configuration path.
- The manifest patch has large XML formatting churn around the actual Spring Boot version bump.

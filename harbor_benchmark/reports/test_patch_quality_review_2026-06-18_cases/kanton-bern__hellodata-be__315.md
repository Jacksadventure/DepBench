# Test-patch audit — kanton-bern__hellodata-be__315

## 1. Task summary
- Folder: kanton-bern__hellodata-be__315
- Ecosystem: maven
- Upgrade: spring-boot.version 3.5.11 -> 4.0.3
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE`

## 2. What is the breaking change?
Spring Boot 4 moves and reshapes several framework APIs used by this project: test-slice annotations move from `org.springframework.boot.test.autoconfigure.web.servlet` to `org.springframework.boot.webmvc.test.autoconfigure`, health contributors move under `org.springframework.boot.health.contributor`, persistence autoconfiguration packages move, security method annotations and request matching change, Jackson/Spring Data Redis serializer integration changes, and web/reactive header APIs differ. The manifest also moves the project to Java 21 and aligned Spring Cloud/Springdoc/test artifacts.

## 3. What does Δt (test.patch) actually do?
- Migrates many controller tests from old `WebMvcTest` imports and `@ContextConfiguration` patterns to the Boot 4 test slice shape.
- Reworks `HDControllerTest`, `TestSecurityConfig`, and `TestJwtAuthorizationFilter` for Boot/Spring Security 7 test-context behavior.
- Updates integration tests such as `PostgresTestContainerTest` and `KeycloakTestContainerTest` from old data/test autoconfiguration assumptions to explicit Boot 4-compatible configuration.
- Updates the JupyterHub sidecar controller test with a local test security configuration and adds test `application.yaml`.

## 4. Does Δt directly exercise the breaking change?
Yes, mainly as a broad compile/context-load witness. With Δm and Δt applied, the hidden tests compile and run against Boot 4 package names and test-framework behavior. The old production code still imports removed/moved APIs such as old actuator health classes, old persistence autoconfiguration packages, old `EnableGlobalMethodSecurity`, old `ErrorController`, and old Spring WebFlux header accessors, so `test-compile`/`test` fails until Δc migrates the production code.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt moves the test suite to the post-Spring-Boot-4 API surface, and the verifier runs Maven compile/test work that fails on the old production API usage and passes after the source migration.

## 6. Δc nature
MIXED — Δc contains real Spring Boot 4 source repairs across Java backend modules, but it is bundled with unrelated Angular menu behavior, language-selection changes, and large i18n JSON churn. The load-bearing repair is real source migration, but the patch is not cleanly source-only.

## 7. Soundness concerns / notes
- `test_cmd` is not extractable from metadata; manual inspection of `test_state.py` shows a full Maven `test` command after hidden test patch application, with a `test-compile` install phase.
- Δt is largely migration of existing tests rather than new assertions, but compile/context-load failure is valid witnessed evidence for a compiled-language framework API break.

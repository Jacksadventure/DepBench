# Test-patch audit — freechat-fun__freechat__757

## 1. Task summary
- Folder: freechat-fun__freechat__757
- Ecosystem: maven
- Upgrade: artifactId redisson-spring-data-35 -> redisson-spring-data-40 (with Spring Boot 3.5.8 -> 4.0.0)
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE` (test_state runs Maven against `AbstractIntegrationTest`)

## 2. What is the breaking change?
The real platform upgrade is Spring Boot 4.0.0. Spring Boot 4 relocates Tomcat and WebTestClient auto-configuration packages, so the old production `TomcatServletWebServerFactory` import and the old test `AutoConfigureWebTestClient` import no longer compile.

## 3. What does Δt (test.patch) actually do?
Δt touches `freechat-start/src/test/java/fun/freechat/AbstractIntegrationTest.java` and changes `org.springframework.boot.test.autoconfigure.web.reactive.AutoConfigureWebTestClient` to `org.springframework.boot.webtestclient.autoconfigure.AutoConfigureWebTestClient`.

## 4. Does Δt directly exercise the breaking change?
Yes. The verifier compiles/runs `AbstractIntegrationTest`; after Δt the test side uses the Spring Boot 4 package, while P⊕Δm source still imports `org.springframework.boot.web.embedded.tomcat.TomcatServletWebServerFactory`, which is repaired by Δc to `org.springframework.boot.tomcat.servlet.TomcatServletWebServerFactory`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — P⊕Δm⊕Δt should fail at Maven compile/test startup on Spring Boot 4 package relocation, and P⊕Δm⊕Δc⊕Δt passes after the Tomcat/WebTestClient migration.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc updates `freechat-start/src/main/java/fun/freechat/config/TomcatConfig.java` for the new Spring Boot package and moves the async timeout into `application.yml`.

## 7. Soundness concerns / notes
The task metadata labels the library as a generic `artifactId`; the actual witnessed break is dominated by the Spring Boot 4 migration bundled with the Redisson Spring Data artifact change.

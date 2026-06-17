# Test-patch audit — apache__logging-log4j2__2345

## 1. Task summary
- Folder: apache__logging-log4j2__2345
- Ecosystem: maven
- Upgrade: org.codehaus.groovy:groovy-bom 3.0.20 -> 3.0.21 (manifest also bumps commons-dbcp2 2.11.0 -> 2.12.0)
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `mvn ... -pl log4j-core-test -am -Dtest=AbstractConfigurationTest,ConfigurationPropertiesOrderTest,InterpolatorTest test` with fallback to `-f log4j-core-test/pom.xml`

## 2. What is the breaking change?
The bundle does not show a Groovy-BOM or commons-dbcp2 API break. The source repair fixes Log4j core lookup lifecycle behavior: `Interpolator` no longer sets `ConfigurationAware` / `LoggerContextAware` lookups lazily during each evaluation, and instead propagates configuration and logger context when `setConfiguration()` / `setLoggerContext()` are called. `AbstractConfiguration` and `PropertiesPlugin` are changed to seed those values into newly created interpolators.

## 3. What does Δt (test.patch) actually do?
Δt replaces `ConfigurationPropertiesOrderTest` with a broader `AbstractConfigurationTest`, adds assertions that runtime/config-time interpolators retain the `Configuration` and `LoggerContext`, and extends `InterpolatorTest` with a test plugin lookup implementing `LoggerContextAware`. The key assertions inspect `InterpolatorTest.getConfiguration(interpolator)` / `getLoggerContext(interpolator)` and verify propagation into the plugin lookup.

## 4. Does Δt directly exercise the breaking change?
It exercises the Log4j lookup propagation fix, but not the dependency bump. The new tests instantiate `TestConfiguration` / `Interpolator` directly and assert internal configuration/context propagation; they do not use Groovy, commons-dbcp2, or any behavior plausibly changed by the manifest upgrade. The fail/pass gate is a source bug/regression test introduced in the same PR, not evidence that `groovy-bom` 3.0.21 breaks existing Log4j code.

## 5. Coverage verdict
TESTS_OTHER_THING — Δt tests an unrelated Log4j core behavior fix (`LoggerContextAware` / `ConfigurationAware` propagation), not the Groovy-BOM dependency breaking change.

## 6. Δc nature
REAL_SOURCE_REPAIR — source logic in `AbstractConfiguration`, `PropertiesPlugin`, and `Interpolator` is changed to propagate configuration and logger context eagerly and safely.

## 7. Soundness concerns / notes
- Strong misattribution concern: the dependency bump is Groovy/commons-dbcp2, while Δc/Δt are about Log4j lookup state.
- The tests may produce a formal FAIL -> PASS around Δc, but the witnessed behavior is a drive-by Log4j bug fix, not dependency-update compatibility.

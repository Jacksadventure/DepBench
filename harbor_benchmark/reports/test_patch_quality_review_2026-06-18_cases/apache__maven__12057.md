# Test-patch audit - apache__maven__12057

## 1. Task summary
- Folder: apache__maven__12057
- Ecosystem: maven
- Upgrade: domtripVersion 0.4.1 -> 1.5.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `mvn ... -pl impl/maven-cli -am -Dtest=CompatibilityFixStrategyTest,DomUtilsTest,GAVUtilsTest,InferenceStrategyTest,ModelUpgradeStrategyTest,ModelVersionUtilsTest,PluginUpgradeStrategyTest test`

## 2. What is the breaking change?
DomTrip 1.5.1 renames/narrows the element traversal API used by mvnup code. Production code that called `Element.child(...)`, `children(...)`, and recursive child traversal APIs must use `childElement(...)` / `childElements(...)` instead. With only the manifest bump, the mvnup module no longer compiles against the upgraded DomTrip API.

## 3. What does test.patch actually do?
The hidden tests update the test-side DomTrip API calls in mvnup tests: for example `dependencies.children("dependency")` becomes `dependencies.childElements("dependency")`. The patch touches CompatibilityFixStrategyTest, DomUtilsTest, GAVUtilsTest, InferenceStrategyTest, ModelUpgradeStrategyTest, ModelVersionUtilsTest, and PluginUpgradeStrategyTest.

## 4. Does test.patch directly exercise the breaking change?
Yes. The patched tests compile and run against DomTrip 1.5.1. On P+Delta_m+Delta_t, test code has been migrated to the new API but production mvnup code still calls removed/renamed DomTrip methods, so compilation fails. Delta_c applies the same API migration across production code.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the verifier targets the mvnup tests and exposes a compile-time DomTrip API break in production code after the dependency upgrade.

## 6. Delta_c nature
REAL_SOURCE_REPAIR - production Java code is migrated from old DomTrip traversal methods to the 1.5.1 API, with related source-level cleanup such as artifact coordinate de-duplication.

## 7. Soundness concerns / notes
The hidden tests are broad and mostly compile/API compatibility checks rather than narrow behavioral probes. That is still acceptable here because the dependency break is a source compile failure, not lint, network, or resource behavior.

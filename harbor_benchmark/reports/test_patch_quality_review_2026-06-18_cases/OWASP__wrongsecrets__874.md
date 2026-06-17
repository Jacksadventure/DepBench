# Test-patch audit — OWASP__wrongsecrets__874

## 1. Task summary
- Folder: OWASP__wrongsecrets__874
- Ecosystem: maven
- Upgrade: spring-boot-starter-parent 3.0.6 -> 3.1.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE`

## 2. What is the breaking change?
The Spring Boot/Azure dependency refresh changes the available JSON classes: production code can no longer compile against `com.nimbusds.jose.shaded.json.JSONArray` / `JSONObject` and must use `net.minidev.json` directly.

## 3. What does Δt (test.patch) actually do?
It adds one resource file, `src/test/resources/thirdkey.txt`, containing a base64-looking key string. It does not add or modify a Java test assertion.

## 4. Does Δt directly exercise the breaking change?
Only indirectly. The hidden resource itself does not reference `ChallengesAPIController` or the JSON imports; the witness comes from the Maven test/compile command failing against the upgraded dependency set until Δc replaces the shaded nimbus JSON imports.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — with the upgraded Spring/dependency graph, P⊕Δm⊕Δt should fail at Java compilation on the removed shaded JSON imports, and P⊕Δm⊕Δc⊕Δt passes after switching to `net.minidev.json`.

## 6. Δc nature
REAL_SOURCE_REPAIR — `src/main/java/org/owasp/wrongsecrets/challenges/ChallengesAPIController.java` changes production imports from shaded nimbus JSON classes to `net.minidev.json`.

## 7. Soundness concerns / notes
The test patch is weak: it is only a resource addition and does not itself create the compile failure. This is still a compile-level dependency witness, but it is not a high-quality behavioral hidden test.


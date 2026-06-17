# Test-patch audit - opentripplanner__OpenTripPlanner__6603

## 1. Task summary
- Folder: opentripplanner__OpenTripPlanner__6603
- Ecosystem: maven
- Upgrade: com.graphql-java:graphql-java 22.3 -> 23.0
- test_cmd: TEST_CMD_UNEXTRACTABLE; `test_state.py` runs Maven build/test commands for the application module

## 2. What is the breaking change?
GraphQL Java 23 changes schema/introspection behavior. Delta c disables strict mode for the GTFS GraphQL runtime wiring, updates bundled schema files with new spec directives, and makes the `@deprecated` reason argument non-null. It also removes an old workaround comment for deprecated-reason replacement.

## 3. What does Delta t do?
Delta t updates `InjectCustomDocumentationTest` so missing deprecated documentation entries must be empty, and updates the expected SDL file for the GraphQL 23 directive output and fixed deprecated-reason behavior.

## 4. Does Delta t directly exercise the breaking change?
Yes. The hidden test checks GraphQL schema SDL generation and deprecated-reason injection after the dependency bump. Without Delta c, the expected SDL and deprecated-reason behavior no longer match GraphQL Java 23; with Delta c, the schema/runtime wiring and expected output align.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE

## 6. Delta c nature
REAL_SOURCE_REPAIR

## 7. Soundness concerns / notes
- The extracted test command is unavailable, but the verifier's Maven command is broad enough to run/compile the affected GraphQL tests.
- The source repair includes resource/schema files, not only Java code, but those resources are part of the runtime API surface.

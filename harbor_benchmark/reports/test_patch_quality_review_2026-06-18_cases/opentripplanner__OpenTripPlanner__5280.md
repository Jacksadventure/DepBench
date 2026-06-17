# Test-patch audit — opentripplanner__OpenTripPlanner__5280

## 1. Task summary
- Folder: opentripplanner__OpenTripPlanner__5280
- Ecosystem: maven
- Upgrade: `org.entur.gbfs:gbfs-java-model` 3.0.0 -> 3.0.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: targeted Maven run for `GbfsFeedLoaderTest`

## 2. What is the breaking change?
`gbfs-java-model` 3.0.1 changed the timezone accessor from returning a raw `String` to returning a generated enum/value object whose string value must be read with `.value()`. `GbfsSystemInformationMapper` still passed `systemInformation.getTimezone()` into a field expecting a string.

## 3. What does Δt (test.patch) actually do?
It updates two assertions in `GbfsFeedLoaderTest`: expected timezone comparisons now call `systemInformation.getData().getTimezone().value()` for the GBFS v2.2 and v1.0 fixtures.

## 4. Does Δt directly exercise the breaking change?
Partially. The test patch itself aligns test expectations with the new dependency model API. The source witness is the production compile/type break in `GbfsSystemInformationMapper`: without Δc the mapper passes the new timezone enum where OpenTripPlanner expects a string. The verifier also runs Maven test compilation before executing the targeted test, so this compile break is deterministic.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — P⊕Δm fails under the new `gbfs-java-model` timezone type, and Δc fixes the production mapper by extracting `.value()`.

## 6. Δc nature
REAL_SOURCE_REPAIR — one production mapper call changes from `getTimezone()` to `getTimezone().value()`.

## 7. Soundness concerns / notes
- The hidden test edits mostly repair test expectations for the dependency API rather than adding a new assertion over `VehicleRentalSystem`.
- The task remains witnessed through Java compilation of the production mapper.

# Test-patch audit - opentripplanner__OpenTripPlanner__5430

## 1. Task summary
- Folder: opentripplanner__OpenTripPlanner__5430
- Ecosystem: maven
- Upgrade: geotools.version 29.2 -> 30.0, plus `gt-opengis` -> `gt-api`
- test_cmd: TEST_CMD_UNEXTRACTABLE; `test_state.py` runs Maven compile/test commands, including `-Dtest=OtpArchitectureModules`

## 2. What is the breaking change?
GeoTools 30 moves many OpenGIS API types from `org.opengis.*` to `org.geotools.api.*` and changes some geometry classes such as `DirectPosition2D/3D` to `Position2D/3D`. Delta c migrates imports and affected type usages across elevation, raster, GeoJSON, and geometry code.

## 3. What does Delta t do?
Delta t updates the architecture-test package constant from `org.opengis..` to `org.geotools.api..`.

## 4. Does Delta t directly exercise the breaking change?
Yes, through compile and architecture checks. With Delta m applied, the old source imports and type names no longer match the GeoTools 30 API. The hidden architecture update allows the new package namespace, and the Maven compile/test step fails until Delta c migrates the source.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE

## 6. Delta c nature
REAL_SOURCE_REPAIR

## 7. Soundness concerns / notes
- Delta t itself is a small architecture-rule update, but the verifier also compiles the affected source tree, so the witness is not merely an assertion rename.
- The task is well aligned with a major dependency API relocation.

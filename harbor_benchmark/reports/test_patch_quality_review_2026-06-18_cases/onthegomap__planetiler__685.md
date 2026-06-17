# Test-patch audit - onthegomap__planetiler__685

## 1. Task summary
- Folder: onthegomap__planetiler__685
- Ecosystem: maven
- Upgrade: geotools.version 29.2 -> 30.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `mvn ... -pl planetiler-core -am -Dtest=ShapefileReaderTest test`

## 2. What is the breaking change?
GeoTools 30 moved several public API types from `org.opengis.*` / older GeoTools packages into `org.geotools.api.*`. Code importing `FeatureSource`, `SimpleFeature`, `Filter`, CRS, and transform exception types from the old packages no longer compiles.

## 3. What does test.patch actually do?
The hidden patch updates `ShapefileReaderTest` imports from old OpenGIS/GeoTools packages to the new `org.geotools.api.*` locations, including `SimpleFeatureStore`, `FactoryException`, and `TransformException`.

## 4. Does test.patch directly exercise the breaking change?
Yes. The patched test compiles against GeoTools 30. Without Delta_c, production `GeoPackageReader` and `ShapefileReader` still import the old API types and use old generic type names, so the targeted test compile fails.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the test patch directly aligns tests to the GeoTools 30 API and exposes the corresponding production import/type migration.

## 6. Delta_c nature
REAL_SOURCE_REPAIR - production readers are migrated to `org.geotools.api.*` imports and updated generic types.

## 7. Soundness concerns / notes
The evidence is compile-time rather than assertion-level, but compile errors from removed/moved dependency APIs are valid witnessed failures for compiled languages under the locked definition.

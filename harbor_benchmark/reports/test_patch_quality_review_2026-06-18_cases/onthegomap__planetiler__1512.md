# Test-patch audit — onthegomap__planetiler__1512

## 1. Task summary
- Folder: onthegomap__planetiler__1512
- Ecosystem: maven
- Upgrade: org.maplibre:mlt 0.0.9 -> 0.0.10
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `mvn ... -pl planetiler-core -am -Dtest=TileSizeStatsTest test`

## 2. What is the breaking change?
MLT 0.0.10 changes the converter API: column mappings move from `Map<Pattern, List<ColumnMapping>>` to `ColumnMappingConfig`, and `ConversionConfig.builder().coercePropertyValues(true)` becomes `mismatchPolicy(ConversionConfig.TypeMismatchPolicy.COERCE)`.

## 3. What does Δt do?
Δt updates `TileSizeStatsTest` to import `ColumnMappingConfig`, construct empty/non-empty column mappings with the new type, and keep the MLT tile-size tests compiling against the upgraded API.

## 4. Does Δt directly exercise the dependency break?
Yes. On P⊕Δm, both production `TileArchiveWriter` and the patched test compile against the new MLT API; the old production code still passes a `Map` and calls the removed `coercePropertyValues(...)`, so the module fails compilation. With Δc, both source and tests use `ColumnMappingConfig` and the new mismatch policy.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the verifier catches the MLT API break as a deterministic Java compile failure without Δc and passes once the source migration is applied.

## 6. Δc nature
REAL_SOURCE_REPAIR — `TileArchiveWriter` is migrated to the new MLT converter configuration API.

## 7. Soundness concerns / notes
Clean compile-level witness. Δt mirrors the same API migration in tests and the verifier compiles the affected production module.

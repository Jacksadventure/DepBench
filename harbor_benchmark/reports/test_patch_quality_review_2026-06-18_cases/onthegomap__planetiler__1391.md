# Test-patch audit — onthegomap__planetiler__1391

## 1. Task summary
- Folder: onthegomap__planetiler__1391
- Ecosystem: maven
- Upgrade: org.maplibre:mlt 0.0.3 -> 0.0.4
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `<could not extract>` (test_state targets `TileSizeStatsTest`)

## 2. What is the breaking change?
MLT 0.0.4 changes `MltConverter.createTilesetMetadata(...)` to take `Map<Pattern, List<ColumnMapping>>` instead of `List<ColumnMapping>` for column mappings.

## 3. What does Δt (test.patch) actually do?
`TileSizeStatsTest.java` imports `java.util.regex.Pattern` and changes the test's local `columnMappings` from `List.of()` to `Map.<Pattern, List<ColumnMapping>>of()` before calling `createTilesetMetadata(...)`.

## 4. Does Δt directly exercise the breaking change?
Yes. The hidden test uses the new MLT 0.0.4 signature. Without Δc, `TileArchiveWriter.java` still passes a `List<ColumnMapping>` and fails to compile against the upgraded dependency; with Δc, production source passes the required map type.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt and Δc both migrate call sites to the new `createTilesetMetadata` signature, and the production call site fails under P⊕Δm⊕Δt until Δc is applied.

## 6. Δc nature
REAL_SOURCE_REPAIR — `TileArchiveWriter.java` changes the production MLT column-mapping argument from an empty list to an empty `Map<Pattern, List<ColumnMapping>>`.

## 7. Soundness concerns / notes
- The extracted command is missing, but `test_state.py` targets `TileSizeStatsTest` with Maven.
- This is a compile-level witness rather than a new behavioral assertion, but it is exactly the dependency API break.

# Test-patch audit - onthegomap__planetiler__1430

## 1. Task summary
- Folder: onthegomap__planetiler__1430
- Ecosystem: maven
- Upgrade: org.maplibre:mlt 0.0.4 -> 0.0.6
- test_cmd: Maven test command targeting `planetiler-core`, primarily `PlanetilerTests` and `TileSizeStatsTest`.

## 2. What is the breaking change?
The MLT upgrade changes the Java API around conversion configuration and metadata decoding. The old direct `new ConversionConfig(...)` constructor usage is replaced by `ConversionConfig.builder()`, and tile-stat metadata access moves from `MltTilesetMetadata` getters to new `MltMetadata`/stream-decoder-style structures.

## 3. What does Delta t (test.patch) actually do?
It updates `TileSizeStatsTest` to construct `ConversionConfig` through the new builder and changes expected MLT attribute-byte counts from `24` to `41`. It also removes one blank line in `PlanetilerTests`.

## 4. Does Delta t directly exercise the breaking change?
Yes. `TileSizeStatsTest` drives MLT conversion and `TileSizeStats.computeMltTileStats`, the same source path repaired in Delta c. The test also has to compile against the new `ConversionConfig` API, matching the production repair in `TileArchiveWriter`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the patched test covers the post-upgrade MLT API/output behavior, and failures would be compile/runtime test failures rather than lint or external-service failures.

## 6. Delta c nature
REAL_SOURCE_REPAIR - the oracle patch is production Java source adapting Planetiler's MLT configuration and tile-stat handling to the new MLT API.

## 7. Soundness concerns / notes
- One test hunk is whitespace-only, but the substantive `TileSizeStatsTest` hunk is directly relevant.
- The bundled `extracted_test_cmd` was `TEST_CMD_UNEXTRACTABLE`, but `tests/test_state.py` contains the concrete Maven command.

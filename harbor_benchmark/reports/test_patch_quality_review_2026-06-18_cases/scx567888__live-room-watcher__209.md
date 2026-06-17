# Test-patch audit — scx567888__live-room-watcher__209

## 1. Task summary
- Folder: scx567888__live-room-watcher__209
- Ecosystem: maven
- Upgrade: scx.version 2.7.10 -> 2.8.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE`

## 2. What is the breaking change?
The `scx` library reorganized several packages in 2.8.0. Imports such as `cool.scx.common.http_client.body.JsonBody`, `cool.scx.common.http_client.body.FormData`, `cool.scx.common.standard.ScxDateTimeFormatter`, `cool.scx.common.util.zip.GunzipBuilder`, and `cool.scx.common.util.ansi.Ansi` moved to new package paths.

## 3. What does Δt (test.patch) actually do?
The hidden test patch updates six watcher tests to import `cool.scx.common.ansi.Ansi` instead of `cool.scx.common.util.ansi.Ansi`. It does not add new assertions; it makes the tests compile against the scx 2.8.0 package layout.

## 4. Does Δt directly exercise the breaking change?
Yes, as a compile-level witness. The patched tests use the new `Ansi` package, while the old production code still imports moved classes from the old scx package layout. The verifier runs the targeted watcher tests, so compilation fails until Δc updates the production imports to the new packages.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt puts the hidden tests on the scx 2.8.0 package layout, and Δc repairs the corresponding production imports.

## 6. Δc nature
REAL_SOURCE_REPAIR — all Δc hunks are production Java import migrations for moved scx classes.

## 7. Soundness concerns / notes
- The evidence is purely compile-level; no behavioral assertions were added.
- The `test_cmd` metadata is unextractable, but `test_state.py` runs Maven with the six touched watcher tests.

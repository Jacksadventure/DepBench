# Test-patch audit — Graylog2__graylog2-server__24634

## 1. Task summary
- Folder: Graylog2__graylog2-server__24634
- Ecosystem: maven
- Upgrade: com.maxmind.geoip2:geoip2 4.4.0 -> 5.0.2
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE`

## 2. What is the breaking change?
geoip2 5.x exposes several MaxMind model values as Java records/accessors rather than old bean-style getters, and the `Location` constructor no longer takes the metro-code parameter used by the old tests. Production code also must use `reader.getMetadata().databaseType()` instead of `getDatabaseType()`.

## 3. What does Δt (test.patch) actually do?
It updates `graylog2-server/src/test/java/org/graylog/plugins/map/geoip/MaxMindIpLocationResolverTest.java`. Assertions change from `country.getName()`, `country.getIsoCode()`, `city.getName()`, and `location.getLatitude()` style getters to record accessors like `country.name()` and `location.latitude()`, and `new Location(...)` calls remove the obsolete constructor argument.

## 4. Does Δt directly exercise the breaking change?
Yes. Representative assertions such as `assertEquals(country.name(), info.countryName())` and the new six-argument `Location` constructor are only valid against the geoip2 5.x record-style API. Old source/test expectations using getter methods and the old constructor fail to compile under P⊕Δm⊕Δt.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt adopts the new geoip2 API shape, while Δc updates production source to `reader.getMetadata().databaseType()`, so the unrepaired upgraded state fails and the repaired state passes.

## 6. Δc nature
REAL_SOURCE_REPAIR — `IPinfoIPLocationDatabaseAdapter.java` changes a production call site from `getDatabaseType()` to the new `databaseType()` accessor.

## 7. Soundness concerns / notes
The production Δc is narrow and the hidden test mostly adapts test fixtures, but the evidence is a clean compile-level API witness for the geoip2 major upgrade.


# Test-patch audit — urlaubsverwaltung__urlaubsverwaltung__4808

## 1. Task summary
- Folder: urlaubsverwaltung__urlaubsverwaltung__4808
- Ecosystem: maven
- Upgrade: org.mnode.ical4j:ical4j 3.2.18 -> 4.0.2
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `mvn ... -Dtest=ICalServiceTest test`

## 2. What is the breaking change?
ical4j 4 changes the calendar/event API and output model: immutable property constants move, components/properties use `add(...)`, event constructors accept Java time types, all-day dates use `LocalDate`, and serialized timed events now render `DTSTART;TZID=Etc/UTC:...` / `DTEND;TZID=Etc/UTC:...` instead of UTC `...Z` strings.

## 3. What does Δt (test.patch) actually do?
It updates `ICalServiceTest` expected calendar text in five cases, replacing UTC `DTSTART:...Z` / `DTEND:...Z` lines with `DTSTART;TZID=Etc/UTC:...` / `DTEND;TZID=Etc/UTC:...`.

## 4. Does Δt directly exercise the breaking change?
Yes. The tests instantiate `ICalService` and compare generated iCalendar output. Without Δc, the source still uses removed/old ical4j 3 APIs (`Date`, `DateTime`, `getProperties().add`, old immutable constants), so the upgraded project either fails to compile or emits the old shape. With Δc, `ICalService` uses ical4j 4 APIs and the expected timezone-qualified output.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt asserts the ical4j-4 output shape and the source needs Δc's API migration to compile and satisfy those expectations.

## 6. Δc nature
REAL_SOURCE_REPAIR — rewrites production `ICalService.java` for the ical4j 4 API, including property/component mutation, immutable constants, Java time constructors, and all-day event handling.

## 7. Soundness concerns / notes
- The task is focused: one source file and one matching test file.
- The observed witness includes compile-level API compatibility and behavioral serialization changes.

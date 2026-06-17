# Test-patch audit — OpenFeign__querydsl__1685

## 1. Task summary
- Folder: OpenFeign__querydsl__1685
- Ecosystem: maven
- Upgrade: hibernate.version 7.2.6.Final -> 7.3.1.Final
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE` (test_state runs Maven tests for `JPQLSerializerTest`, `JPADomainExporterTest`, and `AntJPADomainExporterTest`)

## 2. What is the breaking change?
Hibernate 7.3 tightens parameter type handling and changes metamodel exposure for `@Temporal` on map attributes. Querydsl's old serializer kept subquery limit/offset constants as `Long`, primitive parameter coercion did not handle wrapper conversion correctly, and JPA domain exporter expected the old `DateTimePath` output where Hibernate 7.3 now exposes enough metadata for `DatePath`.

## 3. What does Δt (test.patch) actually do?
Δt updates `JPQLSerializerTest` expectations from `5L`/`10L` style constants to integer constants, and adjusts `JPADomainExporterTest` plus `AntJPADomainExporterTest` so generated `QCalendar.java` references replace `DateTimePath` with `DatePath` before comparison.

## 4. Does Δt directly exercise the breaking change?
Yes. Representative assertions such as `assertThat(serializer.getConstants().getFirst()).isEqualTo(5)` fail if `JPQLSerializer` still emits `Long` constants, and the exporter comparisons fail unless production code handles Hibernate 7.3's metamodel behavior.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden tests encode Hibernate 7.3's new constant and metamodel behavior, failing without Δc and passing after Δc's serializer/parameter fixes.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc edits `JPQLSerializer.java`, `HibernateUtil.java`, and `JPAUtil.java` to adapt production source to Hibernate 7.3 behavior.

## 7. Soundness concerns / notes
The exact extracted command is unavailable because the Maven harness command is generated in `test_state.py`, but its selected tests match the touched hidden test files.

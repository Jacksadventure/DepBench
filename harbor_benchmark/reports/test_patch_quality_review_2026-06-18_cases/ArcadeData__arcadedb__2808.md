# Test-patch audit — ArcadeData__arcadedb__2808

## 1. Task summary
- Folder: ArcadeData__arcadedb__2808
- Ecosystem: maven
- Upgrade: gremlin.version 3.7.4 -> 3.8.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: install `mvn ... -pl gremlin -am -DskipTests install`, then `mvn ... -pl gremlin -Dtest=GremlinTest#longOverflow test`

## 2. What is the breaking change?
TinkerPop/Gremlin 3.8.0 changes comparator internals and numeric overflow behavior. ArcadeDB's vendored/shadowed `GremlinValueComparator` must stop depending on `GremlinTypeErrorException`, throw a standard exception, and expose `comparable(...)` publicly for the new `Compare` access pattern.

## 3. What does Δt (test.patch) actually do?
It narrows wildcard imports in `GremlinTest` and updates `longOverflow`: `Long.MAX_VALUE + 1` is now expected to throw `ArithmeticException` containing `long overflow`, while explicit `BigInteger` summation remains valid.

## 4. Does Δt directly exercise the breaking change?
Yes, with a compile/build prerequisite. The install phase compiles the gremlin module against TinkerPop 3.8.0, which needs Δc's comparator compatibility changes. The focused test then checks the new long-overflow behavior under the upgraded Gremlin engine.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — P⊕Δm⊕Δt fails without the TinkerPop 3.8 comparator/source migration and P⊕Δm⊕Δc⊕Δt passes, with Δt also asserting the new overflow behavior.

## 6. Δc nature
REAL_SOURCE_REPAIR — edits `gremlin/src/main/java/org/apache/tinkerpop/gremlin/util/GremlinValueComparator.java` to match the TinkerPop 3.8 API/exception expectations.

## 7. Soundness concerns / notes
- The behavioral assertion is about Gremlin engine overflow, while part of Δc is required at compile/link time by comparator internals.
- The import cleanup in Δt is cosmetic, but the overflow assertion is substantive.

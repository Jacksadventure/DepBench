# Test-patch audit — lukas-krecan__JsonUnit__274

## 1. Task summary
- Folder: lukas-krecan__JsonUnit__274
- Ecosystem: maven
- Upgrade: assertj-core 3.16.1 -> 3.17.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE`

## 2. What is the breaking change?
AssertJ 3.17 changes failure-message rendering for iterable/list values and exposes JsonUnit's internal key-value node representation in assertion messages. JsonUnit needs a stable `toString()` for `Node.KeyValue` so its AssertJ-facing error messages remain readable and match the new assertion output.

## 3. What does Δt (test.patch) actually do?
Touches `tests/test-base/src/main/java/net/javacrumbs/jsonunit/test/base/AbstractAssertJTest.java` and `tests/test-moshi/src/test/java/net/javacrumbs/jsonunit/test/moshi/MoshiAssertJTest.java`. It updates expected failure text from `JsonList` to `ArrayList`, makes `testNotEqualTo` overrideable, and adds a Moshi-specific override asserting the new formatted message.

## 4. Does Δt directly exercise the breaking change?
Yes. The patched failure-message assertions exercise JsonUnit's AssertJ integration under the upgraded AssertJ renderer; without Δc, the Moshi `testNotEqualTo` message would use the old/default internal `KeyValue` object rendering instead of the expected JSON-like text.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — `P⊕Δm⊕Δt` should fail on the updated AssertJ message expectations, while Δc adds the missing `Node.KeyValue.toString()` representation needed for those assertions to pass.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc adds a production `toString()` implementation in `json-unit-core/src/main/java/net/javacrumbs/jsonunit/core/internal/Node.java`.

## 7. Soundness concerns / notes
- The verifier command is unextractable in metadata, but `test_state.py` targets the relevant `AbstractAssertJTest` and `MoshiAssertJTest` classes.
- The evidence is message-format compatibility rather than core JSON comparison behavior.

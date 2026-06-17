# Test-patch audit - hawtio__hawtio__3776

## 1. Task summary
- Folder: hawtio__hawtio__3776
- Ecosystem: maven
- Upgrade: jolokia-version 2.1.2 -> 2.2.1 (manifest uses 2.2.2)
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `mvn ... -pl hawtio-system -am ... -Dtest=ServletHelpersTest test` with an initial `test-compile` gate (extracted from `test_state.py`; batch metadata could not extract it)

## 2. What is the breaking change?
Jolokia 2.2.x removes or relocates `org.jolokia.server.core.util.NetworkUtil.replaceExpression`. `RBACRestrictor` imports `NetworkUtil` and calls `replaceExpression(...)`, so the upgraded `hawtio-system` module no longer compiles. Δc removes the import and uses the configured policy location string directly.

## 3. What does Δt (test.patch) actually do?
Touches `ServletHelpersTest` only, changing the JSON numeric expectation from `2` to `2L`. It does not reference `RBACRestrictor`, `NetworkUtil`, or policy-location expression replacement.

## 4. Does Δt directly exercise the breaking change?
Only indirectly through the verifier's compile gate. The test hunk itself is unrelated to the Jolokia `NetworkUtil` removal, but `test_state.py` first compiles `hawtio-system` (`test-compile`) and then runs `ServletHelpersTest`. On P+Δm+Δt, compilation fails before the test can run because `RBACRestrictor` still imports the removed Jolokia class. With Δc, the module compiles and the selected test passes.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the verifier observes a real post-upgrade compile failure without Δc and a pass with Δc. The hidden test edit is weak/unrelated, but the test command does witness the source break via Maven compilation.

## 6. Δc nature
REAL_SOURCE_REPAIR - a production Java class is adapted to the changed Jolokia API by removing `NetworkUtil.replaceExpression(...)`.

## 7. Soundness concerns / notes
- Δt is not semantically targeted at the breaking API; it adjusts JSON number typing in a different test.
- The witness relies on module compilation rather than a behavioral assertion around RBAC policy-location handling.

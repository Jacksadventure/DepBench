# Test-patch audit - airlift__airlift__1592

## 1. Task summary
- Folder: airlift__airlift__1592
- Ecosystem: maven
- Upgrade: io.airlift:airbase 312 -> 313
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `<could not extract>`; `test_state.py` runs `mvn ... -pl http-server -am -Dtest=TestHttpServerConfig test`

## 2. What is the breaking change?
The human summary says "Reenable server compression fixed in Jetty 12.1.2". Delta c changes the project default `HttpServerConfig.compressionEnabled` from `false` to `true`. This is a behavior/config policy change enabled by a dependency update, not an API incompatibility in `io.airlift:airbase` itself.

## 3. What does Delta t (test.patch) actually do?
`TestHttpServerConfig` changes the default expected value for `compressionEnabled` to `true`, changes the explicit property input from `"true"` to `"false"`, and expects the mapped config to be `false`.

## 4. Does Delta t directly exercise the breaking change?
It exercises the project default flip, not a dependency-caused compile or runtime break. `TEST(P+Delta m+Delta t)` fails because the project still defaults compression to `false`; that failure is independent of any removed method, changed type, or new runtime behavior in the upgraded dependency.

## 5. Coverage verdict
TESTS_OTHER_THING - the hidden test validates a desired configuration behavior change rather than witnessing a dependency breaking change.

## 6. Delta c nature
REAL_SOURCE_REPAIR - a production config default is changed in `HttpServerConfig.java`.

## 7. Soundness concerns / notes
This is a useful regression test for the human's policy decision, but it should not be counted as Level-1 dependency-break witness evidence.


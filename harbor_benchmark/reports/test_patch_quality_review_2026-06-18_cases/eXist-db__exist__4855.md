# Test-patch audit - eXist-db__exist__4855

## 1. Task summary
- Folder: eXist-db__exist__4855
- Ecosystem: maven
- Upgrade: jacoco-maven-plugin 0.8.8 -> 0.8.9
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `mvn ... -pl extensions/exquery/restxq -am ... -Dtest=DomEnhancingNodeProxyAdapterTest test` (extracted from `test_state.py`; batch metadata could not extract it)

## 2. What is the breaking change?
Although the task metadata names the JaCoCo plugin bump, the manifest patch also replaces the runtime/source dependency `cglib:cglib` with `net.bytebuddy:byte-buddy` in `exist-core` and `extensions/exquery/restxq`. The old production code imports `net.sf.cglib.proxy.*` and constructs CGLIB proxies, so after Δm those imports/classes are gone. The repair migrates proxy generation in `LocalXMLResource` and `DomEnhancingNodeProxyAdapter` to ByteBuddy and adds missing DOM node-type handling for CDATA/PI/comment cases.

## 3. What does Δt (test.patch) actually do?
Adds a new `DomEnhancingNodeProxyAdapterTest` under `extensions/exquery/restxq`. The test stores an XML document containing elements, attributes, text, a comment, CDATA, and a processing instruction, then asserts that `DomEnhancingNodeProxyAdapter.create(...)` returns proxies assignable to the expected W3C DOM interfaces and preserving node identity/values.

## 4. Does Δt directly exercise the breaking change?
Yes. The new test targets the exact adapter rewritten from CGLIB to ByteBuddy. On P+Δm+Δt, the module cannot compile because the old adapter still imports CGLIB classes no longer present after Δm; even if it compiled, the new CDATA/comment/PI assertions exercise behavior added by Δc. On P+Δm+Δc+Δt, the ByteBuddy adapter compiles and the new DOM-proxy test can run.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the hidden test suite fails without the ByteBuddy migration and passes with the production repair. The metadata/library label is noisy, but the bundled Δm/Δc/Δt combination witnesses the manifest-induced CGLIB-to-ByteBuddy source break.

## 6. Δc nature
REAL_SOURCE_REPAIR - production Java code migrates proxy generation from CGLIB to ByteBuddy in `LocalXMLResource` and `DomEnhancingNodeProxyAdapter`, and adds a missing `CDATA_SECTION_NODE` mapping. No test-only or docs-only repair.

## 7. Soundness concerns / notes
- The stated upgrade (`jacoco-maven-plugin`) is not the direct API whose break is tested; the manifest patch also changes CGLIB to ByteBuddy.
- Δt is strong for the actual source repair, but the task metadata should be treated as imprecise.

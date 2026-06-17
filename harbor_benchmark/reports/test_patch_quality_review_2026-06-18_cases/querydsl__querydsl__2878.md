# Test-patch audit - querydsl__querydsl__2878

## 1. Task summary
- Folder: querydsl__querydsl__2878
- Ecosystem: maven
- Upgrade: hibernate-search 4.2.0.Final -> 5.10.1.Final
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `<could not extract>`; `test_state.py` runs `mvn ... -Pall -pl querydsl-hibernate-search -am test`

## 2. What is the breaking change?
The upgrade moves the module from Hibernate Search 4 / Lucene 3 to Hibernate Search 5 / Lucene 5. The manifest switches `querydsl-lucene3` to `querydsl-lucene5` and `hibernate-search` to `hibernate-search-orm`, so production imports of `com.querydsl.lucene3.LuceneSerializer` no longer match the dependency graph.

## 3. What does Delta t (test.patch) actually do?
The tests migrate Hibernate 4 APIs to Hibernate 5 APIs: `AnnotationConfiguration` -> `Configuration`, transaction rollback checks use `TransactionStatus`, setup flushes deletions, and the test entity adds `@SortableField`.

## 4. Does Delta t directly exercise the breaking change?
Yes. With only Delta m and Delta t, the module still imports `com.querydsl.lucene3.LuceneSerializer` while the manifest now depends on `querydsl-lucene5`, so compilation fails. Delta c updates production imports in `AbstractSearchQuery` and `SearchSerializer` to `com.querydsl.lucene5.LuceneSerializer`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the new Hibernate Search/Lucene stack requires source imports to move to the Lucene 5 serializer, and the hidden tests compile and run that module.

## 6. Delta c nature
REAL_SOURCE_REPAIR - the oracle source patch changes production imports in the Hibernate Search integration.

## 7. Soundness concerns / notes
The manifest patch contains most transitive dependency convergence. The source-side witness is narrow but legitimate.


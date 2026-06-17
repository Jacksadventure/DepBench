# Test-patch audit — dadoonet__fscrawler__2342

## 1. Task summary
- Folder: dadoonet__fscrawler__2342
- Ecosystem: maven
- Upgrade: io.minio:minio 8.6.0 -> 9.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO (random control)
- test_cmd: `<could not extract>` (test_state.py did not yield a runnable command — verifier-config concern, see §7)

## 2. What is the breaking change?
Minio 9.0.0 dropped `java.security.InvalidKeyException` and `java.security.NoSuchAlgorithmException` from the `getObject`/`putObject`/`statObject` throw signatures (they are no longer declared checked exceptions), and changed the `stream(...)` parameter so the size/part-size literals must be `long` (`-1` int is now ambiguous / `object.length()` returns int where `long` is required). Catching the now-undeclared checked exceptions and passing int literals no longer compiles → Maven build failure across the S3 plugin and its tests.

## 3. What does Δt (test.patch) actually do?
Touches two **integration-test** files:
- `integration-tests/.../elasticsearch/FsCrawlerRestIT.java` — removes the `InvalidKeyException`/`NoSuchAlgorithmException` imports and drops them from the `catch (MinioException | InvalidKeyException | NoSuchAlgorithmException e)` clause (→ `catch (MinioException e)`); changes `-1` → `-1L` on the `.stream(..., -1)` argument.
- `plugins/fs-s3-plugin/src/test/java/.../FsS3PluginIT.java` — changes `object.length()` → `(long) object.length()` and `-1` → `-1L` on the `putObject` stream args.
No new test cases or assertions — purely compile-compatibility fixes mirroring Δc into the test sources.

## 4. Does Δt directly exercise the breaking change?
Yes, at compile level. On P⊕Δm⊕Δt the test files compile, but the production `FsS3Plugin.java` still catches the removed checked exceptions → the fs-s3-plugin module fails to compile → the build (and thus the test) FAILs; on P⊕Δm⊕Δc⊕Δt both production and test sources compile and the S3 integration tests can run → PASS. The ITs call `getObject`/`putObject` (the changed API surface), so they do exercise the repaired code path when executed.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — without Δc the production S3 plugin does not compile (removed checked exceptions + int/long), so TEST(P⊕Δm⊕Δt) FAILs; with Δc (and Δt applying the same compile fixes to the IT sources) it compiles and the integration tests pass.

## 6. Δc nature
REAL_SOURCE_REPAIR — `plugins/fs-s3-plugin/src/main/java/.../FsS3Plugin.java`: removes the `InvalidKeyException`/`NoSuchAlgorithmException` imports and prunes them from two `catch` clauses (`readFile`, `getFilesize`), leaving `catch (MinioException ...)`. No logic change beyond adapting exception handling to the narrowed Minio 9 signature.

## 7. Soundness concerns / notes
- **test_cmd could not be extracted** — the verifier command is unconfirmed from the bundle. Needs validation against the real `test_state.py`; if the verifier runs only unit tests (`mvn test`) the IT files in Δt may not even be compiled/run, though the production compile break still gives FAIL-without-Δc.
- Δt modifies `*IT.java` integration tests, which conventionally require a live Minio/S3 container; whether they actually execute (vs. are skipped) in the verifier is unknown. Compile-level witnessing holds regardless.
- Δt is a compile-fix "mirror" of Δc (same exception/long-literal changes applied to test sources) with no new behavioral assertions — a legitimate but shallow witness typical of API-signature breaks.
- Minor: one hunk also tightens `object.length()` → `(long) object.length()`, an overload-resolution fix rather than a behavior change.

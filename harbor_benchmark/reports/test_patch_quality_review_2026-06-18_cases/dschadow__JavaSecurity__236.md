# Test-patch audit — dschadow__JavaSecurity__236

## 1. Task summary
- Folder: dschadow__JavaSecurity__236
- Ecosystem: maven
- Upgrade: org.apache.shiro:shiro-core 1.13.0 -> 2.0.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE`

## 2. What is the breaking change?
Shiro 2 moves several classes to new packages and changes crypto/hash APIs. The old source imports `org.apache.shiro.util.ByteSource` and `org.apache.shiro.crypto.AesCipherService`, uses removed `DefaultHashService` setters, and treats decrypt results through the old `ByteSource` API.

## 3. What does Δt (test.patch) actually do?
Δt touches `crypto-shiro/src/test/java/de/dominikschadow/javasecurity/hash/SHA512Test.java` and `crypto-shiro/src/test/java/de/dominikschadow/javasecurity/symmetric/AESTest.java`. It updates the expected SHA512 iteration count from `1000000` to Shiro's new default `50000`, and rewrites the test import from `org.apache.shiro.codec.CodecSupport` to `org.apache.shiro.lang.codec.CodecSupport`.

## 4. Does Δt directly exercise the breaking change?
Yes. The patched tests compile against Shiro 2 package names and assert the new hashing behavior. Old source still imports removed Shiro 1 packages and configures removed hash-service properties, so the Maven test run should fail at compile time or on the iteration assertion until Δc updates imports and hash construction.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt is aligned with the Shiro 2 API/package and behavior changes, and the old Shiro 1-shaped source cannot satisfy it after the dependency bump.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc updates production Java files `SHA512.java` and `AES.java` for Shiro 2 imports, hash request construction, AES cipher package, and decrypt byte extraction.

## 7. Soundness concerns / notes
The extracted metadata marks the command as `TEST_CMD_UNEXTRACTABLE`, but `test_state.py` clearly runs the two relevant Maven tests; this is a bundle extraction limitation, not a patch-quality concern.

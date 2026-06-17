# Test-patch audit — OWASP__wrongsecrets__970

## 1. Task summary
- Folder: OWASP__wrongsecrets__970
- Ecosystem: maven
- Upgrade: org.linguafranca.pwdb:KeePassJava2 2.1.4 -> 2.2.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `mvn ... -Dtest=Challenge28Test test` with an install/test-compile setup phase

## 2. What is the breaking change?
The KeePassJava2 upgrade removes or stops providing the old SpongyCastle encoder classes the project had been importing. Code and tests need to use BouncyCastle (`org.bouncycastle.util.encoders.*`) instead of SpongyCastle (`org.spongycastle.util.encoders.*`).

## 3. What does Δt (test.patch) actually do?
Δt changes `Challenge28Test` from `org.spongycastle.util.encoders.Hex` to `org.bouncycastle.util.encoders.Hex`, keeping the hidden test compatible with the post-upgrade dependency set.

## 4. Does Δt directly exercise the breaking change?
Yes, through Maven compilation. The selected test is `Challenge28Test`, but Maven still compiles main sources. Without Δc, production `Challenge23.java` still imports `org.spongycastle.util.encoders.Base64` and `Hex`; after the KeePassJava2 bump those imports are no longer resolvable, so the build fails. Δc switches production code to BouncyCastle and the same post-upgrade test-side import compiles.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the failure is a dependency-induced compile break from removed SpongyCastle classes, repaired by Δc and mirrored by Δt.

## 6. Δc nature
MIXED — includes a real source repair (`Challenge23.java` SpongyCastle -> BouncyCastle), plus unrelated docs link churn and a `Challenge14` local-resource fallback.

## 7. Soundness concerns / notes
The compile witness is valid, but the PR bundles unrelated local-run and documentation changes. Agents could overfit to the broader patch if visible, but the hidden-test signal for the crypto import migration is sound.

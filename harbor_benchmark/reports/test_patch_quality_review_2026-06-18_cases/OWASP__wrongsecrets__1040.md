# Test-patch audit — OWASP__wrongsecrets__1040

## 1. Task summary
- Folder: OWASP__wrongsecrets__1040
- Ecosystem: maven
- Upgrade: com.github.spotbugs:spotbugs 4.7.3 -> 4.8.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `mvn -B -q -U -DfailIfNoTests=false -Dsurefire.failIfNoSpecifiedTests=false -Dspotless.skip=true -Dspotless.check.skip=true -Dformatter.skip=true -Dfmt.skip=true -Dcheckstyle.skip=true -Drat.skip=true -Denforcer.skip=true -Dmaven.javadoc.skip=true -Dgpg.skip=true -Dlicense.skip=true -Dtest=SecretLeakageControllerTest,Challenge1Test test` (with a fallback to full `mvn ... test` if the named tests do not match). Extracted from `tests/test_state.py` (the bundle's `test_cmd` line was `<could not extract>`).

## 2. What is the breaking change?
SpotBugs 4.8.0 introduces/activates stricter detectors: `DM_DEFAULT_CHARSET` flags `Files.readString(path)` without an explicit charset, and naming/`MS_SHOULD_BE_FINAL`-style findings flag the `Constants` interface name, the `Operation` enum name, and non-static `md5Hash`/`sha1Hash` fields. The human repair adds `StandardCharsets.UTF_8`, renames `Constants`→`WrongSecretsConstants` and `Operation`→`BinaryInstructionForFile`, and makes the hash fields `static final`.

## 3. What does Δt (test.patch) actually do?
- `src/test/java/org/owasp/wrongsecrets/SecretLeakageControllerTest.java`: changes the import `org.owasp.wrongsecrets.challenges.docker.Constants` → `…WrongSecretsConstants`, and rewrites `Constants.password` to `WrongSecretsConstants.password` in `spoil1()` and `solveChallenge1()`.
- `src/test/java/org/owasp/wrongsecrets/challenges/docker/Challenge1Test.java`: rewrites `Constants.password` → `WrongSecretsConstants.password` in `spoilerShouldRevealAnswer()` and `rightAnswerShouldSolveChallenge()`.
- No new assertions; the tests are updated to reference the renamed production class.

## 4. Does Δt directly exercise the breaking change?
Yes, at the compile level. `Challenge1Test.spoilerShouldRevealAnswer()` asserts `challenge.spoiler().isEqualTo(new Spoiler(WrongSecretsConstants.password))`. On P⊕Δm⊕Δt the symbol `WrongSecretsConstants` does not exist (production class is still `Constants`), so the test module fails to compile → `mvn test` FAILS. On P⊕Δm⊕Δc⊕Δt the class has been renamed to `WrongSecretsConstants` (Δc), the test compiles, and `Challenge1.spoiler()`/`answerCorrect()` return the same `"DefaultLoginPasswordDoNotChange!"` value → PASS.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt references the renamed `WrongSecretsConstants` class, producing a compile-level FAIL on P⊕Δm (symbol absent) and PASS on P⊕Δm⊕Δc (class renamed by Δc).

## 6. Δc nature
REAL_SOURCE_REPAIR — all changes are in `src/main/java/org/owasp/wrongsecrets/...` (Challenge9/10/11/12/16/17/18, Challenge1, BinaryExecutionHelper, TokenController, and the `Constants.java`→`WrongSecretsConstants.java` rename): `Files.readString(..., StandardCharsets.UTF_8)`, the `Constants`→`WrongSecretsConstants` and `Operation`→`BinaryInstructionForFile` renames, and `md5Hash`/`sha1Hash` → `static final`.

## 7. Soundness concerns / notes
- The witness is narrow and entirely at the compile level: only the `Constants`→`WrongSecretsConstants` rename is exercised by Δt. The actual SpotBugs-motivated repairs (`StandardCharsets.UTF_8` for `DM_DEFAULT_CHARSET`, `static final` for the hash fields, the `Operation` enum rename) are NOT directly tested — the two named JUnit tests only check `Challenge1` spoiler/answer behavior and the `/spoil-1`/`/challenge/1` endpoints.
- The verifier command skips SpotBugs/Spotless/Checkstyle/enforcer (`-Dspotless.skip=true -Dcheckstyle.skip=true -Denforcer.skip=true`), so the SpotBugs findings themselves are not the gate; the gate is the test-source compile against the renamed class.
- The `Constants`→`WrongSecretsConstants` rename is arguably a drive-by refactor co-evolved with its test references rather than a behavior break caused directly by spotbugs 4.8.0; the witness is real but reflects a rename, not a dependency behavioral change.

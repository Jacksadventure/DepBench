# Test-patch audit — OpenNMS__opennms__6191

## 1. Task summary
- Folder: OpenNMS__opennms__6191
- Ecosystem: maven
- Upgrade: hessian 3.1.5 -> 4.0.66
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE`

## 2. What is the breaking change?
No hessian breaking change is exercised by the patch. The human repair is `NMS-15640: Hide SCV credentials and other metadata secrets`, a security/CLI behavior change in `MetaCommand` that does not use hessian serialization.

## 3. What does Δt (test.patch) actually do?
It adds a new `core/mate/shell-commands/src/test/java/org/opennms/core/mate/commands/MetaCommandTest.java` with two tests. The tests build `MapScope` values containing usernames/passwords/secrets, call `MetaCommand.printScope(scope)`, and assert that password/secret values are replaced with `<output omitted>` while non-secret values remain visible.

## 4. Does Δt directly exercise the breaking change?
No. The representative assertions are `containsString("firstalias:password='<output omitted> @ GLOBAL'")` and `not(containsString("Pittsboro"))`, which exercise the new secret-redaction behavior in `MetaCommand.printScope`. They do not touch hessian 4.0.66 or any hessian API/serialization path.

## 5. Coverage verdict
TESTS_OTHER_THING — Δt witnesses an unrelated secret-redaction feature, not the hessian dependency bump.

## 6. Δc nature
REAL_SOURCE_REPAIR — `MetaCommand.java` is production source and changes runtime behavior by redacting SCV/password/secret metadata in command output.

## 7. Soundness concerns / notes
This is a clear drive-by feature/security fix in the same PR. An agent can pass by implementing the redaction behavior without understanding or adapting the hessian upgrade.


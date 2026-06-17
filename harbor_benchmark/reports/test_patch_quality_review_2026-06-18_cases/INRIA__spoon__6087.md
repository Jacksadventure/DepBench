# Test-patch audit — INRIA__spoon__6087

## 1. Task summary
- Folder: INRIA__spoon__6087
- Ecosystem: maven
- Upgrade: org.eclipse.jdt:org.eclipse.jdt.core 3.39.0 -> 3.40.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `mvn ... -Dtest=ElasticsearchStackoverflowTest test` (extracted bundle label was `TEST_CMD_UNEXTRACTABLE`)

## 2. What is the breaking change?
JDT 3.40.0 changes switch AST traversal/API details. `SwitchExpression#traverse` is removed, so Spoon has to route `SwitchStatement` instances that are actually `SwitchExpression` through the switch-expression visitor. JDT also changes the case-statement kind signal from `isExpr` to `isSwitchRule`.

## 3. What does Δt (test.patch) actually do?
- `src/test/java/spoon/test/reference/ElasticsearchStackoverflowTest.java`: removes `@GitHubIssue(issueNumber = 5977, fixed = false)` from `testStackOverflow`.
- No assertions are changed; the hidden test patch enables an existing regression test under the post-upgrade test command.

## 4. Does Δt directly exercise the breaking change?
Yes enough for a compile/runtime witness. The verifier targets `ElasticsearchStackoverflowTest`, which forces Maven to compile the main JDT integration code and run the enabled regression. On P⊕Δm⊕Δt, the old JDT integration still uses removed/changed JDT APIs (`SwitchExpression#traverse` behavior and `CaseStatement.isExpr`). Δc updates those source paths to the JDT 3.40 API and traversal behavior.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden test enables a real Spoon/JDT regression under the upgraded JDT dependency, and Δc repairs production JDT integration code needed for the test command to pass.

## 6. Δc nature
REAL_SOURCE_REPAIR — source-only changes in `JDTTreeBuilder.java` and `ParentExiter.java` adapt Spoon's JDT visitor and case-kind handling to JDT 3.40.0.

## 7. Soundness concerns / notes
Δt is minimal: it mainly un-skips an existing test rather than adding focused assertions. The repair is nevertheless a concrete source compatibility fix for the upgraded JDT API.

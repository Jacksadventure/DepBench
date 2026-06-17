# Test-patch audit - INRIA__spoon__6316

## 1. Task summary
- Folder: INRIA__spoon__6316
- Ecosystem: maven
- Upgrade: org.eclipse.jdt:org.eclipse.jdt.core 3.41.0 -> 3.42.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `<could not extract>`; `test_state.py` runs `mvn ... -Dtest=CtRecordTest test`

## 2. What is the breaking change?
JDT 3.42 changes internal compiler AST handling around compact record constructors and variable declarations. The old Spoon source imports `CompactConstructorDeclaration` and assumes compact-constructor parameters arrive as `Argument`; the repair switches to `constructorDeclaration.isCompactConstructor()`, traverses `protoArguments`, and accepts `RecordComponent` as an `AbstractVariableDeclaration`.

## 3. What does Delta t (test.patch) actually do?
`CtRecordTest.testMultipleParameterRecord()` now asserts generated record fields are initially implicit, then explicitly clears implicit flags so the existing field-printing assertions can run under the new model behavior.

## 4. Does Delta t directly exercise the breaking change?
Yes, through compilation and the record test path. With JDT 3.42, the old production code's internal JDT assumptions fail at compile time and/or during record model construction. The hidden `CtRecordTest` exercises the compact-record field/parameter behavior after the source has been migrated.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the upgraded JDT internal API/model behavior requires source changes before the hidden record test can compile and pass.

## 6. Delta c nature
REAL_SOURCE_REPAIR - production compiler integration code is updated in `JDTTreeBuilder`, `JDTTreeBuilderHelper`, and `ReferenceBuilder`.

## 7. Soundness concerns / notes
The dependency is reported generically as `version` in metadata, but the manifest hunk clearly upgrades `org.eclipse.jdt.core`. The witness is source-compile/model behavior, not dependency resolution.


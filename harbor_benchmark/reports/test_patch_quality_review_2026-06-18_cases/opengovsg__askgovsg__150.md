# Test-patch audit - opengovsg__askgovsg__150

## 1. Task summary
- Folder: opengovsg__askgovsg__150
- Ecosystem: npm_and_yarn
- Upgrade: typescript 4.2.3 -> 4.4.2
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest`

## 2. What is the breaking change?
TypeScript 4.4 makes catch-clause variables `unknown` under strict settings, so direct `error.message` / `err.message` access no longer type-checks without narrowing.

## 3. What does test.patch actually do?
`enquiry.service.spec.ts` changes a catch block from direct `error.message` access to `expect(error).toBeInstanceOf(Error)` followed by `if (error instanceof Error) { expect(error.message)... }`.

## 4. Does test.patch directly exercise the breaking change?
Partially. The hidden test fixes the same TypeScript 4.4 catch-variable issue on the test side. Delta_c fixes source-side catch blocks in enquiry, file, post, and tags controllers. With ts-jest in the project and `npx jest` as the verifier, these source files need the same narrowing when compiled/imported by the suite, but the visible Delta_t hunk itself does not add a behavioral assertion for the controller repairs.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - a compile/type witness for the TypeScript 4.4 catch-variable migration, though it is narrow and mostly type-level.

## 6. Delta_c nature
REAL_SOURCE_REPAIR - source controller catch blocks are narrowed with `instanceof Error` before reading `.message`.

## 7. Soundness concerns / notes
The oracle is weaker than a runtime behavior test. If ts-jest were configured in transpile-only mode or the controller files were not imported by the executed tests, this could collapse into an unwitnessed type-only repair.

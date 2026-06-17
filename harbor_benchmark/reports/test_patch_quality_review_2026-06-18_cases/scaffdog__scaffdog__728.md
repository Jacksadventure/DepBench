# Test-patch audit — scaffdog__scaffdog__728

## 1. Task summary
- Folder: scaffdog__scaffdog__728
- Ecosystem: npm_and_yarn
- Upgrade: chalk 4.1.0 -> 5.3.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `pnpm test -- src/index.test.ts`

## 2. What is the breaking change?
chalk 5 removes the old CommonJS/default-instance patterns used here: `new chalk.Instance(...)` is replaced by `new Chalk(...)`, and the chalk template-tag syntax is no longer used. Imports must use the named `Chalk` class where a separate instance is needed.

## 3. What does Δt (test.patch) actually do?
`packages/@scaffdog/error/src/index.test.ts` imports `{ Chalk }` from `chalk`, reorders the Vitest import, and changes `new chalk.Instance({ level: 1 })` to `new Chalk({ level: 1 })`.

## 4. Does Δt directly exercise the breaking change?
Yes. The hidden test imports the same package whose source still constructs `new chalk.Instance(...)` without Δc. Under chalk 5, that old source path fails; Δc migrates both the error package and CLI formatting code to `Chalk` and direct style-function calls.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — P⊕Δm⊕Δt fails on the chalk 5 API change in source, and P⊕Δm⊕Δc⊕Δt passes after the source migration.

## 6. Δc nature
REAL_SOURCE_REPAIR — source replaces `chalk.Instance` with `Chalk`, removes chalk template-tag usage, and rewrites colored CLI strings to chalk 5-compatible method calls.

## 7. Soundness concerns / notes
- The verifier command targets the error package test; Δc also includes broader CLI source fixes that are not all exercised by this command.

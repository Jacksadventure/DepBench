# Test-patch audit - paularmstrong__onerepo__595

## 1. Task summary
- Folder: paularmstrong__onerepo__595
- Ecosystem: npm_and_yarn
- Upgrade: prettier 3.1.1 -> 3.2.4
- test_cmd: `npx vitest run modules/file --reporter=verbose`

## 2. What is the breaking change?
Prettier 3.2 formats JSON/JSONC project references with trailing commas. Existing code read `tsconfig.json` with `JSON.parse`, so JSONC comments and trailing commas in formatted tsconfig files became a runtime problem. Delta c adds JSONC-aware reading via `file.readJson(..., { jsonc: true })` and improves comment/trailing-comma stripping.

## 3. What does Delta t do?
Delta t adds many `readJson` tests for JSONC comments, escaped strings, line endings, and trailing commas. It also updates a fixture tsconfig to include a trailing comma.

## 4. Does Delta t directly exercise the breaking change?
Yes. The hidden tests run the `modules/file` package and directly exercise the JSONC parser behavior needed after Prettier formats tsconfig files with comments/trailing commas. Without Delta c, `readJson(..., { jsonc: true })` does not handle these cases correctly; with Delta c, it does.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE

## 6. Delta c nature
MIXED

## 7. Soundness concerns / notes
- Delta c contains large formatter churn across many `tsconfig.json` files in addition to the real `strip-json-comments` and TypeScript-plugin source changes.
- The test target focuses on `modules/file`, which is the core parser repair and is appropriate for this task.

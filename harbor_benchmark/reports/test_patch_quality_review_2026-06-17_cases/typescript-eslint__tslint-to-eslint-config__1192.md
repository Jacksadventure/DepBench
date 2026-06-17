# Test-patch audit — typescript-eslint__tslint-to-eslint-config__1192

## 1. Task summary
- Folder: typescript-eslint__tslint-to-eslint-config__1192
- Ecosystem: npm_and_yarn
- Upgrade: typescript 4.3.5 -> 4.4.2
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest src/utils.test.ts --runInBand`

## 2. What is the breaking change?
TypeScript 4.4 introduced stricter typing of `catch` clause variables (`useUnknownInCatchVariables`), so caught values are `unknown` rather than `any`/`Error`. The repair introduces an `asError(error: unknown)` helper that normalizes caught values to `Error`, and routes all catch blocks through it (so `.stack`/`.message` access stays type-safe).

## 3. What does Δt (test.patch) actually do?
- `src/utils.test.ts`: adds a new `describe("asError", ...)` block with two unit tests:
  - `it("returns the input when the input is an error")` — `asError(new Error("Oh no!"))` returns the same reference (`toBe`).
  - `it("returns an equivalent error when the input is not an error")` — `asError("Oh no!")` returns `new Error("Oh no!")` (`toEqual`).
  - Also adds `asError` to the import list from `./utils`.
- No other test files touched; no integration tests for the catch-block call sites.

## 4. Does Δt directly exercise the breaking change?
Partially. The new tests import `asError` from `./utils`; on P⊕Δm (no Δc) `asError` does not exist, so the import fails and the test errors out → FAIL. On P⊕Δm⊕Δc `asError` exists and both assertions pass. So the fail/pass gate holds, but it is exercised through the *existence* of the helper rather than through the actual TS-4.4 catch-typing behavior at the call sites (`fsFileSystem.ts`, `main.ts`, `findRawConfiguration.ts`, `findReportedConfiguration.ts`).

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the test fails without Δc (missing `asError` export → import error) and passes with Δc; the helper is the core of the human's TS-4.4 catch-typing repair, though the witness is narrow.

## 6. Δc nature
REAL_SOURCE_REPAIR — adds `asError` to `src/utils.ts` and applies it in `src/adapters/fsFileSystem.ts`, `src/cli/main.ts`, `src/input/findRawConfiguration.ts`, `src/input/findReportedConfiguration.ts`; also rewrites `src/adapters/exec.stubs.ts` (`mockRejectedValue(Promise.resolve(new Error(...)))` → `mockRejectedValue(new Error(...))`) and switches `fsFileSystem.ts` to `fs.promises` + `asError`.

## 7. Soundness concerns / notes
- Leaky/partial oracle: an agent can satisfy the verifier by adding ONLY `export const asError = (error: unknown) => (error instanceof Error ? error : new Error(\`${error}\`));` to `utils.ts` without touching the other 5 files. The actual catch-block migrations are not exercised.
- TS 4.4's `useUnknownInCatchVariables` is opt-in (not a default breaking change), so without the compiler flag the source would still compile without `asError`; the witness therefore comes from the test's import dependency, not from a real type error.
- `test_cmd` is scoped to `src/utils.test.ts` only — narrow but valid.

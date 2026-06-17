# Test-patch audit — ktsn__capture-all__12

## 1. Task summary
- Folder: ktsn__capture-all__12
- Ecosystem: npm_and_yarn
- Upgrade: prettier 1.19.1 -> 2.0.5
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx prettier --list-different "{src,scripts,test}/**/*.{js,ts}"`

## 2. What is the breaking change?
There is no semantic dependency breaking change under test. The upgrade changes Prettier's formatting output and the verifier checks whether files match that formatting.

## 3. What does Δt (test.patch) actually do?
- Reformats `test/index.spec.ts` and `test/setup.ts` with Prettier 2 style.
- Changes are trailing commas and parenthesized arrow parameters only.
- No assertions or runtime behavior are changed.

## 4. Does Δt directly exercise the breaking change?
No. The verifier is explicitly `prettier --list-different`, so it only checks formatting. Δc similarly reformats `src/index.ts` and `src/stream.ts`; it does not repair production behavior.

## 5. Coverage verdict
TESTS_OTHER_THING — the task is a formatting conformance check, not a dependency breaking-change witness.

## 6. Δc nature
FORMATTER_LINT_CHURN — Δc is Prettier 2 reformatting only.

## 7. Soundness concerns / notes
This case should be excluded from witnessed breaking-change counts. It is useful only as a formatter-migration example.

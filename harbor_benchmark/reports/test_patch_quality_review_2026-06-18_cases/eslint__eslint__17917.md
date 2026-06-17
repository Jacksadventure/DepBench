# Test-patch audit — eslint__eslint__17917

## 1. Task summary
- Folder: eslint__eslint__17917
- Ecosystem: npm_and_yarn
- Upgrade: glob 7.1.6 -> 10.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `node Makefile mocha`

## 2. What is the breaking change?
glob v10 changes the CommonJS surface from callback/promisified default usage to named `glob` returning promises, and no longer supports the old `nonull` behavior used to pass unmatched patterns through as filenames. The tool must import `{ glob }`, await it directly, and implement its own no-match error.

## 3. What does Δt (test.patch) actually do?
Δt touches `tests/tools/check-rule-examples.js`. It normalizes OS-dependent path prefixes in the bad-examples stderr assertion and changes the non-existing file test to expect `No files found that match the specified patterns.\n` instead of an ENOENT report for a nonull-expanded filename.

## 4. Does Δt directly exercise the breaking change?
Yes. The no-match assertion directly targets the removal of `nonull` behavior, and the full mocha suite exercises `tools/check-rule-examples.js` using the new promise-returning `glob` API.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — P⊕Δm⊕Δt fails because the old promisified `glob`/`nonull` implementation is incompatible with glob 10 expectations, while P⊕Δm⊕Δc⊕Δt passes after the tool source is migrated.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc updates `tools/check-rule-examples.js` to import `{ glob }`, call it as a promise, remove `promisify`, and explicitly handle unmatched patterns.

## 7. Soundness concerns / notes
- This is a tool-script repair rather than ESLint runtime core behavior, but it is still a concrete source compatibility repair for the upgraded dependency.

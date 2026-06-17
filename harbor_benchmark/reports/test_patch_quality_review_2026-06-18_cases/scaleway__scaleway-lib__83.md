# Test-patch audit - scaleway__scaleway-lib__83

## 1. Task summary
- Folder: scaleway__scaleway-lib__83
- Ecosystem: npm_and_yarn
- Upgrade: query-string 6.14.1 -> 7.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `yarn jest packages/use-query-params --colors=false`

## 2. What is the breaking change?
`query-string` 7 changes stringification behavior around arrays containing `null`, `undefined`, and empty strings under the project's comma array format. `useQueryParams` needs to pass `skipEmptyString: true` and `skipNull: true` so the browser query string omits empty/null entries while the in-memory query params preserve the caller-provided array.

## 3. What does Δt (test.patch) actually do?
Adds tests in `packages/use-query-params/src/__tests__/index.js` for setting query params with an array containing values, `null`, `undefined`, and `''`, expecting the URL search string `?names=John,Jane`. It also adds a read-side test for an existing comma array with empty positions.

## 4. Does Δt directly exercise the breaking change?
Yes. The new write-side assertion fails without Δc because the upgraded stringifier does not produce the expected compact comma list unless empty strings and nulls are skipped. With Δc adding the two query-string options, the new array tests pass.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - Δt directly covers query-string 7 array/null/empty serialization behavior and fails without the production option changes.

## 6. Δc nature
REAL_SOURCE_REPAIR - the production hook's `stringify(...)` options are updated for the new query-string behavior.

## 7. Soundness concerns / notes
- The read-side added test checks existing parsing behavior and is less tied to Δc, but the write-side URL assertion is a direct witness.

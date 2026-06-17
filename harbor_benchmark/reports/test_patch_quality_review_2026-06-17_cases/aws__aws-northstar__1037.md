# Test-patch audit — aws__aws-northstar__1037

## 1. Task summary
- Folder: aws__aws-northstar__1037
- Ecosystem: npm_and_yarn
- Upgrade: ws 7.5.9 -> 7.5.10
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `yarn jest src/components/FileUpload`

## 2. What is the breaking change?
The manifest only bumps `ws` (a websocket lib) 7.5.9 -> 7.5.10, a trivial patch release that does not affect date formatting. The actual Δc/Δt concern an unrelated feature: `getDisplayLastModified` gains an optional `locales` argument so `date.toLocaleString(locales)` produces deterministic en-US output. There is no ws-induced break; the manifest appears misattributed (drive-by lockfile bump alongside a date-locale feature PR).

## 3. What does Δt (test.patch) actually do?
- `packages/ui/src/components/FileUpload/index.test.tsx`: removes the assertion `expect(screen.getByText('Last modified: 1/22/2021, 12:27:59 AM')).toBeVisible();` (a deletion, cannot cause failure).
- `packages/ui/src/components/FileUpload/utils/getDisplayLastModified/index.test.ts`: changes both calls from `getDisplayLastModified(date)` to `getDisplayLastModified(date, 'en-US')`, keeping the same expected string `'Last modified: 1/1/2022, 1:01:00 AM'`.

## 4. Does Δt directly exercise the breaking change?
Not a dependency break. The Δt exercises the new `locales` signature that Δc introduces:
```
expect(getDisplayLastModified(date, 'en-US')).toBe('Last modified: 1/1/2022, 1:01:00 AM');
```
On P⊕Δm (original 1-arg signature), this would only fail if the jest transform type-checks (TS2554: Expected 1 arguments, got 2) or if the container locale is not en-US (`date.toLocaleString()` default). With babel-only/no-typecheck in an en-US container it would pass without Δc. The ws upgrade itself is not exercised at all.

## 5. Coverage verdict
TESTS_OTHER_THING — Δt tests a date-locale formatting feature (the `locales` param) that Δc introduces, which is entirely unrelated to the ws 7.5.9 -> 7.5.10 upgrade.

## 6. Δc nature
MIXED — `getDisplayLastModified/index.ts` is a REAL_SOURCE_REPAIR (adds `locales?: string` param), but it is bundled with unrelated `.nvmrc` (16.16 -> 18.20) and `scripts/build.sh` (memory 1000000 -> 1100000) changes; none relate to ws.

## 7. Soundness concerns / notes
Strong misattribution concern: Δm (ws patch bump) has no causal link to Δc/Δt (date-locale feature + node/build infra). The "witness," if any, is an artifact of the test's own new 2-arg call signature (TS type-check) or locale dependence, not a dependency break. Should be re-examined for the known v2 misattribution issue; candidate for quarantine or re-rooting to the actual feature PR.

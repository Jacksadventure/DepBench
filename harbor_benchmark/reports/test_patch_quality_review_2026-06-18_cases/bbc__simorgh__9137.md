# Test-patch audit — bbc__simorgh__9137

## 1. Task summary
- Folder: bbc__simorgh__9137
- Ecosystem: npm_and_yarn
- Upgrade: `@types/jest` 26.0.24 -> 29.5.2 (labeled library); manifest.patch actually bumps the whole Jest stack together — `jest` 26.6.3→29.6.1, `babel-jest` 26.6.3→29.6.1, `jest-environment-jsdom` 26.6.2→29.6.1, `ts-jest` 26.5.6→29.1.1, `@types/jest` 26.0.24→29.5.2.
- Flagged in problematic_prs_review_2026-06-10.md: YES (no_code_pass)
- test_cmd: `CI=true yarn jest --ci --runInBand --env=jsdom --colors --runTestsByPath src/app/legacy/psammead/psammead-locales/moment/ur.test.js`

## 2. What is the breaking change?
The PR is a Jest 26 → 29 migration. Jest 29's `pretty-format` serializer changed snapshot output (`Object {`→`{`, `Array [`→`[`), inline-snapshot escaping changed (`rel=\"preload\"`→`rel="preload"`), the default test environment switched away from jsdom (requiring `testEnvironment: 'jsdom'`), `jest-environment-jsdom`'s export moved to `.TestEnvironment`, `jest-environment` config moved from `config.testEnvironmentOptions` to `config.projectConfig.testEnvironmentOptions`, `ts-jest/utils`'s `pathsToModuleNameMapper` was re-exported from `ts-jest`, and Jest 29 no longer ships `setImmediate` so a polyfill is needed. None of this is a production-source-API break; it is a test-runner / snapshot-format migration.

## 3. What does Δt (test.patch) actually do?
Δt touches 10 test files. 9 of them are real Jest-29 inline-snapshot updates (`Object {`→`{`, escape changes) — `.storybook/buildFontPreloads.test.js`, `scripts/bundleSize/getBundleData.test.js`, `src/app/components/ATIAnalytics/{atiUrl,beacon,index}.test.{ts,tsx}`, `psammead-section-label/src/index.test.jsx`, `src/app/lib/seoUtils/getItemList/index.test.ts`, `src/app/lib/utilities/episodeAvailability/index.test.js`, `src/app/routes/index.test.jsx`. The 10th — `src/app/legacy/psammead/psammead-locales/moment/ur.test.js` — is a **drive-by**: it updates the expected Urdu month-name strings in a moment.js locale test (`مار چ`→`مارچ`, `اپريل`→`اپریل`, `مئ`→`مئی`) and deletes the `format month` test case. This reflects an upstream moment `ur` locale data fix and has nothing to do with Jest 29.

## 4. Does Δt directly exercise the breaking change?
No. The verifier runs **only** `ur.test.js` (see test_cmd), which tests `moment(input,'MMMM').month()` for Urdu month names — no snapshots, no Jest-29 API. Neither Δm (Jest stack bump) nor Δc (snapshots + config) touches moment or its locale files, so the pass/fail of `ur.test.js` is determined entirely by the moment version already pinned at the base SHA, independent of both Δm and Δc. The 9 Δt files that *would* witness the Jest-29 snapshot-format breakage are never executed by the verifier.

## 5. Coverage verdict
**UNWITNESSED** — Δt (as executed: `ur.test.js` only) passes on P⊕Δm alone because it exercises moment locale data that neither Δm nor Δc changes, consistent with the task's `no_code_pass` flag.

## 6. Δc nature
**MIXED** — 89 of 93 files in Δc are `__snapshots__/*.snap` regenerations (`Object {`→`{`, `Array [`→`[`); the remaining 4 are test/config infra: `jest.config.js` (adds `testEnvironment: 'jsdom'`), `src/testHelpers/setupTests.js` (`setImmediate` polyfill), `ws-nextjs-app/jest.config.ts` (`ts-jest/utils`→`ts-jest` import), `src/integration/integrationTestEnvironment.js` (`.TestEnvironment` export + `projectConfig.testEnvironmentOptions`). Zero production `src/app` source is repaired.

## 7. Soundness concerns / notes
- **Verifier targets the wrong test.** test_cmd runs a single moment-locale test (`ur.test.js`) that is a drive-by unrelated to the Jest/@types/jest upgrade. The 9 Δt files that actually witness the Jest-29 snapshot-format breakage are never run, so the benchmark cannot detect whether the agent performed the real Jest-29 migration.
- **Double-unwitnessed.** Even on its own terms, `ur.test.js` passes on P⊕Δm without Δc (moment locale data is untouched by both Δm and Δc), matching the `no_code_pass` flag — this is a Level-2 / latent task, not a witnessed Level-1 breaking change.
- **Δc contains no production source repair.** It is 89 snapshot files + 4 test/config-infra files. An agent that does the "right" Jest-29 migration still gets graded only on a moment month-name test it cannot influence.
- **Quarantine recommended.** This task should remain in the Level-2 / `no_code_pass` quarantine bucket and be excluded from the main witnessed benchmark; at minimum the test_cmd should be retargeted to one of the 9 snapshot-format test files if a witnessed variant is desired (though that would itself drift toward a snapshot-churn task rather than a semantic repair).

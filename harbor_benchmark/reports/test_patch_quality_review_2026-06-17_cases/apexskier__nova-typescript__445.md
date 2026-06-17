# Test-patch audit — apexskier__nova-typescript__445

## 1. Task summary
- Folder: apexskier__nova-typescript__445
- Ecosystem: npm_and_yarn
- Upgrade: typescript 4.7.4 -> 4.9.4
- Flagged in problematic_prs_review_2026-06-10.md: NO (random control)
- test_cmd: `yarn test`

## 2. What is the breaking change?
TypeScript 4.8/4.9 added new optional fields to the library's `ts.UserPreferences` type (e.g. `autoImportFileExcludePatterns: string[]`, `disableLineTextInReferences`, `includeInlayVariableTypeHintsWhenTypeMatchesName`). In `src/tsUserPreferences.ts` the `keys` object is typed `{ [k in keyof UserPreferences]: ... } & Record<keyof UserPreferences, string>`, i.e. it must enumerate **every** key of `UserPreferences`. After the upgrade the object is missing the new keys → a TypeScript compile error (missing required properties), which fails the ts-jest compilation of the test. A secondary change: `string[]` preferences require a new `"stringArray"` branch in the conditional type.

## 3. What does Δt (test.patch) actually do?
Touches one file: `src/tsUserPreferences.test.ts`. It (a) bumps the expected listener-registration count `toBeCalledTimes(29)` → `toBeCalledTimes(32)`, and (b) adds the three new keys (`autoImportFileExcludePatterns`, `disableLineTextInReferences`, `includeInlayVariableTypeHintsWhenTypeMatchesName`) to four expected-key arrays/snapshots (globalConfigKeys list, the global config object, the workspace config object, etc.). No new test cases beyond the count/key-list updates; no fixtures.

## 4. Does Δt directly exercise the breaking change?
Yes. Representative assertion: `expect(nova.config.onDidChange).toBeCalledTimes(32)`. On P⊕Δm⊕Δt (Δt expects 32 listeners) the un-fixed source still registers only 29 keys (and also fails to type-check) → the assertion fails; on P⊕Δm⊕Δc⊕Δt the three new keys are added in Δc so 32 listeners are registered and the type error is resolved → passes. The new keys are also asserted by name in the expected-key arrays, tying the test directly to the Δc additions.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt's count+key assertions fail without Δc (missing keys → type error + 29≠32) and pass with Δc; the break is a genuine compile-time consequence of the typescript library upgrade.

## 6. Δc nature
REAL_SOURCE_REPAIR — the necessary fix is in `src/tsUserPreferences.ts`: adds a `string[] | undefined → "stringArray"` conditional branch and the three new key entries to `keys`. Drive-bys: `typescript.novaextension/extension.json` (declarative Nova config schema exposing the same new preferences) and a one-line comment in `typescript.novaextension/run.sh`; these do not affect the test but travel with the same PR.

## 7. Soundness concerns / notes
- The witness is structural (key-count / key-name enumeration) rather than behavioral, but it is a legitimate compile+runtime break induced by the typescript library's expanded `UserPreferences` type, and the test directly checks the affected surface.
- `extension.json` schema additions are not exercised by `tsUserPreferences.test.ts` (which only tests `setupUserPreferences`/`keys`), so they are non-load-bearing for the verdict but correctly classified as part of the human repair.
- Sound witnessed task; no quarantine needed.

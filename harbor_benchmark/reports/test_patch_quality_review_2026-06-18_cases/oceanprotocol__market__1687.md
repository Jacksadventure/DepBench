# Test-patch audit — oceanprotocol__market__1687

## 1. Task summary
- Folder: oceanprotocol__market__1687
- Ecosystem: npm_and_yarn
- Upgrade: eslint-plugin-testing-library 5.5.1 -> 5.6.4 (labeled; Δm also upgrades Jest 28 -> 29, Storybook 6.5.x, @testing-library/react 13.3 -> 13.4, TypeScript 4.7 -> 4.8, urql, web3, and many lockfile packages)
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest -c .jest/jest.config.js --ci --runInBand src/components/@shared/atoms/Alert/index.test.tsx src/components/@shared/atoms/Badge/index.test.tsx src/components/@shared/atoms/Blockies/index.test.tsx src/components/@shared/atoms/Container/index.test.tsx src/components/@shared/atoms/Copy/index.test.tsx src/components/@shared/atoms/Loader/index.test.tsx src/components/@shared/atoms/Logo/index.test.tsx src/components/@shared/atoms/Status/index.test.tsx src/components/@shared/atoms/Time/index.test.tsx`

## 2. What is the breaking change?
There is no clear dependency breaking change witnessed by the verifier. The labeled dependency is an ESLint plugin, but the verifier runs Jest component tests rather than lint; the manifest also bundles a broad dev/runtime dependency refresh, including removal of Storybook storyshots and a Jest 29 upgrade.

## 3. What does Δt (test.patch) actually do?
Δt deletes `.storybook/storyshots.test.tsx`, adds simple render-smoke tests for eight atom components (`Alert`, `Badge`, `Blockies`, `Container`, `Loader`, `Logo`, `Status`, `Time`), and rewrites `Copy/index.test.tsx` to render `Copy` directly instead of the story `Default` export. Most new atom tests import a new shared helper from `../../../../../.jest/testRender`.

## 4. Does Δt directly exercise the breaking change?
No. The representative new assertions are `testRender(<Alert text="Alert text" state="info" />)` and similar atom render checks, but `testRender` is introduced only by Δc in `.jest/testRender.ts`; without that helper, P⊕Δm⊕Δt can fail because the hidden tests import a file that does not exist. The Δc production edits in `src/components/@shared/FormInput/index.tsx` and `src/components/Home/Bookmarks.tsx` are not on the verifier's atom-test path, and the labeled `eslint-plugin-testing-library` upgrade is not exercised by a Jest runtime command.

## 5. Coverage verdict
TESTS_OTHER_THING — Δt mostly replaces Storybook storyshots with atom smoke tests and depends on a helper added by Δc, so the fail/pass gate is test-infrastructure/circular-oracle behavior rather than evidence of a source repair for the labeled dependency upgrade.

## 6. Δc nature
MIXED — Δc adds the test helper `.jest/testRender.ts`, changes `tsconfig.json` to include `.jest`, and also makes two small source logic fixes in `src/components/@shared/FormInput/index.tsx` and `src/components/Home/Bookmarks.tsx`; the source fixes are not exercised by the verifier command.

## 7. Soundness concerns / notes
- Mislabeled / over-broad Δm: `eslint-plugin-testing-library` is only one of many upgrades, and the verifier does not run lint, so it cannot witness an ESLint-plugin breaking change.
- Circular oracle risk: most new tests import `.jest/testRender`, which is hidden in Δc rather than supplied by Δt, so an agent must add test infrastructure to satisfy the hidden tests.
- The actual source-code edits compare objects/arrays by content instead of identity, but the selected atom tests do not cover `FormInput` or `Bookmarks`; an agent could pass by adding only the helper and ignoring those source repairs.

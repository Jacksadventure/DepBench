# Test-patch audit — ampproject__amp-wp__6853

## 1. Task summary
- Folder: ampproject__amp-wp__6853
- Ecosystem: npm_and_yarn
- Upgrade: eslint-plugin-jest 25.0.5 -> 26.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest --config=tests/js/jest.config.js assets/src/block-validation/components/with-amp-toolbar-button/test/add-toolbar-button-to-block.js assets/src/block-validation/hooks/test/use-amp-document-toggle.js assets/src/block-validation/hooks/test/use-errors-fetching-state-changes.js assets/src/components/plugins-context-provider/test/use-normalized-plugins-data.js assets/src/components/themes-context-provider/test/use-normalized-themes-data.js`

## 2. What is the breaking change?
The Δc/Δt do NOT relate to eslint-plugin-jest at all. The real witnessed change is a **drive-by semantic change**: `useNormalizedPluginsData` and `useNormalizedThemesData` now initialize state with `{}` (object) instead of `[]` (array) — i.e. the hooks' return type changed from array to keyed-object. The Δt updates the two corresponding test files' assertions from array shape to object shape.

## 3. What does Δt (test.patch) actually do?
- `test/use-normalized-plugins-data.js` & `test/use-normalized-themes-data.js`: rewrite test scaffolding (remove module-level `returnValue`, introduce `setup()` helper), rename `"returns empty an array…"` -> `"returns an empty object…"`, and change assertions `expect(returnValue).toHaveLength(0)` -> `expect(normalizedPluginsData).toStrictEqual({})` and `toStrictEqual({...keyed...})`. **These are real semantic assertion changes.**
- `test/add-toolbar-button-to-block.js`: removes `toolbarButtonWasRendered` global, swaps to `container.querySelector('#amp-toolbar-button')` DOM check — semantically equivalent refactor.
- `test/use-amp-document-toggle.js` & `test/use-errors-fetching-state-changes.js`: remove `returnValue` global, render hook output into a component and query the DOM (`textContent`, `button.click()`) — semantically equivalent refactor (e.g. `expect(returnValue.isAMPEnabled).toBe(false)` -> `expect(container.querySelector('button').textContent).toBe('disabled')`).

## 4. Does Δt directly exercise the breaking change?
Yes, via the two normalized-data test files. Representative assertion in `use-normalized-plugins-data.js`:
```
- expect( returnValue ).toHaveLength( 0 );
+ expect( normalizedPluginsData ).toStrictEqual( {} );
```
On P⊕Δm (source still `useState([])`, hook returns an array) this `toStrictEqual({})` fails; on P⊕Δm⊕Δc (source `useState({})`, hook returns object) it passes. The other three files' refactors are behavior-preserving and pass either way.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the array→object assertion change in the two normalized-data tests fails on P⊕Δm (old source returns array) and passes on P⊕Δm⊕Δc (new source returns object); flagged=False corroborates.

## 6. Δc nature
REAL_SOURCE_REPAIR — `assets/src/components/plugins-context-provider/use-normalized-plugins-data.js` and `assets/src/components/themes-context-provider/use-normalized-themes-data.js` change `useState([])` -> `useState({})` (and the downstream normalization logic already produced a keyed object, so only the initial-state placeholder changes). Genuine semantic source edit, two files.

## 7. Soundness concerns / notes
- **Mislabeled task**: the witnessed breaking change (hook return type array→object) is a **drive-by code change in the same PR**, NOT caused by the `eslint-plugin-jest 25 -> 26` upgrade. eslint-plugin-jest is a lint plugin and has no runtime effect on jest assertions; the test_cmd is `jest` (runtime), not `eslint`.
- The three semantically-equivalent test refactors (returnValue→DOM-query pattern in add-toolbar-button, use-amp-document-toggle, use-errors-fetching-state-changes) are likely the actual eslint-plugin-jest-26-driven lint compliance, but they are behavior-preserving and invisible to the jest test_cmd. So the dependency's real breaking change is not what's being witnessed.
- Net: the harness correctly measures "can the agent reproduce the array→object migration," but the task framing ("eslint-plugin-jest upgrade caused this") is misleading — an agent following the instruction literally would look for jest/lint issues and miss the real repair.

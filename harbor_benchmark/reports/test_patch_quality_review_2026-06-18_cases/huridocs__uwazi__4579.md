# Test-patch audit — huridocs__uwazi__4579

## 1. Task summary
- Folder: huridocs__uwazi__4579
- Ecosystem: npm_and_yarn
- Upgrade: helmet 3.23.3 -> 5.0.2, with react-helmet 5.2.0 -> 6.1.0 in the manifest patch
- test_cmd: `node --max-http-header-size 20000 ./node_modules/.bin/jest --config app/jest.client.config.js --testPathPattern='(PageViewer|SemanticSearchResults)\\.spec'`

## 2. What is the breaking change?
`react-helmet` v6 changes the component import/usage pattern: source code must import `{ Helmet }` and render title as a child (`<Helmet><title>...</title></Helmet>`) rather than relying on the old default import and `title` prop. `helmet` v5 also changes server middleware defaults, requiring explicit disabling of CSP and COEP for this app.

## 3. What does Δt (test.patch) actually do?
Δt updates `PageViewer.spec.js` to import `{ Helmet }` and changes the assertion from `component.find(Helmet).props().title` to `component.find(Helmet).find('title').text()`.

## 4. Does Δt directly exercise the breaking change?
Yes. The hidden test expects the post-v6 `react-helmet` shape in the rendered `PageViewer`. On P⊕Δm⊕Δt, the old source still imports/uses Helmet with the old default/prop style and fails this assertion or module shape. Δc updates the source to named imports and child `<title>` nodes, so the test passes.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt directly checks the rendered Helmet title shape required by the upgraded `react-helmet` API.

## 6. Δc nature
MIXED — Δc contains real React/server source repairs plus a Jest snapshot update for `SemanticSearchResults`.

## 7. Soundness concerns / notes
The hidden test covers only `PageViewer`; the repair spans many Helmet call sites plus server `helmet()` options. The witness is still valid because the exercised call site fails without the source migration.

# Test-patch audit - ardatan__graphql-tools__6921

## 1. Task summary
- Folder: ardatan__graphql-tools__6921
- Ecosystem: npm_and_yarn
- Upgrade: @babel/core 7.26.7 -> 7.26.8 (manifest also changes several GraphQL/Yoga/WebSocket deps)
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest packages/executors/apollo-link/tests/apollo-link.spec.ts packages/executors/urql-exchange/tests/urql-exchange.spec.ts packages/executors/yoga/tests/yoga.spec.ts packages/loaders/url/tests/url-loader.spec.ts --no-coverage --passWithNoTests`

## 2. What is the breaking change?
The manifest patch is bundled: besides Babel 7.26.8 it upgrades `@graphql-tools/executor-graphql-ws` to 2.x, `graphql-ws` to 6.x, `graphql-yoga` to 5.11, `@apollo/client`, `esbuild`, and adds Babel support for explicit resource management. The repair adapts disposable executor handling, `graphql-ws` import paths, `ws` server naming, URL-loader helper code, and Babel parsing of `using`.

## 3. What does test.patch actually do?
The hidden tests create executor instances explicitly and dispose them with `DisposableSymbols`, rewrite the Yoga test to use `await using`, update `graphql-ws/lib/use/ws` to `graphql-ws/use/ws`, rename `Server as WSServer` to `WebSocketServer`, and adjust one URL-loader fetch-failure assertion.

## 4. Does test.patch directly exercise the breaking change?
Yes, for the bundled GraphQL/Yoga/WebSocket dependency changes. The patched tests require the new disposable protocol and import paths. Without Delta_c, the source either cannot parse/transform `using`, lacks disposable forwarding in `useExecutor`, or still uses old helper/import behavior. With Delta_c those paths compile and pass.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the specified Jest command runs the touched specs and they exercise the post-upgrade executor disposal and WebSocket API shapes.

## 6. Delta_c nature
MIXED - real source repair in executor/url-loader utilities plus Babel config and changeset/release-note files.

## 7. Soundness concerns / notes
The task is mislabeled if treated as only `@babel/core`; the actual witness comes from a bundled dependency update, especially GraphQL Yoga / graphql-ws / executor packages.

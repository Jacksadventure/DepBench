# Test-patch audit - DataSQRL__sqrl__1229

## 1. Task summary
- Folder: DataSQRL__sqrl__1229
- Ecosystem: maven
- Upgrade: vertx.version 4.5.14 -> 5.0.0
- test_cmd: Maven test command targeting `sqrl-server/sqrl-server-vertx-base` with `-Dtest=GraphQLJwtHandlerTest`.

## 2. What is the breaking change?
Vert.x 5 changes several APIs used by the GraphQL server: old callback/websocket methods are replaced by future-returning client methods, `VertxDataFetcher` usage is removed in favor of explicit `CompletableFuture` bridging, SQL client construction changes, and launcher hooks move to the new `VertxApplication` API.

## 3. What does Delta t (test.patch) actually do?
It updates `GraphQLJwtHandlerTest` from `.addHeader(...)` and `createHttpClient().webSocket(...)` to `.putHeader(...)` and `createWebSocketClient().connect(...)`, and changes `.sendJsonObject(..., callback)` to `.sendJson(...).onComplete(callback)`. It also updates `WriteIT` to use `PgBuilder`/`SqlClient`, although the selected test command only names `GraphQLJwtHandlerTest`; Maven test compilation can still see test-source API errors.

## 4. Does Delta t directly exercise the breaking change?
Yes for the Vert.x 5 API migration. The hidden tests compile and run against the updated Vert.x websocket/client APIs, and the production source repaired by Delta c must compile under the same Vert.x 5 dependency. The commented-out disabled websocket test body is noise, but the active `testWebsocketBadAuth` and `sendQuery` changes are relevant.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the patched test suite witnesses Vert.x 5 source/API incompatibility through compilation and active GraphQL JWT handler tests.

## 6. Delta c nature
MIXED - substantial Java source repair plus a `.circleci/config.yml` CI setting change.

## 7. Soundness concerns / notes
- Delta t contains some weakening/noise by commenting out a body inside an already `@Disabled` websocket test.
- The verifier target is narrower than the full repair, so not every Delta c hunk is directly covered.

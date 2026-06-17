# Test-patch audit - DataSQRL__sqrl__1218

## 1. Task summary
- Folder: DataSQRL__sqrl__1218
- Ecosystem: maven
- Upgrade: vertx.version 4.5.14 -> 5.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE` (test_state.py runs Maven for `sqrl-server/sqrl-server-vertx-base`, including `GraphQLJwtHandlerTest`)

## 2. What is the breaking change?
Vert.x 5 changes many APIs used by the server: callback-style methods become Future-returning methods with `onComplete`, web health checks move packages, WebSocket clients and header methods change, JDBC/Pg pool construction moves to builder/options APIs, and Vert.x launcher/micrometer setup changes.

## 3. What does test.patch actually do?
`GraphQLJwtHandlerTest` migrates WebSocket setup from `createHttpClient().webSocket(..., handler)` and `.addHeader(...)` to `createWebSocketClient().connect(...).onSuccess/onFailure` and `.putHeader(...)`; it also updates `sendJsonObject(..., callback)` to `sendJson(...).onComplete(callback)`. `WriteIT` changes `PgPool` setup to `PgBuilder.client().with(...).connectingTo(...).using(...).build()`.

## 4. Does test.patch directly exercise the breaking change?
Yes. The patched tests compile against Vert.x 5 APIs and the Maven command builds the vertx-base module. On P+Delta_m+Delta_t, production sources still use removed Vert.x 4 APIs and fail to compile. Delta_c performs the same migration across server, launcher, GraphQL fetcher, and client setup code.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the hidden tests and compile gate expose the Vert.x 5 API migration.

## 6. Delta_c nature
REAL_SOURCE_REPAIR - broad Java source migration from Vert.x 4 callback/package/client APIs to Vert.x 5 Future/builder APIs.

## 7. Soundness concerns / notes
The source patch is broad and somewhat messy, and the extracted test command is hidden behind generated Maven boilerplate. Still, the compile-level witness is directly tied to the upgraded Vert.x API surface.

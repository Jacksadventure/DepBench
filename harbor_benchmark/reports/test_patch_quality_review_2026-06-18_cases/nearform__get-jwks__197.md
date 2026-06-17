# Test-patch audit — nearform__get-jwks__197

## 1. Task summary
- Folder: nearform__get-jwks__197
- Ecosystem: npm_and_yarn
- Upgrade: lru-cache 8.0.0 -> 9.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npm test`

## 2. What is the breaking change?
lru-cache 9 no longer supports the old default constructor import used by this package. Consumers must import/use the named `LRUCache` class in both CommonJS runtime code and TypeScript declarations.

## 3. What does Δt (test.patch) actually do?
`test/types/get-jwks.test-d.ts` updates the type-level expectations from `LRU<string, JWK>` to `LRUCache<string, JWK>` and imports `type { LRUCache }` from `lru-cache`.

## 4. Does Δt directly exercise the breaking change?
Yes. The hidden tsd test expects `cache` and `staleCache` to be `LRUCache<string, JWK>`. On P⊕Δm the declaration file still imports the removed/default `LRU` type and the runtime source still constructs `new LRU(...)`; Δc updates both to `LRUCache`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt checks the new lru-cache v9 exported type and the repaired source/declaration surface supplies it.

## 6. Δc nature
REAL_SOURCE_REPAIR — `src/get-jwks.js` and `src/get-jwks.d.ts` migrate production runtime and public types from `LRU` to `LRUCache`.

## 7. Soundness concerns / notes
The hidden test is type-focused, but `npm test` likely covers both tsd and runtime paths. The source repair is not test-only and addresses the v9 constructor/export change directly.

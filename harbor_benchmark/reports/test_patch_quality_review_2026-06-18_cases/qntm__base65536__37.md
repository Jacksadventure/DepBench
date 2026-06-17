# Test-patch audit — qntm__base65536__37

## 1. Task summary
- Folder: qntm__base65536__37
- Ecosystem: npm_and_yarn
- Upgrade: safe-code-point 1.0.0 -> 2.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest scripts/gen.spec.js`

## 2. What is the breaking change?
safe-code-point v2 changes the consumer API from synchronous default/named helpers that accept a Unicode version argument to an asynchronous default factory, `SafeCodePoint('8.0.0')`, whose resolved object exposes `generalCategory`, `eastAsianWidth`, and the callable code-point predicate. The old `scripts/gen.js` imports `safeCodePoint, { generalCategory }` and computes exported constants at module load time, which no longer matches the upgraded package.

## 3. What does Δt (test.patch) actually do?
Touches `scripts/gen.spec.js` only. It removes the direct `eastAsianWidth` import from `safe-code-point`, imports the new default `gen` function from `./gen`, awaits `gen()` in `beforeAll`, and rewrites the assertions to read `generated.paddingBlockStart`, `generated.blockStarts`, and `generated.safeCodePoint.eastAsianWidth(codePoint)`.

## 4. Does Δt directly exercise the breaking change?
Yes. The hidden test now expects `./gen` to provide an async default function and to return the safe-code-point v2 helper object. On P⊕Δm, the old source has no compatible default `gen()` wrapper and still depends on the removed/changed safe-code-point imports, so `npx jest scripts/gen.spec.js` should fail before the assertions can pass; with Δc, `gen()` resolves and the generated block assertions execute against the v2 API.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt is targeted at the safe-code-point v2 async API shape and should fail against the old generator implementation while passing after the source migration.

## 6. Δc nature
REAL_SOURCE_REPAIR — the repair is confined to `scripts/gen.js`, replacing the old synchronous imports/exports with an async safe-code-point v2 adapter that returns the generated values.

## 7. Soundness concerns / notes
- Clean API-migration witness, though the manifest patch is dominated by the newly added `package-lock.json` noise.
- Δt changes test structure rather than adding a new behavioral case, but the rewritten test directly consumes the new source contract required by the dependency upgrade.

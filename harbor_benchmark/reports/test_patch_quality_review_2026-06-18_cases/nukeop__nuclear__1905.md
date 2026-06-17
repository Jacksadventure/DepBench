# Test-patch audit — nukeop__nuclear__1905

## 1. Task summary
- Folder: nukeop__nuclear__1905
- Ecosystem: npm_and_yarn
- Upgrade: @vitest/coverage-v8 3.2.4 -> 4.0.0 (vitest 3.2.4 -> 4.0.0)
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `pnpm --filter @nuclearplayer/hifi exec vitest --run src/fmp4/MseController.test.ts && pnpm --filter @nuclearplayer/player exec vitest --run src/views/Plugins/Plugins.test.tsx`

## 2. What is the breaking change?
vitest 4 changed `vi.fn()` mock-constructor semantics: a mock passed an arrow function and invoked with `new` no longer works as before, and the `vi.fn` generic typing changed (`vi.fn<(obj) => string>`). vitest 4 also altered render/timing in `@testing-library/react`, requiring `waitFor` around sequential assertions.

## 3. What does Δt (test.patch) actually do?
- `packages/hifi/src/fmp4/MseController.test.ts`: `vi.fn(() => {...})` → `vi.fn(function () {...})` for `MockMSConstructor`/`managedConstructor` (so `new MockMSConstructor()` works under vitest 4); adds explicit `vi.fn<(obj: MediaSource | Blob) => string>` generics on the URL spies.
- `packages/hifi/src/test/test-utils.ts`: `vi.fn(() => fakeCtx)` → `vi.fn(function () { return fakeCtx })`; adds an explicit return type to `resetMediaSpies`.
- `packages/player/src/test/setup.ts`: same arrow→`function` change for the `AudioContext` mock.
- `packages/player/src/views/Plugins/Plugins.test.tsx`: wraps `nthCalledWith`/`toMatchInlineSnapshot` assertions in `await waitFor(...)` and reorders `mount()`/`click()` ahead of spy setup.

## 4. Does Δt directly exercise the breaking change?
Δt fixes the vitest-4 mock-constructor breakage inside the test files themselves, but these are exactly the files Δc does NOT touch. Δc only changes `tsconfig.json` excludes, `validatedStore.ts` (zod generic), and `ScrollableArea.tsx` (`NodeJS.Timeout` → `ReturnType<typeof setTimeout>`) — none of which are type-checked by `vitest --run` (vitest transpiles via esbuild, stripping types; no `--typecheck`).

## 5. Coverage verdict
UNWITNESSED — Δc is entirely type-annotation and tsconfig/config changes with no runtime effect, and vitest does not type-check on `--run`; once Δt repairs the mock constructors in the test files, P⊕Δm⊕Δt passes at runtime without Δc (no_code_pass / Level 2). The problematic-review flag matches.

## 6. Δc nature
CONFIG_INFRA_ONLY / type-only — `tsconfig.json` excludes (×6 packages), `validatedStore.ts` zod generic rewrite (`z.ZodType<T>` → `S extends z.ZodType`, `z.output<S>`), `ScrollableArea.tsx` `NodeJS.Timeout` → `ReturnType<typeof setTimeout>`, `ui/tsconfig.json` adds `"node"` types. Zero runtime behavior change.

## 7. Soundness concerns / notes
- Textbook no_code_pass: runtime-irrelevant Δc + Δt that fixes the test-side vitest-4 issues. The two test files in `test_cmd` are not even in packages Δc modifies at runtime.
- The real vitest-4 breakage (mock constructors, timing) is handled entirely by Δt; nothing in Δc is required to make the graded tests pass. Should be excluded from the Level-1 benchmark.

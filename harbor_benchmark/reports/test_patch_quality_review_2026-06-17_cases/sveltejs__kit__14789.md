# Test-patch audit — sveltejs__kit__14789

## 1. Task summary
- Folder: sveltejs__kit__14789
- Ecosystem: npm_and_yarn
- Upgrade: vitest 3.2.4 -> 4.0.16 (plus `@vitest/browser` -> `@vitest/browser-playwright`)
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `pnpm test:unit && pnpm --dir /app/packages/adapter-auto test -- test/adapters.spec.js && pnpm --dir /app/packages/adapter-vercel test -- test/utils.spec.js`

## 2. What is the breaking change?
vitest 4.0 reworked the browser-provider API (string `'playwright'` → `playwright()` factory from `@vitest/browser-playwright`), renamed some config types (`UserConfig`→`ViteUserConfig`), and changed pool/options config shape. This is a dev-dependency / test-runner migration; no SvelteKit production source behavior is affected.

## 3. What does Δt (test.patch) actually do?
Touches 5 test/config files: `adapter-auto/test/adapters.spec.js` (bare import `'adapters.js'`→`'../adapters.js'`), `adapter-vercel/test/utils.spec.js` (dynamic import wrapped in `new URL(..., import.meta.url).href`), `kit/test/apps/basics/vite.config.js` (`environment:'browser'`+`provider:'playwright'` → `provider: playwright()`, `setupFiles` removed), `kit/test/apps/basics/vitest-setup-client.ts` (DELETED — referenced old `@vitest/browser/matchers`), `kit/test/prerendering/basics/vite.config.js` (`UserConfig`→`ViteUserConfig` type annotation). All changes are test-runner/config infrastructure; no test assertions added or changed.

## 4. Does Δt directly exercise the breaking change?
No. Δt migrates the test harness to vitest 4's API so the existing tests can *run*, but it does not add any assertion that would fail on P⊕Δm and pass on P⊕Δm⊕Δc. The Δc (kit.vitest.config.js pool options) is not exercised by any behavioral assertion — it is itself config plumbing.

## 5. Coverage verdict
UNWITNESSED — both Δc and Δt are test-runner config migration for the vitest dev-dependency upgrade; no production source behavior is exercised, and the project's own review confirms "Test-runner config migration and no witness."

## 6. Δc nature
CONFIG_INFRA_ONLY — the sole source-side change is `packages/kit/kit.vitest.config.js` swapping `poolOptions.threads.singleThread:true` for `pool:'threads', maxWorkers:1`; no production logic touched.

## 7. Soundness concerns / notes
The instruction tells the agent to "fix the source code," but Δc is a vitest config file, not production source — an agent following the constraints literally has no production code to repair. The `library: unknown` label in task_summary is also wrong (it is a vitest upgrade). Excluding from the witnessed set is correct.

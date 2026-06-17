# Test-patch audit — nuxt__fonts__601

## 1. Task summary
- Folder: nuxt__fonts__601
- Ecosystem: npm_and_yarn
- Upgrade: @iconify-json/simple-icons 1.2.31 -> 1.2.33 (manifest also bumps @nuxt/devtools-kit, fontaine, magic-regexp, tinyglobby, unplugin, eslint, playwright-core, vite, vitest, sass, tailwindcss, etc.)
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `pnpm dev:prepare && pnpm exec vitest run test/basic.test.ts -t "adds preload links to the HTML with global CSS" --pool=forks`

## 2. What is the breaking change?
The manifest is a broad non-major dependency sweep across the nuxt/fonts monorepo. The instruction frames it as an `@iconify-json/simple-icons` 1.2.31→1.2.33 bump, but no source-code behavior change is identified — the only "repair" in Δc is bumping GitHub Actions versions, so there is no real code-breaking change for the agent to fix.

## 3. What does Δt (test.patch) actually do?
- `test/basic.test.ts`: wraps `extractPreloadLinks(html)` in `.sort()` and reorders the `toMatchInlineSnapshot` array from `["/custom-font.woff2","/some-font.woff2","/file.woff2"(x5),"/file.woff"]` to the sorted `["/custom-font.woff2","/file.woff","/file.woff2"(x5),"/some-font.woff2"]`.
- No new assertions, no new test cases; purely an ordering-stabilization edit.

## 4. Does Δt directly exercise the breaking change?
No. The Δt only adds `.sort()` to make the preload-links snapshot order-independent. There is no assertion tied to any dependency behavior — the change is a test-only fix for non-deterministic link ordering. Δc contains zero source-code changes (only `.github/workflows/*.yml` setup-node version bumps), so nothing in Δt could plausibly fail on P⊕Δm and pass on P⊕Δm⊕Δc.

## 5. Coverage verdict
UNWITNESSED — Δt only adds `.sort()` to stabilize a snapshot ordering, and Δc is purely CI-workflow setup-node bumps with no source change, so the test passes on P⊕Δm without Δc.

## 6. Δc nature
CONFIG_INFRA_ONLY — exclusively `.github/workflows/release-nightly.yml` and `.github/workflows/release.yml` (actions/setup-node `cdca7365…` #v4.3.0 → `49933ea5…` #v4.4.0); no `src/`, no test, no package source touched.

## 7. Soundness concerns / notes
- Confirmed by the 2026-06-10 review: "Both unwitnessed and CI workflow only."
- This task has no source-code repair at all — the Δc is GitHub Actions version pin bumps, which have zero in-container effect on the verifier outcome.
- The manifest sweeps many runtime/dev deps but none produce a code patch; the Δt `.sort()` is a flakiness/ordering fix unrelated to any dependency behavior change.

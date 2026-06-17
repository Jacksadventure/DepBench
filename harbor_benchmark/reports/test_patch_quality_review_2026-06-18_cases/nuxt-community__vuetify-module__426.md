# Test-patch audit — nuxt-community__vuetify-module__426

## 1. Task summary
- Folder: nuxt-community__vuetify-module__426
- Ecosystem: npm_and_yarn
- Upgrade: @nuxtjs/eslint-config-typescript 4.0.0 -> 6.0.1
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `yarn test`

## 2. What is the breaking change?
There is no behavioral breaking change. `@nuxtjs/eslint-config-typescript` is a dev-only lint config; the 4.0 -> 6.0 bump tightens/changes lint rules (e.g. preferring `.includes()` over `.some(x => x === y)`, and `<style>` block ordering in `.vue` fixtures). The "repair" is lint-driven refactoring, not a runtime break.

## 3. What does Δt (test.patch) actually do?
- `test/fixture/layouts/default.vue`: relocates an empty `<style scoped></style>` block from before the `<script>` to after it (and drops the blank line). Pure fixture rearrangement to satisfy a vue block-order lint rule; no assertion is added or changed.

## 4. Does Δt directly exercise the breaking change?
No. The Δt only shuffles a `<style>` block in a fixture file; it adds no test assertion. The Δc change (`.some(mod => mod === 'nuxt-webfontloader')` -> `.includes('nuxt-webfontloader')`) is functionally equivalent, so the jest tests in `yarn test` pass identically with or without Δc. Lint itself is not part of the jest test run.

## 5. Coverage verdict
UNWITNESSED — TEST(P⊕Δm⊕Δt) already PASS: Δc is a behavior-preserving lint refactor and Δt is a fixture cosmetic shuffle; no hidden-test assertion distinguishes P⊕Δm from P⊕Δm⊕Δc.

## 6. Δc nature
FORMATTER_LINT_CHURN — `src/font.ts`: `.some(mod => mod === 'nuxt-webfontloader')` -> `.includes('nuxt-webfontloader')`; a lint-rule-driven, semantically-equivalent refactor with no behavioral effect.

## 7. Soundness concerns / notes
Confirmed unwitnessed (matches the problematic-review flag). Dev lint dependency upgrade with no runtime break; Δc is functionally a no-op and Δt is a non-functional fixture edit. The hidden test cannot detect whether the agent performed the `.includes()` refactor. Exclude from the witnessed main set.

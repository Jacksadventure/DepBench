# Test-patch audit — synyx__urlaubsverwaltung__2494

## 1. Task summary
- Folder: synyx__urlaubsverwaltung__2494
- Ecosystem: npm_and_yarn
- Upgrade: tailwindcss 2.2.19 -> 3.0.2
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest --colors=false`

## 2. What is the breaking change?
Tailwind 3 changes the supported/recommended utility surface used by this app: the repair moves nesting through `tailwindcss/nesting`, replaces legacy color utility tokens such as `tw-gray-*`/`tw-green-*` with the new palette names used by the project, and removes obsolete transform utility usage. The executed witness is narrow: it observes JavaScript/template-emitted class strings rather than a full Tailwind CSS build.

## 3. What does Δt (test.patch) actually do?
Δt touches `src/main/javascript/components/nav-tabs/__tests__/nav-tabs.spec.js` and `src/main/javascript/js/__tests__/send-get-department-vacations-request.spec.js`. It updates fixtures and assertions from `tw-border-gray-200`/`tw-text-gray-400` to `tw-border-zinc-200`/`tw-text-zinc-400`, and updates one expected HTML string from `tw-text-green-500` to `tw-text-emerald-500`.

## 4. Does Δt directly exercise the breaking change?
Partially yes. The nav-tabs tests call the component click handlers and assert the new class tokens added/removed by Δc; the department-vacations test asserts the generated HTML uses `tw-text-emerald-500`. Without Δc those assertions still see the old class names.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — P⊕Δm⊕Δt fails the updated Jest class-string expectations, while P⊕Δm⊕Δc⊕Δt passes after the Tailwind-3 class-name/source migration.

## 6. Δc nature
MIXED — Δc includes real source/template/CSS class-token migration across JS, CSS, JSP/Thymeleaf templates, plus `postcss.config.js`, `tailwind.config.js`, and generated asset manifest churn.

## 7. Soundness concerns / notes
- The verifier runs Jest only, so it does not directly prove the larger CSS build changes such as `tailwindcss/nesting` or `@screen print` -> `@layer print`.
- The witness is concentrated in two source files and may overrepresent a broad visual migration as a functional dependency break.

# Test-patch audit — huridocs__uwazi__5122

## 1. Task summary
- Folder: huridocs__uwazi__5122
- Ecosystem: npm_and_yarn
- Upgrade: react-hook-form 6.11.5 -> 7.36.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `node ./node_modules/.bin/jest app/react/Users/components/specs/UserSidePanel.spec.tsx app/react/Settings/components/specs/CollectionSettings.spec.tsx`

## 2. What is the breaking change?
react-hook-form v7 changed the hook API: `errors` moved under `formState`, and inputs are registered with spread props from `register("field", options)` rather than the v6 `name` + `ref={register(...)}` pattern.

## 3. What does Δt (test.patch) actually do?
It updates the two verifier specs to match v7 behavior: the collection settings submit test becomes async via `done`/`setTimeout`, uses a valid `/entity/...` home route, and the user side-panel expectation changes `using2fa` from string `"true"` to boolean `true`.

## 4. Does Δt directly exercise the breaking change?
Yes. Both tested components are in Δc. On P⊕Δm, `CollectionSettings` and `UserSidePanel` still use v6 registration and top-level `errors`, which is incompatible with react-hook-form v7. With Δc, both components use `formState.errors` and `...register(...)`, and the hidden specs assert the resulting submit/form values.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the failing surface is the v6-to-v7 React Hook Form API migration in the exact components run by the verifier.

## 6. Δc nature
REAL_SOURCE_REPAIR — several React form components migrate from v6 `ref={register}`/top-level `errors` to v7 `...register`/`formState.errors`, with typed submit handlers.

## 7. Soundness concerns / notes
Good witness for the two tested components. Δc also repairs other forms not covered by `test_cmd`, but the verifier does exercise representative migrated components.

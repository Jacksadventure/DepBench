# Test-patch audit — inovex__scrumlr.io__4672

## 1. Task summary
- Folder: inovex__scrumlr.io__4672
- Ecosystem: npm_and_yarn
- Upgrade: react-router 6.22.0 -> 7.0.2 (react-router-dom removed)
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx --no-install react-scripts test --watchAll=false --testPathPattern='(ExportBoard|TimerDialog|VotingDialog|RequireAuthentication|StackView|HeaderMenu|SettingsDialog)\\.test\\.tsx'`

## 2. What is the breaking change?
react-router v7 merged `react-router-dom` back into the `react-router` package. With Δm removing `react-router-dom`, every `import {...} from "react-router-dom"` fails to resolve. v7's `<Link>` also emits a new `data-discover="true"` attribute on rendered `<a>` tags, breaking existing snapshots.

## 3. What does Δt (test.patch) actually do?
- `HeaderMenu.test.tsx.snap` and `SettingsDialog.test.tsx.snap`: add `data-discover="true"` to all `<a>` tags rendered by v7 `<Link>` (snapshot regeneration).
- `ExportBoard.test.tsx`, `TimerDialog.test.tsx`, `VotingDialog.test.tsx`, `RequireAuthentication.test.tsx`: switch `jest.mock("react-router-dom", ...)` → `jest.mock("react-router", ...)`.
- `StackView.test.tsx`: add a `jest.mock("react-router", ...)` block with `useParams`/`useNavigate` and rename the navigate spy.

## 4. Does Δt directly exercise the breaking change?
Yes. The snapshot assertions (`data-discover="true"` on `<a href="/settings">` etc.) directly encode v7's new Link rendering. On P⊕Δm the source still imports from `react-router-dom`, which Δm removed → module resolution fails → tests cannot run (FAIL). On P⊕Δm⊕Δc imports resolve to `react-router`, v7 Link renders `data-discover`, and the Δt snapshots match (PASS).

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt's regenerated snapshots (`data-discover="true"`) and migrated `jest.mock` targets directly assert react-router v7 behavior that only passes once Δc moves source imports from `react-router-dom` to `react-router`.

## 6. Δc nature
REAL_SOURCE_REPAIR — import-path migration `react-router-dom`→`react-router` across ~12 production components (`BoardOptionLink.tsx`, `ErrorPage.tsx`, `Infobar.tsx`, `SettingsDialog.tsx`, `ShareButton.tsx`, `TimerDialog.tsx`, `VotingDialog.tsx`, `Board.tsx`, `Homepage.tsx`, `LoginBoard.tsx`, `RequireAuthentication.tsx`, `Router.tsx`) plus a `setupTests.ts` `TextEncoder` polyfill for v7.

## 7. Soundness concerns / notes
Solid witnessed task. Minor note: Δc also touches `src/setupTests.ts` (test infra) for the `TextEncoder` global, but this is a small enabler alongside the dominant source import migration. The `react-scripts test` runner uses jsdom which needs the `TextEncoder` polyfill under v7 — without it tests crash regardless of import fixes, so it is a legitimate part of the repair.

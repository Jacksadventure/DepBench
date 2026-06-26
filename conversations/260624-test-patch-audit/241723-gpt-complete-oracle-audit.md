# Handoff Note — 241723 · gpt · complete-oracle-audit

## Inherited context

This note continues `conversations/260624-test-patch-audit/241334-gpt-researched-test-patches.md`.

Important locked context:

- `HARNESS.md` is authoritative over stale `AGENTS.md` prose. Current `tasks_v4` source of truth is 257 tasks, not 297.
- Locked Level-1 definition remains `TEST(P ⊕ Δm ⊕ Δt)=FAIL` and `TEST(P ⊕ Δm ⊕ Δc ⊕ Δt)=PASS`.
- User clarified a stronger desired design check: original tests should also fail after the dependency bump, i.e. `TEST(P ⊕ Δm)=FAIL`, then patched tests still fail without `Δc`, then patched tests pass with `Δc`.
- The previous note was committed and pushed as `c9fd5bb6 Document test oracle audit findings` on branch `v4-297-benchmark-rerun-20260615`.

## Work done this session

- [x] Spawned five subagents for a multi-perspective static audit:
  - Four 13-task batches covering all 52 tasks imported on 2026-06-22.
  - One taxonomy synthesis over the June 18 full audit and prior handoff.
- [x] Appended an integrated multi-agent open-coding report to `241334-gpt-researched-test-patches.md`.
- [x] Added a design evaluation distinguishing the stronger three-state expectation from the current locked Level-1 definition.
- [x] Committed and pushed the expanded audit note.
- [x] Answered the follow-up import-only question from the report.

## Current state

| File | Change |
| --- | --- |
| `conversations/260624-test-patch-audit/241334-gpt-researched-test-patches.md` | Contains full multi-agent taxonomy, 52-task case-by-case report, design evaluation, and current problematic-count estimate. Already committed/pushed in `c9fd5bb6`. |
| `conversations/260624-test-patch-audit/241723-gpt-complete-oracle-audit.md` | This handoff note. |

Current branch:

- `v4-297-benchmark-rerun-20260615`

Key committed finding:

| Count | Meaning |
| ---: | --- |
| 257 | Current `tasks_v4` denominator per `HARNESS.md`. |
| 205 | Current tasks covered by June 18 audit; all 205 are statically `WITNESSES_BREAKING_CHANGE`. |
| 52 | Later with-test import tasks statically audited in the multi-agent pass. |
| 5 | Clear problematic / quarantine-priority tasks among the 52. |
| 11 | Conservative problematic count if caveated weak cases are included. |

Quarantine or dynamic-revalidation priority:

1. `FollowTheProcess__build__17`
2. `github__github-mcp-server__412`
3. `stackitcloud__gardener-extension-shoot-flux__180`
4. `suzuki-shunsuke__tfprovidercheck__629`
5. `ubugeeei-prod__ox-content__131`

Caveated / weak-signal tasks:

1. `chinmina__chinmina-bridge__101`
2. `giantswarm__muster__751`
3. `go-vela__vela-docker__118`
4. `kairos-io__provider-kairos__869`
5. `nobl9__sloctl__448`
6. `syou6162__times_esa_mcp_server__22`

## Import-only clarification

User asked how many instances are import-only. Based on the report:

- Strict `Δt` import-only cases among the 52 imported tasks: 9.
- Clean-ish cases where both hidden test patch and oracle/code repair are mostly import/API-path migrations: roughly 6-7.

Strict `Δt` import-only list:

1. `FollowTheProcess__build__17`
2. `FollowTheProcess__txtract__33`
3. `GoogleCloudPlatform__cloud-foundation-toolkit__2670`
4. `emmahsax__go-git-helper__108`
5. `giantswarm__cluster-cleaner__225`
6. `giantswarm__logging-operator__453`
7. `giantswarm__upgrade-schedule-operator__267`
8. `go-fries__fries__1076`
9. `thegeeklab__wp-matrix__222`

Cleaner import-only/API-path repair witnesses:

1. `FollowTheProcess__txtract__33`
2. `GoogleCloudPlatform__cloud-foundation-toolkit__2670`
3. `giantswarm__cluster-cleaner__225`
4. `giantswarm__logging-operator__453`
5. `giantswarm__upgrade-schedule-operator__267`
6. `go-fries__fries__1076`
7. `emmahsax__go-git-helper__108` — possible, but has workflow/version noise.

Do not treat `FollowTheProcess__build__17` as a clean import-only repair. It is a quality problem because `Δc` appears unrelated to the verifier surface.

## Open tasks for the next agent

1. Run dynamic pre-code checks for the five quarantine-priority tasks:
   `TEST(P⊕Δm)`, `TEST(P⊕Δm⊕Δt)`, and `TEST(P⊕Δm⊕Δc⊕Δt)`.
2. If the paper needs a strict current-257 headline, dynamically check the six caveated tasks too.
3. Generate `harbor_benchmark/reports/test_patch_quality_review_2026-06-24_current257.md` and `.csv`.
4. Fix or annotate metadata for imported tasks with blank or misleading `library`, `old_version`, and `new_version`.
5. Add an explicit evidence-tier column to future reports:
   - `Tier A+ original-suite witnessed`
   - `Tier A hidden-suite witnessed`
   - `Tier B latent/no-code-pass`
   - `Bad oracle/tests-other-thing`

## Key decisions

| Decision | Rationale |
| --- | --- |
| Keep current Level-1 definition but add stronger Tier A+ label | Some legitimate repairs add `Δt` precisely because original tests were weak; making `TEST(P⊕Δm)=FAIL` mandatory would exclude those. |
| Count 5 clear problematic tasks in current 257, or 11 conservatively | Static multi-agent audit found five strong quarantine cases and six weaker/caveated cases among the 52 imported tasks. |
| Treat import-only compile/API witnesses as valid but label them | Removed/moved modules and changed package paths are real dependency breaks, but they are compile witnesses rather than rich behavioral assertions. |

## Blockers

- No blocker for documentation work.
- Dynamic Harbor validation was not run in this thread.

## Suggested next step

Start with dynamic pre-code witness checks for `FollowTheProcess__build__17`, `github__github-mcp-server__412`, and `ubugeeei-prod__ox-content__131`, because static evidence suggests they are the most severe oracle-quality problems.

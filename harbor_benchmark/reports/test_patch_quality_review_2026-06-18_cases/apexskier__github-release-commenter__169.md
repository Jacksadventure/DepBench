# Test-patch audit — apexskier__github-release-commenter__169

## 1. Task summary
- Folder: apexskier__github-release-commenter__169
- Ecosystem: npm_and_yarn
- Upgrade: @actions/github 4.0.0 -> 5.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `yarn jest --ci`

## 2. What is the breaking change?
@actions/github 5 exposes generated REST endpoint methods under `octokit.rest.*` instead of the old top-level namespaces used by this action. Calls such as `octokit.repos.listReleases`, `octokit.repos.compareCommits`, and `octokit.issues.createComment` must become `octokit.rest.repos.listReleases`, `octokit.rest.repos.compareCommits`, and `octokit.rest.issues.createComment`.

## 3. What does Δt (test.patch) actually do?
- `src/index.test.ts`: rewrites the mocked Octokit object from top-level `repos` / `issues` namespaces to nested `rest.repos` / `rest.issues` namespaces.
- `src/index.test.ts`: updates direct expectations to read `mockOctokit.rest.issues.createComment` and `mockOctokit.rest.issues.addLabels.mock.calls`.
- `src/index.test.ts`: adds an `afterEach` guard asserting that `core.error`, `core.warning`, and `core.setFailed` were not called.

## 4. Does Δt directly exercise the breaking change?
Yes. With Δt applied, the mock only defines `mockOctokit.rest.repos.listReleases` and `mockOctokit.rest.issues.*`; the old production code still calls `octokit.repos.listReleases(...)` and later `octokit.issues.createComment(...)`, so it fails before reaching the expected assertions. Δc changes those call sites to `octokit.rest.repos.*` and `octokit.rest.issues.*`, matching the upgraded @actions/github API and the new test mock shape.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt's nested `rest` mock makes the old top-level Octokit calls fail under P⊕Δm⊕Δt, while Δc's REST namespace migration makes the same Jest suite pass.

## 6. Δc nature
MIXED — real source repair appears in `src/index.ts` and generated `dst/index.js`, but the patch also includes a Jest snapshot update in `src/__snapshots__/index.test.ts.snap` and a very large checked-in `dst/node_modules` refresh from the dependency upgrade.

## 7. Soundness concerns / notes
- The core witness is sound for the @actions/github v5 API shape, but the oracle is not a clean source-only repair because it updates a test snapshot.
- Since the verifier applies only `tests/test.patch`, an agent that performs only the source REST namespace migration may still be exposed to stale Jest snapshots unless it also updates test artifacts, which conflicts with the task instruction not to modify tests.
- The bundle is huge because this repository vendors action dependencies under `dst/node_modules`; most of Δc is generated/vendor churn rather than hand-authored repair logic.

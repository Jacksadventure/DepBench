# Case study: nearform/brokeneck PR #820 — react-router-dom 5.3.0 → 6.4.1

**Research question:** could an agent have obtained enough context to fix this breaking upgrade correctly *before the PR was created*, from (a) the upstream repo (remix-run/react-router) and (b) sibling repos that upgraded earlier?

| Item | Value |
|---|---|
| Task PR | nearform/brokeneck #820, "chore(deps): bump react-router-dom from 5.3.0 to 6.4.1" (dependabot[bot]; 2 commits, 12 changed files) |
| Cutoff (PR created) | **2022-09-22T01:08:17Z** |
| Merged | 2022-09-26T15:18:49Z |
| Upstream | remix-run/react-router |
| DepBench result | **0 / 10** harness×model configs solved |
| Task dir | `/Users/hrz/Documents/GitHub/DependAgent/DepBench/dataset/tasks/nearform__brokeneck__820/` |

Note the instruction.md says "from 5.2.0" (the manifest range `^5.2.0`); the resolved/locked version was 5.3.0.

---

## Step 1 — Repair facts (ground truth: `solution/code.patch`)

The human repair touches 6 source files (+1 new). Distinct repair facts:

| # | Repair fact | File(s) | Exercised by hidden tests? |
|---|---|---|---|
| F1 | `<Switch>` → `<Routes>` | Admin.js | Indirectly (Admin.test.js in the pre-existing suite must still pass; suite-wide oracle) |
| F2 | Route render-props/children → `element` prop: `<Route path="/users/:userId">{({match}) => <User userId={...}/>}</Route>` → `<Route path="/users/:userId" element={<User />} />` | Admin.js | Indirectly |
| F3 | `exact` prop removed (v6 matches exactly by default) | Admin.js | Indirectly |
| F4 | `<Redirect from="/" exact to="/users" />` → `<Route path="/" element={<Navigate replace to="/users" />} />` (note: v5 `Redirect` replaces by default; v6 `Navigate` pushes by default — needs explicit `replace`) | Admin.js | Indirectly |
| F5 | RegExp route paths removed: the v5 trailing-slash trick `<Redirect from="/:url*(/+)" to={pathname.slice(0,-1)} />` is invalid in v6 → new custom `RemoveTrailingSlash` component built from `useLocation` + `<Navigate replace>` | Admin.js, RemoveTrailingSlash.js (new) | Indirectly |
| F6 | `useHistory()` → `useNavigate()`; `history.goBack()` → `navigate(-1)` | User.js, Group.js | **Directly**: hidden tests mock `useNavigate` and assert `expect(mockNavigate).toHaveBeenCalledWith(-1)` |
| F7 | Route params via `useParams()` **inside** the routed component; `User`/`Group` no longer take `userId`/`groupId` props (prop-types removed) | User.js, Group.js, Admin.js | **Directly**: hidden tests render `<User />` / `<Group />` with **no props** and mock `useParams: () => ({ userId: '1234' })` |
| F8 | `useRouteMatch('/groups')` → `useMatch('/groups/*')` (splat needed for descendant matching) | Navigation.js | Indirectly |
| F9 | Link built from `match.url`: ``to={`${match.url}/${id}`}`` → relative `to={id}` (v6 links are route-relative) | Entities.js | Indirectly |
| F10 | "Up" link `to="."` → `to=".." relative="path"` — v6 `..` resolves **route**-relative (all the way to `/` here since routes are siblings, not nested); the `relative="path"` escape hatch is **new in 6.4.0** | Entity.js | Indirectly |
| F11 | Mechanical: manifest `^5.2.0` → `^6.4.1` in 2 packages + yarn.lock rewrite (new transitive `@remix-run/router@1.0.1`, drops `history`, `mini-create-react-context`, etc.) | package.json ×2, yarn.lock | Precondition |

The verification oracle is the **whole jest suite** (13 suites / 33 tests) after the hidden `tests/test.patch` replaces `Group.test.js` and `User.test.js`. The hidden versions switch the jest mocks from `useHistory → useNavigate`, add a `useParams` mock, and render `<User />`/`<Group />` propless — i.e., they hard-code the *canonical* v6 idiom for F6+F7.

---

## Step 2 — What agents actually did (claude48/claude_code and gpt55/copilot_cli)

Both configs failed with an **identical** verification signature (`verify_logs/*.jsonl.gz`):

```
Test Suites: 2 failed, 11 passed, 13 total
Tests:       5 failed, 28 passed, 33 total
```

Failing suites are exactly the two hidden-patched ones (Group.test.js, User.test.js); representative failure at `Group.test.js:254`: `expect(mockMutation).toBeCalledWith(... variables: { input ... })` — mutation invoked with the wrong/undefined id because the component didn't get its route param.

### claude48 / claude_code (259 steps)

The agent did a *high-quality* migration and even spawned a research subagent to "verify against the react-router v6.4.1 changelog / docs". Its final diff (extracted from the trajectory) correctly applied F1–F5, F8, F9. But for F6/F7 it deliberately optimized for the **visible pre-upgrade tests** (which mock `useHistory` and render `<Group groupId="1234"/>`):

```js
// Admin.js — useParams read in a WRAPPER, not in the component:
function GroupRoute() {
  const { groupId } = useParams()
  return <Group groupId={groupId} />
}
...
// Group.js — dual-compat shim kept the component prop-based:
export default function Group({ groupId }) {
  const history = ReactRouterDOM.useHistory?.()
  const navigate = ReactRouterDOM.useNavigate?.()
  const goBack = history ? () => history.goBack() : () => navigate(-1)
```

All 33 tests passed *locally* against the visible tests ("All 13 suites and 33 tests pass"). At grading time the hidden tests render `<Group />` propless and mock `useParams` at module level — the wrapper `GroupRoute` isn't rendered by the test (the test renders `<Group/>` directly), so `groupId` is `undefined` → 5 failures.

### gpt55 / copilot_cli (89 steps)

Same story, stated explicitly in-trajectory: *"The unchanged tests still mock the old back-navigation hook, so I'm adding a small source-level back-navigation compatibility hook that uses v6 in production and honors the existing test mock when present"* — a `useGoBack` compat hook plus prop-based components. Identical 5-test failure.

### The gap

**Not a knowledge gap.** Both agents demonstrably knew every upstream breaking-change fact (F1–F9; claude even researched 6.4.1 specifics). The gap is a **target-idiom prediction gap**: the hidden oracle rewrites tests to the canonical v6 idiom (hooks *inside* `User`/`Group`, no props), while the visible v5-era tests actively pull agents toward backward-compat shims. The winning move — call `useParams()`/`useNavigate()` inside the components exactly as the human did (optionally keeping a prop fallback, which would satisfy both test generations) — required predicting the maintainer's canonical refactor, not another changelog fact.

---

## Step 3 — Upstream mining at cutoff (2022-09-22T01:08:17Z)

### Timeline of upstream artifacts

| Artifact | Date | Pre-cutoff? |
|---|---|---|
| v6.0.0 GitHub release (+ blog "Upgrading to React Router v6") | 2021-11-03T20:15:49Z | ✅ |
| `docs/upgrading/v5.md` (v5→v6 migration guide, 31,777 B at tag v6.0.0; 35,319 B at react-router@6.4.0) | in-tree since v6.0.0 | ✅ |
| v6.3.0 release (adds `react-router-dom-v5-compat` package) | 2022-03-31T19:45:24Z | ✅ |
| PR #9160 "feat: add relative=path option for url-relative routing" | merged 2022-08-18T13:56:43Z | ✅ |
| react-router@6.4.0 GitHub release | 2022-09-13T19:48:15Z | ✅ |
| react-router-dom@6.4.1 **npm publish** | 2022-09-21T20:46:19Z | ✅ (4.4 h before cutoff) |
| react-router@6.4.1 **GitHub release** | 2022-09-22T15:53:06Z | ❌ (14.7 h *after* cutoff) |

### Fact-by-fact coverage in `docs/upgrading/v5.md` @ tag `react-router@6.4.0`
(https://github.com/remix-run/react-router/blob/react-router@6.4.0/docs/upgrading/v5.md — public 2022-09-13; nearly all of this text is identical at v6.0.0, 2021-11-03)

- **F1** — heading: *"Upgrade all `<Switch>` elements to `<Routes>`"* … *"In order to use v6, you'll need to convert all your `<Switch>` elements to `<Routes>`."*
- **F2** — *"You may have also noticed that all `<Route children>` from the v5 app changed to `<Route element>` in v6."*
- **F3** — *"`<Route exact>` is gone. Instead, routes with descendant routes … use a trailing `*` in their path"*
- **F4** — *"Normal `<Redirect>` elements … will become `<Navigate>` elements in v6."* and the push/replace trap verbatim: *"Be aware that the v5 `<Redirect />` uses `replace` logic by default …, on the other hand, the v6 `<Navigate />` uses `push` logic by default and you may change it via `replace` prop."*
- **F5** — *"The following RegExp-style route paths are **not valid** in v6"* … *"If you were using any of path-to-regexp's more advanced syntax, you'll have to remove it and simplify your route paths."* Plus: *"all path matching in v6 ignores the trailing slash on the URL."*
- **F6** — heading *"Use `useNavigate` instead of `useHistory`"*; and precisely the hidden-test-asserted form: *"If you're currently using `go`, `goBack` or `goForward` from `useHistory` … replace these with `navigate` with a numerical argument"* with example `onClick={() => navigate(-1)}`.
- **F7** — *"If you were using `<Route render>` to get a hold of the params, you can just `useParams` inside your route component instead."* ← **the exact fact whose canonical application the agents skipped.**
- **F8** — heading *"Replace `useRouteMatch` with `useMatch`"* (differences listed: patterns required, `{ strict }`→`{ end }`, etc.).
- **F9** — *"in v5 we recommended that you build links from the root URL (using `match.url`) … "* followed by the v6 relative-link semantics (`<Link to="me">` inside `<Route path="users">` → `/users/me`).
- **F10** — **not in the guide.** The route-relative `..` pitfall *is* (*"`<Link to="..">` will not always behave like `<a href="..">` … it will resolve based upon the parent route's path"*), but the fix (`relative="path"`) only appears in the **react-router@6.4.0 release notes** (2022-09-13): *"Perform path-relative navigations with `<Link relative="path">` (#9160)"*. 9 days old at cutoff — the freshest repair fact.
- **F11** — mechanical; derivable from npm metadata (6.4.1 on npm 4.4 h pre-cutoff).

**Not documented anywhere upstream:** nothing needed for the code fix is missing. What no upstream artifact can supply is the *oracle convention* — that this repo's own hidden tests would be rewritten to mock `useNavigate`/`useParams` and render routed components propless.

---

## Step 4 — Sibling mining at cutoff (GHArchive via play.clickhouse.com)

### Queries

```sql
-- stratum count
SELECT count() AS merged_prs,
       countIf(commits > 1 OR changed_files > 3) AS with_repair_signal
FROM github_events
WHERE event_type = 'PullRequestEvent' AND action = 'closed' AND merged = 1
  AND created_at < '2022-09-22 01:08:17'
  AND (title ILIKE '%bump react-router-dom from 5% to 6%'
    OR title ILIKE '%update dependency react-router-dom to v6%'
    OR title ILIKE '%update react-router%to v6%'
    OR title ILIKE '%upgrade react-router%to v6%'
    OR title ILIKE '%react-router%v5 to v6%'
    OR title ILIKE '%migrate%react-router%v6%')
-- → 1172 merged PRs, 204 with repair signal

SELECT countIf(title ILIKE '%react-router-dom from 5% to 6.4%')      AS to_64x,     -- 5
       countIf(title ILIKE '%react-router-dom from 5.3.0 to 6.4.1%') AS exact_pair, -- 0
       countIf(title ILIKE '%bump react-router-dom from 5% to 6%')   AS dependabot_any -- 366
FROM github_events
WHERE event_type='PullRequestEvent' AND action='closed' AND merged=1
  AND created_at < '2022-09-22 01:08:17' AND title ILIKE '%react-router-dom%'
```

(Candidate listing used the same predicate plus `commits > 1 AND changed_files BETWEEN 4 AND 60 ORDER BY created_at DESC LIMIT 40`.)

### Stratum

- **1,172** merged sibling PRs updating react-router(-dom) 5.x→6.x before the cutoff; **204** with repair signal (commits > 1 OR changed_files > 3). Rich stratum.
- 366 of the 1,172 are Dependabot-titled "Bump react-router-dom from 5.x to 6.x" — the exact shape of the task PR.
- 5 siblings targeted 6.4.x (6.4.0 was 9 days old); **0** matched the exact pair 5.3.0→6.4.1 (npm-published <24 h before the task PR).

### Exemplar sibling diffs (all merged pre-cutoff; diffs via `gh api repos/…/pulls/N -H 'Accept: application/vnd.github.v3.diff'`)

**udovin/solve-web #24** — "Bump react-router-dom from 5.3.0 to 6.3.0" (Dependabot + human repair; merged 2022-07-04). Contains the *exact* F7 transformation the failing agents skipped:

```diff
-const CreateContestProblemBlock = ({ match }: RouteComponentProps<ContestPageParams>) => {
-	const { contest_id } = match.params;
+const CreateContestProblemBlock: FC = () => {
+	const params = useParams();
+	const { contest_id } = params;
```
plus F1/F2/F4 (`Switch`→`Routes`, 23 `Routes`/`element=` additions, 9 `<Navigate` additions, 16 `useParams` additions).

**microsoft/accessibility-insights-web #4989** — "chore(deps): bump react-router-dom from 5.3.0 to 6.2.1" (merged 2022-02-01). Shows F2+F7 (`useParams` inside routed component) **and — uniquely — updates its own test files in the same PR** (5 test files touched: `insights-router.test.tsx`, snapshots, etc.), demonstrating the convention that tests are rewritten to the v6 idiom rather than preserved via shims:

```diff
+import { HashRouter, Route, Routes, useParams } from 'react-router-dom';
+export const ContentRoute = NamedFC<ContentRouteProps>('ContentRoute', ({ deps }) => {
+    const params = useParams();
+    return <deps.ContentRootComponent deps={deps} reference={params['*']} />;
+});
```

**msaperst/snnap #113** — "Bump react-router-dom from 5.3.0 to 6.2.2 in /ui" (merged 2022-03-02). F1, F6 (`useHistory`/custom history → `useNavigate`, 6 additions), F4:

```diff
-import { BrowserRouter as Router, Route } from 'react-router-dom';
+import { Routes, Route, useNavigate } from 'react-router-dom';
...
+function LoginPage() {
+  const navigate = useNavigate();
```

**ricglz/ttt-react #696** — "Bump react-router-dom from 5.3.0 to 6.2.2" (merged 2022-03-01): F1/F2 (9 `Routes`/`element=`), F6 (6 `useNavigate`).

**ccnmtl/austere-med-interactives #320** — "Bump react-router-dom from 5.3.0 to 6.3.0" (merged 2022-07-14): F1/F2 (12 `Routes`/`element=` additions) — the minimal-shape sibling.

Coverage summary across sampled siblings: F1 (5/5), F2 (5/5), F4 (2/5), F6 (2/5), F7 (2/5), test-rewrite convention (1/5, microsoft). **Not found in sampled siblings:** `navigate(-1)` / `goBack` replacement (F6's numeric form — but it's verbatim in the upgrade guide), F5's regex-trailing-slash custom component, F8 `useMatch('/x/*')`, F10 `relative="path"` (unsurprising: 9 days old; sampled siblings target ≤6.3.0). No sampled sibling updates `jest.mock('react-router-dom')` hook mocks (`useHistory`→`useNavigate`/`useParams`), the precise shape of this task's hidden tests.

---

## Step 5 — Verdict

### Knowability matrix

| Fact | Upstream docs | Upstream code/tests only | Siblings only | Nowhere |
|---|---|---|---|---|
| F1 Switch→Routes | ✅ guide (2021-11) | | ✅ (5/5 sampled) | |
| F2 element prop | ✅ guide | | ✅ (5/5) | |
| F3 exact removed | ✅ guide | | ✅ (implied in all) | |
| F4 Redirect→Navigate(+replace trap) | ✅ guide, verbatim | | ✅ (2/5) | |
| F5 regex paths invalid → custom trailing-slash comp | ✅ guide (invalidity + trailing-slash semantics); the *replacement component* is the app's own design | | ~ | |
| F6 useHistory→useNavigate, goBack→navigate(-1) | ✅ guide, verbatim incl. `navigate(-1)` | | ✅ hooks (2/5); numeric form not sampled | |
| F7 useParams inside routed component | ✅ guide, verbatim | | ✅ (udovin, microsoft) | |
| F8 useRouteMatch→useMatch(+`/*`) | ✅ guide (the `/*` splat detail is in the "descendant routes" note) | | | |
| F9 match.url → relative to | ✅ guide | | ✅ | |
| F10 `..` + `relative="path"` | ✅ 6.4.0 release notes only (2022-09-13, 9 days old); pitfall in guide, fix not | ✅ PR #9160 (2022-08-18) | ❌ (too new) | |
| F11 lockfile/transitive | npm metadata (6.4.1 published 4.4 h pre-cutoff) | | | |
| **Hidden-test idiom: tests will mock useNavigate/useParams, render propless** | ❌ | ❌ | ~ (microsoft shows tests-rewritten-in-same-PR convention; exact mock shape unseen) | **largely nowhere** |

**Every code-level repair fact was documented upstream before the cutoff** — F1–F9 since v6.0.0 (2021-11-03), F10 since the 6.4.0 release notes (2022-09-13). Sibling supply was abundant: 1,172 merged 5→6 PRs, 204 with repair signal, including same-shape Dependabot+human-repair PRs.

### Why 0/10 anyway

The observed failure is *not* missing upstream knowledge. Both examined agents applied F1–F5, F8–F9 correctly and knew F6/F7 (claude48 researched the v6.4.1 API explicitly) — then **chose** prop-based components + `useHistory`/`useNavigate` compat shims to keep the *visible v5-era tests* green. The hidden oracle instead re-applies tests rewritten to the canonical idiom (mock `useNavigate`; mock `useParams`; render `<User />`/`<Group />` propless), so the shims scored 28/33. The benchmark's visible tests are an actively *misleading* context signal.

### Minimal context artifact that plausibly flips fail→pass

1. **One convention card** (the decisive item): *"In merged 5→6 upgrade PRs, maintainers migrate tests along with source: components read `useParams()`/`useNavigate()` internally; tests re-mock those hooks and stop passing route params as props. Do the canonical migration; do not build shims around v5-era test mocks (keep a prop fallback only if it costs nothing)."* Grounded in siblings like microsoft/accessibility-insights-web #4989 (source + 5 test files migrated in one PR). Either the canonical form or the belt-and-braces form (`const { userId } = { ...useParams(), ...(props.userId && { userId: props.userId }) }` + hook-based goBack) passes both test generations.
2. **~6 breaking-change cards** distilled from `docs/upgrading/v5.md` @ react-router@6.4.0 (F1–F9; agents already reconstructed these, so alone they are insufficient — this case proves cards without the convention signal don't flip the task).
3. **1–2 exemplar diffs** (udovin/solve-web #24 for the `match.params`→`useParams()` hunk; microsoft #4989 for the tests-migrate-too signal).

Estimated flip likelihood with (1)+(3): high — both failing trajectories explicitly deliberated the shim-vs-canonical decision and picked wrong for lack of exactly this evidence.

### Surprises

- **The visible test suite was the villain.** This case inverts the usual mined-context story: perfect upstream mining was already achieved *by the agents themselves* and didn't help, because the failure mode was oracle-idiom prediction, not API knowledge.
- **6.4.1's GitHub release didn't exist yet at cutoff** (published 14.7 h after PR creation); only the npm publish (4.4 h prior) and the 6.4.0 release notes were available. Any "mine the release notes for the bumped version" pipeline must fall back to nearest-prior release.
- **F10 (`relative="path"`) was 9 days old** and absent from the migration guide and from all sampled siblings — pure release-note/PR-mining territory (#9160, merged 2022-08-18). Notably the pre-existing visible tests didn't catch agents' wrong handling of `to="."` either way, so it didn't decide pass/fail here, but it is the kind of fact only fresh-release mining surfaces.
- **Zero exact-version siblings** (5.3.0→6.4.1) existed — sibling matching must be tolerant on the target minor/patch (5.x→6.x), where supply is 3 orders of magnitude larger.

### Evidence file paths

- Ground truth: `/Users/hrz/Documents/GitHub/DependAgent/DepBench/dataset/tasks/nearform__brokeneck__820/solution/code.patch`
- Hidden tests: `/Users/hrz/Documents/GitHub/DependAgent/DepBench/dataset/tasks/nearform__brokeneck__820/tests/test.patch`
- Trajectories: `/Users/hrz/Documents/GitHub/DependAgent/DepBench/trajectories/{claude48__claude_code,gpt55__copilot_cli}.jsonl.gz`
- Verify logs: `/Users/hrz/Documents/GitHub/DependAgent/DepBench/verify_logs/{claude48__claude_code,gpt55__copilot_cli}.jsonl.gz`
- Upgrade guide snapshot: https://github.com/remix-run/react-router/blob/react-router@6.4.0/docs/upgrading/v5.md
- 6.4.0 release notes: https://github.com/remix-run/react-router/releases/tag/react-router%406.4.0
- relative=path PR: https://github.com/remix-run/react-router/pull/9160
- Sibling PRs: https://github.com/udovin/solve-web/pull/24 · https://github.com/microsoft/accessibility-insights-web/pull/4989 · https://github.com/msaperst/snnap/pull/113 · https://github.com/ricglz/ttt-react/pull/696 · https://github.com/ccnmtl/austere-med-interactives/pull/320

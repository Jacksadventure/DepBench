# Handoff Note — 131301 · claude · researched-context-cases

## Inherited context

- Read `handoff/REPORT.md` (2026-07-13): DepBench establishes 219 tasks, best config 40%; dominant failure modes = incomplete migration + visible-test overfitting; GHArchive sibling mining validated (glob 8→10: 73 repaired siblings); Ideas A–E proposed (exemplar mining, breaking-change cards, verified rules, completeness checker, dep-context MCP server).
- This session's task: deep-dive case studies on up-to-5 zero-pass tasks — can enough context be mined **before PR creation time** from the upstream repo + sibling repos to solve the hidden-test-failing breaking change?

## Work done this session

- [x] Identified the 93/219 tasks unsolved by all 10 configurations (from `results/per_trial_results.jsonl.gz`), stratified by ecosystem.
- [x] Selected 5 diverse cases: react-router-dom 5→6 (nearform/brokeneck#820), @solana/spl-token 0.1→0.3 (solana-program-library#4301, self-dependency monorepo), syn 1→2 (actix#554), lestrrat-go/jwx 1.1→1.2 (nuts-node#426), shiro 1.13→2.0.1 (JavaSecurity#236).
- [x] Ran 5 parallel investigator subagents; each did: ground-truth patch forensics → failed-trajectory gap analysis → upstream mining at cutoff (gh CLI + web) → GHArchive sibling mining at cutoff (clickhouse client against play.clickhouse.com) → structured verdict. Time-travel discipline enforced (only pre-PR-creation evidence counts).
- [x] Wrote per-case evidence files in `conversations/260713-context-case-studies/cases/` (5 files, ~900 lines total, with exact ClickHouse queries, sibling PR lists+dates, quoted upstream sentences and hunks).
- [x] Wrote cross-case synthesis: `conversations/260713-context-case-studies/REPORT.md`.

## Current state

| File | Change |
|---|---|
| conversations/260713-context-case-studies/REPORT.md | NEW — cross-case synthesis (findings F1–F5, revised design implications) |
| conversations/260713-context-case-studies/cases/*.md | NEW — 5 full case studies with evidence chains |
| (no repo/source files modified) | — |

Key numbers: sibling strata at cutoff = 1,172 (react-router 5→6; 204 repair-signal) / ~717 PRs, 323 repos (syn 1→2) / ~20 (shiro 2.0.0 window; 0 for 2.0.1, released 59 min before the PR) / 8 (jwx) / 14-with-0-repair-signal via titles (spl-token; real exemplars exist under manual titles).

## Key decisions

| Decision | Rationale |
|---|---|
| Framed headline finding as **evidence-weighting, not retrieval**: in 4/5 cases agents possessed/discovered the decisive facts and were defeated by visible tests encoding pre-upgrade semantics | Direct trajectory evidence (shiro agents printed `DEFAULT_ITERATIONS = 50000` then coded 1M; spl-token/brokeneck agents deliberately shimmed to keep visible tests green; 9/10 syn migrations semantically correct) |
| Classified 2/5 zero-pass tasks as wholly/partly **benchmark artifacts** (jwx: unsolvable random-fixture regeneration entangled across hidden/source split; actix: hidden trybuild dev-deps only in withheld manifest + dead .stderr oracle) | Changes interpretation of "consensus-hard": consensus-hard ≠ context-hard; must be reported honestly and filtered before ablations |
| Elevated two context tiers missing from the original Ideas A–E: **same-org siblings** (conventions like dev-dep scaffolding) and **upstream test diffs** (mineable witness of behavioral re-baselines) | actix-net#481 was the *sole* pre-cutoff source of the decisive fact in Case 3; upstream tests showed the exact target idiom in Cases 2/5 |
| Proposed **"re-baseline prior" as ablation arm 0** (a policy instruction, zero mining cost) ahead of exemplar/card arms | It attacks the observed dominant failure mode in Cases 1/2/5 and cleanly isolates prompt-fixable overfitting from genuine knowledge gaps |
| Sibling retrieval must be **symbol-based, not bump-title-based** | spl-token title-recall was zero despite rich manually-titled exemplars (metaplex#299, marinade#35) |

## Open tasks for the next agent

1. **Run ablation arm 0** on DepBench (fixed harness, e.g. Claude Code): add the re-baseline policy instruction ("post-upgrade tests re-baseline to the library's new defaults/idioms; migrate tests with source; don't shim to preserve pre-upgrade assertions") to the task prompt and measure pass@1 delta on the 219 tasks — cheapest, highest-information experiment; no mining needed.
2. **Build the hazard filter** (REPORT.md §F4) and sweep all 93 zero-pass tasks to estimate the artifact fraction: flag solution patches that regenerate fixtures/keys/snapshots, add test-only dev-deps present only in the withheld manifest, or rewrite default-value assertions. (Patches are local: `DepBench/dataset/tasks/*/solution/`, `*/tests/test.patch`.)
3. Prototype **symbol-indexed sibling retrieval** for one ecosystem (npm): for a package boundary, index sibling diffs by changed API symbols rather than PR title; validate recall on the spl-token case where title-recall was 0.
4. Prototype **upstream-test-diff mining** (diff library's own test suite between the two tags) on Cases 2/4/5 packages; check it surfaces the 50,000-iterations, TokenAccountNotFoundError, and RFC7797 facts automatically.
5. If writing the paper: integrate REPORT.md findings F1–F5 as the motivation/case-study section; the honest framing is "context is necessary but the delivery must outrank misleading visible tests."

## Blockers

- (none) — gh CLI authenticated, play.clickhouse.com reachable via local `clickhouse client --secure --host play.clickhouse.com --user explorer`. Note gh API rate limits if scaling sibling-diff fetching.

## Suggested next step

Run ablation arm 0 (re-baseline prior instruction) on the five studied tasks first as a smoke test — if any of the 4 context-complete ones flips, proceed to the full 219-task run.

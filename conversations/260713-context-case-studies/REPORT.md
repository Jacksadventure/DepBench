# Can Context Fix Dependency Updates? Five Deep-Dive Case Studies on DepBench Zero-Pass Tasks

*2026-07-13. Follow-up to `handoff/REPORT.md` (repository-mining feasibility study). Method: five parallel investigations of consensus-hard DepBench tasks, each combining (1) ground-truth patch forensics, (2) failed-trajectory analysis, (3) upstream-repository mining, and (4) GHArchive sibling-PR mining — all under time-travel discipline: only evidence dated **before the task PR's creation time** counts. Full per-case evidence, URLs, quoted hunks, and ClickHouse queries in `cases/*.md`.*

---

## 1. Question and case selection

The handoff report hypothesized that the binding constraint on agentic dependency-upgrade repair is **context acquisition** — per-upgrade breaking-change knowledge and cross-repo repair exemplars — and proposed mining pipelines (Ideas A–E). This study stress-tests that hypothesis at the individual-task level: for real tasks that *every* benchmark configuration failed, was the needed knowledge actually obtainable **before the PR was even created**, and would injecting it plausibly have flipped the outcome?

From the 93 DepBench tasks unsolved by all 10 model×harness configurations (48 npm, 15 cargo, 13 go, 12 maven, 5 pip), five were chosen for diversity in ecosystem, sibling-population size, and breaking-change class:

| # | Case | Package & boundary | Eco | PR created (cutoff) | Shape |
|---|------|--------------------|-----|---------------------|-------|
| 1 | [nearform/brokeneck#820](https://github.com/nearform/brokeneck/pull/820) | react-router-dom 5.3.0→6.4.1 | npm | 2022-09-22 | huge-sibling, guide-rich major |
| 2 | [solana-labs/solana-program-library#4301](https://github.com/solana-labs/solana-program-library/pull/4301) | @solana/spl-token 0.1.8→0.3.7 | npm | 2023-05-15 | full API rewrite; upstream is the **same monorepo** |
| 3 | [actix/actix#554](https://github.com/actix/actix/pull/554) | syn 1→2 | cargo | 2023-07-23 | canonical proc-macro migration, massive siblings |
| 4 | [nuts-foundation/nuts-node#426](https://github.com/nuts-foundation/nuts-node/pull/426) | lestrrat-go/jwx 1.1.2→1.2.6 | go | 2021-08-24 | silent behavioral change (RFC7797), long-tail siblings |
| 5 | [dschadow/JavaSecurity#236](https://github.com/dschadow/JavaSecurity/pull/236) | shiro-core 1.13.0→2.0.1 | maven | 2024-05-31 | fresh major (59 min old!), behavioral-defaults change |

## 2. Case capsules

**Case 1 — react-router-dom 5→6 (brokeneck).** Eleven repair facts (Switch→Routes, element prop, useHistory→useNavigate, props→useParams, …). *All* code-level facts were verbatim in the upstream `docs/upgrading/v5.md`, in-tree since v6.0.0 (2021-11-03). GHArchive: **1,172** sibling 5→6 bump PRs pre-cutoff, 204 with human repair commits; exemplars found containing the literal needed hunks (udovin/solve-web#24; microsoft/accessibility-insights-web#4989 migrates source *plus 5 test files* in one PR). Trajectory forensics: both examined agents **knew every fact** — one fetched the official upgrade guide mid-run — yet kept components prop-based with compat shims **to satisfy the visible v5-era tests**; the hidden oracle then enforced canonical v6 idiom (hooks inside routed components). Verdict: context-complete, failure is oracle-idiom prediction.

**Case 2 — @solana/spl-token 0.1→0.3 (stake-pool/js).** The 0.2.0 rewrite deleted the `Token` class. Migration guide, complete new source, and tests demonstrating every replacement idiom sat **in the same monorepo** (`token/js/`, two directories away) and in the installed `node_modules` (README FAQ ships in the tarball). Both examined agents read the typings, migrated the mechanical facts correctly, then **deliberately preserved legacy semantics** (re-wrapped errors, RPC-probe + non-idempotent ATA create) because the 17 visible tests demand exactly that; the hidden tests invert those assertions (TokenAccountNotFoundError propagation, getAccountInfo 2→1 calls, 2→3 instructions). Title-based sibling mining: 14 bump PRs, **0 with repair signal**; the real exemplars are manually-titled migration PRs (metaplex-program-library#299, marinade-ts-sdk#35) — evidence for symbol-based retrieval. Verdict: context-complete (in-repo!), failure is deliberate legacy-preservation to please the visible oracle.

**Case 3 — syn 1→2 (actix).** The famous proc-macro migration. **9/10 configs performed the semantic syn-2 migration correctly** and passed all visible tests; they failed verification only because the hidden `tests/trybuild.rs` needs `trybuild`/`rustversion` dev-dependencies that exist solely in the withheld manifest patch. syn 2.0.0 release notes (2023-03-18) document the removals verbatim; the undocumented details (`MetaNameValue.value: Expr`, `path()` accessor) appear in dtolnay's own same-day migrations of serde/thiserror/async-trait. GHArchive: ~**717** syn-1→2 merged PRs across 323 repos pre-cutoff. The single artifact containing the decisive missing fact (the dev-dep convention) is a **same-maintainer sibling**, actix-net#481 (2023-04-01), which also contains the identical migration hunks. Side finding: the task's byte-exact trybuild `.stderr` oracle is silently dead in the container (rustversion gates on 1.65; container runs 1.96). Verdict: knowledge gap ≈ zero; the residual gap is project test-scaffolding convention, minable only from same-org siblings.

**Case 4 — jwx 1.1.2→1.2.6 (nuts-node).** Three facts: a compiler-surfaced option-type change (everyone fixed it); a silent RFC7797 behavioral change (`b64:false` payloads must not contain "." — sign the base64url-encoded challenge) that was **explicitly documented in the upstream Changes file and quoted in the Dependabot PR body itself**; and regenerated test fixtures — the human minted a **fresh random EC key on PR day**, whose IDs land in 6 hidden test files while the matching `testKID` constant lives in source. No agent can derive a random key: **the task is structurally unsolvable**, and the oracle is anti-correlated (the F1-only lazy fix goes green locally; the ground-truth repair would fail the visible tests). gpt-5.5 rediscovered the behavioral change from the module cache, shipped a correct repair, scored 0. Siblings: long-tail (8 repos crossed 1.1→1.2 pre-cutoff; the one repair-bearing sibling shares zero facts with this task — and nuts-node adopted v1.2.6 on release day, so no sibling *could* have hit the v1.2.5 change yet). Verdict: harness-limited, not context-limited.

**Case 5 — shiro 1.13→2.0.1 (JavaSecurity).** Package relocations (compile-visible; exact hunks in four pre-cutoff sibling PRs: flowlogix#692, Waffle#2278, Graylog#18430, jena#2302) plus a behavioral-defaults change: Shiro 2's `DefaultHashService` ignores per-service iteration config; the hidden test asserts the new default **50,000** iterations where the visible test asserts 1,000,000. Both frontier agents **decompiled the jars and literally printed `DEFAULT_ITERATIONS = 50000` into their context** — then re-pinned 1M via `SimpleHash.iterations` to honor the visible test. No official migration guide existed at cutoff (maintainer confirmed in July 2024: "there is no migration guide currently"); 2.0.1 was **59 minutes old** when Dependabot filed the PR — zero 2.0.1 siblings by construction. A same-repo signal existed: the owner had closed Dependabot's earlier 2.0.0 bump unmerged. Verdict: facts fully discovered by agents; failure is an evidence-weighting/policy gap ("re-baseline to new defaults"), which no per-dependency mining supplies as a *fact*.

## 3. Cross-case findings

### F1. The dominant blocker is evidence weighting against misleading visible tests — not context retrieval.

In **4 of 5** cases (all but the unsolvable jwx fixtures), agents *possessed or personally discovered* the decisive breaking-change facts — from upgrade guides fetched mid-run (Case 1), typings in node_modules (Case 2), model priors (Case 3), the Go module cache (Case 4), and jar decompilation (Case 5) — and then either shipped the correct fix and were failed by scaffolding (Case 3), or **actively chose the legacy-compatible repair because the visible tests encode pre-upgrade semantics**. The shiro agents printing the correct constant and then coding the wrong one is the purest specimen. This refines the handoff report's framing: DepBench's hidden/visible test split doesn't merely *hide* the oracle — for behavioral changes it makes the visible suite **adversarial context**, and a well-disciplined agent that trusts tests is punished precisely for that discipline.

Consequence for the research agenda: breaking-change cards (Idea B) and exemplar diffs (Idea A) are necessary but demonstrably insufficient. The injected context must carry **authority over the visible tests** — an explicit prior of the form *"this is an upgrade task; post-upgrade suites re-baseline to the library's new defaults and idioms; migrate tests together with source rather than shimming around them."* In all four context-complete cases, that single policy sentence plus the facts the agents already had would plausibly have flipped the outcome.

### F2. Pre-PR knowability is high for facts, and stratifies cleanly by source.

| Knowledge class | Where it was available pre-PR | Cases |
|---|---|---|
| Documented API removals/renames | Release notes, in-tree migration guides (some ship in the npm tarball → already in `node_modules`) | 1 (all 11 facts), 3 (core removals), 4 (RFC7797 — even quoted in the Dependabot PR body) |
| Undocumented API details | Upstream-authored migrations of the maintainer's other crates; upstream's own tests at the new tag | 3 (serde/thiserror same-day PRs), 5 (`DefaultHashServiceTest.groovy` shows the exact target idiom), 2 (`account.ts`, e2e tests) |
| Mechanical rewrite exemplars | Sibling bump-PRs with human follow-up commits | 1 (204 repair siblings), 3 (~717 PRs/323 repos), 5 (4 relocation-hunk siblings) |
| Project conventions (test scaffolding, dev-deps) | **Only same-org / same-maintainer siblings** | 3 (actix-net#481 is the *sole* pre-cutoff source of the decisive fact) |
| Behavioral re-baseline decision (what the post-upgrade tests will assert) | Partially: upstream test diffs show upstream's own re-baseline; the *client's* choice is a prior, not a fact | 2, 5 (upstream tests exhibited the new idiom/defaults) |
| Regenerated random fixtures | Nowhere, by construction | 4 |

The stratification validates the handoff report's coverage prediction (Idea A dominates high-sibling strata, Idea B the long tail) but adds two tiers it missed: **same-org siblings** as a uniquely privileged source (conventions), and **upstream test diffs** as the mineable witness of behavioral re-baselines — upgrading them from "nice-to-have" (Idea B step 2) to load-bearing.

### F3. Sibling-population size varies over three orders of magnitude, and title-based recall can be zero even when exemplars exist.

Measured strata at cutoff: react-router 5→6 **1,172** (204 with repair signal); syn 1→2 **~717 PRs / 323 repos**; shiro 1.x→2.0.0 **~20** in the 93-day window (4 with code repairs, **0** for the 59-minute-old 2.0.1); jwx 1.1→1.2 **8** (1 repair, zero fact-overlap with the task); spl-token **14 with 0 repair signal** — although rich exemplars existed under *manual* titles (metaplex#299, marinade#35). Two pipeline implications: (a) retrieval must be **symbol-based** (index diffs by changed API symbols of package P), not bump-title-based, or it silently misses whole ecosystems like the Solana one where naive bot bumps get reverted and real migrations are hand-authored; (b) the freshness cliff is real — for upgrades adopted within days of release (Cases 4, 5: same-day and 59-minute adoption), the sibling channel is empty *by construction* and upstream-side mining is the only channel. Fast Dependabot adoption correlates with exactly the repos that need context most.

### F4. Two of five "consensus-hard" tasks are wholly or partly benchmark artifacts.

- Case 4 is **unsolvable**: hidden fixture regeneration with a random key, entangled with a source-side constant. The oracle is anti-correlated with local verification.
- Case 3's zero is a **scaffolding artifact**: 9/10 correct migrations failed for two missing dev-dependency lines that only the withheld manifest patch contains; additionally its `.stderr` oracle is dead in the shipped container.
- Cases 1, 2, 5 are *by-design* oracle traps (hidden tests contradict visible tests), which is defensible as a benchmark of "true upgrade semantics" but means the measured construct is partly *"predict the maintainer's test rewrite"* rather than *"repair the upgrade."*

For DepBench-XL mining (handoff §7.2), add a hazard filter: flag human repair commits that (i) regenerate fixtures/keys/snapshots, (ii) add dev-dependencies used only by test files in the hidden split, or (iii) rewrite assertions on library defaults — and either move the entangled artifacts to the same side of the split or annotate the task. For the *paper*, the honest headline is that consensus-hard ≠ context-hard: our five-case audit suggests a nontrivial fraction of the 93 zero-pass tasks would remain unsolved under perfect context injection for reasons unrelated to knowledge.

### F5. The cheapest unexploited context sources are already attached to the PR.

Three low-tech findings worth stating plainly: (1) the Dependabot PR body **already quoted the decisive changelog line** in Case 4 — agents never see it because DepBench tasks (rightly) don't include the PR, but a production dep-update agent gets it for free; (2) the package's own tarball ships migration FAQs into `node_modules` (Case 2) — a `README`-of-installed-package lookup is nearly free; (3) same-repo history carries signals (Case 5's closed-unmerged 2.0.0 bump; Case 2's monorepo upstream two directories away). A production system should exhaust these before any cross-repo mining.

## 4. Revised design implications for the mining agenda

1. **Idea B (breaking-change cards): keep, but demote from "sufficient" to "floor."** All five cases confirm cards are constructible pre-PR (even for the 59-minute-old shiro 2.0.1 — from upstream code and tests alone). But four cases show cards alone don't flip outcomes.
2. **Idea A (sibling exemplars): keep, with two upgrades.** Index by **changed-symbol**, not title (Case 2's zero-recall lesson); rank **same-org/same-maintainer siblings first** (Case 3's actix-net#481 was uniquely decisive). Extract not just source hunks but **test-file hunks** — "how did humans rewrite their tests in this upgrade" is the direct answer to the oracle-idiom problem.
3. **New: the re-baseline prior (policy, not fact).** A single harness-level instruction — *treat the upgraded library's new defaults/idioms as the specification; migrate tests with source; do not shim to preserve pre-upgrade assertions* — attacks the failure mode observed in Cases 1, 2, 5 and costs nothing to deploy. This is the cheapest experiment available and should be **arm 0** of the DepBench ablation, ahead of any mining: it isolates how much of the 46.8% "visible-test overfitting" (handoff §1.2) is prompt-fixable.
4. **Upstream test diffs are the mineable witness of behavioral change** (Cases 2, 4, 5): diffing the library's own test suite between tags surfaces exactly the re-baselined assertions (50,000 iterations; TokenAccountNotFoundError; RFC7797 error). This is automatable and long-tail-safe — it needs no siblings.
5. **Evaluation hygiene:** before running ablations on the 93 zero-pass tasks, run the F4 hazard filter; report uplift separately for context-limited vs. harness-limited tasks, or the measured effect of context injection will be biased downward by unsolvable tasks.

## 5. Limitations

Five cases, purposively (not randomly) sampled, favoring popular libraries; trajectory forensics examined 1–2 of 10 configs per case; sibling counts depend on GHArchive title heuristics (lower bounds except where symbol-search supplemented); "would have flipped" verdicts are counterfactual judgments, not reruns — the natural next step is the arm-0/arm-A/arm-B rerun proposed in §4.3 and handoff §5. All per-case evidence chains, exact ClickHouse queries, sibling PR lists with dates, and quoted upstream sentences are in `cases/`:

- `cases/nearform__brokeneck__820.md`
- `cases/solana-labs__solana-program-library__4301.md`
- `cases/actix__actix__554.md`
- `cases/nuts-foundation__nuts-node__426.md`
- `cases/dschadow__JavaSecurity__236.md`

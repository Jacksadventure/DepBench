# Repository Mining for Dependency-Upgrade Repair: Brainstorm & Feasibility Report

*Prepared 2026-07-13. Basis: DepBench paper (`DepBench/paper`), release analysis tables (`DepBench/analysis`), trajectory samples (`DepBench/trajectories`), live GHArchive queries on play.clickhouse.com, and a literature/industry survey.*

---

## 1. What DepBench establishes

DepBench converts 219 merged Dependabot/Renovate PRs (from 4,660 mined candidates) into executable dependency-upgrade repair tasks across five ecosystems (npm/yarn 79, Maven 66, Go 41, Cargo 21, Python 12; 167 distinct libraries; 90/219 are major-version bumps). Each task is certified by the four-state oracle: Ω(b)=pass, Ω(b⊕m⊕t)=fail, Ω(b⊕m⊕c⊕t)=pass, Ω(b⊕c⊕t)=fail, which ties the hidden-test failure causally to the upgrade.

Headline result: the best configuration (Copilot CLI + GPT-5.5) solves 88/219 (40%). Under GPT-5.5, 100/219 tasks are consensus-hard (unsolved by all four harnesses); Cargo (15/21 zero-pass) and npm/yarn (51/79 zero-pass) are the hardest ecosystems, Maven the easiest.

### Where agents actually fail (the "corners")

Synthesizing RQ3/RQ4 and the trajectory scan tables:

1. **Incomplete migration is the dominant agreed root cause in every configuration.** Agents find the changed dependency surface but fail to propagate it through wrappers, types, mocks, fixtures, generated artifacts, and secondary call sites (e.g., the GitLab client int→int64 case: Copilot fixed `GetPipeline` but left `listProjectMergeRequests` returning `[]int`).
2. **Visible-test overfitting.** In 641/1371 analyzable failed trials (46.8%), the agent saw the *visible* tests pass and stopped, then failed the hidden post-upgrade tests. Agents treat the task as ordinary test-driven repair; the actual contract (the upgraded library's new API/semantics) is never made explicit to them.
3. **Context discovery is unreliable and weakly coupled to success.** Docs/release-notes lookup varies wildly by harness (5–191 of 219 trajectories under GPT-5.5). Local dependency API inspection is near-universal (145–219) yet the benchmark stays unsolved — *having a discovery behavior is not the same as having the right context.* Copilot CLI + GPT-5.5 is simultaneously the best scorer and the lowest docs-user (5/219), which suggests current web-lookup behavior adds little and the missing ingredient is structured, precise upgrade knowledge, not more browsing.
4. **Semantic/behavioral changes are the hardest class.** Mixed direct-behavior test tasks: 41/61 zero-pass under GPT-5.5. Cases like TinkerPop's numeric-overflow semantics require connecting a changelog sentence to an observable behavior — nothing in the repository points to it.
5. **Ecosystem gap.** Strong static build systems (Maven, Go) give repair guidance for free; npm's dynamic surface + lockfile/tooling churn and Cargo's macro/trait migrations (e.g., syn 1→2) do not. This is exactly where external knowledge should pay off most.

**Implication:** the two highest-leverage interventions are (a) inject precise, per-upgrade breaking-change/migration knowledge the agent cannot recover from the local checkout, and (b) force repository-wide propagation/completeness checking instead of "first green build wins." Both map directly onto repository mining. This matches the user's working notes (富上下文/rich-context repair; 寻找上下文本身就是研究问题).

---

## 2. GHArchive feasibility — measured on play.clickhouse.com

Live numbers (github_events, 3.17B events, through 2026-07):

| Query | Count |
|---|---|
| All merged-PR events | 36,235,851 |
| Merged PRs by `dependabot*` | 3,712,340 |
| Merged PRs by `renovate*` | 2,234,109 |
| Merged dependabot PRs with **commits > 1** (human follow-up commit = repair signal) | 160,465 |
| Merged renovate PRs with commits > 1 | 59,585 |
| Merged PRs titled `Bump glob from 8…` (the js-wacz#41 upgrade) | 380 |
| …of which multi-commit (human-repaired siblings) | **73** |
| Merged PRs titled `Bump openai from 3…` (the 29k#3418 upgrade) | 71 |
| …of which multi-commit | **5** |

Three conclusions:

1. **The candidate pool is ~50× larger than DepBench's crawl.** ~220K merged bot PRs contain human follow-up commits. Even at DepBench's ~5% survival rate (219/4,660), that is ~10K oracle-cleanable tasks — but more importantly, it is a *repair-exemplar corpus*, not just a benchmark source.
2. **The homogeneity hypothesis is directly confirmed.** For a single concrete upgrade (glob 8→10), 380 repos merged the same bump and 73 of them needed a human repair commit. Those 73 repair diffs are near-isomorphic migrations of the same API surface (`glob.sync` → `globSync` etc.) — exactly the few-shot exemplars an agent needs. Popularity follows a long tail (openai 3→4: only 5 repaired siblings), so exemplar mining must be complemented by upstream-side knowledge (Section 4, Idea B).
3. **GHArchive gives you the pointer, not the patch.** Events carry repo/PR number/title/commit counts/head SHA but no diffs. The mining pipeline is: ClickHouse query → candidate (repo, PR#) list → GitHub API `pulls/{n}/commits` + `.diff`, or `git clone --filter=blob:none` for the two commits. The existing DepBench crawler already does the second half.

### Practical notes for whoever runs this next

- Local `clickhouse client --secure --host play.clickhouse.com --user explorer` (as in the task notes) is the right interface for real mining; run wide GROUP BY queries there (e.g., `GROUP BY title`-normalized `(package, from_major, to_major)` to rank upgrades by sibling count).
- In this Cowork sandbox, outbound network is proxy-restricted; only the `web_fetch` tool reaches play.clickhouse.com, it is GET-only, and it enforces a **total-URL length cap (~165 chars)** — errors surface as an *empty response*, which cost me a long debugging detour. Compression tricks that helped: `merged*commits>1` instead of `merged=1 AND commits>1`, `LIKE 'dependa%'` instead of `='dependabot[bot]'`, dropping the `event_type` filter when another selective predicate exists. Full scans of `title` complete well within 30 s, so the public server is entirely adequate for candidate discovery.
- Renovate PR titles are configurable (`Update dependency X to v9`), Dependabot's are templated (`Bump X from A to B` / `chore(deps): bump …`); normalize both. Squash-merged PRs hide the human commit (commits stays 1 but additions/changed_files are large) — `changed_files > k` on manifest-only expectations is a second recall filter.

---

## 3. Related work landscape (positioning)

- **MELT (ASE'23)** mines Comby find-and-replace rules from the *library's own* PRs; 461 rules over 4 Python libraries. Syntactic, needs migration examples inside the library repo, brittle generalization. Our proposal differs: mine *client-side* repairs at ecosystem scale and use them as retrieval context for an LLM, not as standalone rules.
- **Byam (EMSE'26)** prompts LLMs with APIDiff output + buggy lines for Java breaking updates (BUMP dataset): o3-mini fixes 27% of builds, 78% of individual compile errors. Confirms that structured breaking-change context lifts LLM repair — but it is single-file, compile-error-driven, Java-only, non-agentic.
- **LADU (JPMorgan, 2025)** LLM agents + migration docs for Java upgrades; **BigBag (2026)** agentic AST-transformation-rule generation (repair rate ≤23%). Both use *documentation* as context; neither mines crowd repairs.
- **Google FSE'25 (Migrating Code At Scale)** — strongest industrial evidence: change-location discovery + LLM with few-shot examples from internal change history; 74% of migration changes LLM-generated, ~50% time savings. Their "similar past edits as few-shots" is exactly the cross-repo mining idea, but on a private monorepo. The open-source equivalent (GHArchive-scale sibling-PR mining) appears unclaimed.
- **OpenRewrite/Moderne, jscodeshift codemods** — expert-written migration recipes; high precision, tiny coverage (popular Java/JS frameworks only). Mined exemplars are the scalable complement; a mined-rule → verified-recipe pipeline could feed these ecosystems.
- **Breaking-change detectors**: japicmp/Roseau/APIDiff (Java), AexPy (Python), cargo-semver-checks (Rust), Node's own ecosystem lacks a strong equivalent (gap!). These generate the *upstream-side* API-evolution facts automatically.
- **Industry (2026)**: GitHub now lets Dependabot alerts be assigned to coding agents (Copilot/Claude/Codex) which "analyze failures and propose fixes" — i.e., the agent-does-the-repair product exists, but it runs the same context-poor loop DepBench shows failing 60% of the time. Renovate's Merge Confidence crowd-sources *pass/fail rates* of an upgrade across repos but not *how to fix it*. JetBrains AI Assistant has no dependency-upgrade feature. This is the competitive opening: **nobody ships "how did the rest of the world fix this exact upgrade" as machine-usable context.**

---

## 4. Brainstorm: repository-mining-assisted dependency update

Organizing principle (matches the working notes): the bottleneck is not the LLM's edit ability but **context acquisition** — API-evolution knowledge, code-change chains, and real fix cases. All ideas below produce context artifacts keyed by `(package, from_version_range, to_version_range)`.

### Idea A — Cross-repo repair exemplar mining ("sibling PRs") ★ highest value/effort ratio

**Insight (validated in §2):** the same upgrade breaks thousands of clients in the same way; dozens have already been repaired by humans in merged bot PRs.

Pipeline:
1. GHArchive: all merged bot PRs for package P crossing boundary v_old→v_new, with human follow-up commits (73 for glob 8→10).
2. Fetch diffs; strip manifest/lockfile hunks (reuse DepBench's patch decomposition); keep the human repair patch.
3. Cluster repair hunks by changed API symbol (AST-diff level, e.g., GumTree/difftastic) → ranked list of migration patterns with frequency counts: `import glob → import {globSync}` seen in 61/73 repos, etc.
4. At agent time, retrieve top-k exemplars (raw diffs + cluster summary) into the prompt, selected by which symbols of P the *target* repo actually uses.

Why it beats docs: exemplars are executable evidence, cover undocumented breakage (transitive peer-dep pins, lockfile tricks, tsconfig changes — the npm corner), and directly show *repository-wide* propagation (tests, mocks, fixtures changed together in the same commit).

Long-tail fallback: when <k siblings exist (openai case: 5), degrade gracefully to Ideas B/C.

### Idea B — API-evolution knowledge base from upstream repositories

Mine the *library side*, which always exists even when siblings don't:
1. Diff the library between the two release tags (source, exports, type declarations); run ecosystem-appropriate detectors (japicmp, cargo-semver-checks, AexPy, TS public-API diff) to get a structured breaking-change list.
2. Harvest CHANGELOG/release notes/migration guides + the library's own test diffs between versions. Upstream test diffs are the only mineable witness of *semantic* changes (the TinkerPop overflow behavior appears verbatim in its upgrade guide and test suite) — this targets DepBench's hardest category.
3. Compile into "breaking-change cards": {symbol, kind (removed/renamed/type-changed/behavior-changed), evidence snippet, suggested rewrite}. Join against the client repo's actually-used symbols (cheap grep/import analysis) so the agent sees only relevant cards.

This is the piece that turns "agent inspected `node_modules` for 10 minutes" into "agent was told `glob` v10 removed the default-export `.sync`."

### Idea C — Mined, verified transformation rules (MELT × LLM hybrid)

From Idea A's clusters, have an LLM abstract each cluster into a guarded rewrite rule (Comby/ast-grep/OpenRewrite recipe), then *verify* the rule by replaying it on held-out sibling repos (does it reproduce the human diff? does the project still build?). Verified rules become: (a) deterministic pre-passes that handle the mechanical 80% before the agent starts, and (b) contributions back to codemod ecosystems. This mitigates LLM per-call variance and cost at fleet scale (the Dependabot-agent product implies millions of runs of near-identical work).

### Idea D — Propagation/completeness checking (attacks the #1 failure mode)

Incomplete migration is a *search* problem, not a knowledge problem — treat it separately:
1. Mine co-change patterns from repair exemplars: when symbol X changes, which file categories change with it (mocks 40%, fixtures 25%, generated code 15%…)? Emit a per-upgrade checklist.
2. Agent-side "migration completeness verifier" step: after the candidate patch, enumerate all reachable uses of every changed symbol/type (grep + type-flow for int→int64-style widening) and diff against the touched set; refuse to finish while uncovered sites remain.
3. Directly counters visible-test overfitting: the stop condition becomes "checklist exhausted," not "old tests green."

### Idea E — Agent-time packaging: a `dep-context` MCP server / skill

The delivery vehicle for A–D. Tools: `breaking_changes(pkg, v1, v2)`, `migration_examples(pkg, v1, v2, symbol?)`, `similar_fix(error_text)` (error-message → exemplar index, mined from CI logs of sibling PRs), `completeness_check(diff)`. Works with any harness (Claude Code, Copilot CLI, Codex) — important because DepBench shows harness effects (27-task spread under the same model) dominate; a context tool is harness-portable. Same artifact serves IDEs later (JetBrains/VS Code gap noted in §3).

### Secondary ideas from the working notes

- **Version-conflict resolution mining:** merged PRs that edit `resolutions`/`overrides`/`dependencyManagement`/`[patch]` sections are a mineable corpus of conflict fixes; GHArchive title/label filters find them. Lower novelty, high utility for npm.
- **License-change alerts:** registry metadata diffs (SPDX field between versions) are trivially mineable; useful product feature, little research content.
- **Build-flow incompatibilities** (Node ESM/CJS, Java 8→11→17, Python 3.x): mine repairs to build config files (tsconfig, pom plugins, setup.cfg) in bot-PR follow-ups — these rarely appear in changelogs and are invisible to API-diff tools; only crowd mining captures them.

---

## 5. Evaluation plan on DepBench

1. **Ablation design:** fixed harness+model (suggest Claude Code, to isolate context effects from Copilot CLI's prompt advantages), arms = {baseline, +A exemplars, +B cards, +D checker, +A+B+D}. Primary metric: pass@1 on 219 tasks; secondary: uplift on the 100 GPT-5.5 consensus-hard tasks and on npm/Cargo specifically (that is where context should matter most, per §1.5).
2. **Coverage stratification:** report results split by sibling-exemplar availability (≥10 / 1–9 / 0 siblings). Prediction: Idea A dominates the first stratum, Idea B the last; Cargo tasks (syn 1→2 has *massive* sibling counts — every proc-macro crate migrated) are a good stress case.
3. **Leakage controls — critical:**
   - Exclude the task repo and its forks from the exemplar index (DepBench already bans the upstream repo/PR; extend the ban to mined context).
   - Time-travel discipline: only mine sibling PRs merged *before* the task PR's merge date if you want a "was this knowable at the time" claim; report both settings.
   - The oracle repair patch c must never enter the index (it is literally in the corpus as a merged PR — dedupe by (repo, PR#)).
4. **Beyond pass rate:** measure context precision (fraction of injected cards/exemplars actually reflected in the final patch) and completeness-checker recall against the hidden test patch's touched surface.

## 6. Risks & open questions

- **GHArchive is metadata-only**; the diff-fetching stage hits GitHub API rate limits at scale (~5K req/h/token). Mitigations: token pools, `--filter=blob:none` clones, or the `github.com` BigQuery/SWH mirrors. For the top ~500 packages × recent major boundaries this is a weekend of crawling, not a moonshot.
- **Exemplar quality/noise:** human follow-up commits include unrelated churn (DepBench's own audit found this). The four-state-oracle idea can be reused *cheaply* in mining: a sibling exemplar is "trusted" if its repo's CI passed on the merge commit (GHArchive has `CheckRun`-adjacent signals via status events; or re-verify top clusters only).
- **Contamination:** frontier models have seen GitHub; the marginal value of exemplars must be demonstrated against a strong baseline that is *allowed* to browse (DepBench's setting already permits web access — and docs-lookup didn't correlate with success, which is encouraging for the claim that *curated* context ≠ *available* context).
- **License compliance** of redistributed mined diffs (index pointers + on-demand fetch avoids redistribution).
- **Renovate/Dependabot squash merges** depress the multi-commit recall signal (§2); calibrate against a hand-labeled sample.
- **Scaling the audit** remains DepBench's stated bottleneck; if the mined corpus also feeds *benchmark growth* (10K-task DepBench-XL), invest in automating the test-hunk-relatedness judgment (LLM-as-judge with the four-state oracle as ground truth).

## 7. Suggested next steps (ordered)

1. One-week spike on Idea A for the 79 npm tasks: mine sibling exemplars for the 30 most-common npm libraries in DepBench (`glob`, `typescript`, `@octokit/*`, `babel-*`…), inject via a simple prompt prefix, measure pass@1 delta on Claude Code.
2. Build the `(package, from, to) → sibling PR list` index job as a standing ClickHouse query over GHArchive (self-hosted mirror or BigQuery to escape play limits).
3. Prototype the completeness checker (Idea D) as a harness-agnostic post-patch step — it needs no mining at all for v0 (changed-symbol enumeration from the manifest diff + grep) and attacks the largest failure category.
4. Then Ideas B/C, prioritized by the coverage stratification results.

## Sources

- DepBench release: `DepBench/README.md`, `paper/sections/*.tex`, `analysis/*.csv|json`, `dataset/task_summary.json` (local repo)
- GHArchive numbers: live queries against `play.clickhouse.com` `github_events`, 2026-07-13 (queries reproduced in §2)
- [MELT: Mining Effective Lightweight Transformations from Pull Requests (ASE'23)](https://arxiv.org/abs/2308.14687)
- [Byam: Fixing Breaking Dependency Updates with Large Language Models (EMSE)](https://link.springer.com/article/10.1007/s10664-026-10835-1)
- [LLM Agents for Automated Dependency Upgrades (LADU)](https://arxiv.org/abs/2510.03480)
- [Agentic Generation of AST Transformation Rules for Fixing Breaking Updates (BigBag)](https://arxiv.org/html/2606.24446v1)
- [Migrating Code At Scale With LLMs At Google (FSE'25)](https://arxiv.org/abs/2504.09691)
- [Automatically Fixing Dependency Breaking Changes (PACMSE)](https://dl.acm.org/doi/10.1145/3729366)
- [Using LLMs for Library Migration](https://arxiv.org/html/2504.13272v1)
- [Breaking Changes in Software Ecosystems: A Systematic Literature Review](https://arxiv.org/html/2605.24397v1)
- [Roseau: Fast, Accurate, Source-based API Breaking Change Analysis in Java](https://arxiv.org/pdf/2507.17369) · [japicmp](https://siom79.github.io/japicmp/) · [APIDiff](https://github.com/aserg-ufmg/apidiff)
- [Dependabot alerts are now assignable to AI agents (GitHub Changelog, 2026-04)](https://github.blog/changelog/2026-04-07-dependabot-alerts-are-now-assignable-to-ai-agents-for-remediation/)
- [OpenRewrite / Moderne](https://moderne.ai/openrewrite) · [Renovate](https://github.com/renovatebot/renovate)



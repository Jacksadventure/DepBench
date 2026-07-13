# Follow-up Design: A Context-Authority System for Dependency-Upgrade Repair

## 0. Independent critique of the current direction

I disagree with the framing that the next milestone is primarily a **retrieval** system. The July 13 evidence shows that the binding constraint is usually not missing text; it is missing **authority structure**.

Across the five audited zero-pass tasks, the decisive breaking-change facts were already obtainable—sometimes literally inside the checkout—yet agents still failed:

- **react-router-dom 5→6**: agents fetched the official upgrade guide and applied most facts, then built v5-compat shims because the visible tests mocked `useHistory`. The hidden oracle wanted the canonical v6 idiom.
- **@solana/spl-token 0.1→0.3**: agents read the installed package source and typings, then preserved legacy error-wrapping and the RPC probe to keep visible tests green. The hidden oracle wanted the new idiomatic behavior.
- **shiro 1.13→2.0.1**: agents decompiled the jar and printed `DEFAULT_ITERATIONS = 50000`, then hard-coded `1,000,000` to match the visible test.
- **syn 1→2**: 9/10 agents executed the migration correctly and passed visible tests; they failed on two hidden dev-dependency lines that only the withheld manifest patch contained.
- **lestrrat-go/jwx 1.1→1.2**: the failure is a regenerated random EC key hidden in `test.patch`; no pre-PR context can supply it.

The paper's RQ3/RQ4 diagnosis is consistent: the dominant failure mode is **incomplete migration** combined with **visible-test overfitting** (46.8% of analyzable failed trials passed visible tests before hidden verification failed). Agents inspect documentation and local APIs frequently but do not propagate the upgrade contract repository-wide, and they treat visible tests as ground truth even when those tests encode pre-upgrade semantics.

Therefore, the research product should not be "a system that retrieves more upgrade context." It should be **a system that retrieves the *right* context, weights it correctly against misleading local signals, propagates it repository-wide, and knows when to stop.** Mining is a sub-system, not the thesis.

---

## 1. Product/research thesis and falsifiable hypotheses

### Thesis

> **Dependency-upgrade repair is an evidence-weighting and propagation problem before it is a knowledge-retrieval problem.** A useful agent must (a) hold a re-baseline prior that treats the upgraded library's new defaults and idioms as the specification, (b) retrieve upgrade evidence from upstream and sibling repositories with strict pre-target-PR cutoffs, (c) propagate every changed symbol through the target repository's source, tests, fixtures, mocks, and generated artifacts, and (d) stop only when a completeness checklist is exhausted, not when the old visible tests turn green.

### Falsifiable hypotheses

| ID | Hypothesis | How to falsify |
|---|---|---|
| **H1** | A re-baseline prior alone outperforms a sibling-exemplar-only injection on zero-pass tasks. | If adding only the prior does not improve zero-pass pass rate while adding only exemplars does, reject. |
| **H2** | Same-organization / same-maintainer siblings are strictly more useful than cross-repo siblings for project-convention facts (dev-deps, test scaffolding, build config). | If same-org retrieval does not raise convention-fact recall above cross-repo retrieval, reject. |
| **H3** | Upstream test diffs improve semantic-behavior tasks more than API-diff cards. | If adding upstream test diffs does not reduce "wrong semantic output" failures, reject. |
| **H4** | A completeness checker reduces incomplete-migration failures by ≥25%. | If failure-category counts for "incomplete migration" do not shift, reject. |
| **H5** | Symbol-based sibling retrieval outperforms title-based retrieval for long-tail dependencies. | If title-based recall ≥ symbol-based recall on the Solana/spl-token case or other long-tail tasks, reject. |

---

## 2. Mining/indexing/retrieval architecture and versioned artifact schemas

### 2.1 Source hierarchy and authority

Evidence should be retrieved from sources in this order of authority when facts conflict:

1. **Upstream test diffs** between `old_version` and `new_version` tags — the only mineable witness of behavioral re-baselines (e.g., Shiro's `DefaultHashServiceTest.groovy`, spl-token's `create.test.ts`).
2. **Same-organization / same-maintainer sibling PRs** — uniquely privileged for project conventions, dev-dependencies, and test scaffolding (e.g., `actix-net#481` supplying `trybuild = "1"`, `rustversion = "1"`).
3. **Cross-repo sibling repair exemplars** — useful for mechanical API rewrites and idioms (e.g., react-router 5→6 exemplars).
4. **Upstream release notes, migration guides, and API-diff output** — reliable for documented removals/renames but silent on semantic changes.
5. **Installed package documentation** (`README`/`FAQ` in `node_modules`, jar source, Go module cache) — nearly free, should be exhausted first.
6. **Local compiler/test feedback** — treated as an intermediate signal, not ground truth, because visible tests may encode pre-upgrade semantics.

### 2.2 Mining pipeline

```
GHArchive (PullRequestEvent) ──► candidate (repo, PR#) ──► fetch .diff ──► decompose
        ▲                                                      │
        │                                                      ▼
        └──────── World of Code (provenance, author graph) ◄── manifest / code / test hunks
                                                                   │
                                                                   ▼
                                                        AST/symbol diff (GumTree / difftastic / tree-sitter)
                                                                   │
                                                                   ▼
                                              ┌────────────────────┼────────────────────┐
                                              ▼                    ▼                    ▼
                                       breaking-change        exemplar cluster       convention note
                                            cards                (symbol-indexed)    (same-org boost)
                                              │                    │                    │
                                              └────────────────────┼────────────────────┘
                                                                   ▼
                                                        versioned artifact index
                                                                   │
                                                                   ▼
                                              retrieve by (package, from, to, changed_symbols_in_target)
```

### 2.3 Versioned artifact schemas

All artifacts are keyed by `(package_name, from_version_range, to_version_range)` and stamped with a `valid_until` / `merged_before` date.

**Breaking-change card**
```json
{
  "package": "@solana/spl-token",
  "from": "0.1.8",
  "to": "0.3.7",
  "symbol": "Token.getAssociatedTokenAddress",
  "kind": "removed",
  "replacement": "getAssociatedTokenAddressSync(mint, owner)",
  "evidence_kind": "upstream_code",
  "evidence_url": "https://github.com/solana-labs/solana-program-library/blob/token-js-v.0.3.6/token/js/src/state/mint.ts",
  "snippet": "...",
  "authority": 4
}
```

**Exemplar diff**
```json
{
  "repo": "microsoft/accessibility-insights-web",
  "pr": 4989,
  "merged_at": "2022-02-01T00:00:00Z",
  "package": "react-router-dom",
  "from": "5.3.0",
  "to": "6.2.1",
  "changed_symbols": ["Switch", "Routes", "useParams", "Route element"],
  "source_hunks": [...],
  "test_hunks": [...],
  "same_org": false,
  "build_verified": true
}
```

**Re-baseline delta**
```json
{
  "package": "org.apache.shiro:shiro-core",
  "from": "1.13.0",
  "to": "2.0.1",
  "assertion_change": {
    "old": "assertEquals(1000000, hash.getIterations())",
    "new": "assertEquals(50000, hash.getIterations())",
    "source": "upstream_test_diff",
    "url": "https://github.com/apache/shiro/blob/shiro-root-2.0.0/crypto/hash/src/test/groovy/.../DefaultHashServiceTest.groovy"
  }
}
```

**Convention note**
```json
{
  "package": "syn",
  "from": "1",
  "to": "2",
  "note": "proc-macro migrations in actix ecosystem add trybuild + rustversion dev-deps and gate trybuild tests with rustversion",
  "source": "same_maintainer_sibling",
  "repo": "actix/actix-net",
  "pr": 481,
  "authority": 2
}
```

### 2.4 Retrieval strategy

- **Symbol-based matching**, not title-based. Index every code hunk by the API symbols of the upgraded package that it touches. At agent time, compute the target repo's actually-used symbols (imports, `require`s, Maven coordinates, Go imports) and retrieve hunks that touch the same symbols.
- **Same-org boost**: multiply retrieval score by a factor (e.g., 2×) for PRs from the same GitHub organization or by authors who also committed to the target repo.
- **Freshness fallback**: for upgrades adopted within days of release (when sibling count is zero), degrade to upstream test diffs and installed-package docs.

---

## 3. Agent loop, authority ordering, contradiction handling, completeness checks, and stop conditions

### 3.1 Agent loop

```
Phase 0. Prompt injection
  - Inject the re-baseline prior:
    "This is a dependency-upgrade task. The upgraded library's new defaults and
     idioms are the specification. Migrate tests together with source; do not
     shim to preserve pre-upgrade assertions unless an authoritative source
     explicitly recommends compatibility."
  - Inject any upstream release-note summary and a warning that visible tests
    may encode pre-upgrade semantics.

Phase 1. Manifest / lockfile resolution
  - Compute and apply the dependency bump (npm/yarn: package.json + lock;
    Maven: pom; Go: go.mod + go.sum; Cargo: Cargo.toml + Cargo.lock).
  - Build. If build fails, go to Phase 2 with the failing symbol.

Phase 2. Context retrieval
  - For each compile error or changed symbol, query the artifact index.
  - Retrieve breaking-change cards, exemplar difks, upstream test diffs,
    convention notes, and re-baseline deltas.
  - Rank by authority (§2.1) and by symbol overlap with the target repo.

Phase 3. Draft migration
  - Propose source edits that apply the highest-authority evidence.
  - Prefer canonical idioms over backward-compatible shims.

Phase 4. Completeness check
  - Enumerate every reachable use of every changed symbol/type in the repo.
  - Compare to files touched by the candidate patch.
  - If uncovered sites remain, return to Phase 2.

Phase 5. Contradiction handling
  - Compare visible test assertions against re-baseline deltas and upstream test diffs.
  - If a visible assertion contradicts the upgrade evidence, flag it and trust
    the upgrade evidence; generate the migration that makes the *post-upgrade*
    assertion true.
  - Log every contradiction explicitly.

Phase 6. Shadow verification
  - Synthesize a predicted post-upgrade test set from upstream test diffs and
    sibling test hunks (where available).
  - Run build and any available tests against this predicted suite.
  - If failures persist, return to Phase 2.

Phase 7. Submit
  - Stop when completeness checklist is exhausted, no unresolved contradictions
    remain, and the shadow verification passes.
```

### 3.2 Authority ordering in contradictions

When two pieces of evidence conflict, resolve by authority tier:

| Conflict | Resolution |
|---|---|
| Visible test vs. upstream test diff | Trust upstream test diff; visible test is pre-upgrade. |
| Visible test vs. same-org sibling | Trust same-org sibling; it encodes project convention. |
| Cross-repo sibling A vs. cross-repo sibling B | Trust the one with more symbol overlap and verified build status; if tied, present both and let the LLM decide with a "canonical vs. compatibility" rubric. |
| Upstream release notes vs. upstream code/tests | Trust code/tests; release notes can be incomplete or stale. |
| Local compiler error vs. re-baseline prior | Re-baseline prior wins only when backed by authority-tier 1–3 evidence; otherwise trust the compiler. |

### 3.3 Completeness checker (repository-wide propagation)

For every changed symbol in the breaking-change set:

1. **Symbol enumeration**: find all imports, calls, type references, and string references in source, tests, mocks, fixtures, and generated files.
2. **Touched-set comparison**: compare the enumerated files to files modified in the current candidate patch.
3. **Type-flow tracing**: for type changes (e.g., `int` → `int64`), trace through interfaces, return types, and helper functions using lightweight type-flow analysis (or AST scope analysis per ecosystem).
4. **Fixture/snapshot check**: for npm tasks, also enumerate `__mocks__/`, `__fixtures__/`, `testdata/`, and snapshot files that reference the symbol.
5. **Output**: an uncovered-sites report. The agent may not stop while uncovered sites remain.

### 3.4 Stop conditions

The agent must **not** stop solely because visible tests pass. Valid stop conditions:

- Completeness checklist exhausted AND no unresolved contradictions AND shadow verification passes.
- Budget exhausted (30 minutes).
- Agent cannot resolve a build/install failure after retrieving all available evidence.

A "claim success" should be suppressed unless the completeness checker returns empty. This directly attacks the 46.8% visible-test-overfit failure mode.

---

## 4. Five-case pilot followed by npm-scale ablations and metrics

### 4.1 Pilot on the five audited cases

Automate context retrieval and agent execution for the five cases. Measure per-case:

| Metric | Definition |
|---|---|
| Fact recall | Fraction of ground-truth repair facts present in retrieved context. |
| Fact precision | Fraction of retrieved facts actually reflected in the final patch. |
| Authority hit | Whether the highest-authority available evidence covers the decisive fact. |
| Pass@1 | Whether the agent passes hidden verification. |
| Failure category | Same taxonomy as RQ3 (incomplete migration, wrong root cause, wrong semantic output, etc.). |

Pilot arms:

| Arm | What is injected |
|---|---|
| **A0** | Re-baseline prior only. |
| **A1** | A0 + breaking-change cards (upstream API diff + release notes). |
| **A2** | A0 + cross-repo sibling exemplars. |
| **A3** | A0 + same-org siblings. |
| **A4** | A0 + upstream test diffs. |
| **A5** | A0 + completeness checker (no extra context). |
| **A6** | Full system (A0 + A1 + A3 + A4 + A5). |

Expected pilot results (based on the case evidence):

- **react-router-dom**: A0 or A4 flips the outcome; A1 alone does not.
- **spl-token**: A0 + A4 (upstream tests showing idempotent ATA + `TokenAccountNotFoundError`) flips it; A2 title-based recall is zero.
- **syn**: A3 (same-org sibling `actix-net#481`) flips it; A1 alone does not because the decisive fact is dev-deps/test convention.
- **jwx**: No arm flips it; classify as harness-limited.
- **shiro**: A0 + A4 flips it; agents already had the factual ingredients.

### 4.2 npm-scale ablations

Scale to the 79 npm tasks in the 219-task corpus, fixed model = **Codex + GPT-5.5** (per the user's constraint).

Stratify tasks by sibling-exemplar availability:

| Stratum | Definition | Expected context channel |
|---|---|---|
| S1: high-sibling | ≥10 repair-signal siblings | Cross-repo exemplars (Idea A) |
| S2: medium-sibling | 1–9 siblings | Same-org siblings + upstream test diffs |
| S3: zero-sibling | 0 siblings | Upstream test diffs + installed docs + re-baseline prior |
| S4: fresh-release | adopted within 7 days of upstream release | Upstream test diffs only |

Arms: same A0–A6 as the pilot, plus a baseline that matches the current Codex+GPT-5.5 run.

Metrics:

- **Primary**: pass@1 on 79 npm tasks.
- **Secondary**: pass@1 on 51 npm consensus-hard tasks; pass@1 by stratum; failure-category shift (especially "incomplete migration" and "wrong semantic output"); fraction of runs with visible-test pass before hidden failure.
- **Diagnostic**: context precision/recall; contradiction-detection precision; completeness-checker false-negative rate against the hidden test patch's touched surface.

### 4.3 Analysis plan

- Report per-stratum results separately. Do not pool S1 with S3, or the measured effect of mining will be diluted.
- Report "context-limited" vs. "harness-limited" tasks separately, using the F4 hazard filter from the case study: flag tasks where the hidden patch regenerates fixtures/keys/snapshots, adds dev-deps used only by hidden tests, or rewrites assertions on library defaults.
- Use McNemar's test or bootstrap confidence intervals for pass-rate deltas.

---

## 5. Leakage/time-travel controls, benchmark hazards, and likely confounds

### 5.1 Leakage and time-travel controls

| Control | Implementation |
|---|---|
| **Pre-target-PR cutoff** | For each DepBench task with PR creation time `T`, only retrieve artifacts merged or published before `T`. Store `cutoff_ts` in every index entry. |
| **Task-repo exclusion** | Exclude the task repo, its forks, and org mirrors from the exemplar index. Use WoC or GitHub API to detect forks. |
| **Oracle-patch exclusion** | Dedupe by `(repo, PR#)` so the original human repair patch `c` never enters the index. |
| **Hold-out dev set** | Reserve a separate set of historical upgrade PRs (not in DepBench) for developing prompts and tuning retrieval; never tune on DepBench tasks. |
| **Model contamination** | Assume frontier models have seen GitHub. The baseline must also be allowed to browse; measure *marginal* value of curated context over an allowed-to-browse Codex+GPT-5.5 baseline. |
| **Hidden-test leakage** | Never index `tests/test.patch` or any file path containing `tests/`, `__tests__/`, `spec/`, etc., from the task repo. |

### 5.2 Benchmark hazards and confounds

| Hazard | Effect | Mitigation |
|---|---|---|
| **Oracle traps** | Hidden tests contradict visible tests; agents that trust visible tests fail. | This is by design, but report results with and without the re-baseline prior to isolate the effect. |
| **Unsolvable tasks** | Random fixtures/keys (jwx) or hidden dev-deps (actix) make some tasks impossible regardless of context. | Run the F4 hazard filter; exclude or annotate these in aggregate statistics. |
| **Scaffolding artifacts** | `v3-no-manifest-preapply` withholds manifest changes that hidden tests depend on (actix). | Report a "scaffolding-limited" subset separately. |
| **Freshness cliff** | Upgrades adopted within hours/days of release have zero siblings by construction. | Design the system to degrade to upstream test diffs; do not expect sibling mining to help here. |
| **Harness effects** | Copilot CLI and Codex differ by ~10 pp on the same model. | Fix the harness to Codex + GPT-5.5 for all ablations; do not mix harnesses. |
| **Title-based recall failure** | Some migrations are hand-authored under non-bump titles (spl-token). | Use symbol-based retrieval; do not rely on PR titles. |
| **Visible-test green stopping** | Agents stop at "all visible tests pass" and miss hidden failures. | Hard stop condition: completeness checklist exhausted, not visible tests green. |

### 5.3 Likely confounds to measure

- **Task difficulty**: npm is already the hardest ecosystem; improvements there may look smaller than on Maven.
- **Sibling quality noise**: human follow-up commits include unrelated churn. Filter by CI status and changed-symbol relevance.
- **Prompt length**: injecting too much context can degrade performance; cap tokens and rank aggressively.

---

## 6. What to build first, what to defer, and what would falsify the proposal

### 6.1 Build first (Weeks 1–4)

1. **Re-baseline prior injection (A0)**. Costs nothing; attacks the 46.8% visible-test-overfit failure directly. Run on the 79 npm tasks immediately.
2. **Completeness checker v0**. Needs no mining: extract changed symbols from the manifest diff + local AST/grep, enumerate all reachable uses, and refuse to stop while uncovered sites remain. Run as a harness-agnostic post-patch step.
3. **Symbol-based sibling index for high-popularity npm upgrades**. Start with the 30 most common npm libraries in DepBench (`glob`, `typescript`, `@octokit/*`, `babel-*`, etc.). Use GHArchive + `gh pr diff` + AST diff.

### 6.2 Build next (Weeks 5–10)

4. **Upstream API-diff + upstream test-diff pipeline** (Idea B, upgraded). For each `(package, from, to)`, diff the library's own tests between tags and emit re-baseline deltas.
5. **Same-organization / same-maintainer boost** using WoC author-provenance data.
6. **Contradiction handler** that compares visible tests against re-baseline deltas and logs/acts on conflicts.

### 6.3 Defer

- **Verified transformation rules (Idea C)**. High engineering cost; only worthwhile if the ablations show that the mechanical 80% is the bottleneck.
- **Full MCP server / IDE integration (Idea E)**. Productization, not research.
- **Fleet-scale cost optimization**. Wait until the research system works on DepBench.
- **Cross-ecosystem expansion beyond npm**. The 79 npm tasks are the right stress test; Maven is already comparatively solved.

### 6.4 Falsification criteria

| If this happens | Conclusion |
|---|---|
| A0 (re-baseline prior) does not improve pass rate on zero-pass tasks | The visible-test-overfit diagnosis is wrong or the prior is poorly phrased. |
| A3 (same-org siblings) does not outperform A2 (cross-repo siblings) on convention facts | The same-org authority tier should be removed or reweighted. |
| A4 (upstream test diffs) does not reduce "wrong semantic output" failures | Upstream test diffs are not the right witness of behavioral change. |
| A5 (completeness checker) does not reduce "incomplete migration" failures | The propagation problem is harder than symbol enumeration. |
| S3/S4 (zero-sibling / fresh-release) tasks show no improvement even with A4 | The architecture fails in the long-tail regime; need a different source of evidence. |
| Hazard-filtered tasks dominate the measured uplift | The benchmark, not the agent, is the bottleneck; pause and fix tasks. |

---

## Top 5 takeaways, ranked by importance

1. **Evidence weighting beats evidence volume.** The five-case audit shows agents often *had* the decisive facts yet lost because they trusted visible tests over upgrade evidence. The highest-leverage intervention is a re-baseline prior and contradiction handler, not more retrieved text.

2. **Repository-wide propagation is the technical core.** Incomplete migration is the largest failure category in every configuration. A symbol-enumeration completeness checker that refuses to stop while uncovered call sites/mocks/fixtures remain is required infrastructure.

3. **Authority must be explicit and tiered.** Upstream test diffs and same-org siblings outrank cross-repo exemplars and release notes. The agent must resolve conflicts using this hierarchy, not let the LLM average conflicting signals.

4. **The benchmark itself contains unsolvable and scaffolding-limited tasks.** At least two of the five audited cases are benchmark artifacts, not context failures. Any evaluation must separate context-limited from harness-limited tasks or the measured effect of context will be biased downward.

5. **Start cheap, then scale.** The first experiments should inject the re-baseline prior and a symbol-based completeness checker on the 79 npm tasks—no mining required. Only after that baseline moves should we invest in GHArchive/WoC indexing, upstream test diffs, and same-org retrieval. If the cheap interventions fail, the expensive ones will not save the proposal.

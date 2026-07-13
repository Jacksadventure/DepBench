Now let me read the ensemble responses and the remaining key sources for completeness.

---

# Architecture and Experiment Design: Context-Aware Dependency-Upgrade Repair

---

## 0. Critique of the Current Direction

The five-case audit (REPORT.md) delivers a verdict that should reorder the research agenda: **in 4/5 zero-pass tasks, agents already possessed or personally discovered the decisive breaking-change facts from upgrade guides (Case 1), typings in `node_modules` (Case 2), jar decompilation (Case 5), or the Go module cache (Case 4). They failed anyway** — not from ignorance, but from three systemic failures: **evidence-weighting bias toward visible tests** (the re-baseline problem), **incomplete repository-wide propagation** (RQ3's dominant failure mode), and **oracle-idiom misprediction** (choosing backward-compat shims when the hidden oracle encodes the maintainer's canonical refactor).

This means the proposed mining pipeline (Ideas A–E from the handoff report) is **necessary but radically insufficient**. Adding breaking-change cards or exemplar diffs to an agent that already decompiled `DEFAULT_ITERATIONS = 50000` and then deliberately coded `ITERATIONS = 1000000` will add text to the context window, not flip outcomes. The binding constraint is not _what_ facts the agent possesses but _how it weighs them against contradictory local evidence_ (the visible test suite, the old fixture set, the instruction text "make the existing tests pass").

Therefore I propose splitting the architecture into two orthogonal systems:

1. **A context acquisition pipeline** (mining, indexing, retrieval) — this is commodity work; the case studies confirm the data exists pre-PR.
2. **A repair execution harness** that rewires the agent's evidence weighting, propagation checking, and stopping criteria — this is where the research contribution lives.

These two systems interact at a thin interface: the mined context is delivered as **structured, typed evidence with explicit authority annotations** (not raw text append), and the execution harness has a **mandatory migration checklist** that gates completion on repository-wide coverage, not on test green.

I will now design both, with the second receiving twice the detail budget of the first.

---

## 1. Research Thesis and Falsifiable Hypotheses

**Thesis.** Current coding agents fail dependency-upgrade repair (40% pass rate, 46.8% visible-test overfitting) because they treat upgrades as ordinary test-driven repair: they discover facts, satisfy the visible test suite, and stop. A context-augmented agent can surpass this ceiling IF AND ONLY IF three mechanisms are simultaneously present: (1) structured, versioned, authority-annotated context artifacts that are _retrieved_ into the agent's workspace; (2) a _re-baselining prior_ that causes the agent to treat the upgraded library's defaults and idioms as the specification, with injected context outranking local visible-test evidence; and (3) a _propagation completeness checker_ that prevents the agent from declaring completion while unrepaired call sites exist for changed API surfaces. Context retrieval without mechanisms (2) and (3) is demonstrably insufficient (five-case audit); mechanisms (2) and (3) without context retrieval address the evidence-weighting and propagation problems but cannot supply missing facts (the jwx unsolvable case, the actix dev-dep convention).

**Falsifiable hypotheses (H1–H5):**

- **H1 (Re-baseline prior).** Adding a single paragraph to the task instruction — stating that post-upgrade test suites re-baseline to the library's new defaults/idioms and that source code should undergo the canonical migration rather than shimming around old test mocks — increases pass@1 by ≥5 percentage points across the 219-task corpus relative to the current instruction, without any mined context. (Arm 0; two-sentence ablation.)

- **H2 (Completeness checker).** A post-patch completeness checker — which enumerates every reachable use of each changed API symbol and refuses to declare the task done while unrepaired sites exist — reduces the "incomplete migration" failure category (23–36 agreed cases per configuration in RQ3) by ≥40%. This is measured on the 219-task corpus without mined context: the checker does not need mining, only the agent's own candidate patch and static analysis.

- **H3 (Structured context + authority annotation).** Delivering breaking-change cards and exemplar diffs as typed, authority-annotated artifacts (not raw text) flips ≥3 of the 4 context-complete case-study tasks (brokeneck, spl-token, actix, shiro) from fail to pass — when the same artifacts without authority annotation (e.g., raw changelog text in the prompt) do not.

- **H4 (Sibling exemplar utility is strata-dependent).** On the 79 npm tasks, the per-task pass@1 uplift from sibling exemplar injection is positively correlated (Spearman ρ ≥ 0.4) with the sibling-population size for that (package, major boundary) pair as measured from GHArchive, controlling for task difficulty (hidden-test size, ecosystem-specific zero-pass rate). Tasks in the zero-sibling stratum receive zero uplift from exemplars; uplift is concentrated in the ≥10-sibling stratum.

- **H5 (Same-org siblings dominate generic siblings).** For tasks where same-organization sibling migrations exist at cutoff, injecting same-org sibling diffs is ≥2× more effective per byte of context than injecting random-sibling diffs (measured by pass@1 change), because same-org diffs carry project conventions (test scaffolding, dev-dep patterns, monorepo layout) that generic siblings never encode.

The overarching claim is: **context retrieval is a second-order effect; evidence weighting and propagation completeness are first-order.** The empirical strategy quantifies each factor's marginal contribution to pass@1 in a fixed-configuration ablation ladder.

---

## 2. Mining, Indexing, and Retrieval Architecture

### 2.1 Versioned Artifact Schemas

Every context artifact is typed with a schema that carries version, provenance, cutoff timestamp, and authority level. The schema is defined as a protocol buffer (for index-time validation and language-agnostic serialization) plus a JSON Lines serialization for the agent-facing surface.

```protobuf
// artifact.proto
message ContextArtifact {
  string artifact_id = 1;          // sha256(content)
  ArtifactType type = 2;
  PackageCoordinate package = 3;   // {ecosystem, name}
  VersionRange from_range = 4;     // e.g., ">=5.0.0,<6.0.0"
  VersionRange to_range = 5;       // e.g., ">=6.0.0,<7.0.0"
  google.protobuf.Timestamp cutoff = 6;  // latest admissible timestamp
  string source_url = 7;           // persistent URL to original evidence
  string source_repo = 8;          // e.g., "remix-run/react-router"
  string source_pr_number = 9;     // if from a PR
  EvidenceStrength strength = 10;  // see below
  AuthorityTier authority = 11;    // see §3
  repeated ChangedSymbol symbols = 12;  // AST-level symbol index
  repeated string file_paths = 13;      // paths in the source artifact
  string content_md = 14;          // the evidence, in Markdown
}

enum ArtifactType {
  BREAKING_CHANGE_CARD = 0;        // single API-level change fact
  EXEMPLAR_DIFF = 1;               // sibling repo's repair hunk(s)
  UPSTREAM_TEST_DIFF = 2;          // library's own test changes between versions
  MIGRATION_GUIDE_SECTION = 3;     // relevant section of upstream docs
  RELEASE_NOTE_SECTION = 4;        // relevant section of release notes
  SAME_ORG_MIGRATION = 5;          // same-org sibling (elevated authority)
  INSTALLED_PACKAGE_README = 6;    // README/FAQ shipped in the tarball
  BUILD_CONFIG_EXEMPLAR = 7;       // tsconfig/pom/Cargo.toml change from sibling
}

enum EvidenceStrength {
  CONCRETE_HUNK = 0;      // literal before/after code
  DOCUMENTED_RULE = 1;    // prose describing a change (e.g., changelog)
  HEURISTIC = 2;          // inferred from co-change patterns
  POLICY = 3;             // task-level prior, not per-dependency evidence
}

enum AuthorityTier {
  UPSTREAM_MAINTAINER = 0;       // library author's own migration/release
  SAME_ORG_SIBLING = 1;          // same GitHub org, same maintainer
  CROWD_VERIFIED = 2;            // ≥5 sibling repos with identical hunk
  CROWD_WEAK = 3;                // 1–4 siblings
  INFERRED = 4;                  // from upstream test diff / API diff, no crowd
}
```

**Key design decisions:**

- **`ChangedSymbol`** is the retrieval index. Sibling diffs and breaking-change cards are indexed at ingest time by the set of API symbols they touch (for npm: `import {X}` → symbol `X` from package `P`; for Go: `pkg.FuncName`; for Maven: fully qualified class/method; for Cargo: `use` path + trait/type name). This is what makes symbol-based retrieval (Case 2's lesson) possible — the spl-token exemplars that title-matching missed are recoverable because the agent knows which symbols of `@solana/spl-token` the target code imports.

- **`cutoff`** enforces pre-target-PR time-travel globally: every artifact carries the latest timestamp for which it is admissible, and retrieval queries include a `cutoff <= target_pr_created_at` filter.

- **`source_repo` + `source_pr_number`** enable deduplication: artifacts whose source is the target task's own repo/PR are excluded at retrieval time (the oracle leakage guard).

- **`content_md`** is the human-and-LLM-readable payload. For `EXEMPLAR_DIFF`, this is the unified diff of the non-manifest, non-lockfile hunks from the sibling's repair commit, with metadata header. For `BREAKING_CHANGE_CARD`, it is a structured card: `{symbol, kind, before, after, note}`.

### 2.2 Mining Pipelines (Five Sources)

Each pipeline is an offline batch job. Output flies into a versioned artifact store (filesystem directory tree + SQLite metadata index) keyed by `(ecosystem, package, from_major_version, to_major_version)`.

**Source 1 — GHArchive / sibling PR mining.** Queries `github_events` on ClickHouse (or BigQuery mirror):
1. For each `(package_name, from_major, to_major)` boundary: fetch all merged PRs whose title matches a normalized regex over Dependabot/Renovate templates, created before the target task's PR creation time.
2. Discard the target task's own `(repo, number)`.
3. Filter to repair-signal PRs (`commits > 1` OR `changed_files > manifest_expected_files` — the latter catches squash-merged repairs).
4. For promising candidates (stratified random sample up to 200 per boundary, biased toward larger repos and more changed files): fetch the PR diff via GitHub API, strip manifest/lockfile hunks (reuse DepBench's `refetch_split.py` path classifier), extract the repair diff.
5. **Index by symbol**: parse the repair diff with Tree-sitter to extract the set of changed API symbols. This is the hard engineering step — for each ecosystem, maintain a grammar that can extract symbol references (imports, function calls, type uses, method calls, trait bounds). Start with: npm/TS (`tree-sitter-typescript`), Go (`tree-sitter-go`), and Java (`tree-sitter-java`). Defer Cargo and Python.
6. Cluster repair hunks across siblings by the changed-symbol set to produce ranked, deduplicated exemplar diffs. The rank is `n_siblings_with_identical_hunk` (the CROWD_VERIFIED tier).

**Source 2 — Upstream release/source/test mining.** For each `(package, from_tag, to_tag)`:
1. Fetch the upstream repo; check out `to_tag`.
2. Run ecosystem-appropriate API diff: `japicmp` for Maven, `cargo-semver-checks` for Cargo, TypeScript compiler API for npm (generate `.d.ts` for both tags and diff), `apidiff` or `gorelease` for Go. Produce a machine-readable breaking-change list: `[{symbol, kind (removed/renamed/type_changed/signature_changed), old_signature, new_signature}]`.
3. Diff `to_tag`'s test suite against `from_tag`'s: extract *test assertions that changed* (the upstream's own re-baseline of its defaults). This is the upstream-test-diff source. For Java: parse Groovy/Java test files, extract assertion-value changes (e.g., `assertEquals(1000000, ...)` → `assertEquals(50000, ...)`). For npm/TS: similarly parse Jest/Mocha assertions.
4. Extract changelog/upgrade-guide sections from the upstream repo at `to_tag`: `CHANGELOG.md`, `docs/upgrading/*.md`, `MIGRATION.md`, GitHub release body.
5. For npm packages: unpack the npm tarball at the target version and extract `README.md` / `UPGRADING.md` / FAQ sections — these ship inside `node_modules` and are the cheapest context available (Case 2 lesson).

**Source 3 — Same-organization history.** For each target task's GitHub organization, query GHArchive for all merged PRs from that org touching the same package boundary, created before the target PR. Same-org siblings carry uniquely high authority because they share code conventions, test scaffolding, monorepo layout, and often the same author (Case 3's actix-net#481). Index them as `SAME_ORG_MIGRATION` artifacts with `AuthorityTier = SAME_ORG_SIBLING`.

**Source 4 — Installed-package documentation.** For npm tasks: after a successful `npm install <pkg>@<new_version>`, walk `node_modules/<pkg>/` and index `README.md`, `CHANGELOG.md`, `UPGRADING.md`, and any `.md` file mentioning "breaking" or "migration." For Go: walk the module cache. For Maven: extract javadoc/README from downloaded jars. This is a *runtime* retrieval step (not offline), but the index schema is the same — it produces `INSTALLED_PACKAGE_README` artifacts.

**Source 5 — World of Code (WoC).** WoC indexes every file version in every public Git repository. It enables two queries that sibling-PR mining cannot:
- **Symbol co-change patterns**: "across all repos that use package P, when symbol X was removed between two blob versions, what other files in those repos changed in the same commit?" This produces a per-symbol propagation checklist (H2 input).
- **Cross-ecosystem exemplars**: a Maven upgrade's repair pattern may appear first in a different repo than the one Dependabot targeted.

Practical constraint: WoC's current API is a constrained REST service hosted at Purdue. For the prototype, defer WoC to post-ablation scale-out. The GHArchive pipeline covers the npm scale target.

### 2.3 Retrieval Interface

Batch injection, not agent-tool call. The retrieval system runs *before* the agent starts, produces a context artifact bundle (the "context card deck"), and writes it to `/tmp/dep-context/` inside the container. This avoids the discoverability problem (the agent must know to call the right tool with the right query) that the RQ4 trajectory table shows is severe: Copilot CLI + GPT-5.5, the best scorer, used docs in only 5/219 trajectories.

The bundle has fixed structure:

```
/tmp/dep-context/
├── meta.json              # {package, from_ver, to_ver, cutoff, n_siblings, n_cards}
├── policy.md              # re-baseline prior (same for every task)
├── cards/
│   ├── 01_<symbol>_removed.md
│   ├── 02_<symbol>_signature_changed.md
│   └── ...
├── exemplars/
│   ├── sibling_<repo>_<pr>.diff
│   ├── same_org_<repo>_<pr>.diff
│   └── ...
├── upstream_test_diff.diff
└── guide_section.md
```

The agent's instruction.md appends a `## Upgrade Context` section that lists the bundle path and the ordered authority tiers. The agent is instructed to *read the context deck before making any edits*, and to treat cards with `UPSTREAM_MAINTAINER` or `SAME_ORG_SIBLING` authority as overruling contradictory local test evidence.

---

## 3. Agent Loop, Authority Ordering, Contradiction Handling, Completeness Checks, and Stop Conditions

This is the core contribution. The execution harness wraps Codex + GPT-5.5 with four mandatory phases that the agent CANNOT skip (they are enforced by a thin harness layer, not by prompt convention).

### 3.1 Phase Architecture

```
Phase 0: CONTEXT ACQUISITION (5 min, enforced)
  → Agent reads /tmp/dep-context/ in its entirety.
  → Agent produces a migration_checklist.txt:
      - Every changed API symbol (from the context cards)
      - For each symbol, every file in /app that imports/uses it (grep output)
      - A propagation checklist: test files, mock files, fixture files, generated files
        that may transitively depend on the symbol (from co-change patterns if available,
        else from a heuristic: match filename patterns from the sibling exemplar's
        changed-file set)
  → The harness validates that checklist.txt is non-empty and covers all cards.
    If not, the agent loops.

Phase 1: MANIFEST UPGRADE + BUILD (10 min)
  → Apply the dependency bump, resolve the lockfile, build.
  → If build fails: agent fixes compile errors using context cards.
  → Build must succeed before Phase 2.

Phase 2: SEMANTIC MIGRATION (15 min, primary work phase)
  → For each item in migration_checklist.txt:
      - Apply the breaking-change card's replacement idiom
      - Apply the highest-authority exemplar hunk (same-org > crowd-verified > crowd-weak)
      - Mark the item done
  → After every edit, the harness runs a completeness check (see §3.3).
  → The agent may run tests during this phase, but the harness intercepts
    test output and annotates it with a warning:
      "WARNING: Visible tests encode PRE-UPGRADE semantics.
       Test failures that check OLD defaults, OLD API surfaces,
       or OLD error types are EXPECTED. Do not shim around them.
       Consult the context cards for the POST-UPGRADE contract."
  → The agent is explicitly instructed: "A test failure on a context-card
    symbol is a CONFIRMATION that the migration is progressing, not a
    signal to revert."

Phase 3: COMPLETENESS VERIFICATION (5 min, enforced)
  → The harness runs the completeness checker.
  → If unrepaired sites exist for any changed symbol: agent loops back to Phase 2
    (max 2 additional loops, then forced submission with incompleteness annotation).
  → Agent runs the full visible test suite exactly once, as a sanity check.
  → Agent produces a final diff.
```

### 3.2 Authority Ordering and Contradiction Handling

The five-case audit reveals the binding failure pattern: the agent holds two contradictory pieces of evidence — the context card says "SHA-512 default is now 50,000 iterations, upstream's own test migrated to accept this" and the visible test file asserts `assertEquals(1000000, hash.getIterations())` — and must choose which to trust. Currently, agents universally trust local tests over injected context.

The fix is NOT to tell the agent "never trust tests." It is to give the agent an explicit, ordered authority model:

```
AUTHORITY LADDER (highest to lowest):
1. UPSTREAM_MAINTAINER evidence (release notes, official migration guide, upstream's own tests at the new tag)
2. SAME_ORG_SIBLING evidence (the same maintainer repaired the same upgrade in a sibling repo)
3. CROWD_VERIFIED evidence (≥5 independent repos converged on the same repair hunk)
4. CROWD_WEAK evidence (1–4 siblings)
5. Local compiler output (type errors, missing symbols — these are facts about the current API surface)
6. Local visible test assertions (these may encode pre-upgrade expectations)
```

This ladder is communicated once in `policy.md` and reinforced as a system prompt annotation. When the agent encounters a contradiction between tiers 1–4 and tier 6, it MUST favor the higher tier. The harness cannot programmatically enforce this (it's an LLM reasoning requirement), but it can (a) verify that the agent did read the context deck (by checking for context-card paraphrases in the agent's reasoning trace), (b) flag contradictions at completeness-check time (if the agent uses an old symbol that a card declared removed), and (c) surface contradictions as explicit warnings.

For the re-baseline prior specifically: `policy.md` contains the following, generated once:

```markdown
## Re-baseline Policy (harbor-canary GUID 26c5b67b...)

This is a DEPENDENCY UPGRADE task, not an ordinary bug fix. The following
rules override normal test-driven development behavior:

1. **The upgraded library's defaults and idioms are the specification.**
   If the library changed a default value, removed an export, or introduced
   a new error type, the POST-UPGRADE code must use the new form. Do not
   shim, wrap, or re-export to preserve the old API surface.

2. **Visible tests may encode PRE-UPGRADE expectations.** A test failure
   on a changed API symbol is EXPECTED and CONFIRMATORY — it means the
   migration is touching the right surfaces. Do not revert your migration
   to make the old tests pass.

3. **Migrate source AND tests together.** The upstream maintainer's test
   diffs (in context deck) show how the library's own tests were re-baselined.
   Sibling exemplar diffs show how other projects migrated their tests.
   Follow their pattern: update test mocks, assertions, and fixtures to
   match the new library contract.

4. **Complete the migration before running tests.** The completeness
   checker must show zero unrepaired sites before you consider the task
   done. A green test run with incomplete propagation is a FALSE POSITIVE.
```

This is the "arm 0" ablation referenced in §4. It costs zero mining and tests whether the binding constraint is truly the agent's behavioral policy rather than information access.

### 3.3 Completeness Checker (Independent Tool, Not Prompt Engineering)

The completeness checker is a **deterministic static-analysis tool** that runs inside the container and gates agent progress. It answers one question: "For every changed API surface identified in the context cards, has every reachable use site in `/app` been updated?"

Algorithm:
1. **Input**: the agent's current patch (`git diff`), the set of `ChangedSymbol` entries from the context cards.
2. For each changed symbol `S`:
   - `S.old_form` and `S.new_form` come from the card (e.g., `useHistory()` → `useNavigate()`, `int` → `int64`).
   - **grep** `/app` (excluding `node_modules`, `.git`, `target/`, `vendor/`) for `S.old_form`.
   - For each match: determine if the match is (a) a use site that should be migrated, (b) a comment/docstring (ignore), (c) a vendored or generated file (ignore if path matches known patterns).
   - If any use site remains: emit `UNREPAIRED: <file>:<line>: <symbol> (old form still present)`.
3. **Output**: `COMPLETE` (zero unrepaired sites) or `INCOMPLETE` (with the list).

The key design choice: the checker uses **grep + regex**, not full AST analysis. This is deliberately imprecise in the direction of false positives (flagging comments, string literals) rather than false negatives (missing a hidden use site). The agent can inspect each flagged site and either migrate it or annotate it as a false positive (and the harness accepts the annotation).

For **type-propagation changes** (like the GitLab int→int64 case), the checker has a special mode: for a type-widening change, it also greps for variables of the old type that flow from or to the changed function, using a simple dataflow heuristic: if function `F` returns `S.old_type` and the card says `F` now returns `S.new_type`, grep for all callers of `F` and flag those where the return value is assigned to a variable typed `S.old_type`.

For **removed-exports** (like the solana Token class), the checker verifies that `import { Token } from '@solana/spl-token'` appears nowhere in `/app/src`.

### 3.4 Stop Conditions

The agent may stop (declare the task complete) ONLY when ALL of the following hold:

1. **Manifest applied**: the dependency version in the manifest/lockfile matches the target version (verified by the harness with a simple grep).
2. **Build passes** (for compiled languages) or **no syntax errors** (for interpreted).
3. **Completeness checker returns COMPLETE** (or all flagged sites are agent-annotated false positives that the harness accepts).
4. **At least one edit was made** (detect no-ops — the agent can't pass without changing a file).
5. Phase 3 has been entered at least once (the agent cannot skip the completeness check).

Note what is deliberately **absent**: "visible tests must pass." The agent is allowed to submit with failing pre-upgrade tests, because the post-upgrade test suite (applied by the hidden test.patch) is the grading oracle. This is the single most important behavioral change: **decoupling the agent's local stop condition from the visible test suite.**

The harness intercepts the agent's final test run and, if tests fail, annotates the output with: `"Some pre-upgrade tests failed — this is expected for behavioral changes. The grading oracle uses the post-upgrade test suite. Submitting now."` This annotation is also in the system prompt so the agent knows it won't be penalized by the harness for "incomplete work."

---

## 4. Five-Case Pilot → npm-Scale Ablation Ladder

### 4.1 Pilot Phase (5 Cases)

The pilot validates the architecture against the five audited cases before any scale investment.

**Step 0 — Re-baseline prior only (arm 0).** For each of the 5 cases, run Codex + GPT-5.5 with ONLY the re-baseline policy instruction appended to the standard `instruction.md`. No mined context. This directly tests: for the 4 context-complete cases (brokeneck, spl-token, actix, shiro), does the policy alone flip the outcome? Expected: the solana and brokeneck cases should flip (both failed because agents chose backward-compat shims; the policy directly forbids that). Shiro: agents decompiled the correct constant and still chose wrong; the policy instructs the opposite. Actix: the policy doesn't add the missing dev-deps, so it should still fail — confirming the need for same-org sibling context.

**Step 1 — Full context injection (arm A+B+same-org).** For each case, build the complete context deck manually (following the artifact schemas in §2.2, with real data from the case study files) and inject it alongside the re-baseline policy. Run Codex + GPT-5.5. Expected: 4/5 pass (brokeneck, spl-token, actix, shiro); jwx remains fail (structurally unsolvable). The actix case should flip because same-org sibling (actix-net#481) provides the decisive dev-dep lines.

**Step 2 — Completeness checker validation.** For the cases where the agent produced a non-passing patch, run the completeness checker on that patch and verify it correctly identifies the unrepaired sites. For cases where the agent passes, verify that the completeness checker returns COMPLETE on the agent's final patch.

**Pilot metrics**: per-case pass/fail, agent trajectory step count, context-deck size (bytes), completeness-checker recall against the ground-truth code.patch (what fraction of the human's changed sites were flagged), and — critically — a binary flag: "did the agent produce a shim/compat wrapper to preserve visible-test behavior?" (expected: 0 under the re-baseline policy).

### 4.2 npm-Scale Phase (79 npm Tasks)

Only after the pilot passes (≥3/4 context-complete cases flip) does scale-out begin. The npm subset is chosen because (a) it's the hardest ecosystem (51/79 consensus-hard under GPT-5.5), (b) it has the richest sibling strata, (c) the case studies show npm tasks are disproportionately affected by the re-baseline problem.

**Ablation arms (all with Codex + GPT-5.5, 30min budget, 79 npm tasks):**

| Arm | Context | Re-baseline policy | Completeness checker | Purpose |
|-----|---------|-------------------|---------------------|---------|
| Baseline | None (current instruction.md) | No | No | Reproduce 21/79 for Codex+GPT-5.5 |
| Arm-P | None | Yes | No | Isolates policy effect (H1) |
| Arm-C | None | No | Yes | Isolates checker effect (H2) |
| Arm-PC | None | Yes | Yes | Policy + checker, no mining |
| Arm-A | Sibling exemplars (title-based retrieval) | Yes | Yes | Handoff Idea A |
| Arm-B | Breaking-change cards from upstream | Yes | Yes | Handoff Idea B |
| Arm-A+ | Sibling exemplars (symbol-based retrieval) | Yes | Yes | Tests H4+H5 |
| Arm-Full | Cards + symbol-exemplars + same-org + upstream test diffs | Yes | Yes | Full system |

**Primary metric**: pass@1 on 79 npm tasks. **Secondary metrics**:
- Uplift stratified by sibling-population size (0, 1–9, ≥10 merged repair-signal PRs for the package boundary at cutoff) — tests H4.
- Uplift stratified by whether a same-org sibling exists at cutoff — tests H5.
- Completeness-checker recall: for PASS tasks, what fraction of the code.patch's changed files were flagged as requiring repair by the checker?
- "Visible-test overfitting rate": for FAIL tasks, what fraction had a visible-test-pass signal in the trajectory before submission? (Compare to the paper's 46.8% baseline.)
- Context precision: of the injected cards/exemplars, what fraction produced a matching hunk in the agent's final diff?
- Agent runtime (did the context deck materially increase time-to-first-edit or reduce loops?).

### 4.3 Beyond npm

If npm-scale results are positive (Arm-Full ≥10 percentage points over Baseline), extend to Go (41 tasks) and Cargo (21 tasks). Maven (66 tasks) is the lowest priority — it's already the easiest ecosystem, and the one case-study Maven task (shiro) showed agents successfully recovering all facts from jar decompilation; the marginal value of mined context for Maven is likely small.

---

## 5. Leakage, Time-Travel Controls, Benchmark Hazards, and Confounds

### 5.1 Leakage Controls

The DepBench harness already blocks the target repo and PR URLs (§1 of HARNESS.md). The mining pipeline adds two additional leakage vectors:

1. **Oracle repair patch contamination.** The task's `solution/code.patch` is literally a PR in the dataset (`https://github.com/<task_repo>/pull/<task_number>.diff`). If the mining pipeline includes that PR in the exemplar index, the agent receives the answer. **Fix**: the artifact store deduplicates by `(source_repo, source_pr_number) == (task_repo, task_pr_number)`. Additionally, the retrieval query for exemplars excludes repos whose name fuzzy-matches the task repo after owner normalization.

2. **Same-org sibling contains near-identical repair.** Cases like actix-net#481 contain hunks that are literally the same code as the ground truth (same author transplanted the recipe). This is not a leakage bug — it is the *intended behavior* of same-org mining — but it must be reported transparently. **Fix**: for every task, annotate whether any same-org sibling diff shares ≥80% of hunks (by line-edit similarity) with the hidden `code.patch`. Tasks where this is true are flagged as "near-oracle" and reported separately in ablation results.

### 5.2 Time-Travel Discipline

Every artifact has a `cutoff` field. The retrieval system filters to `cutoff <= task_pr_created_at`. This is implemented as a SQL WHERE clause in the artifact index. The five-case audit confirmed this is feasible: all required evidence (react-router v5→v6 guide since 2021, solana README since 2022, Shiro 2.0.0 source since Feb 2024, syn 2.0.0 release notes since Mar 2023, actix-net#481 since Apr 2023) predates the respective task PRs.

The time-travel discipline has one edge case: npm publishes can occur hours before the corresponding GitHub release (react-router-dom 6.4.1: npm 2022-09-21T20:46, GitHub release 2022-09-22T15:53, task PR 2022-09-22T01:08 — npm publish pre-cutoff, GitHub release post-cutoff). The mining pipeline uses the *earliest* of (npm publish time, GitHub release time, tag creation time) as the evidence availability timestamp for upstream artifacts.

### 5.3 Benchmark Hazards

1. **Task instruction wording.** The current `instruction.md` says "so that the existing tests pass against the upgraded dependency." Under the re-baseline policy, this directive is **actively wrong** for behavioral-change tasks. The policy overrides it, but we should measure the interaction: does the old instruction's wording reduce the policy's effectiveness? **Mitigation**: Arm-P uses the current instruction + policy appended; measure the pass rate with both.

2. **The jwx-class unsolvable tasks (random fixtures).** The pilot will quantify how many of the 219 tasks are structurally unsolvable under any context regime. Based on the five-case audit, estimate 5–15%. Report ablation results both with and without these tasks. **Detection heuristic before running**: for each task, hash the `tests/test.patch` against `solution/code.patch`; flag tasks where the test patch introduces new random-looking hex/base64/did strings that also appear in the code patch (indicating an entangled fixture regeneration).

3. **The actix-class scaffolding tasks (dev-deps only in hidden manifest).** Flag tasks where `tests/test.patch` adds test files that require dev-dependencies not present in the visible manifest and not added by `code.patch`. These are solvable only with same-org sibling mining. Report separately.

4. **Verifier time budget.** The completeness checker and context-deck reading consume agent time. The 30-minute budget may need adjustment if Phase 0+1+2+3 with context reading squeezes the migration work. **Mitigation**: measure agent phase timings in the pilot and add a 5-minute budget extension if Phase 0 (context reading) consistently consumes >3 minutes.

### 5.4 Confounds

1. **Model progress confound.** Between the paper's runs (model snapshot circa 2026-04/05) and the ablation runs, GPT-5.5 may improve independently. The Baseline arm reruns Codex + GPT-5.5 with the current instruction and current model to establish the contemporary baseline; do NOT compare against paper Table IX numbers directly.

2. **Prompt-length confound.** The context deck adds significant tokens (potentially 10K–30K for high-sibling tasks). Any pass-rate improvement must be tested against a length-matched control: insert an equal token count of irrelevant text (e.g., the package's entire upstream README for a *different* version) and measure whether the effect is context-content or just "more tokens → better reasoning."

3. **Harness confound.** The execution harness (phases, completeness checker, test-output interception) changes the agent's interaction with the environment beyond just adding context. The Arm-PC vs Arm-C arms distinguish the harness effect from the context effect.

4. **Selection bias in the five cases.** The five cases were purposively sampled for diversity and high sibling counts. The npm-scale experiment tests whether the findings generalize to the full distribution (including long-tail packages with zero siblings).

---

## 6. Build Order and Falsification

### 6.1 What to Build First (Next 2 Weeks)

1. **Arm 0 re-baseline policy experiment** (1 day). Write `policy.md`, append it to the five case-study task instructions, run Codex + GPT-5.5 via `harbor trials start` on those 5 tasks. This is the single highest-information experiment and costs zero engineering beyond editing `instruction.md`.

2. **Completeness checker prototype** (3 days). A Python script (~300 lines) that takes a `git diff` and a JSON list of `ChangedSymbol` entries (manually written for the five cases), greps `/app`, and emits `COMPLETE` or `INCOMPLETE`. Validate against the five cases' ground-truth patches (does it flag all human-repaired sites?).

3. **Manual context deck for the five cases** (2 days). Following the artifact schemas, create the context deck files by hand for the five cases — using the evidence already gathered in the case study files. This validates the schema design without building any mining pipeline.

4. **End-to-end pilot run** (2 days). Run the five cases through the full harness (Arm-Full for the pilot) with Codex + GPT-5.5. If ≥3/4 context-complete cases flip, proceed to npm scale. If ≤2/4 flip, the thesis is in trouble — analyze why and iterate on the policy wording or authority model.

### 6.2 What to Defer

1. **Full GHArchive → artifact pipeline.** The sibling mining pipeline is ~1–2 weeks of engineering (ClickHouse query automation, GitHub API diff fetching, Tree-sitter symbol parsing, artifact store). Defer until the pilot confirms that (a) the context architecture flips outcomes and (b) the completeness checker adds signal. If Arm-PC (policy + checker, no mined context) already produces a large uplift, the incremental value of sibling mining is smaller and the pipeline can be scoped down.

2. **World of Code integration.** WoC is a "nice to have" for co-change patterns and cross-ecosystem retrieval. The prototype should use the heuristic grep-based co-change list (match file patterns from sibling exemplars) instead.

3. **Cargo/Python/Go mining pipelines.** Start with npm (largest ecosystem, hardest, best sibling strata). Maven is easy enough that context may not help; Cargo and Go are smaller and have fewer siblings. Validate on npm first.

4. **Rule verification and codemod generation (Idea C).** This is a production-engineering problem, not a research contribution. Defer until (or if) the system demonstrates 50%+ pass@1 on npm.

5. **MCP server / IDE plugin (Idea E).** The execution harness is the delivery vehicle for the ablation; an MCP server is follow-on packaging work that any intern can do once the architecture is validated.

### 6.3 What Result Would Falsify the Proposal

- **Arm-P (re-baseline policy) produces zero or negative uplift on the five-case pilot.** If telling agents "post-upgrade tests re-baseline; don't shim to old tests" fails to flip the brokeneck or shiro cases — where agents explicitly deliberated the shim-vs-canonical choice and picked wrong — then the evidence-weighting theory is wrong, and the failure mode is something deeper (e.g., the agent cannot actually execute the canonical migration correctly without seeing the target idioms).

- **Arm-PC (policy + checker, no mining) passes ≥15/79 npm tasks (vs. baseline ~21/79), making Arm-A and Arm-B contribute ≤5 incremental passes.** If the policy+checker alone recovers nearly all the uplift, the mining pipeline adds complexity for marginal gain. The project becomes "write a better prompt and a grep script," not "mine the world's repair history." That is still a publishable result (and a useful one), but it means the GHArchive/WoC effort should be descoped to a discussion-section "future work" paragraph.

- **The completeness checker produces >30% false-positive rate (flags unchanged/unrelated lines) and agents waste time dismissing false positives.** If the grep-based heuristic is too noisy, the checker becomes a time sink rather than a guardrail. Fallback: tighten the regex patterns (only flag exact symbol matches at import/call sites, not any substring) or add a simple allowlist of false-positive patterns per ecosystem.

- **H4 null: sibling exemplar uplift shows no correlation with sibling-population size.** If tasks with 200 repair siblings and tasks with 2 repair siblings benefit equally (or neither benefits), then the sibling mining pipeline's core premise — that cross-repo repair exemplars encode useful migration knowledge — is wrong. The likely explanation would be that the LLM already has strong priors for popular package upgrades (react-router 5→6 is "in the training data") and for unpopular ones siblings are too noisy. This would redirect effort entirely to upstream-side mining (Idea B) and the policy/checker mechanisms.

---

## Top 5 Takeaways, Ranked by Importance

1. **The five-case audit refutes the premise that adding more retrieved text is the primary lever.** Agents already discovered the decisive facts in 4/5 cases. The binding constraint is evidence weighting (visible tests outweigh injected context), repository-wide propagation (incomplete migration is the #1 failure mode in RQ3), and stopping criteria tethered to the wrong oracle. Any architecture that does not intervene on these three mechanisms is adding bytes, not solving.

2. **The re-baseline policy is the cheapest, highest-information experiment in the project and should be run first.** A two-paragraph instruction costing zero mining addresses the failure mode observed in Cases 1, 2, and 5 (and plausibly the 46.8% "visible-test overfitting" cohort from RQ4). If it doesn't work, the design premise is falsified before any mining pipeline is built.

3. **The completeness checker is not a prompt-engineering trick — it is a deterministic tool that gates task completion on repository-wide symbol coverage.** This directly attacks RQ3's "incomplete migration" category (the largest agreed failure mode in every configuration) and does not require any mined data — just the agent's own candidate patch and the context-card symbol list. Build it before the mining pipeline.

4. **Two of five consensus-hard tasks are benchmark artifacts (jwx: unsolvable; actix: scaffolding).** The hazard filter (automated detection of regenerated fixtures, manifest-only dev-dep gaps) must run before ablations, or the measured effect of context injection will be biased downward by tasks that no amount of context can solve. For the paper, the honest headline is "consensus-hard ≠ context-hard" and the artifact fraction must be disclosed.

5. **Same-org sibling mining is the uniquely privileged context tier that the handoff report missed.** actix-net#481 was the sole pre-cutoff source of the decisive fact in the actix case; no upstream doc, no random sibling, no model prior would have supplied it. Same-org siblings carry project conventions (test scaffolding, dev-dep patterns, macro delegation idioms) that generic crowd exemplars cannot encode. Build the same-org retrieval path into the architecture from day one, not as a post-hoc enhancement.

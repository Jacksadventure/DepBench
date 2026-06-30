# Trajectory Annotation Protocol — DepBench (v1)

> **Self-contained.** A labelling agent needs only this file plus one trial's input
> bundle (below) to produce a complete annotation. Do not assume access to other notes.
> Output one JSON object per trial, exactly per the schema in §7.

---

## 1. Your role

You are a **post-hoc labelling agent**. For a single agent trial on a DepBench
dependency-upgrade-repair task, you read what the coding agent did and produce a
structured annotation covering four dimensions:

- **L. Leakage** — did the agent obtain the solution over the network / from local git
  history instead of deriving it? (always)
- **D. RQ4 discovery & evidence-gathering** — which breaking-change discovery behaviors
  (Docs / API / Tests / BC-hyp) appeared, how central they were, and the visible-then-hidden
  overfit signal. (always) This reproduces and extends the paper's RQ4 measurement.
- **P. Pass alignment** — if it passed, is its fix the same as the oracle's, or a
  plausible-but-different solution? (only when `reward = 1.0`)
- **F. Failure analysis** — if it failed, why? (only when `reward = 0.0`)

Each dimension has exactly **one headline label** that two annotators are scored on for
inter-annotator agreement (§10) — one κ per dimension: L → `leakage.label`,
D → `discovery.evidence_gathering_mode`, P → `pass_alignment.alignment_label`,
F → `failure.failure_category_primary`. All other fields are supporting/descriptive detail
(used for adjudication and mining, not separately κ-scored).

You analyze the run **from the agent's trajectory plus the oracle code patch**, and — **only
when it is present for this trial** — the verifier test log (`verifier_log`, the held-out test
run's stdout). You see the gold repair (`oracle_patch`) but never the held-out test *patch*
itself. The `verifier_log` is available for some runs (e.g. opencode/gemini) and absent for
others; when it is missing, fall back to comparing the agent's edits against `oracle_patch`.
Judge the agent's *behavior and result*; do not re-grade. The `reward` is authoritative for
pass/fail — never override it.

**Method — observation-first (this is what makes the output deterministic).** Build the
annotation bottom-up: first enumerate concrete, step-grounded **lists** of what actually
happened (online resources fetched, local files/sources inspected, tests run, edits made),
each item self-classified with an enum and a short free-text `finding`; *then* derive every
dimension label from those lists. A label with no backing observation is not allowed. The
lists — not the labels — are the primary research asset: we mine them across all trials to
quantify leakage and to develop the paper's research questions.

## 2. Input bundle (given to you per trial)

| Input | What it is |
|---|---|
| `instruction` | `instruction.md` (the **task description**) — the only task text the coding agent saw. Usually just "Bumps X from a→b" + "do not modify tests." |
| `oracle_patch` | `solution/code.patch` — the gold source repair. Your reference for "what a correct fix looks like." |
| `trajectory` | The agent's full step sequence: assistant messages, tool calls (command/url/query + arguments), and observations/results. **This is your only window into the run.** |
| `reward` | `1.0` = pass, `0.0` = fail. May be missing → treat as no-reward (see §8). |
| `verifier_log` | **Optional** — the held-out test run's stdout (`verifier/test-stdout.txt`), present for some runs and absent for others. When present, it is the direct evidence of *how* a `reward = 0` trial failed the hidden tests (and confirms a `reward = 1` pass). When absent, diagnose from edits-vs-oracle (§6.2). Never the held-out test *patch*. |
| `task_id` | `owner__repo__PR` (e.g. `xMoelletschi__renoglaab__30` → owner `xMoelletschi`, repo `renoglaab`, PR `30`). This is the upstream identity for leakage queries. |

> **You do NOT have:** the held-out test *patch*, or any run output beyond the agent's own
> `trajectory` and the optional `verifier_log`. The ground truth for "the correct fix" is
> `oracle_patch`. When `verifier_log` is **present**, use its failing-test output to pin the
> hidden-test failure precisely; when it is **absent**, the hidden-test failure output is not
> available — diagnose by comparing the agent's edits to `oracle_patch` (§6.2), not by inventing
> verifier errors.

**Derive once, up front:** from `oracle_patch`, list the **oracle changed files** and the
**key change** (the essential API/symbol/type/semantic edit — e.g. `glob.sync` → `globSync`,
`int` → `int64`). You will compare the agent against these.

## 3. Procedure & the observation layer (deterministic core)

The annotation is built **bottom-up**: first enumerate observations as lists, then derive
every label from them. Do these in order.

**Step 1 — Understand the intended fix.** Read `instruction` + `oracle_patch`. Note the
**oracle changed files** and the **key change** (the essential API/symbol/type/semantic edit —
e.g. `glob.sync` → `globSync`, `int` → `int64`).

**Step 2 — Enumerate the four observation lists.** Walk the `trajectory`
chronologically and record every relevant event. **One observation item = exactly one ATIF
`step_id`** (do not merge two steps into one item, or split one step into several) — this is
what lets a second annotator align item-for-item with you (§10). Every item carries that
`step_id` and a short free-text field, so each label is traceable to a concrete step. Leave a
list `[]` if nothing matched.

- **`online_resources`** — every **network** fetch or search (the leakage *and* online-docs
  surface):
  `step_id` · `tool` (e.g. `curl`/`exec_command`, `webfetch`, `web_search_call`) ·
  `target` (URL or search-query string) · `host` (e.g. `tinkerpop.apache.org`,
  `github.com/<owner>/<repo>`) ·
  `category` ∈ {`dependency-docs`, `dependency-registry`, `search-engine`,
  `own-project-repo`, `own-pull-request`, `own-commit-or-patch`, `mirror-or-codesearch`,
  `other-third-party`, `unknown`} ·
  `returned_solution_content` (bool — did the response contain oracle-specific content: an
  oracle changed-file path, the exact replacement API/symbol, or `code.patch` hunk lines?) ·
  `finding` (free text: what it returned and why it matters).
- **`local_inspections`** — every **local** read (no network) used to learn the dependency
  contract or that could expose the fix:
  `step_id` · `target` (path or command, e.g. `node_modules/glob/dist`, `git log -p`) ·
  `category` ∈ {`dependency-source`, `dependency-doc-local`, `project-source`,
  `project-git-history`, `stray-patch-artifact`, `other`} ·
  `finding` (free text: what was read / learned).
- **`tests_run`** — every test/build/lint execution:
  `step_id` · `command` · `kind` ∈ {`build`, `unit-test`, `integration-test`, `lint`,
  `run-script`, `other`} · `result` ∈ {`pass`, `fail`, `error`, `unknown`} ·
  `finding` (free text: which tests, what the outcome told the agent).
- **`code_edits`** — the agent's actual edits (this **is** the agent diff):
  `step_id` · `file` · `summary` (free text: what changed).

> **"What docs were inspected"** = the `online_resources` items with `category =
> dependency-docs` plus the `local_inspections` items with `category = dependency-doc-local`;
> their `finding` fields say what the agent learned. Docs are a tagged, queryable subset — no
> separate list needed.

**Step 3 — Derive the dimensions** L and D (always), then P (pass) or F (fail). Every rollup
label must be backed by ≥1 listed observation.

**Step 4 — Justify in free text.** Each dimension carries a `summary` (or `approach_note` /
`diagnosis`) that justifies its labels by pointing at the observations. Where the lists are
incomplete (truncated log), lower that dimension's `confidence` and say so. Never invent
observations.

## 4. Dimension L — Leakage (annotate for every trial)

### 4.1 The one distinction that governs everything

- **ALLOWED** (intentional benchmark design): consulting the **upgraded dependency's** own
  documentation, release notes, migration guide, changelog, API reference, or general web
  search *about the dependency*. This is the RQ4 "Docs" behavior — **not** leakage.
- **LEAKAGE** (disallowed): obtaining the **task's own project fix** — its GitHub repo, the
  upgrade pull request, the fix/merge commit, the `.patch`/`.diff`, or any mirror / fork /
  code-search snippet that reveals the **downstream repair** the agent was meant to derive.
- **Mnemonic:** reading about the **dependency** = fine; reading the **project's own fix** = leak.

### 4.2 Leak vectors to look for (in tool-call args, observations, AND agent narration)

1. `pr_diff_patch` — URLs/commands hitting `github.com/{owner}/{repo}/pull/{PR}`,
   `.../pull/{PR}.diff|.patch`, `.../commit/{sha}`, `{sha}.patch`,
   `raw.githubusercontent.com/{owner}/{repo}/...`, `api.github.com/repos/{owner}/{repo}/pulls/{PR}`,
   `gh pr view/diff`, `gh api`.
2. `clone_at_fix` — `git clone`/`fetch`/`remote add` of the upstream, then `git log/show/diff`
   of a fixed ref; installing the package from upstream git at the fixed commit.
3. `search_surfaced_fix` — web search/fetch whose query combines repo name + PR number +
   (fix/upgrade/error string) **and** whose returned snippet contains the repair.
4. `mirror_codesearch` — sourcegraph, grep.app, Google cache, npm/crates/pkg.go.dev/Maven
   source browsers, etc., surfacing the **downstream project's** fixed source.
5. `local_git_history` — the agent reads the fix from inside the checkout: `git log/show/diff`
   over a `.git` that contains the post-fix commit, a stray `.orig`/`.patch` in the tree, or
   the dependency vendored at its fixed source. (Non-network vector.)
6. `none` — no leak vector observed.

**These vectors are not judged from scratch — they are read off the observation lists:**
`pr_diff_patch` ⇐ `online_resources.category ∈ {own-pull-request, own-commit-or-patch}`;
`search_surfaced_fix` ⇐ a `search-engine` item with `returned_solution_content = true`;
`mirror_codesearch` ⇐ `mirror-or-codesearch`; `clone_at_fix` ⇐ an `own-project-repo` clone (or
a `project-git-history` read after one); `local_git_history` ⇐
`local_inspections.category ∈ {project-git-history, stray-patch-artifact}`. Put the `step_id`s
of the offending items in `leakage.leak_refs`.

**Negative control — do NOT flag** as leakage: fetching the *dependency's* docs / release
notes / migration guide, or registry metadata for the new version. That is the allowed RQ4
"Docs" behavior.

### 4.3 Leakage label — the headline agreement target (derived from the observation lists)

`leakage.label` is a **3-level ordinal**: `none < suspect < confirmed`. It is **leak-only** —
benign / dependency-directed network use does **not** appear on this scale (that is recorded in
Dimension D, not here). This single label is L's inter-annotator agreement target (§10).

- `none` — **no own-project access**: no `online_resources` item in {`own-project-repo`,
  `own-pull-request`, `own-commit-or-patch`, `mirror-or-codesearch`} and no `local_inspections`
  item in {`project-git-history`, `stray-patch-artifact`}. (Benign dependency-docs/registry
  fetches do **not** raise the label above `none`.)
- `suspect` — ≥1 such own-project / mirror / local-leak item exists (`accessed_own_project =
  true`), but **none** has `returned_solution_content = true`.
- `confirmed` — ≥1 such item has `returned_solution_content = true` **and** `leak_precedes_fix =
  true` (`retrieved_oracle = true`). A `confirmed` on a passing trial is a **tainted pass**.

### 4.4 False-positive guards (required before `confirmed`)

- **Specificity** — the retrieved content must contain solution-specific tokens that are NOT
  already in `instruction` and NOT derivable from the dependency's own docs. ("Bumps X a→b"
  is given; the *repair* is not.)
- **Temporal order** — the retrieval must occur *before* the matching edit. A fetch after the
  fix is not causal → at most `suspect`.
- **Independent-derivability** — if the same fix is plainly available from the dependency's
  official docs, still record the disallowed access, but set `independently_derivable = true`
  so we can separate "leak-enabled pass" from "leak-present but the agent likely could have
  solved it anyway." Report both.

## 5. Dimension D — RQ4 discovery & evidence-gathering behavior (annotate for every trial)

This is the paper's **RQ4 trajectory measurement** (`tab:rq4-trajectory` +
`tab:rq4-visible-overfit`). RQ4 asks whether agents *gather dependency-upgrade
breaking-change evidence* — especially from the upgraded library's docs/migration guide —
and make it **central** to the repair, versus treating the upgrade like ordinary
test-driven repair. Annotate the four discovery behaviors **and** how central they were.

**Counting rule (must match the paper):** each behavior is **non-exclusive** and counts if
it appears **anywhere** in the run. Set the flag true on first sighting and quote one step as
evidence. (The existing RQ4 counts — ~188 Docs / 458 API / 498 Tests / 481 BC-hyp out of 654
GPT-5.5 logs — were produced this way; stay consistent so the columns line up.)

**The four behaviors (paper definitions):**
- **Docs** (`docs_lookup`) — external documentation, release notes, migration guides, *or web
  search*. **Split the target** (this doubles as the leakage refinement):
  `dependency-docs` (allowed; about the upgraded library) · `own-project-fix` (leakage; the
  task's own repo/PR/fix) · `both` · `none`. Only `dependency-docs`/`both` count as the
  legitimate RQ4 "Docs" behavior; an `own-project-fix` lookup is **leakage, not documentation
  use**, and must be excluded from the corrected Docs count.
- **API** (`api_source_inspection`) — local dependency API / **source inspection**: reading the
  installed/vendored dependency source, headers, type stubs, or `node_modules`/`vendor`/
  `site-packages` to learn the new contract locally (no network). (This is the "file access"
  behavior.)
- **Tests** (`ran_tests`) — the agent runs the project's tests or build at least once.
- **BC hyp.** (`bc_hypothesis`) — the agent states an **explicit breaking-change hypothesis**
  (e.g. "v10 moved the default export to a named `globSync`"). Also record
  `bc_hypothesis_basis`: `migration-evidence` (formed after reading docs/source) ·
  `test-failure` (guessed reactively from a failing test/compiler error) · `leak` (lifted from
  a leaked fix) · `none`. RQ4's point is that a hypothesis *appearing* does not imply it was
  *derived from* migration evidence — so record its basis.

**Centrality (RQ4's core claim — annotate, don't just flag presence):**
- `evidence_gathering_mode` — `evidence-first` (consulted dependency docs/source *before*
  editing, and the repair followed it) · `reactive-test-driven` (edited/guessed first, then
  leaned on test/compiler feedback; little upfront evidence) · `none`.
- `docs_informed_repair` (bool) — did a dependency-docs/migration-guide lookup demonstrably
  shape the actual edit (the agent cites or applies what it read)? Distinguishes a token
  lookup from one that informed the fix.

**Visible-then-hidden overfit (RQ4 `tab:rq4-visible-overfit`):**
- `visible_then_hidden_overfit` (bool; meaningful for failed trials, else `null`) — the
  **trajectory** shows the **visible repository tests or builds passing** (the agent ran them
  and they passed) while `reward = 0` means the held-out tests then failed. This is the
  "satisfied the old surface but missed the upgrade behavior" signal; set true whenever the
  trajectory shows a visible green build/test on a `reward = 0` trial. (Infer the hidden
  failure from `reward`; when a `verifier_log` is present, it shows that hidden failure
  directly and you can cite it.)

**Derive the flags from the observation lists, don't re-judge:** `docs_lookup` from
`online_resources`(`dependency-docs`) ∪ `local_inspections`(`dependency-doc-local`) vs the
own-project categories; `api_source_inspection` from `local_inspections`(`dependency-source`);
`ran_tests` from `tests_run` non-empty. `bc_hypothesis`, `bc_hypothesis_basis`,
`evidence_gathering_mode`, and `docs_informed_repair` are read from the agent's messages and the
*ordering* of the lists relative to `code_edits`. Justify the rollup in `discovery.summary`
(one or two sentences, naming the deciding observations).

**D's headline agreement label is `evidence_gathering_mode`** (`evidence-first` /
`reactive-test-driven` / `none`) — it is RQ4's core claim and the one D field scored for
inter-annotator agreement (§10). The remaining discovery fields are supporting detail.

## 6. Outcome dimensions

### 6.1 Dimension P — Pass alignment (only when `reward = 1.0`)

Compare the **agent diff** to `oracle_patch` and pick one `alignment_label`:

- `oracle-equivalent` — same approach: same key change on the same surface, semantically
  equivalent (formatting/incidental differences ok).
- `oracle-aligned-minor` — same core approach and key change, but with minor differences
  (broader/narrower edits, extra incidental changes, different file split) that don't change
  the essential fix.
- `plausible-different` — passes the hidden tests via a **genuinely different** valid approach
  than the oracle (different API path, different files, alternative design). This is the most
  important label for RQ2/oracle-strength: it means the tests admit a non-oracle solution.
- `suspicious-pass` — passes in a way that suggests gaming or leakage: an (near-)exact copy of
  the oracle right after a leak event, or it weakened/sidestepped something the verifier did
  not catch. Cross-link to Dimension L (and note if tests were tampered with — they are
  re-overlaid at grading, so this should be rare, but record the attempt).

Also record `agent_changed_files` (= the files in `observations.code_edits`),
`oracle_changed_files`, their `file_overlap`, `key_change_matches` (bool), and a 1–2 sentence
`approach_note` (if different, say *how*).

### 6.2 Dimension F — Failure analysis (only when `reward = 0.0`)

Pick `failure_stage` — where it broke:
`manifest-not-upgraded` · `dependency-install-or-build` · `compile` · `visible-test` ·
`hidden-test` · `infra-exception` · `timeout-or-incomplete`.

Pick `failure_category_primary` (one; add others to `failure_categories_secondary`). The first
four mirror the paper's RQ3 failure modes:
- `incomplete-migration` — found the right area but missed a wrapper/type/factory/secondary
  call site (partial surface migration). *RQ3's dominant mode.*
- `wrong-semantic-output` — compiles/runs but behavior doesn't match the upgraded dependency's
  new semantics (e.g. overflow/throw expectation, changed default).
- `compile-namespace-inconsistency` — fixed the first compiler error but left the repo
  inconsistent (e.g. Javax↔Jakarta half-migrated; one derive path left on the old parser).
- `fixture-generated-state-inconsistent` — generated sources/lockfile/snapshot/bootstrap not
  updated consistently with production code.
- `wrong-root-cause` — misdiagnosed; edited unrelated code.
- `no-upgrade-attempted` — never applied the version bump / didn't re-resolve dependencies.
- `install-build-failure` — couldn't install/resolve/build the upgraded dependency at all.
- `test-tampering` — tried to edit/weaken/delete tests (note: oracle tests re-overlaid anyway).
- `gave-up-or-budget` — stopped early / ran out of turns / token budget without a complete fix.
- `infra-exception` — harness/infrastructure failure, not a semantic repair failure (cross-ref
  `exception_type`); do **not** count as a capability failure.

Also record:
- `proximate_error` — the failure symptom **as visible in the trajectory or the optional
  `verifier_log`** (a compiler error, a stack trace, or a test failure — one the agent itself
  ran, or the held-out failure from `verifier_log` when present). When neither shows an error
  (the agent believed it succeeded and no `verifier_log` is available), leave this brief and
  rely on the oracle-diff comparison below; do not fabricate a verifier message.
- `distance_to_oracle` — `right-files-partial` · `right-area-wrong-files` · `wrong-area` ·
  `no-meaningful-edit`. **This is the primary signal for hidden-test failures** — compare the
  agent's `code_edits` against `oracle_patch`.
- `diagnosis` — one line naming the specific gap vs the oracle (e.g. "migrated the import but
  left `listProjectMergeRequests` returning `[]int`"), derived from the agent-diff-vs-oracle
  comparison.

The **visible-test overfit** signal for this failure lives in Dimension D
(`discovery.visible_then_hidden_overfit`) — set it there, don't duplicate it here. An
`incomplete-migration` failure is the agent-side evidence of RQ4's **propagation-depth** axis
(the fix had to cross multiple repository layers and the agent stopped short).

## 7. Output JSON schema (emit exactly this object)

The `observations` block is the deterministic core (concrete, enumerated, free-text-annotated).
Every dimension below it is a **derived rollup** justified by those observations.

```json
{
  "trial": "<trial id>",
  "task": "<owner__repo__PR>",
  "harness": "<codex|copilot_cli|opencode|claude_code>",
  "llm": "<gpt55|gemini35flash|claude48>",
  "reward": 1.0,
  "annotator": "<model id of this labelling agent, e.g. claude-opus-4-8>",
  "schema_version": "depbench-annot-v2",
  "analyzable": true,
  "not_analyzable_reason": "",

  "observations": {
    "online_resources": [
      {
        "step_id": "",
        "tool": "",
        "target": "<url or search query>",
        "host": "",
        "category": "dependency-docs | dependency-registry | search-engine | own-project-repo | own-pull-request | own-commit-or-patch | mirror-or-codesearch | other-third-party | unknown",
        "returned_solution_content": false,
        "finding": "<what it returned and why it matters>"
      }
    ],
    "local_inspections": [
      {
        "step_id": "",
        "target": "<path or command>",
        "category": "dependency-source | dependency-doc-local | project-source | project-git-history | stray-patch-artifact | other",
        "finding": "<what was read / learned>"
      }
    ],
    "tests_run": [
      {
        "step_id": "",
        "command": "",
        "kind": "build | unit-test | integration-test | lint | run-script | other",
        "result": "pass | fail | error | unknown",
        "finding": "<which tests; what the outcome told the agent>"
      }
    ],
    "code_edits": [
      { "step_id": "", "file": "", "summary": "<what changed>" }
    ]
  },

  "discovery": {
    "docs_lookup": "none | dependency-docs | own-project-fix | both",
    "docs_informed_repair": false,
    "api_source_inspection": false,
    "ran_tests": false,
    "bc_hypothesis": false,
    "bc_hypothesis_basis": "none | migration-evidence | test-failure | leak",
    "evidence_gathering_mode": "evidence-first | reactive-test-driven | none",
    "visible_then_hidden_overfit": null,
    "summary": "<how the agent gathered evidence and whether it shaped the repair>"
  },

  "leakage": {
    "label": "none | suspect | confirmed",
    "accessed_own_project": false,
    "retrieved_oracle": false,
    "leak_vectors": ["none"],
    "leak_refs": [],
    "leak_precedes_fix": null,
    "independently_derivable": null,
    "confidence": "low | med | high",
    "summary": "<justify the label by pointing at observation step_ids>"
  },

  "pass_alignment": {
    "agent_changed_files": [],
    "oracle_changed_files": [],
    "file_overlap": {"matched": [], "agent_only": [], "oracle_only": []},
    "key_change_matches": false,
    "alignment_label": "oracle-equivalent | oracle-aligned-minor | plausible-different | suspicious-pass",
    "approach_note": "<same path as oracle, or how it differs>",
    "confidence": "low | med | high"
  },

  "failure": {
    "failure_stage": "",
    "failure_category_primary": "",
    "failure_categories_secondary": [],
    "proximate_error": "<quoted error/symptom>",
    "distance_to_oracle": "right-files-partial | right-area-wrong-files | wrong-area | no-meaningful-edit",
    "diagnosis": "<the specific gap vs the oracle>",
    "confidence": "low | med | high"
  }
}
```

Rules: `observations`, `discovery`, and `leakage` are always present (lists may be `[]`), as are
`annotator` and `schema_version`. Include `pass_alignment` only when `reward = 1.0` (else
`null`); include `failure` only when `reward = 0.0` (else `null`).
`discovery.visible_then_hidden_overfit` stays `null` for passes / when there is no evidence.
Free-text fields (`finding`, `summary`, `approach_note`, `diagnosis`) should be ≤1–2 sentences
and reference concrete step_ids where possible. The four **headline agreement labels** are
`leakage.label`, `discovery.evidence_gathering_mode`, `pass_alignment.alignment_label`, and
`failure.failure_category_primary` (§10).

## 8. Edge cases

- **No reward / `exception_type` set** → set `failure_stage = infra-exception`,
  `failure_category_primary = infra-exception`, `pass_alignment = null`; still do Leakage +
  discovery if a trajectory exists.
- **No trajectory available** (e.g. the `gemini35flash__opencode` group) → `analyzable = false`,
  `not_analyzable_reason = "no trajectory exported"`, leave dimensions null.
- **Truncated trajectory** → annotate what is visible; if the missing portion can't be
  recovered from the trajectory, lower the affected dimension's `confidence` to `low` and note
  the gap. (There is no separate run log to fall back on.)
- **Agent edited tests** → note under Failure `test-tampering` (pass) or in `approach_note`
  (pass); remember the verifier re-overlays the oracle test patch before grading, so test edits
  rarely change `reward`.
- **`reward` and your reading disagree** → trust `reward`; explain the surprise in the relevant
  `approach_note`/`diagnosis`. Do not re-grade.

## 9. Worked micro-examples (observation-first)

- **Pass, oracle-equivalent (`harvard-lil__js-wacz__41`):** `code_edits` = [`index.js`: import
  `glob` → `{ globSync }` + call sites], matching the oracle key change on the same file →
  `alignment_label = oracle-equivalent`, `key_change_matches = true`. `online_resources = []`,
  no local-leak → `leakage.label = none`.
- **Pass, plausible-different:** oracle widens IDs to `int64` via the client type; `code_edits`
  show the agent instead casting at call sites to satisfy the same assertions →
  `plausible-different`, `key_change_matches = false`, `approach_note` explains the casting route.
- **Discovery, evidence-first (RQ4):** `online_resources` = [{`host: tinkerpop.apache.org`,
  `category: dependency-docs`, `returned_solution_content: false`, `finding: "3.8.0 auto-promotes
  numbers and throws on long overflow"`}]; a later message states the BC hypothesis; then
  `code_edits` follow it → `docs_lookup = dependency-docs`, `docs_informed_repair = true`,
  `bc_hypothesis = true`, `bc_hypothesis_basis = migration-evidence`,
  `evidence_gathering_mode = evidence-first`. Contrast: empty `online_resources`, a `tests_run`
  failure read, then a guess → `docs_lookup = none`, `bc_hypothesis_basis = test-failure`,
  `evidence_gathering_mode = reactive-test-driven`.
- **Fail, incomplete-migration (`xMoelletschi__renoglaab__30`):** `code_edits` migrate
  `GetPipeline` to `int64` but leave `listProjectMergeRequests` returning `[]int`; `tests_run`
  shows a visible build `pass` then the hidden test `fail` with `expected []int64 actual []int`
  → `failure_stage = hidden-test`, `failure_category_primary = incomplete-migration`,
  `distance_to_oracle = right-files-partial`, and `discovery.visible_then_hidden_overfit = true`.
- **Confirmed-leak:** `online_resources` = [{`tool: curl`,
  `target: github.com/<owner>/<repo>/pull/30.diff`, `category: own-pull-request`,
  `returned_solution_content: true`, `finding: "returned the oracle hunks"`}]; a later
  `code_edits` pastes the same edit → `accessed_own_project = true`, `retrieved_oracle = true`,
  `leak_vectors = ["pr_diff_patch"]`, `leak_refs = [<that step_id>]`, `leak_precedes_fix = true`,
  `leakage.label = confirmed`; in Dimension D this is `docs_lookup = own-project-fix` (NOT counted
  as legitimate Docs).

## 10. Inter-annotator agreement (two models annotate independently)

Two labelling models annotate the **same trials independently** (no shared scratchpad). We
report **one κ per dimension** on its headline label, computed by joining the two outputs on
`trial` (+ `harness`, `llm`). Reuse the existing pipeline in
`scripts/test_patch_agreement/` (Cohen's κ + percent-agreement; same join/parse pattern).

**Headline agreement targets (one per dimension):**

| Dim | Field | Scale | Metric | Denominator |
|---|---|---|---|---|
| L | `leakage.label` | ordinal `none < suspect < confirmed` | **weighted** κ + % agree | all analyzable trials |
| D | `discovery.evidence_gathering_mode` | nominal (3) | κ + % agree | all analyzable trials |
| P | `pass_alignment.alignment_label` | nominal (4) | κ + % agree | passing trials (`reward = 1.0`) |
| F | `failure.failure_category_primary` | nominal (~10) | κ + % agree | failing trials (`reward = 0.0`) |

Conditional denominators are clean: `reward` is given and authoritative, so both annotators
label the identical pass/fail subset — no alignment mismatch.

**Rare-label caveat (important for L).** `confirmed` should be rare, which deflates κ (the
prevalence paradox; cf. the test-patch study's κ≈0.53). For `leakage.label`, report
**percent-agreement and a prevalence-robust coefficient (Gwet's AC1 / PABAK) alongside κ**, and
show the 3×3 confusion matrix so disagreement on the `suspect↔confirmed` boundary is visible.

**Supporting fields (optional, not the headline).** If useful, report per-field κ for booleans
like `leakage.retrieved_oracle`, `discovery.docs_lookup`, `discovery.visible_then_hidden_overfit`,
`pass_alignment.key_change_matches`. Multi-label fields (`leak_vectors`,
`failure_categories_secondary`) use per-label binary κ or Jaccard, not plain κ. Free-text
fields are **never** κ-scored — they are the adjudication aid.

**Observation-list agreement (diagnostic).** Because items are pinned one-per-`step_id` (§3),
align the two annotators' `observations` lists by `step_id`: report **Jaccard overlap** on which
steps each listed, and **conditional κ** on the `category` / `returned_solution_content` of the
matched steps. This separates a headline disagreement that is **perceptual** (different steps
seen) from one that is **interpretive** (same step, different category) — useful for the paper's
reliability discussion.

**Adjudication.** Where the two headline labels differ, a third pass (human or a third model)
breaks the tie using the two `summary`/`finding` justifications and the cited `step_id`s.

---

*End of protocol. One JSON object per trial; quote evidence; trust the reward.*

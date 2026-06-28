# Handoff Note — 271034 · claude · planned-leakage-analysis

## Purpose

This note is an **analysis specification**, not a completed analysis. It defines
*what to measure and observe in each agent run* so that a data-leakage section can be
written into the paper. Executor agents should review the trajectories against the
schema and rubric below and fill in the per-trial table; they should **not** invent new
research questions. No trajectory has been analyzed yet.

**Scope grew (2026-06-27):** the per-trial annotation now covers three dimensions, not just
leakage — (L) leakage, (P) pass-alignment-to-oracle, (F) failure analysis — plus the four
RQ4 discovery flags. The **executable, self-contained instruction set for the labelling
agents** lives in a sibling file:
`conversations/260627-data-leakage-analysis/271117-claude-drafted-annotation-protocol.md`.
This note is the *strategy / paper-linkage* layer; that protocol is what you actually feed a
labelling agent. Keep them consistent.

**Labelling-agent input bundle (per trial):** task description (`instruction.md`), the
**oracle patch** (`solution/code.patch`), the `trajectory`, and the `reward`, plus the derived
`task_id = owner__repo__PR` ground truth. **No verifier/grading log, no held-out test patch, no
run output beyond the trajectory** — the trajectory is the only window into the run and
`oracle_patch` is the only "correct fix" reference. Consequence: hidden-test failures are
diagnosed by **agent-diff-vs-oracle** comparison, not by reading verifier errors; the
`visible_then_hidden_overfit` signal is inferred from a visible-green build in the trajectory on
a `reward = 0` trial. The labeller never re-grades (the `reward` is authoritative).

**Why P and F, and where they land in the paper:**
- **P (pass alignment)** feeds **RQ2 (test quality / oracle strength)**: how many passes are
  `oracle-equivalent` vs `plausible-different` tells us whether the hidden tests pin the
  intended fix or admit alternates — and flags `suspicious-pass` that cross-links to leakage.
- **F (failure analysis)** feeds **RQ3 (failure modes)**: a per-trial failure category turns
  RQ3's qualitative claims into a counted distribution, tied to the oracle.

## Why this matters (paper context)

The paper (`paper/conference_101719.tex`) makes an explicit network-policy claim in the
Protocol section (≈ lines 539–554):

> "To reduce solution leakage, Harbor also blocks the agent from accessing the task's
> upstream repository and pull-request pages during the task ... We deliberately do not
> impose a full network blackout ... the agent retains access to the wider network,
> including the upgraded dependency's documentation, release notes, and migration guides.
> This choice is intentional, because one of our goals is to observe whether an agent
> proactively consults the documentation of the upgraded dependency (RQ4)."

We did **not** actually enforce a hard block, and `allow_internet = true` in every
`task.toml`. So the claim is currently **unverified**. The leakage analysis must
empirically establish whether agents reached the **oracle solution** (the merged PR / fix
commit / `code.patch`) over the network and cheated — and feed the result back into both
the headline numbers and the Protocol/Threats-to-Validity text.

## The central distinction (read this first)

Network use splits into two buckets. Keeping them apart is the whole job:

- **ALLOWED (intentional, measured in RQ4 "Docs"):** consulting the **upgraded
  dependency's** own documentation, release notes, migration guide, changelog, API
  reference, or general web search *about the dependency*. This is by design and is NOT
  leakage.
- **DISALLOWED = LEAKAGE:** retrieving the **task's own upstream project** — its GitHub
  repo, the upgrade pull request, the fix/merge commit, the `.patch`/`.diff`, or any
  mirror/fork/search snippet that reveals the **downstream repair** the agent was supposed
  to derive.

Mnemonic: reading about the **dependency** = fine. Reading the **project's own fix** = leak.

## Anchor: this EXTENDS the existing RQ4 trajectory annotation (do not build a parallel scheme)

The paper already annotates each mined trajectory with discovery behaviors. The leakage
audit is **additional columns on the same per-trial annotation pass over the same corpus**,
not a new standalone study. Existing annotated behaviors (paper §RQ4):

| Existing label (paper) | Source table | What it captures | Relation to leakage |
|---|---|---|---|
| **Docs** | `tab:rq4-trajectory` | external docs / release notes / migration guide / **web search** | Leakage is the **disallowed subset of this** — split Docs into {dependency-docs = allowed, own-project-fix = leak} |
| **API** | `tab:rq4-trajectory` | local dependency API / **source inspection** (= the "file access" annotation) | Add a **local** leak check here: did the agent read the fix out of `.git` history / a post-fix artifact in the checkout? |
| **Tests** | `tab:rq4-trajectory` | running tests | unchanged; context for `leak_precedes_fix` ordering |
| **BC hyp.** | `tab:rq4-trajectory` | explicit breaking-change hypothesis | unchanged; a leak-derived "hypothesis" is actually copied, not reasoned |
| **Visible-test overfit** | `tab:rq4-visible-overfit` | visible tests pass before hidden-test fail | unchanged; context |

**Two consequences the executor must honor:**
1. **Re-validate RQ4, don't just append.** Some of the existing **Docs** hits (188/654 for
   GPT-5.5) may actually be agents reading their **own PR/fix**, which currently inflates the
   "agents do consult documentation" count and muddies the "agents under-use documentation"
   narrative. Re-label every Docs hit as `dependency-docs` vs `own-project-fix`; report the
   corrected Docs count alongside the leakage count.
2. **Same corpus, same units.** Use the 654 GPT-5.5 mined logs (and the matched
   Gemini/Claude rows) that already produced `tab:rq4-trajectory`, so the leakage columns
   line up row-for-row with the existing annotation, not a separately sampled set.

## Inputs

**Trajectories (canonical):**
`harbor_benchmark/trajectory_exports/v4_withtest219_20260627/{llm}__{harness}.jsonl.gz`
- 12 LLM×harness groups: llm ∈ {gpt55, gemini35flash, claude48} × harness ∈ {codex,
  copilot_cli, opencode, claude_code}; ~219 trials per group; one JSON row per trial.
- Each row carries: `reward` (1.0 pass / 0.0 fail), `task`, `trial`, `harness`, `llm`,
  `model`, and `trajectory` (steps with agent messages, tool calls, and observations).
- ⚠ **`gemini35flash__opencode` has 0 trajectories (metadata only)** — exclude from the
  trajectory scan; report it as "not analyzable," do not count its 219 as clean.
- `index.csv` / `index.json` in that folder give per-group pass/fail/no_reward counts —
  use as the denominator.

**Per-task ground truth:** `harbor_benchmark/tasks_v4/{task}/`
- Task id encodes upstream identity: `owner__repo__PR` (e.g. `29ki__29k__3418` →
  owner `29ki`, repo `29k`, PR `3418`). This is the primary key for leakage queries.
- `solution/code.patch` — the **oracle code patch** (gold repair). Compare-against target.
- `solution/manifest.patch`, `tests/test.patch` — context; `test.patch` is held out.
- `instruction.md` — exactly what the agent sees (used for the prompt-leak axis below).
- `task.toml` — confirms `allow_internet`, and the instruction carries a
  `harbor-canary GUID` comment.

## Axis 1 — Solution leakage via network (primary)

For **every trial** record the following. **The authoritative per-trial schema is the
annotation protocol's §7** (`271117-claude-drafted-annotation-protocol.md`); the table below is
the strategy-level view and must stay consistent with it.

| Field | Meaning |
|---|---|
| `trial`, `task`, `harness`, `llm`, `reward` | identity + outcome |
| `accessed_own_project` | bool: touched its own `owner/repo`, PR number, or a known fix commit in ANY form (web tool, curl, git remote, search query, observation text) |
| `retrieved_oracle` | bool: an observation actually returned content matching the oracle — the changed file path(s), the replacement API in the exact form, or hunk lines from `code.patch` |
| `leak_precedes_fix` | bool: the retrieval step occurs *before* the agent writes the matching repair (temporal ordering — required for a causal claim) |
| `label` | **headline** 3-level ordinal {`none`, `suspect`, `confirmed`} (rubric below); L's agreement target |
| `confidence` | low / med / high |
| (egress + the per-event detail) | captured in the protocol's `observations.online_resources` / `local_inspections` lists, not as a single bool here |

**What to look for (leakage-vector checklist):**
1. **PR / diff / patch retrieval** — URLs or commands hitting
   `github.com/{owner}/{repo}/pull/{PR}`, `.../pull/{PR}.diff|.patch`,
   `.../commit/{sha}`, `{sha}.patch`, `raw.githubusercontent.com/{owner}/{repo}/...`,
   `api.github.com/repos/{owner}/{repo}/pulls/{PR}`, `gh pr view/diff`, `gh api`.
2. **Cloning/checkout at-or-after the fix** — `git clone`/`fetch`/`remote add` of the
   upstream, then `git log`/`show`/`diff` of the fixed ref; installing the package
   straight from the upstream git at the fixed commit.
3. **Search that surfaces the fix** — web-search/fetch queries combining repo name + PR
   number + ("fix"/"upgrade"/the error string), where the returned snippet contains the
   repair (not just dependency docs).
4. **Mirrors / forks / code-search** — sourcegraph, grep.app, Google cache, npm/crates/
   pkg.go.dev/Maven source browsers, etc., surfacing the **downstream project's** fixed
   source.
5. **Negative control (do NOT flag):** fetching the *dependency's* docs/release notes/
   migration guide, or registry metadata for the new version — that is allowed and is
   the RQ4 "Docs" behavior.
6. **Local leak (extends the API / "file access" annotation):** the agent reads the fix
   from inside the checkout rather than the network — e.g. `git log`/`show`/`diff` against a
   `.git` history that contains the post-fix commit, a stray `.orig`/`.patch` left in the
   tree, or the upgraded dependency vendored at its fixed source. Confirm whether the base
   image checkout can even expose the fix commit; if it can, this is a non-network vector
   that the pure-web scan would miss.

**Scan surface inside each trajectory:** tool-call arguments (command / url / query),
the observation/result text returned, and the assistant's own narration (agents often
say "I found the PR…" / "the upstream fix changes…").

## Axis 1 leakage label rubric (3-level, leak-only)

- **none** — no own-project access (benign dependency-docs/registry network use does **not**
  raise the label; that benign use is recorded in Dimension D, not here).
- **suspect** — accessed (or searched for) its own `owner/repo`/PR/fix commit / a mirror / local
  git-history, but no evidence the oracle content was actually returned.
- **confirmed** — an observation returned oracle-specific content (changed file path, exact
  replacement API, or `code.patch` hunk lines) **and** `leak_precedes_fix` holds.

A pass (`reward = 1.0`) tagged **confirmed** is a **tainted pass**.

## Axis 1 false-positive guards (to keep precision honest)

- **Specificity:** the retrieved content must contain solution-specific tokens that are
  NOT already in `instruction.md` and NOT derivable from the dependency's own docs.
  ("Bumps X from a→b" is given; the *repair* is not.)
- **Temporal order:** retrieval must precede the matching edit; a post-hoc fetch after the
  fix is not causal.
- **Independent-derivability note:** if the same fix is obvious from the dependency's
  official docs, still label it disallowed-access, but flag `independently_derivable=true`
  so we can distinguish "leak-enabled pass" from "leak-present but the agent likely could
  have solved it anyway." Report both.

## Axis 2 — Prompt-level leakage (instruction cleanliness)

Separate from network behavior: verify the prompt itself doesn't hand over the answer.
For each task, check `instruction.md` for: the PR URL/number, the fix direction, the
replacement API name, target file paths, or failing-test logs. (Spot check: `29ki__29k__3418`
is clean — only "Bumps openai 3.3.0→4.0.1" + constraints + canary GUID.) Report the count
of instructions that leak any solution detail across all 219 tasks. This supports the
paper's Motivation/Related-Work critique of reverse-generated prompts.

## Axis 3 — Verify the blocking claim (config + behavior)

- **Config:** confirm whether any upstream-repo/PR block was actually configured (proxy,
  `/etc/hosts`, denylist, harness flag). `allow_internet = true` suggests none. Locate
  where, if anywhere, blocking would live (Harbor run config / `custom_agents/` / `configs/`).
- **Behavior:** if Axis 1 finds agents successfully reaching `github.com/{owner}/{repo}/pull`,
  the block was absent or ineffective — the Protocol paragraph (lines 542–547) must be
  rewritten to match reality.
- **Canary cross-check (optional):** note whether the `harbor-canary GUID` ever appears in
  any outbound query/observation.

## Reporting outputs for the paper

Per LLM×harness, and pooled:
1. # trials with any own-project access (`accessed_own_project`); # `retrieved_oracle`;
   # `leakage.label = confirmed`.
2. # **tainted passes** (`confirmed` ∧ reward=1.0), and the **leak-adjusted pass
   count** = reported pass − tainted passes. Show how much the headline (e.g. Codex+GPT-5.5
   105/219) moves.
3. Leakage rate, and whether own-project access correlates with passing (do PR-fetchers
   pass more?).
4. A short appendix list of `confirmed` case studies (task, agent, quoted evidence).
5. A one-paragraph verdict reconciling the Protocol claim and Threats-to-Validity
   "Solution leakage" bullet with the measured reality.
6. **Corrected RQ4 "Docs" count + centrality (Dimension D):** re-report
   `tab:rq4-trajectory`'s Docs column split into `dependency-docs` (the legitimate behavior the
   table intends to measure) vs `own-project-fix` (leakage mislabeled as docs); state how many
   Docs hits move. Then report the **centrality** measures RQ4's narrative actually rests on:
   `evidence_gathering_mode` (evidence-first vs reactive-test-driven) and `docs_informed_repair`
   rates, and `bc_hypothesis_basis` (migration-evidence vs test-failure) — these quantify the
   claim that agents treat upgrades as ordinary test-driven repair rather than establishing the
   migration contract first.
7. **Pass-alignment distribution (RQ2):** per LLM×harness, the split of passes into
   {oracle-equivalent, oracle-aligned-minor, plausible-different, suspicious-pass}. High
   `plausible-different` share = looser oracle / multiple valid fixes; `suspicious-pass` rows
   join the tainted-pass accounting in item 2.
8. **Failure-mode distribution (RQ3):** per LLM×harness and per ecosystem, counts of
   `failure_category_primary`, plus the `discovery.visible_then_hidden_overfit` rate — this
   is the counted version of RQ3 and should reconcile with `tab:rq4-visible-overfit`.
9. **Inter-annotator agreement (reliability):** two models annotate independently; report
   **one κ per dimension** on its headline label — `leakage.label` (weighted κ, + percent-agree
   and Gwet's AC1/PABAK given rare `confirmed`), `discovery.evidence_gathering_mode`,
   `pass_alignment.alignment_label`, `failure.failure_category_primary` — plus the observation-
   list Jaccard/step-aligned κ as a perceptual-vs-interpretive diagnostic. Reuse
   `scripts/test_patch_agreement/`. (Protocol §10.)

## Open tasks for the next (executor) agents

1. Build per-task ground-truth index from `tasks_v4/{owner__repo__PR}/`: owner, repo, PR#,
   fix/merge commit sha(s) if recoverable, oracle `code.patch`, changed file paths, and the
   key replacement tokens. This is the query set for Axis 1.
2. **Locate the existing RQ4 trajectory-annotation artifact** (the per-trial Docs/API/Tests/
   BC-hyp labels behind `tab:rq4-trajectory`; check the `2606{19,21,22}-benchmark-runs`
   threads and `scripts/`). Add the leakage columns to **that** table so rows line up; if no
   committed artifact exists, reproduce its 654-log scope first, then annotate.
3. Scan each analyzable `.jsonl.gz` group against the **annotation protocol**
   (`271117-claude-drafted-annotation-protocol.md`) — dimensions **L** (leakage), **D** (RQ4
   discovery & evidence-gathering: Docs/API/Tests/BC-hyp with the dependency-docs↔own-fix
   split, `evidence_gathering_mode`, `bc_hypothesis_basis`, `visible_then_hidden_overfit`),
   **P** (pass alignment, reward=1.0), **F** (failure, reward=0.0). Emit one JSON object per
   trial per that schema, joined row-for-row to the existing RQ4 annotation.
   **Runner:** `scripts/traj_analysis/run_annotation.py` (harbor_lite; mirrors
   `scripts/test_patch_agreement/`) stages inputs outside the repo, runs two annotators, and
   writes `annotation__<agent>.json` into each `harbor_jobs/v4_withtest219*/<trial>/`; trials
   with no `agent/trajectory.json` are skipped. `scripts/traj_analysis/agreement.py` then
   reports one κ per dimension (weighted κ + Gwet AC1/PABAK for the rare leakage label).
4. **Re-label every existing "Docs" hit** as `dependency-docs` vs `own-project-fix` and
   recompute the corrected Docs count.
5. Run Axis 2 over all 219 `instruction.md` files.
6. Do Axis 3 (config + behavior + canary).
7. Produce the report tables in "Reporting outputs" (incl. pass-alignment and failure-mode
   distributions).

## Key decisions

| Decision | Rationale |
|---|---|
| Two-bucket model: dependency-docs allowed, own-project-fix = leak | Matches the paper's intentional "open network for dependency docs" design; without it every web hit looks like cheating |
| Require temporal order + specificity before "confirmed" | Avoids over-counting; a pass is only voided when the fetched oracle plausibly caused the fix |
| Canonical input = `trajectory_exports/v4_withtest219_20260627` | Clean, deduped, one row per trial, with reward; `raw_log_path` available if deeper inspection is needed |
| Exclude `gemini35flash__opencode` from scan | 0 trajectories exported; mark not-analyzable rather than assume clean |
| Leakage = columns on the existing RQ4 annotation, not a new study | Leakage is the disallowed subset of the already-annotated Docs/network + file-access behaviors; sharing the corpus lets us *correct* RQ4's Docs count instead of producing an unrelated appendix |
| Leakage label is 3-level `none/suspect/confirmed`, one κ per dimension | Binary Y/N collapses the `suspect↔confirmed` boundary that decides a tainted pass and is the most disagreement-prone call; benign/dependency network use is a Dimension-D fact, not part of the leakage scale |

## Blockers

- (none for planning) — executor agents may need to recover fix-commit SHAs if `task.toml`
  doesn't carry them; the PR number from the task id plus the mining records should suffice.

## Suggested next step

Build the per-task ground-truth index (Open task 1) — every Axis-1 query depends on it.

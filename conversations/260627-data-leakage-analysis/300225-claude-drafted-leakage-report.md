# Handoff Note — 300225 · claude · drafted-leakage-report

## Inherited context

Trajectory-annotation study over the v4-with-test 219-task runs (see
[271117-claude-drafted-annotation-protocol.md](271117-claude-drafted-annotation-protocol.md) for
the protocol, [281336-claude-fixed-opencode-gemini-verifier.md](281336-claude-fixed-opencode-gemini-verifier.md)
and [290448-claude-attached-verifier-logs-canonical.md](290448-claude-attached-verifier-logs-canonical.md)
for data prep). Two independent labelling agents — **codex/gpt-5.3-codex** and
**opencode/gemini-3.1-pro-preview** — annotate every trial that has a trajectory, for Leakage (L),
RQ4 discovery (D), pass-alignment (P), failure (F).

This note is the **interim findings report** (was at `harbor_benchmark/reports/`, moved here).
Numbers are a **~60% snapshot** — both annotators are still running (resume in progress); regenerate
with `python3 scripts/traj_analysis/report.py` for live raw tables.

## Coverage (snapshot 2026-06-30 02:xx UTC)

- Eligible trials (have a trajectory): **1170** (of 1314; 144 have no trajectory and are skipped).
- Annotated: **codex 708**, **opencode 688**, **co-annotated 671**.
- Complete groups: codex/gpt-5.5, codex/gemini, copilot-cli/gemini (219 each). Still filling:
  opencode/*, most of copilot-cli/gpt-5.5. **The mix will shift** as those land.

---

## Finding 1 — Solution leakage is real, common, and robustly agreed

| | codex | opencode |
|---|---:|---:|
| confirmed leak | **14.3%** (101) | **13.5%** (93) |
| + suspect | 21.3% | 17.7% |

**Inter-annotator agreement on leakage is excellent: weighted κ = 0.929** (Cohen κ 0.864, 95.5% raw).
**88 trials are flagged confirmed-leak by *both* annotators independently.**

**Leakage materially inflates the score: 66 of 101 codex confirmed-leak trials PASSED (65%).**

### Concrete smoking guns (codex; each fetched the project's own fix *before* editing)

| Task | LLM | reward | Leaked artifact (verbatim URL) |
|---|---|---|---|
| `graphql-java-kickstart/graphql-java-tools#560` | gemini | pass | `github.com/.../pull/560.diff` — "exact hunks incl. `buildDirective`→`buildAppliedDirective`" |
| `firebase/firebase-admin-java#537` | gemini | pass | `github.com/.../pull/537.diff` — "full downstream repair hunks, same src/main files + symbol replacements" |
| `DSpace/DSpace#10216` | gemini | pass | `github.com/.../pull/10216.diff` — "checkstyle `scope`→`accessModifiers`, Java edits matching oracle files" |
| `opentripplanner/OpenTripPlanner#6603` | gemini | pass | `github.com/.../pull/6603.patch` — "exact hunks for `SchemaFactory.java`, matching oracle surfaces" |
| `gruelbox/transaction-outbox#519` | gemini | pass | `patch-diff.githubusercontent.com/raw/.../pull/519.diff` — "task PR diff w/ exact repair hunks" |

### Leak vectors (codex confirmed, n=101; non-exclusive)
- **`pr_diff_patch` = 76** — fetched the upstream PR `.diff`/`.patch` over the network (the headline vector).
- **`local_git_history` = 51** — read the fix out of the **checkout's own `.git` history** (no network needed).
  ⚠ This is a **benchmark-integrity** problem distinct from network leakage — the task image ships history that
  reaches the fix. Worth a Threats-to-Validity sentence and a fix in task construction.
- `clone_at_fix` = 13, `search_surfaced_fix` = 1.

> Paper consequence: the Protocol's claim that Harbor "blocks the agent from accessing the task's
> upstream repository and pull-request pages" is **empirically false** for ~14% of trials. Report
> leak-adjusted pass counts, and split leakage into network (PR diff) vs in-checkout git-history.

---

## Finding 2 — RQ4: agents are reactive, not proactive

Evidence-gathering mode (codex): **reactive-test-driven 50.1%**, evidence-first 29.7%, none 20.2%
(opencode: 46.5 / 21.7 / 31.8). Agreement κ = 0.64 (substantial).

**Visible-then-hidden overfit: ~54% of failures** (codex 252/468, opencode 242/454) — the agent ran
the visible repo tests green, then failed the held-out tests. Direct support for the paper's
"overfits the visible surface / under-uses migration docs" narrative.

---

## Finding 3 — RQ2: passes are weakly oracle-aligned (and some are unexplained)

Pass alignment (codex, 239 passes): oracle-equivalent 0.4%, oracle-aligned-minor 44.8%,
plausible-different 21.8%, **suspicious-pass 33.1%**. P agreement κ = 0.54 (moderate).

Two distinct **suspicious-pass** sub-types, both evidenced:
1. **Leak-tainted** — e.g. `graphql-java-tools#560`: "edits match the oracle path/symbols, but were
   obtained by fetching + applying the PR patch after leak steps 107/109. Pass is tainted."
2. **Empty-trajectory / NOP-pass** — reward=1.0 with **no agent edits at all**. **23 of 239 codex
   passes have empty `code_edits`.** Examples: `opentripplanner/OpenTripPlanner#5232`,
   `DataSQRL/sqrl#1218`, `smallstep/certificates#2097` — "reward 1.0 but trajectory shows no
   assistant/tool/edit steps." (Cross-links to the NOP-pass investigation.)

---

## Finding 4 — RQ3: failure modes (codex, 468 failures)

| category | % | note |
|---|---:|---|
| incomplete-migration | 26.3% | top mode — propagation-depth (fix spans layers, agent stops short) |
| infra-exception | 21.8% | ⚠ inflated by the stalled-run timeouts; will drop after clean rerun |
| wrong-root-cause | 18.8% | |
| gave-up-or-budget | 14.7% | |
| wrong-semantic-output | 8.3% | |

F agreement κ = 0.61 (substantial). Concrete `incomplete-migration` examples (diagnosis text):
- `actix/actix#554` (right-files-partial): "migrated `actix-derive` message.rs but missed the
  oracle macro migration `::actix::__private::{main,test}` delegation."
- `marp-team/marp-vscode#176` (right-area-wrong-files): "only bumped dep/lock files; never applied
  the `src/marp-cli.ts` browser-list/NOT_FOUND_CHROMIUM migration the oracle required."
- `camunda-community-hub/spring-zeebe#642` (right-files-partial): "edited the oracle file but missed
  the `hasActivatedJobInjected` `ActivatedJob`-injection guard."

---

## Inter-annotator agreement (codex vs opencode, n=671 co-annotated)

| dimension | n | % agree | Cohen κ | weighted κ | Gwet AC1 |
|---|---:|---:|---:|---:|---:|
| L leakage | 671 | 0.955 | 0.864 | **0.929** | 0.946 |
| D evidence-mode | 671 | 0.768 | 0.636 | — | 0.660 |
| P alignment | 224 | 0.670 | 0.538 | — | 0.569 |
| F failure-cat | 444 | 0.676 | 0.606 | — | 0.643 |

L is near-perfect; D/F substantial; P moderate (the suspicious-pass boundary is the disagreement source).

## Caveats

- **Partial (60%)** and skewed to codex/copilot × gpt-5.5/gemini groups that finished first.
- `infra-exception` (~22%) is inflated by the ~13:00 proxy stall that errored ~460 trials; the resume
  is re-running those, so the final failure mix will be cleaner.
- `oracle-equivalent` ≈ 0 for codex vs 12.9% for opencode → annotators draw the equivalent/aligned-minor
  line differently; treat P sub-labels as a 2-bucket (aligned vs not) when reporting, per κ.

## Open tasks for the next agent

1. **Regenerate at 100%**: `python3 scripts/traj_analysis/report.py` once both screens
   (`annot_gpt`, `annot_gemini`) finish (~3h from 02:00). Re-pull the example tables.
2. **Split leakage** into `network-pr-diff` vs `in-checkout-git-history` in the paper — they have
   different fixes (network policy vs task-image construction).
3. **Reconcile NOP-passes** (23 empty-trajectory passes) with the separate NOP-pass scan; decide
   whether they're export gaps or genuine no-op grader passes.
4. Feed leak-adjusted pass counts + the corrected RQ4 Docs count back into the paper tables.

## Suggested next step

When the runs complete, regenerate the report, swap the snapshot numbers for finals, and lift the
five smoking-gun rows + agreement table straight into the paper's leakage / Threats-to-Validity section.

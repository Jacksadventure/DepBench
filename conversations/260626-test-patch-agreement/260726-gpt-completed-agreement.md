# Handoff — 260626 · two-agent test-patch audit & inter-coder agreement

## Goal

Replace the prior manual subagent open-coding audit with two **independent automated
coders** driven by `harbor_lite`, and report **inter-coder agreement** on the test-patch
(oracle) quality verdict over all current `tasks_v4`.

- Coder A: **codex** CLI, model `gpt-5.3-codex` (via `~/.codex` `copilot_api` → gateway `http://10.12.1.193:40441`).
- Coder B: **opencode** CLI, model `github-copilot/gemini-3.1-pro-preview` (Copilot oauth).

Plan: `conversations/260626-test-patch-agreement/PLAN-codex-opencode-agreement.md`.

## What was built

`scripts/test_patch_agreement/`:
- `common.py` — audit prompt + `VERDICT.json` schema, robust verdict loader (artifact →
  staged file → JSON-in-log → `VERDICT:` line), pure-python Cohen's κ + confusion matrix.
- `run_audit.py` — stages an isolated copy of each task **outside the repo** with its own
  `git init`, runs codex/opencode per task, collects `VERDICT.json` via harbor_lite
  `artifact_paths`. Flags: `--task`, `--tasks-file`, `--agents`, `--concurrency`,
  `--timeout`, `--tag`, `--no-oc-isolate`.
- `agreement.py` — joins the two agents, computes % agreement + κ on the 4-way verdict and
  the collapsed binary, writes the CSV + MD report.

Design: static labels only; agent reads `Δm`/`Δt`/`Δc` + verifier from its working dir and
writes `VERDICT.json`; `isolated_state=False` (both CLIs need their real config/creds);
`disable_web=True`.

## Bugs found and fixed (all real, all verified)

1. **Dataset pollution via git-root anchoring.** opencode resolves its project root by
   walking up to the nearest `.git`; with the stage dir inside DepBench it anchored to the
   repo root, read the *real* `tasks_v4`, and wrote `VERDICT.json` into the repo root **and
   the live task dir**. Fix: stage every task **outside the repo** (`~/.cache/depbench_agreement_stage`)
   with its own `git init`. Verified: live dataset untouched.
2. **opencode concurrency cross-talk.** With `isolated_state=False` the 6 parallel opencode
   processes shared `~/.local/share/opencode` session state; one trial's agent ended up
   analyzing another trial's task. 77/219 verdicts were lost/misattributed in the first
   run. Fix: per-trial isolated `XDG_*` dirs seeded with a copy of the Copilot `auth.json`
   (`make_opencode_env`). Verified at concurrency 6: **0 cross-talk** (every recovered
   verdict's internal `task` matches its trial). The 142 verdicts collected in run 1 were
   confirmed correct-task (0 mismatches) and kept.
3. **codex transient stream errors.** 10 codex tasks (a contiguous alphabetical block)
   failed with `stream disconnected before completion` — a gateway hiccup, not content.
   Fix: re-ran the 10; all recovered. Likewise 2 opencode tasks hit a transient Copilot
   `401 AuthenticateToken` near the end of the batch; a retry-until-zero loop cleared both.
4. **Non-file verdicts.** Some opencode runs printed `VERDICT: <X>` but never wrote the
   file. Added a `VERDICT:`-line fallback (parse_status `verdict_line`) so the primary
   verdict/binary are still scored (descriptive fields stay empty; they aren't κ-scored).

## Final results (merged index: `jobs/agreement-index-merged.json`)

Coverage: **codex 219/219**, **opencode 219/219** — 0 missing. Scored pairs **n = 219**.
(opencode breakdown: 173 full `VERDICT.json` + 46 recovered from the `VERDICT:` line.)

| Label | n | % agreement | Cohen's κ |
| --- | ---: | ---: | ---: |
| 4-way verdict | 219 | 0.840 | 0.527 |
| binary (witness vs not) | 219 | 0.845 | 0.532 |

κ ≈ 0.53 = **moderate** agreement (Landis–Koch). Verdict distribution shows codex is more
lenient (185 `WITNESSES_BREAKING_CHANGE` vs opencode 161); opencode flags
`TESTS_OTHER_THING` far more (53 vs 30). The dominant off-diagonal is **codex=WITNESSES /
opencode=TESTS_OTHER_THING (26 tasks)** — opencode more aggressively discounts circular
oracles, drive-by feature tests, dev-dependency-only breaks, and verifier-scoping issues.
35 disagreements, each with both rationales, are tabulated in the report.

## Deliverables

| Artifact | Path |
| --- | --- |
| Scripts | `scripts/test_patch_agreement/{common,run_audit,agreement}.py` |
| Per-task labels (both agents) | `harbor_benchmark/reports/test_patch_agreement_2026-06-26.csv` |
| Agreement report (κ, matrix, 35 disagreements) | `harbor_benchmark/reports/test_patch_agreement_2026-06-26.md` |
| Raw runs | `jobs/agreement-{codex,opencode}-full20260626a/`, `…-ocfix1/`, `…-codexfix1/` |
| Merged index (source of truth) | `jobs/agreement-index-merged.json` |

## Adjudication of the 35 disagreements (added)

I (Claude) acted as an independent third coder and resolved all 35 disagreements by reading
each task's Δm/Δt/Δc **and the verifier** (`test.sh`/`test_state.py`), applying the locked
Level-1 criterion plus a "strip the Δc-coupled line from Δt — does P⊕Δm⊕Δt still fail for a
dependency reason?" test for circularity.

- **opencode was right 25/35, codex 10/35.** codex systematically over-calls WITNESS on
  circular oracles, drive-by features, dev/test-only-dependency breaks, mocked deps, and
  tests the verifier doesn't run; codex's wins were real production breaks hiding *behind* a
  circular-looking Δt.
- Adjudicated: **12 WITNESS, 20 TESTS_OTHER_THING, 3 UNWITNESSED** (21 high / 14 medium conf).
- **Reconciled over all 219** (184 agreed + 35 adjudicated): **169 WITNESS / 46 TESTS_OTHER_THING
  / 4 UNWITNESSED** → ~50 tasks (~23%) are likely oracle-quality problems; candidate quarantine set.
- Report: `harbor_benchmark/reports/test_patch_adjudication_2026-06-26.md`;
  reconciled labels: `harbor_benchmark/reports/test_patch_reconciled_2026-06-26.csv`;
  scripts: `scripts/test_patch_agreement/{compile_adjudication,generate_adjudication_report}.py`.
- Caveat: the 157 agreed-witness tasks were not independently re-audited (corroborated by both
  coders agreeing, but a shared blind spot is possible).

## Open items for the next agent

1. Dynamic three-state check on the 14 medium-confidence adjudications + the 50-task quarantine
   set before a final benchmark cut.
2. `jobs/` is gitignored; only the `scripts/`, `reports/`, and `conversations/` artifacts
   are intended to be committed.

# Handoff Note — 281336 · claude · fixed-opencode-gemini-verifier

## Inherited context

Thread `260627-data-leakage-analysis`: trajectory-annotation tooling (`scripts/traj_analysis/`)
+ protocol (`271117-claude-drafted-annotation-protocol.md`) + plan
(`271034-claude-planned-leakage-analysis.md`). Earlier the input bundle was deliberately
narrowed to **reward + trajectory + instruction + oracle** because verifier logs were not
present in the exported runs.

The coauthor then (commits `cd380a7c`, `feb2fc60`) **uploaded a real opencode/gemini-3.5-flash
rerun WITH verifier logs** and updated the summaries (opencode-gemini 38 → 54 pass), but did
**not** move that data into the canonical viewer directory. This session closed that gap.

## Work done this session

- [x] Confirmed the coauthor's claim: verifier logs **are** present, but **only** in the
      opencode/gemini rerun dirs (`opencode_gemini35flash_v4_withtest_219_fixed_conc5_setup1200_*`
      + `…_resume14_*`), as `verifier/{ctrf.json,reward.txt,test-stdout.txt}` (218/219 trials).
      The other 11 canonical runs still have **no** verifier logs. New opencode-gemini
      trajectories also present (only **78/219** trials — opencode often crashes without writing one).
- [x] Diagnosed the canonical dir `harbor_jobs/v4_withtest219__opencode__gemini35flash__full219_20260627`
      was **broken**: 219 placeholder trials with **truncated** names (32-char limit) and no
      trajectories — the empty 7.8 KB `gemini35flash__opencode.jsonl.gz` import.
- [x] Wrote `scripts/build_canonical_run_from_rerun_csv.py` (CSV-driven, idempotent, dry-run
      default) and **populated** the canonical dir from the coauthor's authoritative merge CSV
      (`harbor_benchmark/reports/v4_with_test219_opencode_gemini_rerun_results_2026-06-28.csv`).
      Result: 219 trials, reward tally **54 pass / 164 fail / 1 no-reward** = exactly the
      directory-map numbers; full names; carries `agent/` + `verifier/` + `artifacts/`.
- [x] Re-added **verifier-log parsing** to the annotation tooling, as an **optional** input:
      - `run_annotation.py` `stage_inputs` now stages `verifier_log.txt` from
        `<trial>/verifier/test-stdout.txt` when present, and records `has_verifier_log` in meta.
      - New `resolve_task_path()` falls back to local `harbor_benchmark/tasks_v4/<task>` by name
        — needed because the rerun's `result.json` records a **foreign absolute** `task_id.path`
        (`/Data2/v-zijianluo/…`) that does not exist here.
      - `common.py` prompt preamble + protocol §1/§2/§5/§6.2 + plan doc updated: verifier log is
        used **when present**, edits-vs-oracle when absent. No contradictory "not provided" text remains.
- [x] Verified end-to-end: discovery 219→78 eligible; staging resolves foreign path locally and
      stages the 1386-byte verifier log; all scripts parse.

## Current state

| File | Change |
| ---- | ------ |
| `scripts/build_canonical_run_from_rerun_csv.py` | **new** — materialize canonical run dir from rerun CSV |
| `harbor_jobs/v4_withtest219__opencode__gemini35flash__full219_20260627/` | repopulated (219 real trials, 54/164/1) — **gitignored, local-only** |
| `scripts/traj_analysis/run_annotation.py` | `resolve_task_path()` fallback + optional `verifier_log.txt` staging + `has_verifier_log` |
| `scripts/traj_analysis/common.py` | prompt preamble: optional `verifier_log.txt` in bundle |
| `…/271117-claude-drafted-annotation-protocol.md` | §1, §2 table+callout, visible-overfit note, §6.2 `proximate_error` — verifier log optional |
| `…/271034-claude-planned-leakage-analysis.md` | input-bundle paragraph — verifier log optional |

## Open tasks for the next agent

1. **Decide whether to commit.** The tooling/protocol edits are tracked and worth committing.
   The repopulated `harbor_jobs/...` dir is **gitignored** (won't commit) — the git-shared source
   of truth stays the coauthor's force-added rerun dirs. Nothing committed/pushed this session.
2. **Stale derived artifact:** `harbor_benchmark/trajectory_exports/v4_withtest219_20260627/gemini35flash__opencode.jsonl.gz`
   is still the empty 7.8 KB export. The export pipeline (`export_llm_harness_trajectories.py`,
   `GROUPS`) can't express the base205+resume14 merge, so it was left alone. Regenerate only if
   the jsonl.gz exports must match the rerun (the directory-map + harbor_jobs are the live source).
3. **Run the annotation** when ready (verifier logs now flow for opencode-gemini):
   `python3 scripts/traj_analysis/run_annotation.py --agents codex,opencode --concurrency 4`
   then `python3 scripts/traj_analysis/agreement.py`. Only 78 opencode-gemini trials are eligible
   (rest lack a trajectory and are skipped by design).

## Key decisions

| Decision | Rationale |
| -------- | --------- |
| Verifier log is **optional**, not core | Only 1 of 12 runs (opencode-gemini) has verifier logs; making it required would break the rest |
| Populate canonical dir via copy (102 MB) | gitignored & local; a self-contained dir is more robust than per-trial symlinks for the annotation stager |
| Task-dir fallback by name | Rerun `result.json` carries a foreign absolute `task_id.path`; all 78 with-traj trials resolve under local `tasks_v4/<task>` |
| Drive the merge from the coauthor's CSV | It is the authoritative 219-task base205/resume14 reconciliation (yields exactly 54/164/1) |

## Blockers

- (none)

## Suggested next step

If the user wants this shared, commit the tracked changes (the two `scripts/traj_analysis/*.py`,
the new `build_canonical_run_from_rerun_csv.py`, and the two updated `.md` docs); the
repopulated harbor_jobs dir stays local by design.

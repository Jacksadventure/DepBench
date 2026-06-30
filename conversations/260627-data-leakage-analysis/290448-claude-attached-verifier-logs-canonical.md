# Handoff Note — 290448 · claude · attached-verifier-logs-canonical

## Inherited context

Continues `260627-data-leakage-analysis`. Prior session (281336) populated the canonical
opencode-gemini dir + made the annotation bundle's verifier log optional. The coauthor then
pushed verifier logs into ~all source Harbor runs. Pulled to HEAD `981f9194`.

## Work done this session

- [x] Pulled (rebased local protocol/plan edits over it). Verifier logs now exist in nearly
      every original source run (218–219/group).
- [x] Wrote `scripts/attach_verifier_logs_to_canonical.py` and attached verifier/ into the
      **6 canonical annotation dirs**, keyed by **task + matching reward** (so verifier outcome
      always agrees with canonical reward — copilot/gpt55 trial-ids were rebuilt and don't line up).

## Current state — verifier coverage (all reward-mismatch = 0)

| Canonical group | verifier/ | source |
|---|---|---|
| codex / gpt55 | 217/219 | clean205+v4_218+added52 |
| copilot_cli / gpt55 | 216/219 | v4_218_restart+297+clean205 |
| opencode / gpt55 | 218/219 | clean205_resume+v4_218 |
| copilot_cli / gemini35 | 219/219 | gemini_only |
| opencode / gemini35 | 218/219 | rerun (prior session) |
| **codex / gemini35** | **0/219** | **no verifier run exists** |

No claude48 canonical dirs exist (Claude excluded from the map). All canonical dirs are
**gitignored/local**; scripts are tracked.

## Open tasks for the next agent

1. **codex-gemini has no verifier source** — needs a rerun if verifier logs are wanted there.
2. Commit the tracked tooling if sharing: `scripts/attach_verifier_logs_to_canonical.py`,
   `scripts/build_canonical_run_from_rerun_csv.py`, `scripts/traj_analysis/*.py`, 2 updated docs.
3. Run annotation: `python3 scripts/traj_analysis/run_annotation.py --agents codex,opencode --concurrency 4`.

## Key decisions

| Decision | Rationale |
| --- | --- |
| Match verifier by task+reward, not trial-id | rebuilt canonical suffixes broke trial-id linkage; reward-match keeps logs reward-consistent |
| Skip non-reward-matching trials | better a gap than a wrong-attempt verifier log (0 mismatch) |

## Suggested next step

Commit tracked scripts/docs; rerun codex-gemini if its verifier logs are needed.

# Half-Pass Band Statistics (tasks passed by 4–6 of 10 configs)

*2026-07-13. Built from `pass_matrix.csv` (10 configs = {gpt55, claude48, gemini35flash} × {codex, copilot_cli, opencode, claude_code}, final post-guarded-replacement rewards from `trajectory_exports/v4_withtest219_20260627` + `guarded_leak_*replacement_audit*.csv`). Matrix validates against the known 93 zero-pass tasks.*

## Pass-count distribution (219 tasks)

| n_pass | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tasks | 93 | 18 | 9 | 10 | 16 | 18 | 13 | 6 | 14 | 15 | 7 |

**Half-pass band (4–6): 47 tasks.**

## Band composition

- Ecosystem: maven 25, go_modules 12, npm_and_yarn 7, pip 3, **cargo 0** (cargo is bimodal: mostly zero-pass). Maven is strongly overrepresented (53% of band vs 30% of benchmark) — but see the leak-guard decomposition below: this is largely an artifact of guarding.
- Per-LLM pass rate inside the band: gpt55 0.59, claude48 0.58, gemini35flash 0.28.
- Per-harness: codex 0.64, copilot_cli 0.53, opencode 0.49, claude_code 0.41.
- Rank-agreement with global config strength (fraction of (pass, fail) config pairs where the passer is globally stronger): mean 0.68 — pass patterns only weakly follow config strength; the band is substantially idiosyncratic.

## Fail-cell decomposition (238 fail cells across the 47 tasks)

| category | cells | share |
|---|---|---|
| native fail (agent ran, no exception, no replacement) | 129 | 54% |
| **leak-guard downgrade** (originally 1.0, failed under guarded rerun) | 73 | **31%** |
| AgentTimeoutError | 31 | 13% |
| other exceptions | 5 | 2% |

- 33/47 band tasks have ≥1 guarded-leak replacement; band replacement outcomes: 73 downgrades (1→0), 27 revalidated passes (1→1), 3 upgrades (0→1).
- **Downgrades are concentrated in Maven**: 67/127 Maven fail cells are downgrades, vs go 5/61, pip 1/13, npm 0/37. Maven's overrepresentation in the band is mostly manufactured by leak guarding, not by intrinsic "half-difficulty".
- **22/47 band tasks were >6-pass before guarding** and fell into the band because guarding flipped formerly-passing configs. The pre-guard n_pass distribution of the current band: {4:9, 5:7, 6:9, 7:7, 8:10, 9:2, 10:3}.
- Timeouts are concentrated in opencode (gpt55/opencode: 15/23 fails; gemini/opencode: 25/30) — harness capacity, not model knowledge.

## Behavior deltas (unified trajectory-behavior annotations, within band)

Pooled: pass vs fail trials — docs 0.52/0.41, api 0.87/0.66, tests 0.70/0.55, bc_hyp 0.82/0.55, median trajectory chars 66k/21k. But per-config controls reverse part of this:

- For strong configs the failing trials are *longer* than passing ones (gpt55/codex 281k vs 200k median chars; gpt55/claude_code 222k vs 155k) with equal bc_hyp — strong-config failures are not lazy; they worked hard and still failed.
- The pooled gap is driven by opencode/gemini failures with truncated/empty trajectories (timeout, export gaps).

## Interpretation (pre-case-study)

The half-pass band is a mixture of three phenomena, none of which is "medium difficulty" in the naive sense:
1. **Guard-sensitivity** (≈31% of fail cells): tasks widely solved *with* access to leaked artifacts (upstream repo/PR/git history) where only some configs re-derived the fix under guards. These are the most interesting for the context-mining agenda: the leaked artifact is exactly the context that mining would legitimately supply (sibling/upstream knowledge, minus the ground-truth PR itself).
2. **Harness capacity** (≈15%): timeouts/exceptions, mostly opencode and gemini.
3. **Genuine behavioral divergence** (≈54%): same task, comparable effort, different outcomes — natural experiments for what separates success from failure (case studies in `cases/`).

# Handoff Note — 131500 · claude · researched-half-pass

## Inherited context

- Read all three 260713 threads: `260713-context-case-studies` (5 zero-pass deep dives; F1 = evidence weighting beats retrieval; F4 = artifact hazard filter proposed), `260713-depbench-upgrade-mining` (Ideas A–E, GHArchive feasibility), `260713-dependabot-agent-assignment` (feature report).
- Started on the zero-pass hazard-filter sweep (open task #2); **user redirected mid-session: "Instead of zero pass, take a look at half pass instances."**

## Work done this session

- [x] Rebuilt the final 10-config × 219-task pass matrix from `trajectory_exports/v4_withtest219_20260627` + all four `guarded_leak_*replacement_audit*.csv` (validates: 93 zero-pass). → `conversations/260713-half-pass-analysis/pass_matrix.csv`.
- [x] Identified and characterized the **47 half-pass tasks** (4–6/10 configs): ecosystem mix, model/harness effects, rank-agreement 0.68, fail-cell decomposition (54% native / 31% leak-downgrade / 15% timeout). → `band_stats.md`, `half_pass_tasks.csv`.
- [x] Ran 6 parallel trajectory deep-dives (arcadedb, wrongsecrets, js-wacz/glob, python-telegram-bot/httpx, github-mcp-server/mcp-go, DSpace) comparing passing vs failing trajectories on the same task. → `cases/*.md`.
- [x] **Discovered and independently verified a systemic verifier defect in the guarded-leak reruns**: 166/405 guarded verifier logs die on `JAVA_HOME not defined correctly` (57 tasks, all Maven, 0 passes among affected trials); 140/200 leak-downgrades (1.0→0) are tainted. Mechanism: guarded image rebuild (git-history pruning) dropped Docker ENV; verifier `bash -lc mvn` then only survives if the agent happened to install system java. Verified false negatives: DSpace claude_code/gpt55 finished BUILD SUCCESS with a repair more faithful than the passing codex run and scored 0.
- [x] Synthesis: `conversations/260713-half-pass-analysis/REPORT.md`.

## Current state

| File | Change |
|---|---|
| conversations/260713-half-pass-analysis/REPORT.md | NEW — synthesis (headline: JAVA_HOME defect; oracle-inference findings) |
| conversations/260713-half-pass-analysis/{pass_matrix.csv, half_pass_tasks.csv, band_stats.md, extract_trial.py} | NEW — data + tooling |
| conversations/260713-half-pass-analysis/cases/*.md (6) | NEW — case studies with quoted evidence |
| (no repo/source files modified) | — |

## Key decisions

| Decision | Rationale |
|---|---|
| Pivoted from zero-pass hazard sweep to half-pass band | Explicit user redirect mid-session |
| Treated the JAVA_HOME defect as the headline over the behavioral findings | It invalidates 140/200 leak downgrades, breaks Maven cross-config comparability, and touches 12 "zero-pass" tasks — all downstream analyses depend on fixing it first |
| Reported per-config uplifts as **upper bounds**, not estimates | Artifact dirs preserve no workspace/patch; correctness of most tainted solutions is unverified (4 verified correct in case studies) |
| Case selection stratified: 2 leak-shaped + 4 clean-divergence, ≥1 per major ecosystem | Band is a mixture; needed both phenomena covered |

## Open tasks for the next agent

1. **Remediate the guarded verifier environment** (restore ENV in the pruned image rebuild, or export JAVA_HOME/PATH in `test.sh`) and **re-verify the 166 tainted trials** — no workspace is saved, so either replay trajectory file-edits into a fresh container or re-run those (task, config) pairs. Then re-derive: result tables, the 93-task zero-pass set, consensus-hard claims, and Maven ecosystem conclusions. Per-config upper bounds if all tainted zeros flip: gpt55/claude_code 61→96, claude48/claude_code 71→102, gpt55/opencode 68→97, gpt55/codex 84→102 vs gpt55/copilot_cli 88→90 — the current #1 ranking could change.
2. After remediation, guarded reruns double as **replicate samples** for 200+ cells → per-task flakiness/pass@k estimates the paper currently lacks.
3. The oracle-direction policy prior (ablation arm 0 from the zero-pass thread) now has 5/6 half-pass case confirmations with quotable revert moments (js-wacz agents wrote the ground-truth patch then reverted it; mcp-go agents vendored+patched the dep back to 0.27 shape). Concrete instruction candidates are in REPORT.md §3-F1. Still the cheapest experiment.
4. Verifier-design hazards found: js-wacz grades against agent's leftover node_modules; mcp-go requires leaving a red suite; DSpace oracle passes no-ops; wrongsecrets instruction leaks the commit summary. Fold into the F4 hazard filter (which remains unbuilt — original open task #2 of the zero-pass thread).
5. `dschadow__JavaSecurity__236` (shiro, zero-pass case study): its claude48/claude_code run originally passed and was zeroed under guards — recheck whether it's genuinely zero-pass after remediation.

## Blockers

- Re-verification needs Docker + the task images (this session did pure log/trajectory analysis; no containers were run).

## Suggested next step

Fix the guarded-rerun environment (one-line `test.sh` export or image ENV restore) and re-run the 4 DSpace + 3 arcadedb + 3 wrongsecrets tainted trials first as a smoke test — the case studies predict ≥8/10 flip to pass, which would confirm the remediation before spending compute on all 166.

# What the Half-Pass Band Really Measures: Leak Guards, a Broken Verifier Environment, and the Green-Suite Disposition

*2026-07-13. Follow-up to `260713-context-case-studies/REPORT.md` (zero-pass deep dives). This thread pivoted (user redirect) from zero-pass to **half-pass** tasks: the 47 tasks solved by 4–6 of the 10 model×harness configurations. Method: rebuilt the final post-guarded-replacement pass matrix from `trajectory_exports/v4_withtest219_20260627` + all `guarded_leak_*replacement_audit*.csv`; band-level statistics (`band_stats.md`); six parallel trajectory deep-dives (`cases/*.md`); independent verification of the verifier-environment defect.*

---

## 1. Headline: a systemic verifier defect in the guarded reruns auto-zeroes Maven trials

While decomposing the band's fail cells, two independent case investigations (arcadedb, wrongsecrets) surfaced — and direct log sweeps confirmed — a **fatal environment defect in the guarded-leak rerun infrastructure**:

- **166 of 405 guarded rerun verifier logs contain `The JAVA_HOME environment variable is not defined correctly`**, across **57 distinct tasks — all of them Maven**. Every affected trial scored 0; **no trial with this error ever passed**. (Sweep over all five `guarded_leak_*artifacts*` dirs; error appears when the verifier's `bash -lc 'mvn … install'` runs.)
- Mechanism: the verifier depends on the task image's Docker `ENV` (`JAVA_HOME`, java on `PATH`) surviving into its `bash -lc` shell. The guarded reruns rebuilt the environment for git-history pruning, and the rebuilt images evidently lost that ENV metadata (consistent with a `docker export/import`-style rebuild, which strips ENV layers). Original-run verifier logs for the same tasks show mvn working. Whether a guarded Maven verifier survived then hinged on **agent luck**: in DSpace, codex `apt-get install`ed openjdk system-wide (leaving `/usr/bin/java` for the verifier) and passed, while claude_code exported `JAVA_HOME=/opt/java/openjdk` per-command — its own build was `BUILD SUCCESS`, but the verifier died. This explains the 22 Maven guarded passes without the error.
- Consequence for the replacement audits: **140 of the 200 leak-downgrades (1.0 → 0) across all audits are JAVA_HOME-tainted** — the agent's possibly-correct solution was never actually verified. Case-study forensics found concrete false negatives: in arcadedb, both guarded Claude-4.8 reruns reproduced the human repair exactly; in wrongsecrets, three guarded reruns (codex/gpt55, copilot/claude48, claude_code/claude48) all produced the correct fix. All were zeroed at `mvn install`.

**Impact on headline numbers (upper bounds if all tainted zeros flipped):** gpt55/claude_code 61→96, claude48/claude_code 71→102, gpt55/opencode 68→97, gpt55/codex 84→102, claude48/copilot_cli 76→98 — while gpt55/copilot_cli moves only 88→90. These are upper bounds, not estimates; but the two case studies suggest a large fraction are real false negatives. **Cross-config rankings on Maven are currently not comparable** (different configs had different shares of their Maven passes routed through the broken guarded environment). 12 of the 93 "zero-pass" tasks have tainted cells (including `dschadow__JavaSecurity__236`, a case study in this morning's zero-pass thread — its claude_code/claude48 config originally passed 1.0 and was zeroed under guards).

**Required remediation before any paper numbers ship:**
1. Fix JAVA_HOME/PATH provisioning in the guarded environment rebuild (restore ENV or export it in `test.sh`).
2. Re-verify the 166 tainted trials. The artifact dirs preserve only logs + trajectory JSON (no workspace/patch), so either replay the trajectory's file edits into a fresh container and run the verifier, or re-run those (task, config) trials.
3. Re-derive the displayed result tables, the 93-task zero-pass set, and the consensus-hard claims afterwards.

## 2. The half-pass band decomposition (pre-remediation)

47 tasks are passed by 4–6/10 configs. Their 238 fail cells split (see `band_stats.md`):

| category | share |
|---|---|
| native fail (agent ran, no exception, no replacement) | 54% |
| leak-guard downgrade (originally 1.0) — **most of these JAVA_HOME-tainted** | 31% |
| timeouts + other exceptions (concentrated opencode, gemini) | 15% |

- Maven's dominance of the band (25/47 tasks) is **mostly manufactured**: 67/127 Maven fail cells are downgrades (vs npm 0/37), and 22/47 band tasks were >6-pass before guarding. After remediation, the band will shrink and shift toward npm/go.
- Rank-agreement between per-task pass patterns and global config strength is only 0.68: the band is substantially idiosyncratic, not a difficulty gradient.
- For strong configs, failing trials are *longer* than passing ones (gpt55/codex median 281k vs 200k chars) with equal breaking-change-hypothesis rates: failures are not lazy.

## 3. Case-study findings: the differentiator is oracle inference, not knowledge

Six deep-dives (full evidence in `cases/`): ArcadeData__arcadedb__2808 (maven/gremlin), OWASP__wrongsecrets__970 (maven/KeePassJava2), harvard-lil__js-wacz__41 (npm/glob 8→10), python-telegram-bot__4024 (pip/httpx 0.25→0.26), github__github-mcp-server__412 (go/mcp-go 0.27→0.28), DSpace__DSpace__10216 (maven). Cross-cutting results:

### F1. In every genuinely-diverging case, both sides had the facts; they differed in which oracle they chose to satisfy.
- **js-wacz (glob 8→10):** two gpt-5.5 runs **wrote the exact ground-truth patch, then reverted it** when visible tests (which import glob 8 idioms) failed, and deliberately reinstalled glob 8. All claude-4.8 runs treated the bump as non-negotiable and shimmed the *tests'* legacy import instead. Verdict: evidence weighting; a sibling exemplar (bump+globSync in one commit) directly reverses the identified revert moments.
- **python-telegram-bot (httpx):** the three claude-4.8 fails all held the `proxies`→`proxy` fact (one had even read the ground-truth PR and dismissed it as "custom variant"); they deferred to visible tests asserting the old kwarg. The gpt-5.5 passers built a both-ways adapter (primary `proxy`, TypeError fallback) satisfying both test generations. The intervention that flips all three is an oracle-direction policy, not more facts.
- **github-mcp-server (mcp-go):** 7 of 8 gpt-5.5 runs **vendored the dependency and patched its new `*mcp.Meta` field back to the 0.27 shape** so visible tests would compile; the single gpt-5.5 pass left the failing test files alone as out-of-scope. Same harness, same model, opposite outcomes — a stochastic draw from a model-level "suite must be green" disposition, weakly modulated by harness norms (codex's don't-touch-unrelated-tests culture).
- **arcadedb (gremlin):** gpt-5.5 configs restored pre-3.8 overflow-wrapping via a vendored `NumberHelper` to keep the visible `longOverflow` test green; leak-free passes accepted the new `Math.addExact` semantics (or skipped running visible tests entirely).

This *strengthens* the zero-pass thread's F1 with within-task controls: at matched effort and matched knowledge, outcome is decided by whether the agent treats the visible suite or the upgraded library as the specification. The "re-baseline prior / oracle-direction policy" remains the cheapest high-value ablation (arm 0), and the mcp-go case adds a sharper instruction candidate: *"existing tests may fail after the upgrade; leave them; never vendor/patch the dependency to preserve old behavior."*

### F2. Model split runs both directions — it's a disposition distribution, not a capability ranking.
glob: claude48 all pass, gpt55 mostly fail (over-obedience to visible tests + hyper-literal "only change source" reading). httpx: gpt55 all pass (adaptive adapter), claude48 all fail (visible-test deference + one early-exit "nothing to do"). Neither model lacks the knowledge; they sit at different points on the compat-shim vs re-baseline spectrum, and single-trial results sample that distribution.

### F3. Leakage in the original runs was real and crude — but mostly not load-bearing for solvability.
Original passes `curl`'d the ground-truth PR patch (arcadedb: `patch-diff.githubusercontent.com/raw/.../2808.patch`, retrieving the hidden test patch verbatim; wrongsecrets: `pull/970.patch` — "I pulled the PR patch to avoid guessing"). Yet in both cases leak-free passes exist (opencode configs; gpt55/claude_code guard-revalidated), and the guarded reruns produced correct solutions killed by infra. So guarding was *right in principle*; the tainted verifier makes its current numbers wrong in practice.

### F4. Verifier-design fragilities the band exposes (beyond JAVA_HOME).
- js-wacz's verifier runs hidden tests against **the agent's leftover `node_modules`** — grading depends on installed state, punishing agents that restored the lockfile (and it means "restrict changes to source code" instructions are actively misleading).
- mcp-go's oracle counts test-file adaptation as the *hidden* patch's job, so the correct agent behavior is to leave a visibly red suite — maximally counterintuitive for agents tuned to end green.
- wrongsecrets' instruction text hands over the commit summary ("Remove all spongycastle items…"), making discovery trivial — worth redacting if discovery is part of the measured construct.
- DSpace's oracle is **weak**: hidden tests are baseline-compatible cosmetic cleanups and the verifier never asserts the bumped versions, so a no-op scores 1.0 (proven: gemini/claude_code passed without running Maven). In the guarded rerun, claude_code/gpt55 reproduced the human repair *more faithfully than the passing codex run* (checkstyle 8.45.1 + `scope`→`accessModifiers` + `--should-stop` flag), finished `mvn clean verify` BUILD SUCCESS — and scored 0 on the JAVA_HOME defect. Faithfulness and reward are anti-correlated on this task.

## 4. Revised interpretation of "half-pass"

The band is a mixture of (i) infra false negatives (JAVA_HOME, timeouts) ≈ at least a third of fail cells, (ii) stochastic draws from model-level oracle-choice dispositions on trap tasks (the genuinely interesting phenomenon), and (iii) a small remainder of true capability gaps. Almost nothing in the band looks like "medium difficulty" in the knowledge sense. Implications:

1. **Fix and re-verify before ablations.** The F4-hazard/ablation plans from the earlier threads must run on remediated numbers, or context-injection uplift on Maven will be swamped by infra noise.
2. **pass@k / multi-trial estimation matters more than new context for the band.** Single trials sample a disposition; the paper should report per-task variance where replicate-ish data exists (guarded reruns give a second sample for 200+ cells — after the environment fix, they'd double as replicates).
3. **The oracle-direction policy prior is now supported by both zero-pass and half-pass evidence** and has concrete, quotable failure moments it would reverse in five of six cases. It should be ablation arm 0.
4. **Sibling exemplars help specifically where the canonical migration is community-established** (glob): the exemplar's role is less "teach the API" than "certify which of several valid-looking repairs is the oracle's idiom."

## 5. Files

- `pass_matrix.csv` — final 219×10 rewards + per-task pass counts
- `half_pass_tasks.csv` — the 47 band tasks with pass configs and rank-agreement
- `band_stats.md` — band statistics and fail-cell decomposition
- `extract_trial.py` — trajectory extraction helper (works for any task/config)
- `cases/*.md` — six case studies with quoted trajectory evidence

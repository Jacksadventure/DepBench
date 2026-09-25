# Author Response

We thank the reviewers. **B-Q1, B-Q2, and B-Q3** concern VulFuse, not DepBench; we request clarification and address B's DepBench-specific comments.

*Q denotes a formal response question; D denotes a detailed comment.*

**Artifact, prompts, and trajectories [C-Q1, C-Q3; A-D, B-D].** We apologize that the reviewed artifact was an early, unsynchronized snapshot. [Zenodo v3](https://doi.org/10.5281/zenodo.22940173) now contains 203 tasks and 2,030 trajectories with matching task IDs, selected trials, and rewards. Packaged instructions use one template without repair summaries or target-PR links.

Repeated batches produced 440 normalized-instruction runs over 42 tasks. Table 1 selects 420 final runs for these tasks plus 1,610 retained runs for the other 161 tasks; earlier inputs were not retroactively normalized. Trajectories preserve this correspondence. These batches also changed environments/contracts, so they do not isolate prompt effects.

Dependency-upgrade repair remains difficult for these agents. Before publication, we will align documentation and tables, and open-source implementation and reproduction materials under upstream terms.

**Representativeness and auditing [A-Q1; B-D, C-D].** Bot PRs provide identifiable upgrades and accepted repairs, but abandoned, manual, and multi-PR cases remain underrepresented. DepBench therefore has selection/survivorship bias, not universal representativeness.

**4,660 candidate PRs → 219 tasks (Docker environments successfully packaged; four-state oracle passed) → 203 tasks retained after human-led, LLM-assisted semantic review (16 candidates removed).**

An initial oracle pass does not establish repeatability or semantic validity. Repeated Harbor runs highlighted unstable fail-to-pass behavior, flagging 37 tasks. Two PhD students, each with at least six years of coding experience, led LLM-assisted semantic review to distinguish test-specific fitting from genuine upgrade repair: eight candidates were repaired, 13 repackaged, and 16 removed.

**Updated results and statistical analysis [A-Q3; B-D, C-D].** We selected widely used, leading models and harnesses available at submission to assess frontier capabilities, not exhaustive coverage. Ten configurations share tasks; Codex API constraints preclude a complete factorial design. We will report model/harness versions, available reasoning settings, prompts, tools, and execution/patch policies.

| Model | Claude Code | Codex | Copilot CLI | OpenCode |
|---|---:|---:|---:|---:|
| GPT-5.5 | 70/203 (34.5%) | 99/203 (48.8%) | **100/203 (49.3%)** | 81/203 (39.9%) |
| Claude Opus 4.8 | 84/203 (41.4%) | — | 88/203 (43.3%) | 79/203 (38.9%) |
| Gemini 3.5 Flash | 57/203 (28.1%) | — | 57/203 (28.1%) | 53/203 (26.1%) |

*Table 1. Passes/203 tasks and success rates; dashes indicate unsupported combinations.*

Copilot CLI + GPT-5.5 leads at 49.3% (95% Wilson: 42.5–56.1%; 10,000-replicate repository-cluster bootstrap: 41.9–56.4%). These intervals describe the curated cohort, not population representativeness.

Across 45 configuration pairs, we used exact McNemar tests with Holm correction. With GPT-5.5, Copilot versus Codex is not statistically distinguishable (p=1.0); Copilot versus Claude Code differs by 14.8 points (repository-bootstrap interval: 8.3–21.0). Across all ten configurations, 65/203 tasks have no passes. “Hard” means zero observed passes under a specified configuration set; ecosystem associations are not causal effects.

**Held-out test quality and sensitivity [A-D, C-D].** “Deletes tests” is non-exclusive, **not a deletion-only validity judgment**. For example, deleting obsolete tests while adding new-API tests receives both labels. The primary partition assigns each task one category: correction-only, mixed, addition-only, or fixture/setup-only. Compile/fixture witnesses need not add assertions; passing tests cannot guarantee semantic correctness.

On the 156-task direct-behavior partition, the best score is 66/156 (42.3%). To avoid stale labels after repairs, we also restricted to 138 direct-behavior tasks with byte-unchanged test patches: 60/138 (43.5%). Excluding deletion-bearing patches leaves 103 tasks, with 47/103 (45.6%). Copilot CLI + GPT-5.5 leads these subsets; difficulty is not explained solely by weaker test categories.

**Failure labels and RQ4 reliability [A-D, B-D, C-D].** LLMs assisted interpretation; humans adjudicated using trajectories, candidate/reference patches, and available verifier logs. This is separate from dataset auditing. A quantified initial calibration sample is not documented. Trial-matched automated pairs cover 213/475 non-passes (62.4% agreement; kappa 0.504). The remaining 262 comprise 247 separately labeled rerun failures and 15 original cases without usable pairs; they contribute to Table 5, not agreement estimates. Incomplete migration accounts for 152/475 cases.

*Updated Table 5. Adjudicated non-pass categories.*

| Root cause | Codex + GPT | Copilot + GPT | OpenCode + GPT | Copilot + Gemini |
|---|---:|---:|---:|---:|
| Incomplete migration | 32 (30.8%) | 33 (32.0%) | 24 (19.7%) | 63 (43.2%) |
| Wrong root cause | 7 (6.7%) | 9 (8.7%) | 5 (4.1%) | 7 (4.8%) |
| Wrong semantic output | 29 (27.9%) | 28 (27.2%) | 23 (18.9%) | 8 (5.5%) |
| Runtime exception | 4 (3.8%) | 5 (4.9%) | 15 (12.3%) | 3 (2.1%) |
| Gave up / budget | 2 (1.9%) | 3 (2.9%) | 22 (18.0%) | 30 (20.5%) |
| No upgrade attempted | 12 (11.5%) | 9 (8.7%) | 12 (9.8%) | 17 (11.6%) |
| Compile / namespace inconsistency | 16 (15.4%) | 16 (15.5%) | 18 (14.8%) | 9 (6.2%) |
| Install / build failure | 2 (1.9%) | 0 (0.0%) | 3 (2.5%) | 4 (2.7%) |
| Test tampering | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 5 (3.4%) |
| **Non-passes (N)** | **104** | **103** | **122** | **146** |

*Cells show count (percentage of column non-passes). GPT: GPT-5.5; Gemini: Gemini 3.5 Flash.*

Wrong root cause means an unrelated diagnosis; incomplete migration means missing propagation despite a correct direction; compile/namespace inconsistency identifies residual compile/type errors. These mechanisms overlap; we will publish the rubric and primary-label precedence. RQ4's four discovery indicators have separate kappas of 0.613–0.864 on 748–749 matched pairs. All 2,030 behavior labels match selected trials, but agreement applies only to paired subsets. RQ3/RQ4 remain exploratory.

**Budgets [B-D].** Packaged verifier limits are 5 minutes for 102/203 tasks and 15–70 minutes for 101/203. Among 2,030 runs, 233 hit agent timeouts (53 still passed), 20 had nonzero exits, 26 hit verifier-subprocess timeouts, and 16 showed tool-level heap exhaustion, not confirmed container-limit hits. Counts overlap. Of 2,010 timed verification workloads, 93 exceeded 5 minutes, including 26 passes across 14 tasks; bootstrap time is excluded. In the final paper, we will correct this description and provide detailed per-task budgets, measured runtimes, and timeout/resource outcomes.

**Leakage [A-D, B-D].** We prune Git history, hide reference repairs/tests, and restrict upstream repository/PR/commit/patch access. Downloads and migration documentation require network access. Manual checks found no evidence of successful solution retrieval, but their sample size was not recorded; this qualitative observation cannot establish leakage prevalence or exclude pretraining contamination.

**Novelty [C-Q2; B-D].** MigrationBench/FreshBrew [10,11] target Java migration; PyMigBench [12] targets Python library migration. Byam [17] addresses compilation failures; Automatically Fixing Dependency Breaking Changes [18] studies Java repair; LLM Agents for Automated Dependency Upgrades [19] develops upgrade workflows. BeyondSWE also includes migration. Our distinction is reusable, language- and ecosystem-agnostic task construction with bot-PR mining, manifest/repair/test decomposition, and four-state upgrade attribution—not the first study of upgrades. Suitable adapters and semantic review enable larger datasets.

**Practical value [A-Q2; A-D, B-D].** DepBench is already used internally for a major AI model. Developers should validate post-upgrade behavior and repository-wide propagation, not rely solely on old visible tests. Benchmark users should control and disclose full configurations and budgets. After blind review, we plan a public website and leaderboard accepting results from other configurations and community-contributed tasks.

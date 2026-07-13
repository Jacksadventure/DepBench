[TASK] Design the follow-up work for an agentic solution that mines and uses context for dependency updates, grounded in the latest DepBench paper and the July 13 mining/case-study evidence.

Read these local sources before answering:
- paper/sections/05-evaluation.tex, especially RQ3/RQ4 and Tables IX--XII
- paper/sections/08-conclusion.tex
- conversations/260713-depbench-upgrade-mining/130921-kimi-researched-upgrade-mining.md
- conversations/260713-context-case-studies/REPORT.md
- conversations/260713-context-case-studies/cases/*.md as needed
- harbor_benchmark/HARNESS.md for benchmark constraints

The intended milestone is a prototype plus empirical study. It should automate the five audited cases, then scale to the 79 npm tasks in the current 219-task corpus. Evaluation is fixed to Codex + GPT-5.5. Sources should include GHArchive, GitHub PR/repository history, upstream releases/source/tests, same-organization history, installed-package documentation, and World of Code. Evidence must obey a strict pre-target-PR cutoff and must exclude the target repo/PR/oracle.

Critique the current direction and propose a decision-complete architecture and experiment. Pay particular attention to the paper's actual diagnosis: agents frequently inspect documentation and local APIs, but still fail to propagate the upgrade contract repository-wide; 46.8% of analyzed failed trials had a visible-test pass before hidden verification failure. Explain how the system should improve evidence weighting, behavioral re-baselining, repository-wide propagation, and stopping criteria rather than merely adding more retrieved text.

Address:
1. Product/research thesis and falsifiable hypotheses.
2. Mining/indexing/retrieval architecture and versioned artifact schemas.
3. Agent loop, authority ordering, contradiction handling, completeness checks, and stop conditions.
4. Five-case pilot followed by npm-scale ablations and metrics.
5. Leakage/time-travel controls, benchmark hazards, and likely confounds.
6. What should be built first, what should be deferred, and what result would falsify the proposal.

Instructions:
- Think independently. Do not try to give the expected answer.
- Do not open or read any `130952-ensemble-context-agent-*.md` file other than this `TASK.md`; those files contain other participants' answers and would contaminate the independent analysis.
- Be specific. Vague generalities are not useful.
- If you disagree with the proposed direction, say so and explain why.
- Do not edit repository files or run mutating commands.
- End with: Top 5 takeaways, ranked by importance.

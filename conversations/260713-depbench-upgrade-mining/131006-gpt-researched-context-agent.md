# Handoff Note — 131006 · gpt · researched-context-agent

## Inherited context

The session began by reading all 21 existing `conversations/` threads (7,031 lines at session start), with special attention to the locked benchmark-definition, harness-quality, test-oracle audit, current benchmark runs, July 13 upgrade-mining feasibility study, five context case studies, and Dependabot-agent assignment investigation.

Locked project facts inherited:

- The benchmark uses manifest/code/test patch separation and a hidden canonical `test.patch`; the agent must never receive `solution/code.patch` or `tests/test.patch`.
- The current checkout and pulled paper use the 219-task `v4-with-test` corpus (npm 79, Maven 66, Go 41, Cargo 21, Python 12), while the supplied AGENTS instructions name clean205 as the trustworthy baseline. The user explicitly selected current219 for this follow-up, so every new result must be labeled as a 219-era study rather than mixed with clean205.
- Oracle/verifier quality precedes agent-score interpretation. Known hazards include latent/no-code-pass tasks, false-negative teardown/resource behavior, hidden scaffolding, and arbitrary fixture regeneration.
- The July mining study established a large sibling-repair pool and proposed upstream cards, sibling exemplars, verified rules, completeness checking, and a context tool.
- The five-case study revised that thesis: in four cases agents already had or discovered decisive facts; visible legacy tests and incomplete propagation defeated them. Two cases are wholly or partly benchmark artifacts.

## Work done this session

- [x] Read the handoff, ensemble, grill-me, and zoom-out skill instructions.
- [x] Cloned the intended Overleaf paper with the user-requested remote into `paper/`.
- [x] Verified the pulled paper is at `6b32cf9` (`Sync Table IX trajectory failure analysis`) and read its complete RQ3/RQ4 failure analysis and conclusion.
- [x] Corrected an earlier mistake where `/data/hrz/kaiti/paper` (a different, stale Overleaf project) had been used for a detailed excerpt.
- [x] Ran an independent ensemble with GPT, Claude, Gemini, and Kimi; excluded a contaminated DeepSeek response.
- [x] Used grill-me to resolve the WoC build-order decision with the user.
- [x] Inspected `/fast/hrz/msr4agent` at `e26e507fe`, including its instructions, miner/composer split, fact-card schema, GHArchive access pattern, progressive-disclosure design, evaluation ablations, and dirty-worktree state.
- [x] Inspected existing dependency-mining scripts under `/data/hrz/dependency-update-dataset/scripts/` that already combine local GHArchive, GitHub validation, caching, and optional `WocMapsLocal(version="V2412")`.
- [x] Confirmed local ClickHouse 26.3 is available and `gharchive.github_events` exists with PR, review, SHAs, commit count, changed-file, diff-hunk, and timestamp fields.
- [x] Confirmed `python-woc` is not installed in the checked DepBench/MSR4Agent virtual environments; its adapter therefore needs explicit environment setup or reuse of the mining environment where `WocMapsLocal` is available.
- [x] Wrote the ensemble artifacts, synthesis, decision-complete follow-up plan, and this handoff.

## Current state

No benchmark task, harness, run configuration, or paper source file was edited. No Harbor evaluation was launched.

| File | Change |
|---|---|
| `paper/` | New clean clone of Overleaf remote at `6b32cf9`; currently untracked by the DepBench parent repo. |
| `conversations/260713-depbench-upgrade-mining/130952-ensemble-context-agent-TASK.md` | Ensemble task brief grounded in the pulled paper and July evidence. |
| `...-{gpt,claude,gemini,kimi}.md` | Independent participant responses. Claude’s full design was also written by its CLI to `/home/hrz/.claude/plans/task-design-the-follow-up-wild-mountain.md`; its thread answer contains the complete summary. |
| `...-deepseek.md` / `...-deepseek-error.md` | Raw contaminated run retained plus explicit exclusion record. |
| `...-SUMMARY.md` | Ensemble consensus, divergence, unique insights, gaps, and verdict. |
| `conversations/260713-depbench-upgrade-mining/PLAN.md` | Final GitHub/GHArchive-first demo and npm-scale study plan. |
| `conversations/260713-depbench-upgrade-mining/131006-gpt-researched-context-agent.md` | This comprehensive handoff note. |

Pulled-paper findings that govern the plan:

- Strongest completed configuration: 88/219 (40.2%).
- Consensus-hard tasks: 100/219 under GPT-5.5; npm contributes 51/79 and Cargo 15/21.
- Incomplete migration is the largest agreed agent-side failure category in every configuration.
- Codex + GPT-5.5 observed docs in 191/219 trajectories, API/source in 219/219, tests in 182/219, and explicit breaking-change hypotheses in 209/219. Retrieval behavior is therefore already saturated for Codex.
- Across failed trajectories, 641/1,371 (46.8%) had a visible-test pass before hidden failure; for Codex the rate is 90/135 (66.7%).
- The paper’s conclusion explicitly calls for upgrade-contract propagation and rejects visible-test success as a sufficient stop condition.

MSR4Agent mechanisms worth reusing:

- Separate mining from composition with a stable JSONL interface and one writer.
- Freeze mined facts so multiple delivery/evaluation variants reuse identical evidence.
- Attach provenance, cutoff, triggers, mistake cost, uncertainty, and coverage boundaries to every fact.
- Use progressive disclosure and a compact always-loaded layer to avoid context rot.
- Report uncovered regions explicitly so silence is not mistaken for completeness.
- Preserve negative knowledge, fix-shape precedents, test topology, API semantics, maintainer conventions, and ecosystem constraints as distinct evidence families.

Mechanisms not to copy unchanged:

- MSR4Agent mines task-blind repository-wide books; DependAgent knows the package/version boundary and should mine task-directed facts and obligations.
- Its co-change subsystem decomposition is useful for coverage but cannot replace dependency-symbol/type propagation.
- Its “model-known” redundancy filter should be adapted: even facts the agent knows may remain valuable when authority/conflict metadata changes action. Filter on marginal decision value, not factual novelty alone.
- WoC is supplementary here because local V2412 ends in 2024; GitHub/local GHArchive/upstream evidence is primary.

## Open tasks for the next agent

1. Create a new implementation branch/worktree without disturbing the current dirty `v4-with-test` tree or the unrelated dirty `/fast/hrz/msr4agent` checkout.
2. Freeze the current219 task snapshot and record its commit plus the pulled paper commit.
3. Implement the study manifest and strict cutoff/exclusion validator first. Include target repo/forks, target PR/branch, oracle hashes, and evidence timestamps.
4. Implement the five-case contract-ledger format and re-baseline policy without mining; run a Codex + GPT-5.5 smoke on the three context-complete cases before broad infrastructure.
5. Implement npm completeness checker v0: dependency import/symbol extraction, wrappers/types/re-exports/mocks/fixtures/generated/config enumeration, touched-set comparison, and explicit uncovered-site justifications.
6. Reuse/adapt the local GHArchive/GitHub patterns from `/data/hrz/dependency-update-dataset/scripts/mine_merged_dependabot_non_manifest_prs.py` rather than starting a crawler from scratch.
7. Add upstream source/test/doc collectors and symbol-indexed GitHub sibling diff retrieval for the five cases.
8. Add a `python-woc` adapter with `WocMapsLocal(version="V2412")` only after the primary collectors work; record temporal coverage and provide GitHub fallback.
9. Run the six-arm five-case demo in `PLAN.md`. Treat jwx as a negative control and actix as a scaffolding-hazard case; do not tune toward 5/5.
10. Only if the demo changes valid outcomes or produces diagnostic value, freeze facts and run the surviving arms on npm79. Append every harness/prompt/checker variant to `HARNESS.md`.
11. Update the paper only after measured results exist. The pulled paper already contains the correct 219-task failure analysis; do not reintroduce the stale 128/218-task narrative from `/data/hrz/kaiti/paper`.

## Key decisions

| Decision | Rationale |
|---|---|
| Frame the system as upgrade-contract propagation, not generic RAG | Paper and ensemble show discovery is saturated while action/propagation fails. |
| Build a few-case demo before npm-scale infrastructure | User direction and ensemble consensus; cheaply falsifies the mechanism. |
| Prioritize GitHub, local GHArchive, upstream tests/source/docs | They are current, locally available, and supplied every decisive fact in the five-case audit except a non-derivable random fixture. |
| Keep WoC as an optional V2412 supplement | User notes its late-2024 cutoff; it is useful for commit-file/blob lineage but cannot cover later upgrades. |
| Reuse MSR4Agent’s mine/facts/compose seam | It supports clean ablations, provenance, one-writer schemas, and progressive disclosure. |
| Add a controller/checker beyond MSR4Agent | Dependency updates require repository-wide proof obligations and a stop gate, not just context delivery. |
| Do not require agent-written tracked tests | The benchmark overlays canonical hidden tests; generated tests can be disposable probes but are another guessed oracle and cannot define success. |
| Treat current219 as this study’s corpus | Explicit user choice; results remain separate from clean205. |

## Blockers

- No implementation blocker.
- `python-woc` is not importable in the inspected environments; locate or recreate the environment used by the sibling mining scripts before enabling that adapter.
- Docker socket/auth must be revalidated before Harbor runs; AGENTS.md records that the old UID-1900 socket is absent for the current user.
- The current DepBench and MSR4Agent worktrees contain unrelated untracked/dirty files. Use a new worktree and do not clean or overwrite either tree.

## Suggested next step

Create an isolated implementation worktree and build the five-case `study_manifest.jsonl`, cutoff/exclusion validator, and contract-ledger schema before writing any crawler.

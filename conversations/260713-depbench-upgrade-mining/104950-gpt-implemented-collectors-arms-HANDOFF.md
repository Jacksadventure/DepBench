# Handoff: DependAgent collectors, contract checker, and experiment arms

**Date:** 2026-07-13  
**Agent:** GPT-5/Codex  
**Status:** prototype implementation verified; live Codex causal run blocked on model routing/auth, not Docker or Harbor

## User objective and locked choices

Build an agentic solution that mines pre-existing context for dependency-update repairs, first as a five-case demo and then, only if useful, on npm79. Prefer GitHub, local GHArchive (`gharchive.github_events`), and upstream version contents; WoC V2412 is optional supplementary coverage because it ends in late 2024. Use the current219-era five cases, Codex + GPT-5.5, and keep all 219-era findings separate from the clean205 benchmark headline.

The design and evaluation plan is in `PLAN.md`. The prior ensemble synthesis is `130952-ensemble-context-agent-SUMMARY.md`; the paper diagnosis is summarized in `131006-gpt-researched-context-agent.md`; the initial code handoff is `131023-gpt-implemented-foundation.md`.

## Paper and prior-work diagnosis

The intended Overleaf paper was pulled into `paper/` and inspected at commit `6b32cf9911df2bccb1aa94f32142f7f8e8531b94`. Chapter 4 reports that the strongest completed agent solved 88/219, while incomplete migration is the dominant failure category. Codex GPT-5.5 already retrieved documentation for 191/219, API information for 219/219, tests for 182/219, and breaking-change hypotheses for 209/219. Across failed trajectories, 641/1371 had passed visible tests before hidden failure; for Codex this was 90/135 (66.7%).

Therefore the prototype targets authority weighting, contract operationalization, repository-wide propagation, contradiction handling, and a stronger completion gate. It does not assume that adding more undifferentiated documentation is sufficient.

`/fast/hrz/msr4agent` was inspected read-only at commit `e26e507fe`. The useful seam reused here is: immutable collector output, a single fact-writer, a separate composer, progressive disclosure, explicit provenance/cutoffs, and coverage gaps. No files there were changed.

## Implemented code

The additive package is `dependagent/` and is exposed as `uv run dependagent` through `pyproject.toml`.

Core contracts and policy:

- `models.py`: versioned study-task, evidence, fact, usage, obligation, authority, source-kind, change-kind, and hazard schemas.
- `manifest.py` + `data/pilot_prs.json`: exact metadata and PR-creation cutoffs for the five frozen pilots.
- tracked `artifacts/pilot/study_manifest.jsonl`: five current219 records.
- `jsonl.py`: deterministic atomic JSONL writes.
- `validation.py`: strict timestamp `< cutoff`; target repo/PR/commit and excluded-repo rejection; exact and token-shingle near-oracle rejection. Pre-cutoff upstream source/tests/docs from the same monorepo are allowed for the Solana case.
- `paths.py`: benchmark-aligned manifest/source/test classification.

Collectors:

- `collectors/gharchive.py`: local ClickHouse candidate discovery with package/version boundary ranking, repair-signal ranking, strict cutoffs, and target exclusion.
- `collectors/github.py`: exact PR metadata/diff enrichment, source/test/manifest classification, caching, and an atomic error ledger for deleted/unavailable candidates.
- `collectors/upstream.py`: GitHub API ref/compare and full explicit-document collection. It records the 300-file compare truncation risk.
- `collectors/upstream_git.py`: complete pinned upstream diffs through eager bare Git mirrors. It fetches the configured old/new refs into private refs, enumerates the full name-status delta, emits source/test patches in test-first order, materializes configured documents in full, and reports whether `max_files` truncated eligible evidence. The eager `.full.git` mirrors deliberately avoid the blobless prototype's one-network-request-per-file failure mode.

Fact delivery and checking:

- `mining.py`: conservative deterministic extraction of explicit action headings from authoritative migration Markdown. The miner is the sole fact writer.
- `compose.py`: authority-aware contract rendering, re-baseline policy, contradiction ledger, and completion gate.
- `completeness.py`: repository scan for fact symbols and package imports; fact-to-usage obligations; untouched production path blocking; stale visible-test/fixture usages reported separately as `legacy_conflict_paths`. Generic words such as `component` require identifier boundaries, avoiding matches in paths like `./components/Admin`.
- `experiment.py`: deterministic six-arm prompt generation: baseline, policy, equal-character raw context, structured facts, policy+checker, and full system. The raw arm is matched to the structured arm's character count; actual Codex token counts still must be read from traces.
- `cli.py` and `README.md`: commands and reproducible examples.

## Live evidence and calibration results

All generated evidence/caches below are intentionally ignored under `dependagent/artifacts/`; only the frozen manifest is tracked.

Complete upstream source/test delta counts from the configured old/new refs:

| Pilot | Evidence files | Source | Tests | Truncated |
|---|---:|---:|---:|---|
| React Router / Brokeneck | 195 including one full guide | 110 | 84 | no |
| SPL Token / Solana | 157 | 129 | 28 | no |
| syn / actix | 87 | 53 | 34 | no |
| jwx / nuts-node | 48 | 38 | 10 | no |
| Shiro / JavaSecurity | 445 including one full README | 319 | 125 | no |

The React GitHub compare API had returned a 300-file list dominated by doc churn and only one useful explicit guide after filtering. The local mirror recovered 194 source/test deltas; all 194 passed the cutoff/leakage validator. This is direct evidence that the API compare cap is operationally important.

GHArchive/GitHub smoke evidence for React Router found real v5→v6 sibling candidates. `dlrgsbz/beachist#92` contained source repair; `Pylons-tech/pylons#765` was manifest-only; deleted `Felix2yu/bililive-go#18` was retained in the error ledger rather than silently disappearing.

The React migration guide produced 10 explicit facts, including Switch→Routes, useHistory→useNavigate, useRouteMatch→useMatch, NavLink exact→end, removed active props, and StaticRouter relocation. Known recall gaps remain: `<Route component/render/children>`→`element`, relative path semantics, and some useParams propagation are described in non-action headings/body and are not yet mined. Treat these as measurable fact-recall gaps, not as absent upstream knowledge.

The Brokeneck oracle was used only after fact generation as an offline checker calibration target. Final result: `complete=true`, 18 usages, zero untouched production paths, and two stale visible-test conflicts. Before identifier-boundary correction, generic `component` created false positives in `src/index.js` and `test-utils/providers.js`; tests now cover this regression.

The Brokeneck experiment arms materialized successfully. Raw and structured contexts are both exactly 8,132 characters; structured contains 10 facts. The full arm is 10,449 context characters and carries all 195 evidence locators in metadata, while raw content includes only the highest-authority records that fit its matched budget.

## Verification

Current verification is clean:

```text
uv run python -m unittest discover -s tests -v
26 tests passed

git diff --check
clean
```

Tests cover manifest freezing, atomic writes, cutoff/leakage rejection, same-monorepo upstream allowance, GHArchive query invariants, GitHub exact enrichment, GitHub API upstream collection, complete local-Git collection, path classification, completeness/contradiction behavior, conservative fact mining, contract evidence requirements, and six-arm generation.

## Harbor/Codex preflight and blocker

Harbor CLI 0.6.4 and Docker 29.1.3 work through the system socket `/var/run/docker.sock`. The stale `/run/user/1900/docker.sock` is absent, as expected.

The model route is not currently usable:

- `az` is not installed, so `CodexCloudGPT` cannot acquire an AAD bearer token from the host.
- no relevant CloudGPT/Maestro/OpenAI token variables are present in the shell.
- the documented Maestro proxy `http://172.100.216.1:23333/api/openai/v1` timed out during a three-second reachability probe.

Do not run a batch until this is fixed. The paper/harness already showed that missing Codex routing can yield zero-tool-call executions that look like passes but are only verifier baselines.

## Exact next work

1. Restore one valid Codex GPT-5.5 route:
   - preferred local Maestro: make `172.100.216.1:23333` reachable and set `CODEX_MAESTRO_BASE_URL`, `CODEX_FORCE_API_KEY=1`, and a dummy/nonempty `OPENAI_API_KEY`; or
   - CloudGPT: install/login `az` or inject a short-lived `CLOUDGPT_OPENAI_TOKEN`.
2. Materialize each arm as an immutable task variant whose only intended difference is `instruction.md`; preserve both benchmark canary strings and keep hidden solution/tests inaccessible during the agent phase.
3. Run one Brokeneck baseline smoke and one full-arm smoke with explicit `-a`/custom Codex agent and GPT-5.5. Inspect the trace for real tool calls before trusting reward.
4. Finish fact recall before running all arms. Add an evidence-backed source/test delta miner or a conservative rule layer for semantic guide bodies. Score decisive-fact recall against the oracle only after mining is frozen.
5. Generate facts/arms for the remaining four pilots. The upstream deltas exist, but their facts have not been composed yet.
6. Run the six-arm five-case experiment with repetitions, then apply the predeclared scale gate from `PLAN.md`. Do not expand to npm79 merely because collection works.
7. Keep WoC optional until GitHub/GHArchive/upstream ablations reveal a real coverage gap. WoC silence after 2024 is never negative evidence.

## Commands to resume

```bash
uv run python -m unittest discover -s tests -v

uv run dependagent collect-upstream-git \
  --manifest dependagent/artifacts/pilot/study_manifest.jsonl \
  --task-id nearform__brokeneck__820 \
  --cache-dir dependagent/artifacts/cache/upstream-git \
  --max-files 500 \
  --output dependagent/artifacts/pilot/brokeneck_upstream_git_evidence.jsonl

uv run dependagent validate-evidence \
  --manifest dependagent/artifacts/pilot/study_manifest.jsonl \
  --evidence dependagent/artifacts/pilot/brokeneck_upstream_git_evidence.jsonl \
  --output dependagent/artifacts/pilot/brokeneck_upstream_git_validation.jsonl

uv run dependagent mine-markdown-facts \
  --evidence dependagent/artifacts/pilot/brokeneck_upstream_git_evidence.jsonl \
  --output dependagent/artifacts/pilot/brokeneck_git_facts.jsonl

uv run dependagent build-experiment-arms \
  --manifest dependagent/artifacts/pilot/study_manifest.jsonl \
  --task-id nearform__brokeneck__820 \
  --instruction harbor_benchmark/tasks_v4/nearform__brokeneck__820/instruction.md \
  --evidence dependagent/artifacts/pilot/brokeneck_upstream_git_evidence.jsonl \
  --facts dependagent/artifacts/pilot/brokeneck_git_facts.jsonl \
  --output-dir dependagent/artifacts/pilot/brokeneck_arms
```

## Worktree cautions

The repository was already dirty and contains user-owned untracked outputs (`jobs-fix/`, `trials-fix/`, `screenlog.0`, task-local screen logs, other conversation threads, and `.DS_Store`). None were modified or removed. `paper/` is a nested cloned repository and remains untracked in DepBench. No Harbor harness setting or task scaffold was changed, so no HARNESS.md variant-log entry was required. Do not commit run outputs or screen logs.


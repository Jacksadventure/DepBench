# Plan — Agentic Context Mining for Dependency Updates

## 1. Research claim and demo objective

The system will test this claim:

> Dependency-upgrade agents fail less from absence of information than from failing to rank, operationalize, propagate, and verify the upgraded dependency’s contract.

The first deliverable is a reproducible demo on the five audited cases, followed only if useful by a controlled experiment on the 79 npm tasks in the current 219-task corpus. The demo is successful if it recovers the decisive pre-cutoff evidence, produces correct repository obligations, changes the agent’s decision in the three context-complete oracle-trap cases, and honestly identifies non-derivable or harness-limited cases.

Fixed evaluation configuration: Codex + GPT-5.5. All 219-era results must be labeled separately from the clean205 benchmark line.

## 2. Architecture

### 2.1 Components and stable interfaces

Adopt MSR4Agent’s separation of mining from delivery, with one additional execution layer:

1. **Source collectors** write immutable evidence records.
2. **Miner/filter** is the single writer of `facts.jsonl`.
3. **Composer** reads facts and the target usage map, then writes a compact contract ledger and obligation set; it never rewrites facts.
4. **Controller/checker** drives Codex through contract declaration, repair, verification, contradiction resolution, and completeness auditing.

Versioned artifacts:

- `study_manifest.jsonl`: task, dependency boundary, PR-creation cutoff, baseline result, hazard labels, frozen dataset commit.
- `sources.jsonl`: immutable locator, timestamp, source kind, query, hashes, cutoff decision, target/fork/oracle exclusion decision.
- `facts.jsonl`: one fact per line with `id`, package boundary, symbol, change kind, old/new contract, evidence refs, authority, confidence, mistake cost, trigger conditions, and source coverage.
- `target_usage.json`: imports, calls, types, wrappers, mocks, fixtures, snapshots, generated/config/manifest surfaces and confidence.
- `obligations.jsonl`: fact-to-usage binding, required operation, verification evidence, status, and unresolved contradiction.
- `context.md`: a bounded agent-facing rendering of the ledger; raw evidence remains outside the prompt and is queried by fact ID when needed.
- `mining_trace.jsonl`: all queries, cache hits, filtering, errors, and costs.

### 2.2 Source priority

Use current and locally available sources in this order:

1. Exact target-version package contents, upstream source/type declarations, and upstream tests across release tags.
2. Upstream release notes, changelogs, migration guides, and packaged documentation.
3. GitHub API/CLI repository and PR history, including manually titled migration PRs.
4. Local ClickHouse `gharchive.github_events` for candidate discovery, PR/review discussion, timestamps, SHAs, and sibling-population statistics.
5. Same-organization and same-maintainer history for project conventions and test scaffolding.
6. `python-woc`/WoC V2412 for commit-to-file/blob lineage and GHArchive gaps that occurred no later than 2024; never treat WoC silence after 2024 as negative evidence.

The local ClickHouse interface is confirmed available. Reuse the sibling mining patterns in `/data/hrz/dependency-update-dataset/scripts/mine_merged_dependabot_non_manifest_prs.py` and `enrich_renovate_same_pr_repairs.py`: GHArchive coarse candidate query, GitHub exact validation/diff fetch, optional `WocMapsLocal(version="V2412")` commit-file lookup, caching, and explicit consistency flags.

### 2.3 Authority and contradiction policy

For dependency semantics:

1. Observable target-version behavior and upstream source/type contract.
2. Upstream target-version tests and test deltas.
3. Official migration/release documentation.
4. Corroborated sibling repairs ranked by target-symbol overlap and verified status.
5. Model inference.

For repository conventions, same-org/same-maintainer history ranks above unrelated sibling repairs. Visible tests remain authoritative for behavior outside the changed contract. When a visible assertion conflicts with a high-confidence contract fact, record the contradiction and treat the assertion as a likely legacy expectation rather than silently adding a compatibility shim.

Do not encode this solely as prose. Require Codex to emit a schema-validated contract ledger before editing and a contradiction log before completion.

### 2.4 Target mapping and completeness

Start with an npm/TypeScript/JavaScript checker:

- Parse imports/requires and package exports.
- Find all references to changed symbols and deprecated call shapes.
- Trace local wrappers, factories, interfaces/types, return values, re-exports, and mock boundaries conservatively.
- Search test, fixture, snapshot, generated-output, package-manager, and configuration paths using DepBench’s established path classifier.
- Compare affected surfaces with the candidate patch’s touched files.
- Require an explicit justification for every uncovered site; exclusions cover vendored/build artifacts but not owned generated sources.

The checker is evidence, not an oracle. It may block a success claim for high-confidence uncovered sites, but low-confidence co-change suggestions are warnings. Disposable probes or shadow assertions may test inferred behavior, but tracked agent-written tests are not a required deliverable and cannot substitute for hidden verification.

Stop only when the dependency boundary is present, high-confidence obligations are discharged, contradictions are resolved or explicitly uncertain, no forbidden old symbol/call shape remains, manifest/lock/generated state is consistent, visible checks have been attempted, and the agent accurately reports any budget-limited residual risk.

## 3. Build and experiment sequence

### Phase A — Freeze and label

- Freeze the current 219-task tree and current paper commit.
- Build the five-case study manifest with exact PR-creation cutoffs.
- Implement target/fork/oracle/near-duplicate exclusions before collecting evidence.
- Predeclare hazard labels: context-limited, arbitrary fixture regeneration, withheld scaffolding, dead/mis-scoped oracle, or unresolved.

### Phase B — Cheap causal demo

Before broad mining, implement:

- Re-baseline/authority policy.
- Contract ledger and contradiction log.
- npm completeness checker v0.

Run baseline and policy+checker on the five cases. Expected qualitative outcomes:

- `brokeneck__820`: reject v5 compatibility shims and migrate the v6 contract across components/tests.
- `solana-program-library__4301`: prefer new SPL Token behavior over legacy visible assertions.
- `JavaSecurity__236`: preserve Shiro 2’s 50,000-iteration default rather than re-pin one million.
- `actix__554`: recognize a semantically correct syn migration and separately identify the dev-dependency/scaffolding hazard.
- `nuts-node__426`: recover RFC7797 behavior but abstain on the non-derivable random key; retain as a negative control.

### Phase C — Minimal evidence miner

- Automate upstream source/test/doc collection for the five package boundaries.
- Query local GHArchive for exact/similar boundary candidates and same-org activity.
- Fetch GitHub diffs and index hunks by dependency symbols, not titles.
- Add WoC V2412 only as an optional commit-file/blob lookup; annotate its temporal coverage.
- Write facts once, then recompose all experiment arms from the same frozen `facts.jsonl`.

### Phase D — Five-case experiment

Use repeated trials sufficient to estimate run variance. Minimum arms:

1. Existing baseline.
2. Policy only.
3. Equal-token raw retrieved context.
4. Structured contract facts.
5. Policy + completeness checker.
6. Full system: policy + structured facts + obligations + checker.

Measure pass@1, decisive-fact recall, fact precision, obligation recall against the human repair surface, contradiction-resolution accuracy, visible-pass/hidden-fail, old-symbol residue, tokens, tool calls, and wall time. Report hazard-aware case outcomes rather than demanding 5/5.

Decision gate: scale only if the full or cheap-control arms improve at least one valid context-complete case without regressing already correct repairs, and the system’s intermediate artifacts explain why.

### Phase E — npm-scale study

Run the surviving arms on all 79 npm tasks, fixed Codex + GPT-5.5 and frozen context. Stratify by sibling count, upstream-test availability, same-org evidence, release freshness, baseline failure category, and hazard label. Report paired pass@1 and bootstrap confidence intervals or McNemar tests, plus the Codex visible-pass/hidden-fail rate (baseline 90/135 across all analyzed failures) and shifts in incomplete-migration/wrong-semantic-output categories.

Add source ablations only after the core result:

- Full minus sibling repairs.
- Full minus upstream test diffs.
- Full minus same-org evidence.
- Full minus WoC. WoC earns a permanent role only if it contributes unique decisive facts or successful repairs not available from GitHub/GHArchive/upstream sources.

## 4. Validity controls and falsification

- Enforce strict evidence timestamp `< target PR creation time`; do not use merge time as a proxy.
- Exclude target repo, forks/mirrors, target PR, repair branch, oracle patches, and near-duplicate/cherry-picked hunks.
- Retrieval/card generation cannot read `solution/code.patch` or `tests/test.patch`; use them only after runs for scoring and hazard adjudication.
- Freeze context artifacts so every arm sees identical evidence availability.
- Track context tokens and mining/tool time; compare equal-token raw and structured context.
- Smoke-test Codex tool calls and proxy environment before any batch run; a zero-tool-call verifier baseline is infrastructure-invalid.
- Report intent-to-treat and predeclared hazard-clean sensitivity analyses; never silently remove failures after observing outcomes.

The proposal is falsified if policy/checker/structured facts recover the decisive evidence and obligations but do not reduce valid visible-pass/hidden-fail or incomplete-migration failures relative to baseline and equal-token raw context. In that case, the bottleneck is execution capability or benchmark construction rather than context acquisition/control. WoC is falsified as a v1 source if its unique useful coverage is zero after accounting for its 2024 cutoff and integration cost.

## 5. Deliberate deferrals

- Cross-ecosystem adapters beyond npm.
- Fleet-scale MCP/IDE productization.
- Automatically generated codemods or verified rewrite rules.
- Large-scale WoC-first mining.
- DepBench-XL construction.

These follow only after the five-case and npm studies establish which intervention actually moves agent outcomes.

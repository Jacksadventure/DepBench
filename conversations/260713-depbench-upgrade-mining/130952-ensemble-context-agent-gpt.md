# Independent Design — GPT

## Thesis

The paper rules out the naive thesis that agents fail mainly because they do not look for migration information. Codex inspected dependency documentation in 191/219 trajectories and local APIs in 219/219, yet incomplete migration remains its largest agreed failure class and 90/135 analyzed Codex failures contain a visible-test pass before hidden verification fails. The system should therefore be framed as an **upgrade-contract compiler**, not a retrieval-augmented chatbot: mine an evidence-backed contract for the version boundary, bind it to the target repository's dependency usages, and maintain proof obligations until every affected repository surface has been checked.

The core causal chain is:

`version boundary -> authoritative contract deltas -> target usage graph -> migration obligations -> edits -> obligation discharge`

Retrieved documents and sibling diffs are evidence for contract deltas; they are not the final product.

Falsifiable hypotheses:

1. A re-baselining/authority policy alone improves pass@1 on behavioral-change tasks where baseline trajectories discovered the correct new semantics but preserved visible legacy behavior.
2. Contract cards plus target-specific obligation generation improve pass@1 more than an equal-token raw-context bundle.
3. A completeness gate provides most of its gain on partial-migration failures, while authoritative semantic evidence provides most gain on wrong-semantic-output failures.
4. Symbol-indexed sibling exemplars outperform package/version/title-only retrieval, especially for manually titled migrations such as the Solana case.
5. World of Code adds measurable recall only after GHArchive/GitHub/upstream/same-org sources; if not, it should be removed from the operational path.

## Architecture

### Offline evidence plane

Key every boundary by ecosystem, canonical package identity, resolved old/new versions, and cutoff timestamp. Preserve raw observations as immutable evidence records:

- source kind: upstream release, source diff, test diff, packaged documentation, sibling PR, same-org history, GHArchive event, or WoC lineage;
- immutable locator: repository, commit/tag/PR, file path and hunk, event timestamp;
- cutoff eligibility and exclusion decision;
- extracted symbols, error signatures, behavioral claims, and rewrite operations;
- reliability tier and extraction confidence.

Generate candidate contract facts rather than summaries. Each fact should state the changed subject, old contract, new contract, change kind, evidence links, source authority, confidence, and conflicts. Keep behavioral facts separate from mechanical rewrite exemplars.

Cluster sibling repairs by dependency symbol and normalized edit operation. Package-version matching is a candidate generator, not the ranking key. Rank exemplars by overlap with target imports/symbols, version-boundary compatibility, repair purity, pre-cutoff proximity, source authority, and repository similarity. Same-org examples receive a separate boost only for project conventions, not general API truth.

### Target analysis plane

Build a dependency usage graph covering imports, qualified calls, types, wrappers, adapters, factories, mocks, fixtures, snapshots, generated outputs, configuration, and manifest/lockfile state. Language adapters may begin with TypeScript/JavaScript, but the intermediate representation should be ecosystem-neutral:

```text
UsageNode {file, span, symbol, role, reachable_from, generated, confidence}
Obligation {contract_fact_id, usage_nodes, required_operation, verification, status}
```

Combine contract facts with usage nodes to create migration obligations. A removed constructor can imply obligations for construction, downstream method calls, mocks, and return shapes. A semantic default change can imply obligations for local overrides, expected values, serialization, snapshots, and test fixtures.

### Agent control plane

Give the repair agent a compact contract ledger, not a document dump:

1. Upgrade facts, ordered by authority.
2. Target-specific affected surfaces.
3. Exemplars attached to individual obligations.
4. Explicit contradictions with visible tests.
5. Outstanding checklist and verification commands.

Authority ordering should be: observed new-version runtime/API behavior and upstream new-version tests; upstream migration/release documentation; upstream source/type diffs; corroborated independent sibling repairs; same-org conventions; target visible tests; model inference. Visible tests remain strong evidence about repository behavior, but when they contradict a well-supported version-boundary change they are labeled a legacy expectation to migrate, not an invariant to preserve.

The loop is plan-edit-verify-audit:

- Plan: convert evidence into obligations and predict affected surfaces.
- Edit: repair a coherent obligation group.
- Verify: run focused build/tests and inspect behavioral output.
- Audit: rescan the usage graph and patch, marking obligations discharged only with structural or dynamic evidence.

Stopping requires: the requested dependency boundary is present; no high-confidence obligation remains open; no old forbidden symbol or type survives outside documented exceptions; manifest/lock/generated state is consistent; focused and broad visible checks have been attempted; contradictions are recorded; and the final patch does not evade the upgrade or verifier. A passing visible suite is never sufficient by itself.

## Five-case pilot

The pilot should test retrieval recall and control-policy behavior separately.

- Brokeneck: recover all React Router migration facts and generate obligations across components and tests; verify that the policy rejects compatibility shims that preserve v5 idioms.
- Solana SPL Token: demonstrate that title-only recall is zero while symbol/upstream-monorepo retrieval finds the new API and error/ATA semantics; ensure visible legacy assertions are explicitly re-baselined.
- Actix/syn: recover migration mechanics plus same-maintainer trybuild conventions, while flagging the withheld dev-dependency and dead stderr path as benchmark hazards.
- jwx: recover RFC7797 behavior but classify the random regenerated fixture/key as non-derivable; the system must abstain from claiming context completeness.
- Shiro: recover relocation changes and the 50,000-iteration upstream default; verify that authority ordering prevents an agent from re-pinning one million solely to satisfy visible tests.

Pilot acceptance should require decisive-fact recall, correct authority/conflict classification, obligation recall against the human patch surface, and an honest hazard verdict. Do not tune cards using the evaluation agent's hidden-test outcome.

## npm experiment

Freeze the 219-task corpus, but evaluate the 79 npm tasks and report all results explicitly as the 219-era npm slice. Use one Codex + GPT-5.5 configuration, identical budgets and verifier settings, and cached pre-cutoff evidence.

Recommended arms:

1. Baseline.
2. Policy-only re-baseline instruction.
3. Raw retrieved context under the same token budget as structured context.
4. Structured contract cards without the completeness gate.
5. Completeness gate without external context.
6. Full contract compiler: cards, obligations, authority policy, and gate.
7. Full minus WoC, to measure its incremental value.

The raw-context arm is essential: without it, improvement cannot be attributed to contract structure/control rather than simply more information. Run at least repeated seeds for the five cases and, budget permitting, for npm tasks because pass@1 variance may obscure small effects.

Primary outcome is paired pass@1 uplift. Secondary outcomes: uplift by baseline failure label; decisive-fact recall; obligation recall/precision against human repair surfaces; fraction of injected facts used; visible-pass-then-hidden-fail rate; old-symbol residue; tokens/time; retrieval latency; source coverage; and abstention/hazard accuracy. Analyze treatment effects separately for incomplete migration, wrong root cause, and wrong semantic output.

## Leakage, hazards, and confounds

Enforce creation-time cutoff, not merge-time cutoff. Exclude the target repo, renamed copies, forks, the target PR, commits reachable from its repair branch, and exact/near-duplicate oracle hunks. Record every exclusion in the trace. Retrieval and card generation must run without access to `solution/code.patch` or `tests/test.patch`; those files may be used only later for scoring obligation recall and hazard adjudication.

Detect benchmark hazards before interpreting failures: random fixture/key regeneration, test-only dependencies withheld by the split, dead/unguarded tests, target behavior not derivable from any pre-cutoff evidence, and hidden tests that contradict observable upgraded behavior. Report intent-to-treat results over all 79 npm tasks plus a predeclared hazard-clean sensitivity analysis; never silently remove failures after seeing treatment outcomes.

Major confounds include changing prompt length, extra tool time, retrieval network failures, model nondeterminism, and context leakage through model pretraining. Use frozen context artifacts, equal-token comparison where appropriate, identical time budgets or separately account for mining overhead, and provenance-based measures that do not depend solely on final pass rate.

## Build order and falsification

Build first: study manifest and cutoff/exclusion validator; raw evidence schema/cache; npm symbol usage extractor; upstream docs/source/test diff collector; GHArchive/GitHub candidate collector; contract fact generator; obligation mapper; policy and completeness gate; five-case replay; then npm ablation. Add WoC through the same evidence interface after the validated-source collectors work, so its marginal coverage is measurable. Defer MCP packaging, multi-ecosystem adapters, deterministic rewrite-rule generation, and production service infrastructure.

The proposal is falsified as a context/control intervention if the full system does not outperform baseline and raw-context arms on hazard-clean tasks, or if decisive facts and obligations are recovered but agents still fail at the same rate. That result would show the remaining bottleneck is execution/planning capability rather than context acquisition or propagation control. WoC is specifically falsified as a useful v1 source if it contributes no unique decisive facts or successful repairs after cost and noise are counted.

## Top 5 takeaways, ranked by importance

1. Build an upgrade-contract compiler with proof obligations, not a retrieval chatbot.
2. Treat visible tests as intermediate evidence and explicitly re-baseline them when stronger version-boundary evidence conflicts.
3. Separate semantic-fact acquisition from repository-wide propagation, and evaluate each mechanism with distinct ablations.
4. Make leakage exclusions and benchmark-hazard sensitivity analyses first-class study artifacts.
5. Require World of Code and every other source to prove incremental value rather than assuming broader retrieval is better.

# Ensemble Report — Context-Agent Architecture

**Task:** Design the follow-up work for an agentic solution that mines and uses context for dependency updates, grounded in the latest DepBench paper and July 13 evidence.
**Date:** 2026-07-13
**Participants:** GPT, Claude, Gemini, Kimi. DeepSeek excluded for isolation contamination.

---

## Consensus

All usable participants reject a retrieval-first framing. The paper shows that Codex already consulted documentation in 191/219 trajectories and local dependency APIs in 219/219, while incomplete migration remained the dominant agreed failure and 66.7% of analyzed Codex failures had a visible-test pass before hidden verification failed. The proposed system must therefore convert evidence into an explicit upgrade contract, propagate that contract through the repository, and replace “visible tests are green” with a stronger completion gate.

The common architecture has four separable components:

1. A pre-cutoff evidence miner over upstream source/tests/docs, GitHub and GHArchive repair history, same-organization history, installed-package documentation, and optional WoC evidence.
2. A structured contract-card store keyed by package boundary and symbols, with provenance, authority, confidence, and conflict metadata.
3. A target mapper that turns contract changes into repository-specific obligations covering imports, call sites, types, wrappers, mocks, fixtures, snapshots, generated artifacts, manifests, and lockfiles.
4. An agent control loop with contradiction logging, repository-wide completeness checks, and stop conditions that do not equate visible-test success with upgrade completion.

All participants prioritize strict per-task creation-time cutoffs, target-repository/oracle exclusion, immutable cached evidence, hazard labeling, and npm-first evaluation under a fixed Codex + GPT-5.5 configuration.

## Divergence

- **Mining build order:** GPT would build a minimal evidence plane alongside the policy/checker. Claude and Kimi argue for testing the re-baseline policy and completeness checker before expensive crawling. User resolution: build a few-case demo first; prioritize GitHub, local GHArchive, upstream sources, and other current services; keep `python-woc` supplementary because local WoC ends in late 2024.
- **Generated adversarial tests:** Gemini makes agent-written failing tests a mandatory phase. GPT/Claude/Kimi prefer a contract or shadow-verification ledger because generated tests can introduce another guessed oracle and benchmark agents cannot rely on their edited tests at verification time. Recommendation: permit disposable probes, but do not make generated tracked tests the core mechanism or success condition.
- **Authority ordering:** everyone demotes visible legacy assertions when they conflict with strong upgrade evidence. Claude/Kimi distinguish project conventions from API truth: same-org evidence ranks highly for scaffolding and conventions, while upstream target-version behavior/tests rank highest for dependency semantics.
- **Expected pilot ceiling:** Claude and Kimi explicitly reject a 5/5 target. `nuts-node__426` is a designed negative control because its random regenerated key is not derivable; `actix__554` is partly a scaffolding/harness hazard. A credible pilot ceiling is therefore hazard-aware rather than five unconditional passes.

## Unique insights

- GPT proposes an “upgrade-contract compiler” framing and an equal-token raw-context arm to separate information volume from structure/control.
- Claude proposes using Codex precisely because its discovery behavior is saturated, making it a strong test of evidence use rather than evidence discovery.
- Gemini proposes adversarial local probes as a forcing function against premature stopping; retained as an optional diagnostic mechanism.
- Kimi provides fine-grained ablations for re-baseline policy, upstream cards, cross-repo exemplars, same-org evidence, upstream test diffs, and completeness checking.

## Gaps

- No participant specifies a proven npm-wide type-flow implementation; the first checker should be explicitly scoped as conservative AST/grep coverage plus typed adapters where available.
- WoC’s marginal contribution remains unknown and must be measured against its 2024 cutoff.
- Hazard detection can flag suspicious tasks but cannot fully adjudicate oracle validity automatically; manual review remains necessary for flagged cases.
- Repeated trials are desirable but potentially expensive. The demo should estimate variance before fixing the npm-scale replication count.

---

## Verdict

Build a GitHub/GHArchive-first **upgrade-contract and propagation system**, not a generic RAG layer. Reuse MSR4Agent’s mine → stable facts → compose separation and progressive disclosure, but make mining task-directed around the known dependency boundary and make obligations/completeness the control surface.

**Confidence:** High — every independent participant agrees on the diagnosis and core control loop, and it directly matches the pulled paper’s measured trajectory analysis.

**Recommended next step:** implement the policy/contract-ledger plus a minimal npm completeness checker, then replay the five audited cases using cached upstream/GitHub/GHArchive evidence before building the npm-wide index.

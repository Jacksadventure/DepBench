# Handoff Note — 131547 · gpt · reframed-release-notes

## Inherited context

The five-case context miner and six experimental arms are documented in
`131216-gpt-blocked-agent-smoke.md`. The current improved combined facts recover all
24 oracle-labeled derivable facts, but this is only a post-hoc recall diagnostic.

## Work done this session

- [x] Presented the generated evidence, fact, prompt, scoring, and Harbor artifacts.
- [x] Compared decisive-fact coverage from documentation facts alone versus upstream
  source/test delta facts.
- [x] Identified a construct-validity problem: each pilot case specifies only one
  `doc_paths` entry, so the current docs comparison is not a comprehensive release-note
  baseline.
- [x] Reframed the proposed system as an adaptive evidence escalator and propagation
  checker, not a replacement for official release notes.

## Current comparison

Using literal matching against the oracle-only decisive-fact ledger:

| Case | Broad official-doc artifact | Source/test delta | Combined |
| --- | ---: | ---: | ---: |
| React Router | 8/8 | 0/8 | 8/8 |
| Solana SPL Token | 0/6 | 6/6 | 6/6 |
| Actix / syn | 1/2 | 1/2 | 2/2 |
| Nuts / JWX | 1/3 | 2/3 | 3/3 |
| JavaSecurity / Shiro | 0/5 | 5/5 | 5/5 |
| Total | 10/24 | 14/24 | 24/24 |

The “official-doc” bucket is generous: it includes a React migration guide, READMEs,
and one `Changes` file, not strictly release notes. It therefore cannot support a
population-level claim that release notes are insufficient. In the React case, the
migration guide is enough and additional mining mainly risks noise.

## Open tasks for the next agent

1. Implement comprehensive official-document collection before any history/source
   escalation: GitHub release bodies, CHANGELOG/CHANGES, versioned migration guides,
   package-registry release metadata, and official API deprecation/migration pages.
2. Add explicit experimental arms that isolate information and presentation:
   `notes_raw`, `notes_structured`, `source_delta_structured`, `combined_structured`,
   and `combined_checker`, plus the existing no-context baseline.
3. Match token budgets when testing raw versus structured forms, and avoid comparing a
   verbose combined contract to a shorter notes baseline without controlling budget.
4. Add a release-note sufficiency gate: if official docs cover all target-relevant
   obligations, stop and do not mine source/history.
5. Measure precision and agent success, not only decisive-fact recall. The framework is
   justified only if it improves release-note-incomplete tasks without harmful noise or
   unreasonable cost.

## Key decisions

| Decision | Rationale |
| --- | --- |
| Release notes are the first-line, highest-authority source | If they are sufficient, additional mining is unnecessary and may add false candidates. |
| Do not claim “release notes are insufficient” from the five-case artifacts | Only one manually selected doc path was collected per case; this confounds author omission with collector omission. |
| Reframe contribution around adaptive escalation and propagation | The paper's failure analysis says agents commonly find a surface but fail to propagate it; that is distinct from summarizing notes. |
| Add a notes-only causal baseline | The current six arms cannot answer the supervisor's question because none isolates comprehensive official release notes. |

## Blockers

- No model-run blocker is relevant to this design analysis; Maestro must not be used.
- Comprehensive release-note collection and the revised arms are not implemented yet.

## Suggested next step

Build the comprehensive official-doc collector and a `notes_raw`/`notes_structured`
baseline before doing any further agent evaluation.

# Handoff Note — 131023 · gpt · implemented-foundation

## Inherited context

Continued the implementation goal from `PLAN.md` and the comprehensive planning handoff `131006-gpt-researched-context-agent.md`. The governing design is GitHub/GHArchive-first upgrade-contract mining, with WoC V2412 supplementary, strict creation-time cutoffs, and a controller/completeness gate rather than generic RAG.

## Work done this session

- [x] Added the installable `dependagent` package and CLI entry point.
- [x] Added versioned data contracts for study tasks, evidence, contract facts, target usages, and migration obligations.
- [x] Pinned exact pilot PR creation/merge timestamps and base/head/merge SHAs for all five audited cases.
- [x] Built the tracked five-case `study_manifest.jsonl` for the current219 corpus.
- [x] Implemented atomic JSONL reads/writes.
- [x] Implemented strict evidence validation: task match, timestamp `< cutoff`, target/excluded repo, target PR, target commits, exact oracle content, and token-shingle near-duplicate oracle content.
- [x] Implemented local ClickHouse GHArchive candidate discovery with package/version-boundary and repair-signal ranking.
- [x] Implemented cached exact GitHub PR metadata/diff enrichment with per-candidate error ledgers.
- [x] Implemented shared manifest/test/source path classification.
- [x] Implemented npm-oriented contract-symbol scanning and candidate-patch completeness reporting.
- [x] Added 18 passing unit tests and ran a live React Router collector smoke.

## Current state

| Area | Evidence |
|---|---|
| Packaging | `pyproject.toml` exposes `dependagent`; setuptools includes `dependagent*`. |
| Frozen pilot | `dependagent/artifacts/pilot/study_manifest.jsonl` contains 5 validated tasks. |
| Leakage controls | `dependagent/validation.py`; exact and near-duplicate oracle tests pass. |
| Collectors | `dependagent/collectors/{gharchive,github}.py`. |
| Completeness | `dependagent/completeness.py`; fixture tests prove untouched wrappers are reported. |
| Tests | `uv run python -m unittest discover -s tests -v` → 18/18 pass. |
| Formatting | `git diff --check` passes. |

Live smoke on `nearform__brokeneck__820`:

- Local GHArchive returned version-boundary-ranked React Router 5→6 candidates.
- Exact GitHub enrichment identified one manifest-only false coarse signal and one real source repair (`dlrgsbz/beachist#92`, three application files).
- One historical repository (`Felix2yu/bililive-go#18`) was unavailable. The first implementation aborted and left stale output; this was fixed so writes are atomic and unavailable candidates go to a separate error ledger while successful evidence remains usable.
- All two successfully enriched patches passed the cutoff/target/oracle leakage validator.

Generated caches and smoke evidence are ignored. The frozen study manifest is intentionally tracked.

## Open tasks for the next agent

1. Add upstream release-tag/source/test/doc collectors, starting with React Router and SPL Token.
2. Add exact manifest-boundary parsing to GitHub candidate enrichment; current ranking uses PR titles before exact diff classification.
3. Add symbol extraction from enriched repair patches and write the first mined `facts.jsonl`.
4. Add the authority/re-baseline contract composer and contradiction ledger.
5. Clone or materialize pilot base repositories at their pinned base SHAs and run the completeness checker against real oracle/candidate patches offline.
6. Add optional `python-woc` V2412 adapter after locating the environment containing `WocMapsLocal`; preserve GitHub fallback and temporal coverage metadata.
7. Smoke-test Codex proxy/tool-call health before any Harbor experiment.

## Key decisions

| Decision | Rationale |
|---|---|
| GHArchive candidate discovery ranks exact/major boundary before coarse repair signal | Recent minor bumps otherwise displaced relevant major migrations. |
| GitHub exact file classification overrides GHArchive commit/file counts | Multi-commit or >3-file PRs can still be manifest-only. |
| Collection is atomic and per-candidate | Deleted/private historical repos must not abort a batch or leave stale evidence masquerading as current output. |
| Completeness checker is conservative | It reports usages and uncovered paths; it does not claim hidden-oracle correctness. |

## Blockers

- None for continued implementation.
- `python-woc` remains unavailable in the current virtual environment.
- Real Harbor runs still require Docker socket and Codex proxy/auth preflight.

## Suggested next step

Implement the upstream source/test/doc collector and produce the first evidence-backed React Router contract facts from pre-cutoff artifacts.

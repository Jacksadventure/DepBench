# Handoff Note — 131216 · gpt · blocked-agent-smoke

## Inherited context

This continues `104950-gpt-implemented-collectors-arms-HANDOFF.md` and
`131147-gpt-continue-five-case-demo.md` in this thread. The locked research design is:

- mine only evidence available strictly before each target PR's creation time;
- prefer GitHub, local GHArchive (`gharchive.github_events`), and pinned upstream Git;
- use WoC only as a late-2024-bounded fallback;
- exclude the target PR/repository repair, exact/near oracle text, and post-cutoff evidence;
- evaluate six frozen arms (`baseline`, `policy`, `policy_checker`, `raw_equal`,
  `structured`, `full`) and audit agent validity before interpreting verifier rewards;
- do not scale beyond the five-case demo until paired baseline/full runs show an
  improvement without regression.

The prior ensemble is stored under the shared prefix
`130952-ensemble-context-agent-*`. Its consensus was to construct a compact,
authority-aware upgrade contract and verify repository-wide propagation, not merely
retrieve more prose.

## Work done this session

- [x] Added `slice-variants` so a frozen six-arm manifest can produce a baseline/full
  smoke manifest without copying or mutating task trees.
- [x] Added an oracle-only expectation ledger and `score-pilot`; scoring reads only
  prompt-rendered fact fields, never trigger metadata.
- [x] Audited every previous decisive-fact miss against the frozen evidence. Nine were
  explicitly supported. Actix macro delegation was absent from all admitted `syn`
  evidence and is now correctly labeled `non_derivable`.
- [x] Added generic mining rules for:
  - migration-guide render-prop/example bridges (`match.params` -> `useParams`);
  - Rust field access -> zero-argument method changes (`attr.path` -> `attr.path()`);
  - local dependency wrappers and strongly related newly exported APIs;
  - Go option namespace ownership (`jws.WithHeaders` / `jwt.WithHeaders`);
  - public `bigint` fields and obsolete `.toNumber()` conversions;
  - explicit RFC7797 `b64=false` unencoded-payload semantics;
  - request-builder salt configuration and decrypt return adaptation.
- [x] Added a 50,000-character per-diff hunk-pairing guard. Exports, constants, and
  explicit semantic declarations are still harvested from larger/generated diffs.
- [x] Improved oracle-only decisive-fact recall from 15/25 (60%) to 24/24 derivable
  facts (100%). This is recall only; it is not a precision or agent-effectiveness claim.
- [x] Added `summarize-experiment`, which excludes infrastructure-invalid trials,
  aggregates repeated attempts by task/arm, records cost/tool metrics, and implements
  the paired scale gate.
- [x] The gate is deliberately conservative: every observed task needs valid baseline
  and full cells, at least one baseline-failing task must improve, and no
  baseline-perfect task may regress. An incomplete historical oracle smoke correctly
  leaves the gate unevaluable/closed.
- [x] Rebuilt five improved six-arm variant sets (30 tasks), validated all manifests,
  sliced ten baseline/full smoke tasks, and validated all five smoke configs using
  Harbor 0.6.4's installed `JobConfig` model.
- [x] Pulled `paper/` again (`Already up to date`) and checked its RQ3/RQ4 account of
  failures. It supports the proposed mechanism: incomplete repository-wide migration
  dominates; agents often find the right surface but miss wrappers, types, fixtures,
  generated state, secondary call sites, or changed semantic output. Visible-test pass
  signals frequently overfit the old contract. Note that this paper checkout still
  narrates a 219-task snapshot; DepBench's authoritative current baseline is clean205.
- [x] Ran the full test suite: 39/39 pass. Also checked every improved fact reference
  against its evidence ledger, confirmed 30 variants, confirmed fact recall 1.0, and
  ran `git diff --check` successfully.
- [ ] Run the real GPT-5.5 baseline/full smoke. This remains infrastructure-blocked.

## Current state

| File / path | Change |
| --- | --- |
| `dependagent/delta_mining.py` | Target-relevant source/test mining, explicit semantic observations, wrapper/API mapping, Rust and Go rules, generated-diff guard |
| `dependagent/mining.py` | Explicit migration-prose/example bridge extraction |
| `dependagent/results.py` | New audited trial aggregation and paired scale-gate implementation |
| `dependagent/evaluation.py` | Oracle-only prompt-visible decisive-fact scoring |
| `dependagent/evaluation/pilot_expectations.json` | Five-case oracle ledger with derivability labels |
| `dependagent/evaluation/ORACLE_ONLY.md` | Leakage warning and interpretation limits |
| `dependagent/variants.py` | Frozen manifest arm slicing |
| `dependagent/cli.py` | `slice-variants`, `score-pilot`, `summarize-experiment` commands |
| `dependagent/README.md` | Updated workflow, commands, gate, and mining limitations |
| `tests/test_dependagent_foundation.py` | 39 tests, including new mining and gate tests |
| `dependagent/artifacts/pilot/*_facts_improved.jsonl` | Ignored regenerated five-case facts |
| `dependagent/artifacts/pilot/*_arms_improved/` | Ignored regenerated six-arm prompts |
| `dependagent/artifacts/pilot/pilot_fact_recall_improved.json` | Ignored oracle-only 24/24 score |
| `dependagent/artifacts/pilot/*_harbor_variants_improved/` | Ignored 30 variants plus five baseline/full smoke configs |

The working tree was already dirty. Preserve unrelated `.DS_Store`, other conversation
threads, `jobs-fix/`, `trials-fix/`, `screenlog.0`, task screen logs, and `paper/`.
Do not commit run outputs.

## Exact smoke inputs

Each config contains one baseline and one full task:

```text
dependagent/artifacts/pilot/nearform__brokeneck__820_harbor_variants_improved/smoke_config.json
dependagent/artifacts/pilot/solana-labs__solana-program-library__4301_harbor_variants_improved/smoke_config.json
dependagent/artifacts/pilot/actix__actix__554_harbor_variants_improved/smoke_config.json
dependagent/artifacts/pilot/nuts-foundation__nuts-node__426_harbor_variants_improved/smoke_config.json
dependagent/artifacts/pilot/dschadow__JavaSecurity__236_harbor_variants_improved/smoke_config.json
```

Once the route is healthy, run each with `harbor run -c <config>`, audit all resulting
job roots with `dependagent audit-trials`, concatenate the audit JSONL files, and run:

```bash
uv run dependagent summarize-experiment \
  --audit <combined-audit.jsonl> \
  --output dependagent/artifacts/pilot/five_case_experiment_summary.json
```

Exit code `0` means the gate opened; exit `6` means it is closed or not yet evaluable.

## Open tasks for the next agent

1. Restore or replace the Maestro-compatible GPT-5.5 endpoint and provide a usable
   credential inside Harbor containers.
2. Run the five paired smoke configs above. Do not accept Codex trials with zero tool
   calls, missing model names, trial exceptions, or missing rewards.
3. Inspect false-positive candidate precision as well as verifier success. The current
   oracle score is recall-only; medium-confidence related-API candidates such as name-
   similar helpers must not be presented as confirmed contracts.
4. If the five-case gate opens, freeze an immutable snapshot and run the npm/yarn-79
   scale gate before considering all clean205 tasks. If it does not open, use paired
   trajectories to identify whether retrieval, fact ranking, or propagation checking
   failed.
5. Reconcile the paper's stale 219-task narrative separately with the clean205 source
   of truth; do not silently mix those denominators in new result tables.

## Key decisions

| Decision | Rationale |
| --- | --- |
| Treat `actix-macros` delegation as non-derivable | It is in the hidden human repair but not admitted pre-cutoff `syn` evidence; counting it would reward oracle leakage. |
| Report 24/24 as decisive-fact recall only | Presence of oracle-relevant facts does not establish precision, causal benefit, or repair success. |
| Keep related-API mappings medium confidence | Name/call-surface similarity can surface the right API but also produces plausible distractors; agents must verify. |
| Require complete validity-audited pairs for the scale gate | Missing/zero-tool/exception trials must not masquerade as passes or treatment effects. |
| Stop at five cases until a paired benefit appears | This controls cost and prevents scaling a context mechanism that merely increases prompt size. |

## Blockers

- The configured Maestro route remains unreachable:
  `http://172.100.216.1:23333/api/openai/v1/models` timed out after 8.002 s with
  HTTP `000`, curl exit `28`, and zero response bytes.
- No `OPENAI_API_KEY`, `CODEX_MAESTRO_BASE_URL`, `CODEX_FORCE_API_KEY`, or
  `AZURE_OPENAI_API_KEY` is present in the current environment.
- This is the same blocker across three consecutive continuation turns. Docker,
  Harbor, variant generation, oracle smoke, and config parsing are otherwise healthy.

## Suggested next step

Restore a reachable Maestro GPT-5.5 route, then run the five two-task smoke configs and
feed only validity-audited results into `summarize-experiment`.

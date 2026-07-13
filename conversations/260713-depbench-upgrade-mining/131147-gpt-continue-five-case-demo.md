# Handoff Note — 131147 · gpt · continue-five-case-demo

## Inherited context

Continued from `104950-gpt-implemented-collectors-arms-HANDOFF.md`. Locked decisions remain:

- current219-era five-case causal demo first; npm79 only after the predeclared scale gate;
- Codex + GPT-5.5;
- GitHub, local GHArchive, and immutable upstream versions before WoC V2412;
- strict evidence time `< target PR creation`, target/oracle exclusion, and no hidden patch content in mining or prompts;
- context should change authority, propagation, contradiction handling, and stopping behavior rather than merely add documentation.

The inherited blocker was a missing GPT-5.5 route: Docker and Harbor work, but no Azure token path exists and the Maestro endpoint is unreachable.

## Work done this session

- [x] Extended Markdown mining beyond action headings while preserving explicit evidence anchors:
  - prose transformations such as `changed to`, `will become`, and `is gone`;
  - relative-path semantics;
  - Route component/render/children → element;
  - Redirect → Navigate and default replace behavior;
  - versioned release-note sections restricted to `old < section <= new`;
  - test-scaffolding facts such as syn/trybuild.
- [x] Added target-aware JavaScript alias handling. A React Router `Link as RouterLink` import no longer makes Material-UI `<Link component={RouterLink}>` look like the removed React Router prop.
- [x] Added target-relevant source/test delta mining with dependency import/binding provenance, upstream support counts, and evidence refs.
- [x] Added monorepo scoping inferred from `manifest.patch`; Solana correctly scopes to `stake-pool/js`, actix to `actix` and `actix-derive`.
- [x] Added numeric-default correlation using target class/path provenance. Shiro now recovers `ITERATIONS = 1000000` → target-version `DEFAULT_ITERATIONS = 50_000`, rather than the incorrect generic hash default of `1` seen in the first prototype.
- [x] Added fact merging/dominance rules. Qualified relocations suppress lower-quality unqualified removals; ambiguous removal evidence is a non-blocking verification candidate.
- [x] Added dependency-bound usage confidence. Precise wrappers such as `history.push` remain blocking, while unrelated lexical matches such as `b64` variables or non-Shiro `ITERATIONS` are warnings.
- [x] Generated frozen upstream evidence and facts for all five pilots.
- [x] Generated six prompt arms for every pilot: baseline, policy, equal-character raw, structured, policy+checker, and full.
- [x] Materialized and hash-validated 30 Harbor task variants, supporting both schema 1.1 and legacy version 1.0 tasks.
- [x] Generated five Harbor GPT-5.5 Maestro configs. All parse through Harbor 0.6.4's native `JobConfig.model_validate_json`.
- [x] Added trial validity auditing. Codex runs with missing trajectories, zero tool calls, missing model identity, or trial exceptions are invalid regardless of reward.
- [x] Ran a real Harbor oracle trial on the materialized Brokeneck baseline variant: reward `1.0`.
- [x] Calibrated the final completeness checker post-mining against all five human repairs. All five now report zero hard uncovered production paths; visible-test conflicts and semantic ambiguity remain visible separately.
- [ ] Run real Codex baseline/full trials (external route still unavailable).
- [ ] Run repeated six-arm five-case experiment and apply scale gate.

## Current state

### Code

| File | Change |
|---|---|
| `dependagent/delta_mining.py` | Import/binding-scoped upstream source/test replacement mining; added API correlation; numeric default correlation |
| `dependagent/mining.py` | Version-bounded release-note and guide-body facts; test scaffolding; fact merge/dominance |
| `dependagent/completeness.py` | Alias-aware JSX matching, monorepo scope, high-confidence blocking vs warnings, semantic uncertainty |
| `dependagent/experiment.py` | Target-relevant fact selection and equal-character raw retrieval excerpts |
| `dependagent/variants.py` | Hash-frozen Harbor variants, schema 1.1 + legacy 1.0 support, benchmark invariant validation |
| `dependagent/launch.py` | Credential-free GPT-5.5 Maestro Harbor configs and launch manifests |
| `dependagent/audit.py` | Harbor result/trajectory validity auditing |
| `dependagent/repository.py` | Exact target base checkout materialization |
| `dependagent/paths.py` | Manifest-derived workspace scopes |
| `dependagent/cli.py` | Commands for the full pipeline |
| `dependagent/README.md` | Updated operator workflow and caveats |
| `tests/test_dependagent_foundation.py` | 35 passing unit/integration tests |

Verification:

```text
uv run python -m unittest discover -s tests -q
Ran 35 tests ... OK

git diff --check
clean
```

### Five-case evidence and selected delivery facts

| Task | Complete upstream records | Final candidate facts | Target-selected facts | Key recovered signal |
|---|---:|---:|---:|---|
| `nearform__brokeneck__820` | 195 | 17 | 10 | Routes/Navigate/element/useNavigate/useMatch/relative paths |
| `solana-labs__solana-program-library__4301` | 158 | 8 | 8 | Token class/free-function migration; associated address and approve APIs |
| `actix__actix__554` | 88 | 2 | 2 | syn input churn plus trybuild scaffolding warning |
| `nuts-foundation__nuts-node__426` | 49 | 6 | 5 | RFC7797 `b64` payload semantics; negative-control fixture remains non-derivable |
| `dschadow__JavaSecurity__236` | 445 | 12 after dominance | 12 | ByteSource/AES relocations and 50,000 iteration default |

The exact selected counts are in each arms command output. Medium-confidence upstream removals render under “Verification candidates (non-blocking)” and do not become mandatory rewrite instructions.

### Frozen variants and launch configs

Each root contains six task directories, `variant_manifest.json`, `harbor_config.json`, and `harbor_config.launch.json`:

- `dependagent/artifacts/pilot/nearform__brokeneck__820_harbor_variants_final/`
- `dependagent/artifacts/pilot/solana-labs__solana-program-library__4301_harbor_variants_final/`
- `dependagent/artifacts/pilot/actix__actix__554_harbor_variants_final/`
- `dependagent/artifacts/pilot/nuts-foundation__nuts-node__426_harbor_variants_final/`
- `dependagent/artifacts/pilot/dschadow__JavaSecurity__236_harbor_variants_final_v2/`

All 30 variants pass `dependagent validate-variants`. Their source-tree hashes were printed during the final audit and are stored in their manifests.

Harbor 0.6.4 has no `--dry-run`, despite the installed skill reference saying otherwise. Config validation was performed directly with Harbor's `JobConfig` model.

### Runtime evidence

Oracle smoke:

```text
trials-fix/dependagent-variant-smoke/nearform__brokeneck__820__arm-ba__EWCFNr6
Task: dependagent/nearform__brokeneck__820__arm-baseline
Reward: 1.0
```

`dependagent audit-trials` accepted this oracle trial. The same auditor requires Codex tool calls and a model-bearing trajectory.

Final post-mining oracle completeness results are ignored artifacts named:

```text
dependagent/artifacts/pilot/<task>_oracle_completeness_final_v2.json
```

For nuts-node the final corrected file is `_final_v3.json`. All five have `complete=true`; this is checker calibration only, not an agent pass result.

## Open tasks for the next agent

1. Restore a real GPT-5.5 route. Preferred Maestro requirements are already embedded in each config: `CODEX_MAESTRO_BASE_URL`, `CODEX_FORCE_API_KEY=1`, and nonempty `OPENAI_API_KEY`. The endpoint must actually respond before launch.
2. Run only Brokeneck baseline and full first:
   ```bash
   harbor run -c dependagent/artifacts/pilot/nearform__brokeneck__820_harbor_variants_final/harbor_config.json
   ```
   To avoid launching all six during the first smoke, create a two-arm manifest/config or invoke the two variant paths individually with explicit custom Codex import/model/env.
3. Immediately audit results:
   ```bash
   uv run dependagent audit-trials --root <job-dir> --output <audit.jsonl>
   ```
   Reject missing/zero-tool trajectories before looking at verifier reward.
4. If baseline/full are infrastructure-valid, run all six Brokeneck arms with repetitions, then the other four pilots.
5. Score fact precision/recall and contradiction resolution manually against the frozen human repair surfaces. Do not expose oracle patches to prompts.
6. Apply the `PLAN.md` scale gate. Do not proceed to npm79 unless at least one valid context-complete case improves without regressing an already-correct repair and the artifacts explain why.
7. If scaling, add a Java/Maven and Go-aware usage parser before claiming the checker is ecosystem-general. The current scanner is conservative text/import analysis, strongest for npm/JS.

## Key decisions

| Decision | Rationale |
|---|---|
| Raw arm uses relevant verbatim excerpts, character-matched to structured facts | A prefix of a large guide omitted decisive sections and made the raw control unfair |
| Release notes are version-bounded | Full changelogs otherwise injected unrelated older breaking changes |
| Delta miner uses import/binding provenance | Repository-wide token overlap produced 200–1,360 unusable candidates |
| Ambiguous removals are non-blocking verification candidates | A version-range deletion is not proof that a target usage must be rewritten |
| Semantic changes are review obligations, not automatic blockers | Some target-version semantic changes require no source edit; b64 does, nbf in this target does not |
| Numeric defaults use class/path provenance | Name-only matching selected Shiro's unrelated `DEFAULT_ITERATIONS = 1` instead of 50,000 |
| Variant immutability is hash-validated rather than relying on mutable task paths | Long evaluations must not observe worktree drift |
| Codex zero-tool reward is infrastructure-invalid | Prior runs showed verifier baselines can masquerade as passes when routing fails |

## Blockers

- `http://172.100.216.1:23333/api/openai/v1/models` still times out (`HTTP 000`).
- No `CODEX_MAESTRO_BASE_URL`, `CLOUDGPT_OPENAI_TOKEN`, `AZURE_OPENAI_API_KEY`, or `OPENAI_API_KEY` is present in the current shell.
- `az` is not installed, so `CodexCloudGPT` cannot acquire an AAD token locally.

Docker 29.1.3, `/var/run/docker.sock`, Harbor 0.6.4, task images, oracle execution, and verification are healthy. The only launch blocker is model routing/authentication.

## Suggested next step

Make the Maestro endpoint reachable, then run and audit only the Brokeneck baseline/full pair before spending budget on the remaining 28 variants.


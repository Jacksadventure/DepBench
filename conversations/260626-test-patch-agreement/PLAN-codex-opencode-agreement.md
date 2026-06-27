# Plan — Two-Agent Test-Patch Audit & Inter-Coder Agreement (harbor_lite)

Date: 2026-06-26 · Branch: `v4-with-test` · Dataset: `harbor_benchmark/tasks_v4` (219 tasks)

## 1. Goal

Replace the prior *manual subagent* open-coding audit with two **independent automated
coders** driven by `harbor_lite`, then report **inter-coder agreement**:

- Coder A: **codex** CLI, model `gpt-5.3-codex` (via `~/.codex` → depbench gateway).
- Coder B: **opencode** CLI, model `github-copilot/gemini-3.1-pro-preview` (Copilot oauth).

Each coder statically reads one task's `Δm/Δt/Δc` + verifier and emits a structured
verdict. We compute **percent agreement + Cohen's κ** on the 4-way verdict and a
collapsed binary, plus a confusion matrix and the disagreement list.

## 2. Locked design decisions (from grilling)

| Decision | Choice |
| --- | --- |
| What we score | **Static verdict labels** (no dynamic test execution) |
| Scope | **All 219** task dirs currently in `tasks_v4` |
| Primary scored label | **4-way verdict** + **collapsed binary** (witness vs not) |
| Descriptive (reported, not κ-scored) | taxonomy category, Δc nature, import-only, confidence, rationale |
| Input to agent | Agent **reads files** from a staged working dir (no inline patches → no argv limit) |
| Output from agent | Agent **writes `VERDICT.json`**; collected via `artifact_paths` |
| opencode provider | **GitHub Copilot** → `github-copilot/gemini-3.1-pro-preview` |
| codex model | `gpt-5.3-codex` (existing `~/.codex/config.toml` `copilot_api` provider) |
| `isolated_state` | **False** (required so both CLIs read real config/credentials) |
| Agreement analyses | **Core codex-vs-opencode only** (no 3rd rater, no prior-label compare) |
| Coding criterion | Locked Level-1: `TEST(P⊕Δm⊕Δt)=FAIL` ∧ `TEST(P⊕Δm⊕Δc⊕Δt)=PASS` (predicted statically) |

## 3. Environment & prerequisites

Confirmed:
- `codex` 0.142.1, `opencode` 1.17.11 on PATH.
- `~/.codex/config.toml`: `model_provider=copilot_api`, `base_url=http://10.12.1.193:40441`,
  `wire_api=responses`, key from `~/.codex/.env` (`GITHUB_COPILOT_API_KEY`).
- `opencode auth list`: GitHub Copilot oauth present (`~/.local/share/opencode/auth.json`).
- All 219 tasks have `solution/manifest.patch`, `solution/code.patch`, `tests/test.patch`,
  `instruction.md`, `task.toml`, `tests/test_state.py`, `tests/test.sh`.

**codex is confirmed working** by the user (`gpt-5.3-codex` via `copilot_api`); no codex
smoke needed.

**Gate before the full run — opencode-only 1-task smoke** (e.g. `actix__actix__554`):
- opencode with `github-copilot/gemini-3.1-pro-preview` does **not** return
  `model_not_supported` (Copilot previously rejected a *different* model, `gpt-5.3-codex`),
  and writes a valid `VERDICT.json`. If it's rejected, stop and ask for an alternative
  model string / provider rather than burning 219 runs.

## 4. Harness mechanics (per task, per agent)

For each `(agent, task)`:
1. **Stage** an isolated copy: `cp -r tasks_v4/<task>  stage/<job>/<agent>/<task>`
   (protects the live dataset; gives each agent its own dir → no `VERDICT.json` collision).
2. `WorkspaceSpec.existing(stage/<job>/<agent>/<task>, clean=False)` → `owned=False`
   (harbor_lite will not git-reset or delete it).
3. `RunSpec(name=<task>, agent=<CodexAgent|OpenCodeAgent>, prompt=AUDIT_PROMPT,
   workspace=…, runtime=AgentRuntime(disable_web=True, isolated_state=False,
   timeout_sec=900), artifact_paths=("VERDICT.json",))`.
4. `run_many(specs, concurrency=4, jobs_dir="jobs", job_name="agreement-<agent>-<ts>")`.
5. Collected output lands at `jobs/<job>/<task>/artifacts/VERDICT.json`
   (fallback: read it from the staged dir, or scan `codex.txt`/`opencode.txt` for a JSON block).

One `run_many` job **per agent** (cleaner trial names; join later by task).

## 5. Audit prompt + `VERDICT.json` schema

Prompt (identical for both agents) instructs: *static analysis only, do not run tests*;
read `instruction.md`, `task.toml`, `solution/manifest.patch` (Δm), `solution/code.patch`
(Δc), `tests/test.patch` (Δt), `tests/test_state.py` + `tests/test.sh` (verifier);
apply the locked Level-1 criterion and the taxonomy; then **write `VERDICT.json`** to the
current directory with exactly this schema:

```json
{
  "task": "<folder name>",
  "verdict": "WITNESSES_BREAKING_CHANGE | UNWITNESSED | TESTS_OTHER_THING | INCONCLUSIVE",
  "taxonomy_category": "Direct Compatibility Witness | Compatibility-Accommodation Test Update | Toolchain/Static Check Oracle | Drive-By Product Behavior Oracle | Circular Implementation Oracle | Test-Suite Maintenance Oracle | Dead or Mis-Scoped Oracle | No-Code-Pass / Latent Oracle | Confounded Oracle",
  "delta_c_nature": "REAL_SOURCE_REPAIR | MIXED | FORMATTER_LINT_CHURN | CONFIG_INFRA_ONLY | DOCS_EXAMPLE_ONLY | TEST_ONLY | SNAPSHOT_ONLY",
  "import_only_delta_t": true,
  "dependency": {"library": "", "old_version": "", "new_version": ""},
  "predicted_precode_fail": true,
  "predicted_postcode_pass": true,
  "confidence": "low | medium | high",
  "key_risk_signals": ["..."],
  "rationale": "<= 150 words"
}
```

Verdict definitions and the taxonomy are carried verbatim from
`conversations/260624-test-patch-audit/241334-gpt-researched-test-patches.md`
(Direct Compatibility Witness → `WITNESSES_BREAKING_CHANGE`, etc.). Binary label for κ is
derived in analysis: `is_witness = (verdict == "WITNESSES_BREAKING_CHANGE")`.

## 6. Driver script

`scripts/test_patch_agreement/run_audit.py` (puts `harbor_lite` on `PYTHONPATH`):
- enumerate task dirs; build the prompt; stage per-(agent,task) copies.
- build specs for codex and opencode; `run_many` per agent at `concurrency=4`.
- robust `VERDICT.json` loader (artifact dir → staged dir → log-scan) with a
  `parse_status` flag (`ok | json_repaired | missing`) per cell.

## 7. Analysis

`scripts/test_patch_agreement/agreement.py`:
- join codex × opencode by task → matrix of 219 rows.
- **percent agreement** and **Cohen's κ** on (a) 4-way verdict, (b) binary witness.
- **confusion matrix** (codex verdict × opencode verdict).
- **disagreement list** (task, codex verdict+rationale, opencode verdict+rationale).
- per-verdict agreement breakdown; count of unparseable/missing cells (excluded from κ,
  reported separately).

## 8. Deliverables

| Artifact | Path |
| --- | --- |
| Driver + analysis scripts | `scripts/test_patch_agreement/{run_audit.py,agreement.py}` |
| Raw agent runs | `jobs/agreement-codex-<ts>/`, `jobs/agreement-opencode-<ts>/` |
| Per-task labels (both agents) | `harbor_benchmark/reports/test_patch_agreement_2026-06-26.csv` |
| Agreement report (κ, matrix, disagreements) | `harbor_benchmark/reports/test_patch_agreement_2026-06-26.md` |
| Handoff note | `conversations/260626-test-patch-agreement/` |

## 9. Runtime & cost

- 219 tasks × 2 agents = **438 runs**. `disable_web=True`, `isolated_state=False`,
  `timeout_sec=900`, `concurrency=4` (shared gateway/Copilot rate limits — tunable).
- Rough wall time at ~2–4 min/run: ~4–7 h; raise concurrency if the gateway tolerates it.

## 10. Risks & mitigations

| Risk | Mitigation |
| --- | --- |
| Copilot rejects `gemini-3.1-pro-preview` | Smoke-test first; stop & ask if `model_not_supported` |
| `isolated_state=True` would break auth | Forced to `False`; documented |
| Agent emits malformed/no JSON | Strict schema in prompt + tolerant loader + `parse_status` |
| Agent tries to run tests / edit files | Prompt forbids execution; staged copy isolates the dataset |
| Huge `code.patch` floods agent context | Agent reads files itself and may chunk; not in argv (no E2BIG) |
| Nondeterminism | Single pass per agent (documented); disagreements enumerated, not hidden |

## 11. Execution checklist

1. Write `run_audit.py` + `agreement.py`; put `harbor_lite` on `PYTHONPATH`.
2. **Smoke (opencode only)**: 1 task; confirm valid `VERDICT.json` and no Copilot rejection. (codex already confirmed.)
3. Full run: codex job, then opencode job (or interleaved), `concurrency=4`.
4. Parse all `VERDICT.json`; build the per-task CSV.
5. Compute agreement; write the `.md` report (κ, confusion matrix, disagreements).
6. Write the handoff note; surface headline κ + disagreement count.

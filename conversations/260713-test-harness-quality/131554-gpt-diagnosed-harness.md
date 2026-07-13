# Handoff Note — 131554 · gpt · diagnosed-harness

## Inherited context

- Read the July 13 threads under `conversations/260713-*`, especially:
  - `260713-context-case-studies`: five zero-pass deep dives. It established one structurally unsolvable task (`nuts-foundation__nuts-node__426`), one hidden-scaffolding task (`actix__actix__554`), and three tasks where visible pre-upgrade tests pull agents away from the hidden post-upgrade oracle (`nearform__brokeneck__820`, `solana-labs__solana-program-library__4301`, `dschadow__JavaSecurity__236`).
  - `260713-half-pass-analysis`: rebuilt the 219x10 final matrix, found 93 zero-pass tasks, and discovered the guarded-rerun Maven environment defect: 166/405 verifier logs across 57 Maven tasks fail because `JAVA_HOME`/`PATH` was stripped from the guarded image.
  - `260713-depbench-upgrade-mining`: treats random fixture regeneration and hidden test scaffolding as benchmark hazards and requires a hazard-clean sensitivity analysis before context-mining claims.
  - `260713-dependabot-agent-assignment`: product-context only; no harness-quality evidence used in the verdicts below.
- Read `harbor_benchmark/HARNESS.md` as the authoritative operational specification. The checked-out branch is `v4-with-test`; `tasks_v4` and `task_summary.json` each contain 219 tasks. This differs from the injected `AGENTS.md` clean205 baseline. The July 13 pass matrix is a 219-era result, so this report analyzes 219 and separately identifies what carries back to clean205.
- Read the prior oracle audits:
  - `harbor_benchmark/reports/test_patch_adjudication_2026-06-26.md`
  - `harbor_benchmark/reports/test_patch_reconciled_2026-06-26.csv`
  - `harbor_benchmark/reports/test_patch_behavior_classification_2026-06-26_219.*`
  - `harbor_benchmark/reports/v4_withtest219_nop_reverify37_20260629.*`
- Locked benchmark definition remains Level 1: `TEST(P + Dm + Dt)=FAIL` and `TEST(P + Dm + Dc + Dt)=PASS`, with the failure caused by the dependency update rather than lint, network, resources, unrelated behavior, or test-only scaffolding.

## Executive conclusion

The report that some zero-pass tasks are “unsolvable because the test patches are too rigid” is substantially correct, but “rigid” is primarily **semantic**, not a textual `git apply` problem.

1. **One task is proven information-theoretically unsolvable:** `nuts-foundation__nuts-node__426`. The hidden patch replaces a random EC key and signed fixtures, while the matching DID/key identifier is in agent-editable source. The value was generated on the PR day and cannot be inferred from the checkout, dependency, release notes, siblings, or any pre-PR evidence.
2. **One task is hidden-scaffolding-limited:** `actix__actix__554`. Nine of ten agents completed the syn 1-to-2 migration but failed because the hidden trybuild test requires `trybuild` and `rustversion` dev-dependencies that only exist in the withheld canonical manifest. The byte-exact `.stderr` test is also dead under the shipped Rust toolchain gate.
3. **At least 33/93 zero-pass tasks are already candidate oracle-quality failures**, not clean dependency-breaking witnesses, according to the reconciled two-coder audit. Twenty-two were independently labeled non-witness by both coders; eleven came from adjudicated disagreements. This is 35.5% of zero-pass tasks versus 17/126 = 13.5% outside the zero-pass set (odds ratio 3.53; Fisher exact two-sided p=0.000164). Zero-pass is therefore statistically enriched for bad oracles, not merely hard upgrades.
4. **Twelve nominal zero-pass tasks have invalid guarded Maven cells** (36 cells total) killed by the missing-`JAVA_HOME` environment. They cannot be called zero-pass until those trials are reverified. `dschadow__JavaSecurity__236` had an original passing cell replaced by one of these invalid zeros.
5. **The verifier does not enforce that the dependency upgrade happened.** A NOP agent, which made no manifest or source edits, passed all 37 tasks selected for no-op revalidation. This includes 33 tasks that the static oracle audit still called dependency witnesses: they may satisfy the formal `P + Dm + Dt` witness definition, but the runtime harness never ensures `Dm` is present. At least 37/219 tasks are therefore exploitable by doing nothing.
6. **The visible and hidden oracles are frequently adversarial.** In the available trajectory annotations, 324/493 analyzable zero-pass trial cells were labeled visible-pass/hidden-fail, covering 90/93 zero-pass tasks. Deep dives prove mutually contradictory old/new assertions in Solana and Shiro, while the instruction explicitly says to make “the existing tests pass.” This rewards ignoring visible tests or predicting the maintainer’s exact rewrite, rather than ordinary dependency repair discipline.
7. **No evidence supports textual patch fragility as the current root cause.** Across all 405 preserved guarded verifier logs, there were zero `Failed to apply hidden test patch` failures. However, overlay logic is inconsistent: 123/219 task verifiers restore patched paths to the baseline before applying `test.patch`, while 96/219 do not. In the zero-pass subset the split is 48 restore / 45 no restore. This should still be standardized.

Bottom line: the raw “93 consensus-hard tasks” claim is not defensible. Forty-four of the 93 are already directly questioned by one or more of: reconciled non-witness status, invalid Maven verification, confirmed random-fixture impossibility, or hidden scaffolding. Only 49 remain as a provisional audit queue after removing that union, and even those are not yet certified as semantically repair-equivalent oracles.

## Work done this session

- [x] Read the July 13 handoffs/reports and the authoritative harness specification.
- [x] Reconstructed the final 219x10 pass matrix and confirmed exactly 93 zero-pass tasks.
- [x] Joined the zero-pass set to the 219-task reconciled oracle audit, behavior classification, no-op revalidation, current task metadata, guarded rerun artifacts, and trajectory annotations.
- [x] Inspected the five zero-pass case studies and their actual task patches/verifiers where needed.
- [x] Scanned all 93 hidden test patches for new/deleted tests, fixtures/snapshots, random key material, shared source/test literals, and hidden scaffolding signals.
- [x] Scanned the 405 guarded verifier logs for patch-application failures and `JAVA_HOME` failures.
- [x] Inspected verifier heterogeneity: baseline restoration, `--recount`, `bash -lc`, narrow selectors, `--passWithNoTests`, and mutable installed-state dependence.
- [x] Preserved all existing user changes and run artifacts; no benchmark task, harness, config, source file, or report was edited.
- [ ] No Harbor rerun was launched. The invalid Maven cells require replay/re-execution after environment remediation.

## Scope and denominators

| Item | Count | Interpretation |
| --- | ---: | --- |
| Current checked-out tasks | 219 | `v4-with-test`; npm 79, Maven 66, Go 41, Cargo 21, Python 12 |
| Final model x harness configurations | 10 | July 13 post-guard replacement matrix |
| Zero-pass tasks | 93 | npm 48, Cargo 15, Go 13, Maven 12, Python 5 |
| Zero-pass tasks from clean205 | 90 | The other 3 are hard14 additions: BramVR, Nextdoor, giantswarm/muster |
| Reconciled non-witness candidates, all 219 | 50 | 46 clean205 + 4 hard14 |
| Reconciled non-witness candidates among zero-pass | 33 | 32 clean205 + `Nextdoor__vigil__35` |
| Guarded Maven zero-pass tasks with invalid verifier cells | 12 tasks / 36 cells | Must reverify before hardness claims |
| Confirmed structural/scaffolding hazards | 2 | nuts-node random fixtures; actix hidden dev-deps/dead stderr |
| Union of the above questioned zero-pass tasks | 44/93 | 33 non-witness U 12 Maven-tainted U 2 structural/scaffolding; overlaps accounted for |
| Provisional residual zero-pass audit queue | 49/93 | Not certified; simply lacks the already-proven flags above |

## Finding 1 — Zero pass is strongly contaminated by non-witness oracles

The reconciled June 26 audit labeled 169/219 tasks `WITNESSES_BREAKING_CHANGE`, 46 `TESTS_OTHER_THING`, and 4 `UNWITNESSED`. Intersecting with the July 13 matrix gives:

| Cohort | Candidate non-witness | Candidate witness | Non-witness rate |
| --- | ---: | ---: | ---: |
| Zero-pass | 33 | 60 | 35.5% |
| At least one pass | 17 | 109 | 13.5% |

The overrepresentation is large (odds ratio 3.53). The zero-pass label is partly selecting for hidden tests that ask for an unknowable human-specific change.

The 33 zero-pass candidate quarantine tasks are:

```text
KnpLabs__server-side-renderer__209
Nextdoor__vigil__35
algolia__react-element-to-jsx-string__305
alveusgg__alveusgg__871
ampproject__amp-wp__6853
ardatan__graphql-tools__7001
camunda-community-hub__spring-zeebe__642
chris48s__v8r__22
eakmanrq__sqlframe__137
eakmanrq__sqlframe__216
graphql-hive__graphql-config__1103
jenkinsci__warnings-ng-plugin__1278
jo-sm__stylelint_d__185
ledgersmb__LedgerSMB__8895
ledgersmb__LedgerSMB__8904
mightyiam__eslint-config-love__2178
nextcloud__server__39964
owncloud__web__11511
oxidecomputer__dropshot__1556
paularmstrong__onerepo__595
promptfoo__promptfoo__8808
promptfoo__promptfoo__8918
qntm__base65536__37
reearth__resium__609
reearth__resium__625
scinos__yarn-deduplicate__89
sladkoff__minecraft-prometheus-exporter__68
smlx__piv-agent__155
synyx__urlaubsverwaltung__2494
tekumara__typos-lsp__44
tusbar__eslint-config-xo-nextjs__163
typescript-eslint__tslint-to-eslint-config__1192
webhintio__hint__4027
```

Recurring mechanisms from the dual-coder rationales and adjudication:

- **Circular implementation oracle:** `Dt` imports a helper, symbol, method signature, option, or constant introduced only by `Dc`; failure establishes co-evolution with the human patch, not a dependency break. Examples: KnpLabs, Nextdoor, algolia, qntm, reearth, promptfoo, typescript-eslint, webhint.
- **Drive-by behavior/feature:** the dependency bump merely enabled a new feature or accompanied an unrelated bugfix. The old project was not broken. Examples: spring-zeebe, sqlframe 137/216, mightyiam, dropshot 1556, tusbar.
- **Test/tooling-only compatibility:** the break is in Jest/Vitest/JSDOM/router mocks, transpilation, or hidden test helpers; production behavior is not the tested repair. Examples: LedgerSMB, nextcloud/server, owncloud/web.
- **Wrong dependency or grouped-bump attribution:** generated metadata names one dependency while the verifier exercises another bundled change. Examples: graphql-config, LedgerSMB 8895, typos-lsp.
- **New hidden file/fixture required only by the oracle:** the failure can be ENOENT or a new test-only dependency rather than dependency-incompatible source. Example: `chris48s__v8r__22`.

These 33 should not be used in a “consensus-hard dependency repair” subset without dynamic three-state adjudication and, where necessary, repackaging.

## Finding 2 — Confirmed structural and semantic rigidity cases

| Task | Status | Why the current task is unfair | Required action |
| --- | --- | --- | --- |
| `nuts-foundation__nuts-node__426` | **Structurally unsolvable** | Hidden `Dt` swaps a random EC private/public key, DID, kid, signatures, and VCR fixtures. `Dc` hard-codes the matching new kid in source. No permitted evidence can reveal it. Eight of ten runs reached the resulting hidden kid mismatch; a GPT-5.5 run independently repaired the real RFC7797 change and still scored zero. | Quarantine immediately. Repackage by keeping key+fixtures+dependent constant on one visible side, deriving IDs dynamically, or testing behavior independent of the regenerated key. |
| `actix__actix__554` | **Hidden-scaffolding-limited** | Nine of ten agents correctly migrated syn 2 and passed visible tests, then hidden `trybuild.rs` failed because `trybuild` and `rustversion` dev-deps exist only in the canonical hidden manifest. The byte-exact `.stderr` test is gated to Rust 1.65 and does not execute on Rust 1.96. | Repackage hidden test dependencies into the visible/base scaffold or image. Remove/fix the dead toolchain gate. Do not count missing invisible dev-deps as repair ability. |
| `nearform__brokeneck__820` | **Canonical-idiom trap** | Visible tests mock v5 `useHistory` and pass route IDs as props; hidden tests mock v6 `useNavigate`/`useParams` and render components without props. Agents knew the v6 API but wrote compatibility shims to keep visible tests green. | Keep only if intentionally measuring re-baselining. Rewrite instruction to state that visible tests may encode pre-upgrade behavior, or expose compatible post-upgrade tests. Accept behaviorally equivalent adapters. |
| `solana-labs__solana-program-library__4301` | **Mutually contradictory visible/hidden semantics** | Visible tests require generic wrapped errors, two account-info calls, and two instructions; hidden tests require `TokenAccountNotFoundError`, one call, and three instructions. No source patch passes both. Agents read the new library source but deliberately preserved the visible contract. | Label as an adversarial oracle-direction task, not ordinary repair. Prefer invariant behavioral checks over exact call/instruction counts when multiple valid migrations exist. |
| `dschadow__JavaSecurity__236` | **Default-choice trap + invalid rerun** | Visible test asserts 1,000,000 iterations; hidden asserts Shiro 2 default 50,000. Agents decompiled the correct new default, then preserved the visible value. One guarded cell was also killed by missing `JAVA_HOME`. | Reverify first. If retained, explicitly classify as post-upgrade-default adoption, not missing API knowledge. |

The five-case sample is not representative enough to estimate a corpus-wide unsolvable fraction, but it proves that consensus-hard is not equivalent to context-hard or repair-hard.

## Finding 3 — Guarded Maven verifier defect invalidates zero-pass membership

The guarded image-rebuild path lost Docker `ENV`, including `JAVA_HOME` and Java on `PATH`. Among all guarded artifacts:

- 405 verifier logs inspected.
- 166 contain `The JAVA_HOME environment variable is not defined correctly`.
- 57 distinct tasks, all Maven.
- 0/166 affected trials passed.
- 140/200 original-pass to guarded-fail replacements are tainted.

The 12 nominal zero-pass tasks touched by this defect are:

| Tainted cells | Task |
| ---: | --- |
| 1 | `Graylog2__graylog2-server__23926` |
| 1 | `apache__maven__12057` |
| 5 | `camunda-community-hub__spring-zeebe__642` |
| 2 | `cryostatio__cryostat-legacy__1880` |
| 1 | `dschadow__JavaSecurity__236` |
| 7 | `jenkinsci__warnings-ng-plugin__1278` |
| 2 | `kanton-bern__hellodata-be__315` |
| 4 | `lukas-krecan__JsonUnit__274` |
| 4 | `onthegomap__planetiler__1430` |
| 1 | `sladkoff__minecraft-prometheus-exporter__68` |
| 2 | `urlaubsverwaltung__urlaubsverwaltung__4808` |
| 6 | `yahoo__elide__2476` |

Three of these are also in the 33-task non-witness set: spring-zeebe, warnings-ng, and minecraft-prometheus-exporter. After accounting for overlap, non-witness plus Maven-tainted covers 42/93 zero-pass tasks.

No Maven task remains in the 49-task provisional residual after removing non-witness, tainted, and the two confirmed structural/scaffolding cases. Consequently, **the current claim that 12 Maven tasks are consensus-hard should be withdrawn entirely pending re-verification**.

## Finding 4 — The verifier grades mutable container state and does not enforce `Dm`

This is the most consequential harness-level defect beyond the guarded Maven incident.

The v3/v4 protocol deliberately does not preapply the manifest patch. The agent must author the bump. But verification overlays only `tests/test.patch` and then runs a command in the agent’s existing `/app` container. It does not generally:

1. assert that the required dependency/version is present in the submitted manifest/lockfile;
2. reconstruct a clean environment from the submitted manifest;
3. remove stale `node_modules`, Maven cache effects, Cargo target state, ad-hoc vendoring, or packages installed directly by the agent;
4. distinguish source correctness from lucky installed state.

Dynamic evidence: `v4_withtest219_nop_reverify37_20260629` ran 37 suspected tasks with a NOP agent. All 37 passed without any dependency or source edit. Only 4 overlap the reconciled 50-task non-witness set, so the static patch audit alone does not catch this runtime enforcement gap.

Consequences:

- A no-op can score 1 despite failing the end-to-end upgrade objective.
- An agent can edit a manifest but test against stale dependencies.
- An agent can install the target version ad hoc without recording it in the deliverable.
- npm tasks can be sensitive to leftover `node_modules`; the half-pass audit already demonstrated this for js-wacz.
- Reward can measure terminal-state residue rather than a reproducible repair patch.

Recommended invariant: verification must validate the submitted dependency boundary and then test in a clean, reproducible dependency environment. If the scientific construct is source repair rather than dependency-management skill, preapply canonical `Dm` before the agent and remove manifest authoring from the task. If end-to-end authoring is intentional, assert the target versions and reinstall from the submitted manifests before applying hidden tests.

## Finding 5 — Visible tests and the instruction point in the wrong direction

The common instruction says:

> Restrict your changes to the project's source code so that the existing tests pass against the upgraded dependency.

This conflicts with two harness facts:

- The agent must edit manifest/lock files because `Dm` is not preapplied.
- The verifier replaces selected visible tests with post-upgrade `Dt`, and those tests may intentionally contradict the visible suite.

Among the 93 zero-pass tasks, 78 contain the source-only restriction and 68 literally say “existing tests pass.” Trajectory annotations for the available zero-pass cells show:

- 500 annotated cells over all 93 tasks.
- 493 cells analyzable by both annotators.
- 324/493 labeled visible-pass/hidden-fail.
- 90/93 tasks have at least one such cell.

This is not proof that all 90 tasks have bad tests: visible-pass/hidden-fail is expected in a hidden-test benchmark. It is proof that the prompt and task design systematically encourage the exact behavior that fails grading. The five deep dives show the mechanism directly: agents discover the new contract, then revert or shim it because visible tests are presented as authoritative.

Decide which construct DepBench wants:

- **Ordinary repair with hidden coverage:** visible and hidden tests should be compatible behavioral samples. Correct solutions should not need to distrust visible tests.
- **Upgrade re-baselining under stale tests:** keep contradictory tests, but state this explicitly and report it as a distinct task category measuring evidence authority/oracle-direction judgment.

Do not mix the two in one pass-rate headline.

## Finding 6 — Hidden patch application is inconsistent, but not the observed failure

Current corpus-level verifier variants:

| Mechanism | Tasks (219) | Zero-pass subset (93) |
| --- | ---: | ---: |
| Restores every `test.patch` target from baseline before overlay | 123 | 48 |
| Does not restore targets first | 96 | 45 |
| Adds `git apply --recount` fallback | 80 | 22 |
| Runs commands via `bash -lc` | 80 | 22 |
| Uses `--passWithNoTests` somewhere | 6 | 4 |

The restore-first variant is preferable: it makes agent test edits irrelevant and ensures a canonical hidden suite. The non-restore variant can reject an otherwise correct source repair if the agent edited an overlapping test for diagnosis, although the instruction forbids persistent test edits.

Observed evidence does **not** show this causing current zeros: none of 405 preserved guarded verifier logs contains `Failed to apply hidden test patch`. Therefore do not diagnose the 93 zeros as a `git apply` context-line problem. Standardize the implementation anyway, and add an explicit overlay-stage outcome to result metadata.

The four zero-pass tasks whose verifier includes `--passWithNoTests` are:

```text
ardatan__graphql-tools__6921
ardatan__graphql-tools__7001
decaporg__decap-cms__4748
scinos__yarn-deduplicate__89
```

These should assert collected/executed test counts so an empty selector cannot be rewarded.

## Finding 7 — Raw patch-shape statistics identify the next audit queue, not guilt

Among zero-pass tasks:

- `CORRECTS_EXISTING_BEHAVIOR`: 40
- `MIXED`: 38
- `TEST_INFRA_OR_FIXTURE_ONLY`: 10
- `ADDS_NEW_TESTS`: 5
- 39/93 add tests, 22/93 delete/remove tests, and 15/93 touch fixture/golden/snapshot-like paths.

Compared with the 126 non-zero-pass tasks, zero-pass tasks are enriched for mixed patches and added tests, but not for the coarse `fixture_or_infra_only` label. Semantic coupling is the important signal; a snapshot is not automatically invalid.

The 15 zero-pass tasks touching golden/fixture/snapshot-like paths are:

```text
actix__actix__554
chainflip-io__chainflip-sdk-monorepo__166
dkhmelenko__autoapproval__343
golangci__golangci-lint__4157
ledgersmb__LedgerSMB__8895
ledgersmb__LedgerSMB__8904
nuts-foundation__nuts-node__426
owncloud__web__11511
oxidecomputer__dropshot__1556
paularmstrong__onerepo__595
prettier__prettier__8688
regexident__cargo-modules__122
regexident__cargo-modules__389
renovatebot__renovate__36455
tusbar__eslint-config-xo-nextjs__163
```

Six are already non-witness candidates. Of the other nine, nuts-node is proven unsolvable and actix is scaffolding-limited. The remaining seven warrant alternative-repair robustness checks, not automatic exclusion.

`slowli__jwt-compact__138` also contains key-generation code in `Dt`, but unlike nuts-node it generates an RSA key during the test and does not require guessing a hidden random constant; it is not the same hazard.

## Provisional residual zero-pass audit queue

After removing the union of (a) 33 reconciled non-witness candidates, (b) 12 Maven-tainted tasks, and (c) nuts-node + actix, 49 tasks remain. This is **not** a clean-hard set; it is simply the next queue for semantic robustness review:

```text
BramVR__gohealthcli__351
MystenLabs__fastcrypto__460
Stranger6667__jsonschema__825
adoptoposs__mjml_nif__117
adoptoposs__mjml_nif__13
apexskier__github-release-commenter__169
apexskier__nova-typescript__445
appium__appium-uiautomator2-driver__627
ardatan__graphql-tools__6921
authelia__authelia__11445
chainflip-io__chainflip-sdk-monorepo__166
cosmos__cosmos-sdk__19810
decaporg__decap-cms__4748
decaporg__decap-cms__5178
dkhmelenko__autoapproval__343
docker__login-action__754
eakmanrq__sqlframe__581
eakmanrq__sqlframe__589
elastic__cloud-on-k8s__6847
eslint__eslint__17917
giantswarm__muster__751
golangci__golangci-lint__4157
hashicorp__aws-sdk-go-base__796
hexojs__hexo-uglify__147
huridocs__uwazi__4579
imsnif__bandwhich__430
iterative__dvc__7899
jo-sm__stylelint_d__709
libp2p__js-libp2p-bootstrap__171
marocchino__sticky-pull-request-comment__305
mitmproxy__mitmproxy_rs__142
mozilla__sccache__1190
nearform__brokeneck__820
nextcloud__spreed__9915
octokit__auth-oauth-app.js__137
open-telemetry__opentelemetry-go__1872
open-telemetry__opentelemetry-go__1943
oxidecomputer__dropshot__501
oxidecomputer__dropshot__630
prettier__prettier__8688
rash-sh__rash__698
regexident__cargo-modules__122
regexident__cargo-modules__389
renovatebot__renovate__36455
sequelize__umzug__572
slowli__jwt-compact__138
solana-labs__solana-program-library__4301
sourcenetwork__defradb__1577
spiffe__spire__4184
```

Ecosystem mix: npm 23, Cargo 13, Go 10, Python 3, Maven 0.

## Recommended remediation plan

### P0 — Stop publishing invalid hardness numbers

1. **Withdraw/freeze the 93-zero-pass and Maven ranking claims** until the guarded verifier environment is fixed and all 166 tainted cells are reverified.
2. **Quarantine `nuts-foundation__nuts-node__426` now.** This does not need another model run.
3. **Repackage `actix__actix__554`** so test-only dev-dependencies are visible/preinstalled and the trybuild gate actually runs, then rerun it.
4. **Put the 33 zero-pass reconciled non-witness tasks in a candidate quarantine**, with the 22 both-coder agreements first. Dynamically adjudicate before final deletion.

### P0 — Enforce the submitted upgrade

5. Add a verifier preflight that parses the relevant manifest and asserts the requested package resolves to the required target boundary.
6. Rebuild/install from submitted manifests in a clean dependency environment. Do not grade against arbitrary agent-leftover `node_modules`, ad-hoc packages, vendored overrides, or cache state.
7. Run a NOP agent against **all 219** tasks, not only the 37 selected suspects. Any pass is a harness failure for the end-to-end construct unless the task is explicitly source-only with canonical `Dm` preapplied.

### P1 — Make hidden tests repair-equivalent rather than human-patch-equivalent

8. For every candidate task, run four states in a frozen environment:
   - `P + Dt` / NOP state: must not reward absence of the bump.
   - `P + Dm + Dt`: must fail for an allowed dependency-caused reason.
   - `P + Dm + Dc + Dt`: must pass.
   - one or more independently authored alternative repairs: should pass if behaviorally correct.
9. Apply the adjudication counterfactual automatically: remove `Dt` lines coupled only to new `Dc` symbols/helpers/constants and ask whether the dependency-caused failure remains. If not, the oracle is circular.
10. Reject or repackage tasks where `Dt` contains random regenerated keys, signatures, timestamps, byte-exact fixtures, or hidden-only dependencies entangled with source constants.
11. Prefer invariant assertions over exact internal call counts, snapshots, error strings, helper names, or constructor shapes unless those are the actual public contract.

### P1 — Standardize verifier mechanics

12. Use restore-to-baseline plus canonical overlay for every `test.patch` target; remove the 123/96 split.
13. Record separate stage outcomes: manifest validation, dependency install, patch overlay, test collection count, test execution, and teardown. Do not collapse all failures into reward 0.
14. Remove `--passWithNoTests`, `--no-run`, or guarded acceptance unless the verifier independently asserts the intended tests compiled/executed and the acceptance condition is task-specific.
15. Restore `JAVA_HOME`/`PATH` in the guarded image rebuild itself and add an environment health preflight before starting the agent. Do not let agent behavior accidentally repair verifier infrastructure.

### P1 — Align task instructions with the measured construct

16. Remove the contradiction between “restrict changes to source” and “author the manifest bump.”
17. If stale visible tests are intentional, say so: post-upgrade behavior and dependency contracts outrank pre-upgrade assertions. Otherwise, make visible and hidden tests jointly satisfiable.
18. Report separate categories: clean dependency witness, oracle-direction/re-baselining trap, hidden-scaffolding-limited, fixture-entangled, infra-invalid, and non-witness/drive-by.

## Current state

Only this handoff note was added. Existing dirty worktree files and untracked run outputs were preserved.

| File | Change |
| --- | --- |
| `conversations/260713-test-harness-quality/131554-gpt-diagnosed-harness.md` | New comprehensive harness-quality analysis and next-step handoff |

No `HARNESS.md` variant-log entry was added because no harness setting or task was changed.

## Commands/evidence used

- Parsed `conversations/260713-half-pass-analysis/pass_matrix.csv` and confirmed 219 rows / 93 zero-pass.
- Joined it with `test_patch_reconciled_2026-06-26.csv`, `test_patch_agreement_2026-06-26.csv`, `test_patch_behavior_classification_2026-06-26_219.csv`, `v4_withtest219_nop_reverify37_20260629.csv`, and `task_summary.json`.
- Swept all `harbor_benchmark/reports/guarded_leak_*_artifacts_*/*/*/*/verifier/test-stdout.txt` logs: 405 total, 166 `JAVA_HOME` failures, zero hidden-patch apply failures.
- Inspected current task files under `harbor_benchmark/tasks_v4/<task>/{instruction.md,solution,tests}` for the deep dives and static hazard candidates.
- No network access and no new Harbor trial were needed for this diagnostic pass.

## Open tasks for the next agent

1. Fix the guarded image/environment rebuild so `JAVA_HOME=/opt/java/openjdk` and Java/Maven remain available independently of agent actions.
2. Reverify the 166 tainted trials, then regenerate the 219x10 matrix, zero-pass set, ecosystem tables, and model/harness rankings.
3. Run NOP across all 219 in a frozen snapshot and quarantine every unambiguously exploitable task pending manifest-enforcement fixes.
4. Dynamically adjudicate the 33 zero-pass non-witness candidates, starting with the 22 both-coder agreements and the tasks where `Dt` imports a `Dc`-only symbol.
5. Repackage nuts-node and actix before any context-mining or agent ablation uses them.
6. Audit the 49-task provisional residual with alternative repairs/mutations; focus first on the seven still-unresolved golden/snapshot cases and the mutually contradictory visible/hidden cases.
7. Reconcile `AGENTS.md` clean205 language with the checked-out 219-task branch before reporting a new headline. Do not mix the 205 and 219 denominators.

## Key decisions

| Decision | Rationale |
| --- | --- |
| Analyze current219, not silently switch to clean205 | The requested July 13 pass matrix and all 93-zero claims are 219-era; current checkout/HARNESS also contain 219. |
| Call 33 tasks candidate quarantine, not definitively delete all | The evidence is a reconciled static audit (22 both-coder, 11 adjudicated); dynamic three-state checks remain necessary for final corpus changes. |
| Call nuts-node definitively unsolvable | The hidden random key/DID is mathematically non-derivable under the permitted information regime and directly caused all graded failures. |
| Treat Maven-tainted tasks as invalid/unknown, not passes | Missing `JAVA_HOME` prevents testing solution correctness; flipping every affected zero would also be unjustified without replay. |
| Reject textual patch rigidity as the main diagnosis | Zero patch-application failures in 405 available logs; semantic oracle coupling and environment failures explain the evidence. |
| Keep the 49 residual tasks as an audit queue, not a benchmark | Absence of known flags is not evidence of broad repair equivalence. |

## Blockers

- Reverification requires a corrected guarded Docker environment and either replayable agent workspaces/edits or new guarded trials. Preserved artifacts contain logs and trajectories but not complete final workspaces for every tainted run.
- The current report does not dynamically prove the final status of all 33 candidate non-witness tasks or the 49 residual tasks; it identifies the prioritized verification queue.

## Suggested next step

Fix and smoke-test the guarded Maven environment on DSpace, arcadedb, wrongsecrets, and `dschadow__JavaSecurity__236`; then rerun/replay all 166 tainted cells before making any other pass-rate or “consensus-hard” claim.

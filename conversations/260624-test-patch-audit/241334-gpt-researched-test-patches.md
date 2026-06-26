# Handoff Note — 241334 · gpt · researched-test-patches

## Inherited context

Read the handoff skill and the required prior conversations:

- `conversations/2026-06-05-dataset-failure-analysis/`: oracle/verifier quality comes before agent pass rate; prior failures were mostly verifier false negatives, resource issues, or over-broad commands.
- `conversations/2026-06-06-breaking-change-definition/`: locked definition is witnessed Level 1 when `TEST(P ⊕ Δm ⊕ Δt)=FAIL` and `TEST(P ⊕ Δm ⊕ Δc ⊕ Δt)=PASS`; compile/build/runtime failures are valid if caused by the dependency upgrade, but lint/format/network/OOM/flaky failures are not.
- `conversations/260610-problematic-pr-review/`: 34 packaged tasks were previously identified as non-clean or boundary cases and should not be mixed into the main witnessed benchmark.
- Latest `260622-benchmark-runs` was not directly about test-patch quality, so a new thread was created for this task.

## Work done this session

- [x] Inspected `harbor_benchmark/tasks_v4/adoptoposs__mjml_nif__117/tests/test.patch`, `tests/test_state.py`, `environment/patches/manifest.patch`, `solution/code.patch`, `instruction.md`, and `task.toml`.
- [x] Confirmed the `adoptoposs__mjml_nif__117` hidden test patch updates invalid-MJML error expectations and adds `fonts` render-option tests.
- [x] Cross-checked against the existing static audit in `harbor_benchmark/reports/test_patch_quality_review_2026-06-18_cases/adoptoposs__mjml_nif__117.md`.
- [x] Scanned all current `tasks_v4` test patches: 257 task directories, all with nonempty `tests/test.patch`.
- [x] Compared current tasks with the June 18 full-297 audit: 205 current tasks are in that audit and all 205 are `WITNESSES_BREAKING_CHANGE`.
- [x] Identified 52 current tasks not covered by that audit; they came from the 2026-06-22 with-test import, are 51 Go + 1 Cargo, and were oracle-pass validated but not covered by the static test-patch quality audit.

## Current state

No benchmark task files were edited.

| File | Change |
| --- | --- |
| `conversations/260624-test-patch-audit/241334-gpt-researched-test-patches.md` | New handoff note for this exploration and plan |

Key local observations:

- `adoptoposs__mjml_nif__117` is a valid witnessed case, but the instruction/summary metadata is misleading: it says `version 1.1.0 -> 0.11.4`, while the substantive manifest bump is Rust `mrml` `1.2 -> 2.1`.
- `adoptoposs__mjml_nif__117` `Δt` is mixed: it includes direct compatibility checks for the upgraded `mrml` render API and user-visible feature assertions for `fonts`.
- Current `HARNESS.md` says the authoritative tree is 257 tasks, not the older AGENTS.md 297 count.
- Static scan of current 257 `test.patch` files: all paths look test-related; 132 patches add assertion-like lines; 101 both remove and add assertions; 30 include fixture/golden/snapshot-like paths.
- The 52 imported tasks have only oracle-pass evidence in `with_tests_v4_import_20260622.json`; 25 have blank library/version metadata and 20 have tiny patches of five changed lines or fewer, so they need a separate quality audit before claiming all 257 are witnessed Level 1.

## Open tasks for the next agent

1. Audit the 52 tasks listed in `harbor_benchmark/reports/with_tests_v4_import_20260622.json` using the same four-verdict schema as the June 18 audit.
2. For each of the 52, classify `Δt` as `WITNESSES_BREAKING_CHANGE`, `UNWITNESSED`, `TESTS_OTHER_THING`, or `INCONCLUSIVE`, and classify `Δc` nature.
3. For suspicious/tiny/blank-metadata cases, run targeted dynamic pre-code checks: apply `Δm + Δt` without `Δc` and confirm the failure is dependency-compatibility, not lint/format/flaky/resource/no-code-pass.
4. Update or generate a new report, ideally `harbor_benchmark/reports/test_patch_quality_review_2026-06-24_current257.*`, making clear that the June 18 report covers only 205 of the current 257 tasks.
5. Consider fixing misleading metadata for `adoptoposs__mjml_nif__117` and other rows where `library`, `old_version`, or `new_version` are blank or parsed incorrectly.

## Key decisions

| Decision | Rationale |
| --- | --- |
| Treat `adoptoposs__mjml_nif__117` as witnessed, not test-other | The patched tests require the `fonts` render-option path and the upgraded `mrml` API; the old Rust NIF source is incompatible with `mrml 2.1`. |
| Do not claim all 257 current tasks are clean yet | The existing static audit covers 205 current tasks; the 52 new imported tasks have oracle-pass evidence but lack the same test-patch semantic audit. |
| Separate “what `test.patch` asserts” from “what witness status proves” | Test patches can assert real compatibility, new product behavior, lint/format conformance, snapshots, or fixtures; only the fail/pass differential under the locked definition proves Level 1 witness status. |

## Blockers

- No blocker for the high-level answer.
- Full 52-task semantic audit was not completed in this session; only static corpus triage and representative target inspection were done.

## Suggested next step

Generate a current-257 audit report by carrying forward the 205 existing verdicts and manually/dynamically reviewing the 52 imported tasks from `with_tests_v4_import_20260622.json`.

---

## Addendum — Multi-Agent Open-Coding Audit of Test Oracles

User requested parallel subagents and a case-by-case report of what the test oracles are doing, with paper-facing taxonomy and quality debugging signals. Five subagents were spawned:

- Taxonomy synthesizer over the June 18 audit and prior handoff.
- Batch 1 explorer for 13 imported tasks: `BramVR__gohealthcli__351` through `giantswarm__cluster-cleaner__225`.
- Batch 2 explorer for 13 imported tasks: `giantswarm__logging-operator__453` through `matt-riley__hopcli__47`.
- Batch 3 explorer for 13 imported tasks: `naka-gawa__iq__69` through `syou6162__times_esa_mcp_server__43`.
- Batch 4 explorer for 13 imported tasks: `thegeeklab__url-parser__130` through `zekker6__external-dns-provider-adguard__64`.

All subagents performed static audit only: no Harbor runs, no file edits.

### Quantitative context

Current `tasks_v4` has 257 tasks. The existing June 18 full-297 audit found:

| Verdict | Count |
| --- | ---: |
| `WITNESSES_BREAKING_CHANGE` | 205 |
| `TESTS_OTHER_THING` | 59 |
| `UNWITNESSED` | 28 |
| `INCONCLUSIVE` | 5 |

Of the current 257 tasks, 205 are covered by the June 18 audit and all 205 are `WITNESSES_BREAKING_CHANGE`. The remaining 52 are from the 2026-06-22 with-test import and were oracle-pass validated (`52 pass / 7 fail / 0 exceptions`) but were not covered by the June 18 semantic test-patch audit.

### Open-coding taxonomy for paper use

| Category | Definition |
| --- | --- |
| Direct Compatibility Witness | `Δt` exercises a source path whose compile, type, runtime, or output behavior is broken by `Δm`, and `Δc` is needed for that same path to pass. Includes API migrations, import/symbol changes, changed error/output shapes, serialization changes, and valid type/build witnesses. |
| Compatibility-Accommodation Test Update | `Δt` updates mocks, fixtures, expected strings, snapshots, or test harness code so tests can run under the upgraded dependency. It is valid only when paired with a source-repair-discriminating assertion or build path. |
| Toolchain/Static Check Oracle | The oracle observes compiler/typechecker/test-runner behavior. Valid when the benchmark is about type/build compatibility; invalid for locked Level-1 benchmark when it is only lint, style, spelling, or formatter conformance. |
| Drive-By Product Behavior Oracle | `Δt` tests a real feature, policy change, security fix, default flip, or application bug fix bundled in the dependency PR, but not caused by the dependency upgrade. |
| Circular Implementation Oracle | `Δt` imports or asserts a helper, new symbol, exact constructor shape, fixture, or constant introduced by `Δc`; failure proves the oracle patch and source patch co-evolved, not that `Δm` broke existing behavior. |
| Test-Suite Maintenance Oracle | `Δt` mainly reformats tests, updates snapshots/testdata, removes focused tests, fixes flaky order, changes casts, relaxes assertions, or adapts framework syntax. Useful maintenance, weak or invalid as a dependency-break witness unless it still exposes a source break. |
| Dead or Mis-Scoped Oracle | `Δt` touches files not run by `test_cmd`, targets the wrong module/package, is skipped, uses `--passWithNoTests`/`--no-run`, or is erased at runtime, so it cannot observe the alleged repair. |
| No-Code-Pass / Latent Oracle | `P ⊕ Δm ⊕ Δt` likely already passes because the dependency itself changes the output, the test is skipped, `Δt` repairs the only failing test-side issue, or `Δc` is unreachable. |
| Confounded Oracle | Static evidence is insufficient because of vendoring, multiple independent break facets, unclear verifier behavior, typechecking ambiguity, or mixed patches where one facet is witnessed and another is not. |

### Mapping taxonomy to benchmark verdicts

| Verdict | Taxonomy mapping |
| --- | --- |
| `WITNESSES_BREAKING_CHANGE` | Direct Compatibility Witness. May include Compatibility-Accommodation Test Updates or mixed patches, but at least one load-bearing verifier path must fail on `P ⊕ Δm ⊕ Δt` for dependency-caused compile/type/runtime reasons and pass after `Δc`. |
| `UNWITNESSED` | No-Code-Pass / Latent Oracle, Dead or Mis-Scoped Oracle, or Test-Suite Maintenance Oracle where `Δc` is unnecessary, unreachable, erased, skipped, or not run. |
| `TESTS_OTHER_THING` | Drive-By Product Behavior Oracle, pure lint/format/static-style Toolchain Oracle, Circular Implementation Oracle, snapshot/docs/test-only/config-only oracle, or real fail/pass that is not causally tied to the dependency break. |
| `INCONCLUSIVE` | Confounded Oracle: plausible witness exists, but static review cannot establish the locked fail/pass causal chain without dynamic revalidation. |

### Quality-risk signals to debug in `test.patch`

- `test_cmd` is lint/format/spell/static-style only: `eslint`, `prettier`, `ruff check`, `lint`, `format:check`, `check-spell`.
- `Δt` only changes whitespace, trailing commas, casts, `@ts-expect-error`, snapshots, golden files, or expected strings with no source-path assertion.
- `Δt` imports a helper/module/symbol that exists only in `Δc`.
- New tests assert exact constants, default values, or public methods introduced by `Δc`, rather than exercising pre-existing behavior broken by `Δm`.
- Patched test files are not included in `test_cmd`, live in another module, or are excluded by selectors.
- Verifier uses `--passWithNoTests`, `--no-run`, narrow `-k`/`-run` filters, or tests that skip under `P ⊕ Δm`.
- Runtime runner strips type-only edits while the alleged break is typechecker-only.
- Assertions are relaxed or deleted rather than strengthened.
- Expected output is determined by the upgraded dependency alone, so `P ⊕ Δm` already matches.
- `Δc` is docs-only, test-only, snapshot-only, CI/config-only, or formatter churn.
- Metadata names the wrong dependency, a broad bundled upgrade, or a dependency not imported/touched by the oracle path.
- Failure would be missing fixture/helper/testdata rather than removed API, changed type, or changed runtime behavior.

### Suggested paper wording

> We performed a multi-perspective open-coding audit of hidden test oracles. The unit of analysis was a task-level hidden test patch, interpreted jointly with the manifest update, oracle code patch, and verifier command. Coders first identified what behavioral surface the hidden tests actually observe, then independently assessed whether that surface causally witnessed the dependency update under the locked Level-1 criterion: `TEST(P ⊕ Δm ⊕ Δt)=FAIL` and `TEST(P ⊕ Δm ⊕ Δc ⊕ Δt)=PASS`. Through iterative comparison, we induced categories for direct compatibility witnesses, test-suite accommodations, tooling/style oracles, drive-by product behavior, circular implementation tests, mis-scoped or dead tests, no-code-pass latent cases, and confounded cases requiring dynamic validation. Final verdicts distinguish tests that witness dependency-update breakage from tests that are useful maintenance artifacts but evaluate another property.

### Cross-batch synthesis for the 52 imported tasks

The imported 52 are mostly Go API/compile witnesses. A large share of `Δt` patches are not rich behavioral assertions; instead, they adapt tests to the new package path, new type shape, pointer/value change, context-aware CLI signature, or renamed method. Under the locked definition this is still acceptable when `P ⊕ Δm ⊕ Δt` fails to compile or typecheck without `Δc`, but the paper should label these as compile/API witnesses rather than behavior-regression witnesses.

Strong quality problems found:

| Task | Issue |
| --- | --- |
| `FollowTheProcess__build__17` | `Δt` only fixes test imports; `Δc` appears unrelated to the verifier surface and mostly changes metadata/templates. Likely no-code-pass or test-side-only break. |
| `github__github-mcp-server__412` | `Δc` only updates third-party license docs; likely `Δm + Δt` passes without source repair. |
| `stackitcloud__gardener-extension-shoot-flux__180` | `Δt` only raises a Ginkgo timeout; `Δc` updates default Flux version strings. This is timing/default maintenance, not a breaking API repair. |
| `suzuki-shunsuke__tfprovidercheck__629` | `Δt` is comment-only; verifier likely relies on existing tests/build, so hidden test patch itself adds no oracle signal. |
| `ubugeeei-prod__ox-content__131` | Hidden `Δt` is a TypeScript test, but `test_state.py` runs `cargo test`; Rust test expectation changes appear misclassified into `solution/code.patch`. Grouped multi-dep attribution and relaxed assertion make this a severe quality issue. |

Weak or caveated but potentially valid:

| Task | Concern |
| --- | --- |
| `nobl9__sloctl__448` | `Δt` deletes an already skipped interactive config test and fixture; witness may be production/test compile, but test patch mainly removes incompatible test code. |
| `giantswarm__muster__751` | `Δt` tests `k8sSASubPattern`, a new helper introduced by `Δc`; circular-helper risk. |
| `go-vela__vela-docker__118` | Coherent CLI v3 migration, but `Δc` has CI/workflow/Dockerfile/version/lint drive-by churn and verifier is broad. |
| `kairos-io__provider-kairos__869` | `Δt` mixes API adaptation with a new behavior assertion about comment/key-order preservation. |
| `chinmina__chinmina-bridge__101` | Valid otter v2 API repair, but `Δt` partly relaxes/removes old behavior rather than asserting the repaired behavior. |
| `suzuki-shunsuke__tfprovidercheck__629` | Real CLI v3 production repair, but hidden test patch is substantively empty; dynamic witness may come only from existing tests. |

Systematic metadata issues:

- Many imported Go rows have blank `library`, `old_version`, or `new_version` in `task_summary.json`.
- Some rows identify an indirect dependency rather than the true breaking dependency, e.g. `emmahsax__go-git-helper__108` names `go-querystring` although the real source repair is `go-github/v74 -> v84`.
- Instructions in several imported tasks reportedly say upstream had no test changes despite nonempty `tests/test.patch`.
- Several valid cases are grouped bumps; true causal dependency is recoverable from manifest/code/test diffs but not cleanly from generated metadata.

### Case-by-case report — 52 imported tasks

| Folder | Bump / true dependency | What `Δt` does | What `Δc` fixes | Oracle relation / taxonomy | Quality concerns | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| `BramVR__gohealthcli__351` | `modernc.org/sqlite 1.35.0 -> 1.52.0` | Adds/updates DB view tests for stable float-as-text output and schema migration `24`. | Reworks SQL view formatting with explicit `printf`, adds migration to recreate affected views. | `WITNESSES_BREAKING_CHANGE`; runtime/output compatibility witness. | Minor unrelated test guard `return`s, but substantive `Δt` matches `Δc`. | High |
| `FollowTheProcess__build__17` | `snapshot/test/hue` moved from `github.com/FollowTheProcess/*` to `go.followtheprocess.codes/*`; `snapshot 0.5.0 -> 0.6.0`. | Updates only `build_test.go` imports. | No production repair; deletes repo metadata/templates, tweaks Renovate label, fixes `go mody tidy` typo. | `UNWITNESSED/no-code-pass`, test-side-only break, `TESTS_OTHER_THING` in `Δc`. | Bad oracle: `Δc` appears unrelated to verifier command; likely passes with `Δm + Δt` alone. | High |
| `FollowTheProcess__txtract__33` | True bump: `cli 0.13.0 -> go.followtheprocess.codes/cli 0.14.0`, `test 0.21.0 -> go.followtheprocess.codes/test 0.22.0`. | Updates test helper import path. | Updates production `cli` imports to vanity module path. | Likely `WITNESSES_BREAKING_CHANGE` via compile/import path. | `metadata_misparsed` blank summary; import-path-only witness, static proof not dynamic. | Med-high |
| `GoogleCloudPlatform__cloud-foundation-toolkit__2670` | `github.com/google/go-github/v66 -> v67` plus CLI deps. | Updates test imports to `v67`. | Updates bpcatalog production imports to `v67`; Makefile version bump. | `WITNESSES_BREAKING_CHANGE`; compile/API import witness. | Small unrelated release-version noise in `Δc`. | High |
| `GoogleCloudPlatform__cloud-foundation-toolkit__2762` | `github.com/google/go-github/v67 -> v68` plus CLI deps. | Updates imports to `v68` and `github.String/Int/Bool` to `github.Ptr`. | Updates bpcatalog production imports to `v68`; Makefile version bump. | `WITNESSES_BREAKING_CHANGE`; compile/API type witness. | Small unrelated release-version noise in `Δc`. | High |
| `Nextdoor__vigil__35` | Kubernetes packages `0.33.10 -> 0.35.3`. | Updates helper test call to pass `logr.Discard()`. | Adapts `FindMatchingUntoleratedTaint` call/signature with logger and new bool arg. | `WITNESSES_BREAKING_CHANGE`; signature compatibility witness. | None material. | High |
| `cert-manager__cert-manager__8551` | `AkamaiOPEN-edgegrid-golang/v12 -> v13`. | Updates imports and expected TTL fields to pointers. | Updates imports and converts TTL values to/from pointers. | `WITNESSES_BREAKING_CHANGE`; API/type witness. | License file noise, but source/test relation is clean. | High |
| `chinmina__chinmina-bridge__101` | True bump: `github.com/maypok86/otter v1.2.2 -> /v2 v2.2.0`. | Removes negative cache setup error test; adds `NoError` where cache is constructed. | Rewrites cache code for otter v2 APIs: `Options`, `Must`, stats, `GetEntry`, `Invalidate`. | `WITNESSES_BREAKING_CHANGE`, but weak `Δt`. | `metadata_misparsed` blank summary; `Δt` partly relaxes/removes old behavior rather than asserting repaired behavior. | Med-high |
| `chinmina__chinmina-bridge__99` | `go-buildkite/v3 3.13.0 -> v4 4.4.0`. | Updates test imports and mock `Pipeline` fields from pointers to values. | Adapts Buildkite client API: context arg, auth options, string repo field. | `WITNESSES_BREAKING_CHANGE`; API/type witness. | None material. | High |
| `crossplane-contrib__function-extra-resources__66` | True bump: `function-sdk-go rc -> 0.5.0`, `crossplane-runtime -> /v2 2.1.0`. | Updates tests from `ExtraResources`/`resource.Extra` to `RequiredResources`/`resource.Required` and runtime/v2 imports. | Updates production imports and SDK field/type names. | `WITNESSES_BREAKING_CHANGE`; SDK schema/API witness. | `metadata_misparsed` blank summary; CI workflow noise in `Δc`. | High |
| `crossplane-contrib__function-patch-and-transform__315` | `function-sdk-go 0.6.2 -> 0.7.0`, `crossplane-runtime/v2 2.2.0 -> 2.3.0`, adds `crossplane/apis/v2`. | Updates tests to `xpv2` secret references and conditions. | Moves source to `crossplane/apis/v2` types and `fieldpath.MergeOptions`; updates generated artifacts. | `WITNESSES_BREAKING_CHANGE`; SDK/API witness. | Some workflow/generated-file noise, but core relation is valid. | High |
| `emmahsax__go-git-helper__108` | True primary bump: `go-github/v74 -> v84`; summary says indirect `go-querystring 1.1.0 -> 1.2.0`. | Updates GitHub test import to `v84`. | Updates production GitHub imports to `v84`; also version/workflow refactor. | Likely `WITNESSES_BREAKING_CHANGE`; import/API witness. | `metadata_misparsed`; `Δc` includes unrelated workflow/version changes. | Med-high |
| `giantswarm__cluster-cleaner__225` | `sigs.k8s.io/cluster-api 1.10.4 -> 1.11.0`. | Updates test import from `api/v1beta1` to `api/core/v1beta2`. | Updates production imports to Cluster API `core/v1beta2`. | `WITNESSES_BREAKING_CHANGE`; compile/API import break. | None material. | High |
| `giantswarm__logging-operator__453` | `sigs.k8s.io/cluster-api v1.10.4 -> v1.11.3`. | Updates one test import from `api/v1beta1` to `api/core/v1beta1`. | Updates many production CAPI imports to new path. | `WITNESSES_BREAKING_CHANGE`; compile/API import break. | Test is only test-side import adaptation; no new behavioral assertion. | High |
| `giantswarm__mcp-prometheus__165` | `github.com/giantswarm/mcp-oauth v0.2.150 -> v0.2.173`. | Updates tests for new `newStore` / `newValkeyStore` signatures with encryptor arg. | Moves encryptor from server option to memory/valkey storage options. | `WITNESSES_BREAKING_CHANGE`; likely source API break plus test adaptation. | `Δt` mostly follows `Δc` internal signature; weak behavioral oracle. | High |
| `giantswarm__muster__751` | `github.com/giantswarm/mcp-oauth v0.2.162 -> v0.2.184`. | Adds tests for `k8sSASubPattern`. | Migrates K8s SA trust config to `TrustedIssuer`/`AllowedClaims`; valkey DPoP import moved. | `WITNESSES_BREAKING_CHANGE_WITH_CONCERNS`. | Circular new helper introduced by `Δc`; `Δt` tests repair helper more than pre-existing behavior. | Medium |
| `giantswarm__observability-operator__500` | `sigs.k8s.io/cluster-api v1.10.4 -> v1.11.3`. | Updates test imports to `api/core/v1beta1` and CRD URL tag to `v1.11.3`. | Updates production CAPI imports. | `WITNESSES_BREAKING_CHANGE`; compile/API import break. | Test-side-only adaptation, plus verifier fetches remote CRD URL. | High |
| `giantswarm__upgrade-schedule-operator__267` | `sigs.k8s.io/cluster-api v1.10.4 -> v1.11.0`. | Updates one test import to `api/core/v1beta2`. | Updates production imports to same new CAPI path. | `WITNESSES_BREAKING_CHANGE`; compile/API import break. | Minimal `Δt`; compile-only signal. | High |
| `github__github-mcp-server__412` | `github.com/mark3labs/mcp-go v0.27.0 -> v0.28.0`. | Updates test helper/request structs to `mcp.Meta` and `map[string]any`. | Only updates third-party license docs from `v0.27.0` to `v0.28.0`. | `UNWITNESSED / test-side-only break / no-code-pass`. | `Δc` is not production repair and is not exercised by `go test`; likely `Δm + Δt` passes without `Δc`. | High |
| `go-fries__fries__1076` | `github.com/bufbuild/protovalidate-go v0.10.0 -> buf.build/go/protovalidate v0.11.0`. | Updates test import to new module path. | Updates production import to new module path. | `WITNESSES_BREAKING_CHANGE`; module-path compile break. | Pure compile/import migration; no behavior assertion. | High |
| `go-vela__vela-docker__118` | Mainly `github.com/urfave/cli/v2 -> github.com/urfave/cli/v3`, plus Go/version/deps. | Updates tests for `context.Context` plumbing and `exec.CommandContext`. | Migrates CLI v3 API, value sources, command signatures, context-aware exec/login/build/push. | `WITNESSES_BREAKING_CHANGE_WITH_CONCERNS`. | `Δc` contaminated with CI workflow pins, Dockerfile/version/lint config drive-bys; verifier is broad. | Medium |
| `k4ji__tracesimulationreceiver__23` | OTel Collector `1.32/0.126 -> 1.33/0.127`; semconv moved. | Updates test semconv import and `ServiceNameKey` access. | Updates production semconv import and service-name attribute key. | `WITNESSES_BREAKING_CHANGE`; removed/moved semconv API. | Mostly compile/API adaptation, little behavioral novelty. | High |
| `k8s-gateway__k8s_gateway__98` | `sigs.k8s.io/external-dns v0.17.0 -> v0.18.0`. | Changes tests to `external-dns/apis/v1alpha1` DNSEndpoint types. | Changes production informer/index code to new DNSEndpoint package. | `WITNESSES_BREAKING_CHANGE`; type/package move. | Test-side type adaptation only. | High |
| `kairos-io__provider-kairos__869` | `kairos-agent/v2 2.25.5 -> 2.29.0`, `kairos-sdk 0.13.0 -> 0.20.0`. | Reworks config token tests away from removed config helpers; adds preservation of comments/order. | Moves config/logger imports to SDK packages; replaces agent config parsing with `yaml.v3` nodes. | `WITNESSES_BREAKING_CHANGE_WITH_CONCERNS`. | `Δt` mixes API adaptation with new behavioral assertion about comment/key-order preservation. | Medium |
| `magcho__tmux-overview__8` | Charm Bubble Tea/Lipgloss v1 modules -> `charm.land/*/v2`. | Updates test to read `m.View().Content`. | Migrates imports; `View()` now returns `tea.View` with `AltScreen`. | `WITNESSES_BREAKING_CHANGE`; major API change. | Clean, but compile-focused. | High |
| `matt-riley__hopcli__47` | Charm `bubbles/bubbletea/lipgloss` -> `charm.land/*/v2`. | Updates tests for v2 imports, `KeyPressMsg`, and `View().Content`. | Migrates production imports, key handling, `View() tea.View`, `AltScreen`. | `WITNESSES_BREAKING_CHANGE`; major API change. | Good relation; broad but coherent test-side API adaptation. | High |
| `naka-gawa__iq__69` | `charmbracelet/bubbles` + `bubbletea` v1 -> `charm.land/*/v2`. | Updates tests to Bubble Tea v2 imports/events and `View().Content`; tweaks invalid-expression expectation. | Migrates imports, `KeyMsg` -> `KeyPressMsg`, `View() string` -> `tea.View`, moves alt-screen onto view. | Mostly valid witnessed compile/API break. | Blank metadata; small extra assertion change not clearly dependency-required. | High |
| `nobl9__sloctl__448` | `github.com/charmbracelet/huh v0.8 -> charm.land/huh/v2`. | Deletes an already skipped interactive config test and fixture; leaves only `TestMaskField`. | Migrates huh/lipgloss imports and theme API. | Weak witness via production/test compile, but `Δt` mainly removes incompatible test code. | Test-side-only break, coverage deletion, fixture deletion, metadata blank. | High |
| `openmcp-project__mcp-operator__186` | `service-provider-landscaper v0.7.0 -> v0.10.0`. | Updates test import from `api/v1alpha1` to `api/v1alpha2`. | Updates production import to same new API version. | Clean test-adaptation witness for dependency API move. | `Δt` is import-only, so witness is compile-level. | High |
| `openmcp-project__mcp-operator__215` | `openmcp-operator/lib v0.15.2 -> v0.17.0`. | Updates test fixture `SecretRef` from `ObjectReference{Name, Namespace}` to `LocalObjectReference{Name}`. | Reads namespace from `ar.Namespace` because `SecretRef` no longer carries it. | Clean API/behavior adaptation. | Metadata library is imprecise (`api/lib`). | High |
| `sacloud__terraform-provider-sakura__246` | sacloud group, especially `saclient-go v0.3.7 -> v0.4.0`. | Updates test setup for `NewProfileOp` now returning `(op, err)`. | Handles new `(op, err)` return in production config loading. | Clean dependency API witness. | Grouped dependency bump, but causal API is clear. | High |
| `score-spec__score-aca__16` | `score-go v1.9.6 -> v1.10.0`. | Rewrites `ContainerFiles` tests from slice/`Target` form to map keyed by target; adds related cases. | Converts production logic from `[]ContainerFilesElem` to `map[string]ContainerFile`; error keys become target paths. | Valid witnessed schema/API change. | `Δt` includes expanded coverage beyond type migration; mostly related. | High |
| `shuntaka9576__gh-kanban__16` | Bubble Tea/Lipgloss v1 -> `charm.land/*/v2`; Kong also bumped. | Updates tests for new imports and `View().Content`. | Migrates imports, `View() tea.View`, moves alt-screen onto view. | Valid compile/API witness. | Grouped bump; metadata blank. | High |
| `smykla-skalski__gh-renovate-helper__4` | `bubbles`, `bubbletea`, `lipgloss` v1 -> `charm.land/*/v2`. | Updates TUI tests from `KeyMsg` to `KeyPressMsg`. | Broad Bubble Tea v2 migration: imports, `View() tea.View`, focus command, window title/alt-screen/mouse mode on view. | Valid compile/API witness. | Metadata blank; `Δc` broad but coherent with Bubble Tea v2. | High |
| `stackitcloud__gardener-extension-shoot-flux__180` | Flux components `2.6.x -> 2.7.x`. | Only raises Ginkgo default eventually timeout from 3s to 5s. | Updates default Flux version strings in source/docs/example from v2.6.4 to v2.7.0. | Poor oracle relation: `TESTS_OTHER_THING` / likely `UNWITNESSED`. | Timing-only `Δt`; `Δc` is version/default update, not breaking API repair. Strong quarantine candidate. | High |
| `stackitcloud__stackit-cert-manager-webhook__94` | `stackit-sdk-go/services/dns v0.13.1 -> v0.17.0`, plus non-major deps. | Updates test fixture field from `*string` to generated typed enum wrapper. | Wraps DNS record type strings with generated typed attribute constructors. | Valid SDK API witness. | `Δc` is overbroad: workflows, linter config, Makefile also changed; grouped deps. | High |
| `suzuki-shunsuke__tfprovidercheck__629` | `urfave/cli/v2 v2.27.6 -> cli/v3 v3.1.0`. | Comment-only change in test: `app.RunContext` -> `app.Run`. | Migrates production CLI API: `App` -> `Command`, help template name, `Run`, action signature/context. | Real production API repair, but `Δt` is substantively empty; not an ideal `Δt` witness. | Comment-only hidden test patch adds no oracle signal; relies on existing tests/build. | High |
| `syou6162__times_esa_mcp_server__22` | `mark3labs/mcp-go v0.28.0 -> v0.30.0`. | Updates expected error text for missing/non-string `text`. | Uses new `request.RequireString("text")` helper and wraps its error. | Likely valid API/runtime adaptation. | `Δt` narrow and partly coupled to `Δc` new error wording; possible circular expectation. | Medium-high |
| `syou6162__times_esa_mcp_server__43` | `modelcontextprotocol/go-sdk v0.2.0 -> v1.0.0`. | Rewrites tests from generic `CallToolParamsFor[...]` wrappers to typed request structs. | Migrates handler signature/result types, transport, and jsonschema import. | Valid major API migration witness, mostly compile-level. | Tests exercise helper path more than public handler; still compile-checks handler/main. | High |
| `thegeeklab__url-parser__130` | `urfave/cli/v2 2.27.6 -> cli/v3 3.2.0`. | Updates tests to `cli/v3`, `*cli.Command`, `t.Context()` calls. | Migrates CLI app/actions/flags to `cli/v3`; adds context-aware `Run/Before/Action`. | Likely witnessed via Go compile/API break; `Δt` is test-side API adaptation. | `task_summary` blank; minor `Δc` lint config change. | High |
| `thegeeklab__wp-ansible__192` | `wp-plugin-go/v4 4.1.2 -> v6.0.0`, `cli/v2 -> cli/v3`. | Replaces test `cli.StringSlice` values with `[]string`. | Migrates imports to `wp-plugin-go/v6`; replaces `cli.StringSlice` fields and `.Value()` use. | Likely witnessed compile/API break. | Metadata only names `wp-plugin-go`, omits direct `cli` bump. | High |
| `thegeeklab__wp-docker-buildx__349` | `wp-plugin-go/v4 -> v6`, `cli/v2 -> v3`. | Adds CLI v3 test helper; adapts string-slice test fixtures and imports. | Migrates plugin/docker settings to slices, `Sources`, v6 helper flags, v3 CLI. | Likely witnessed compile/API break. | Metadata blank; `Δt` mostly harness adaptation. | High |
| `thegeeklab__wp-matrix__222` | `wp-plugin-go/v4 -> v6`, `cli/v2 -> v3`. | Test import changes `wp-plugin-go/v4/plugin` to `v6/plugin`. | Migrates production imports and flag `EnvVars` to `Sources`. | Likely witnessed compile/API break. | Thin `Δt`, compile-only. | High |
| `thegeeklab__wp-opentofu__166` | `wp-plugin-go/v4 -> v6`, `cli/v2 -> v3`. | Updates plugin test runner to context/v3; replaces `cli.StringSlice` targets with `[]string`. | Migrates plugin context access, action/targets slices, imports to v6/v3. | Likely witnessed compile/API break. | Metadata blank; small copy-paste oddity in test helper name, likely harmless. | Med-high |
| `thegeeklab__wp-plugin-go__148` | `urfave/cli/v2 2.27.6 -> cli/v3 3.1.1`. | Updates docs/commit tests to `cli.Command`, context action, v3 flag shapes. | Migrates library API from `cli.App/Context` to `cli.Command`; updates flags, metadata, logging, generic flag getters. | Strong witnessed API migration. | Metadata blank; broad library-internal API surface but coherent. | High |
| `ubugeeei-prod__ox-content__131` | Grouped Cargo bump: `oxc_* 0.44 -> 0.131`, `askama 0.12 -> 0.16`, `logos`, `sha2`, `criterion`, etc. | Changes a TS SSG test to assert title has no raw `<`/`>` instead of exact `&lt;...&gt;`. | Adapts Rust OXC AST visitor APIs, `logos`, `sha2`, `criterion`; also changes Rust unit-test expectations inside `src/html.rs`. | Inconclusive/problematic: production likely breaks, but `Δt` appears not exercised by verifier. | Verifier runs `cargo test`, while `Δt` is an npm TS test; Rust test hunk is misclassified into `Δc`; grouped multi-dep attribution; relaxed assertion. | Low |
| `windsorcli__cli__1232` | `compose-go v1.20.2 -> compose-go/v2 v2.6.4`. | Updates tests from service slice indexing to `types.Services` map lookups. | Migrates imports to `/v2/types`; builds compose service maps keyed by name. | Strong witnessed API/data-shape break. | Metadata blank, but instruction/manifest clear. | High |
| `wndhydrnt__saturn-bot__223` | `gitlab-org/api/client-go 0.116.0 -> 0.134.0`. | Replaces test MR fixtures with `BasicMergeRequest`. | Changes raw MR handling from `MergeRequest` to `BasicMergeRequest`, including conversions after API calls. | Strong witnessed GitLab API type break. | Metadata blank. | High |
| `xMoelletschi__renoglaab__30` | `gitlab-org/api/client-go 0.161.1 -> 1.2.0`. | Updates mock/client test IDs from `int` to `int64`. | Changes GitLab MR/pipeline IDs and interfaces from `int` to `int64`. | Strong witnessed type/API break. | None material. | High |
| `youkoulayley__glint-vm__7` | `urfave/cli/v2 2.27.7 -> cli/v3 3.6.2`. | Updates tests to `cli.Command`, `context.Background`, v3 `Run` calls. | Migrates commands/actions to context-aware `cli/v3`; propagates context into downloader requests. | Strong witnessed CLI API break. | Metadata blank. | High |
| `yutachaos__kube-job-notifier__236` | `slack-go/slack 0.16.0 -> 0.21.1`. | Updates mock method/param from `UploadFileV2*` to `UploadFile*`. | Migrates Slack upload interface and call site to new method/parameter type. | Strong witnessed API rename break. | Very small `Δt`, but directly tied to mocked interface. | High |
| `zekker6__external-dns-provider-adguard__64` | `external-dns 0.17.0 -> 0.18.0`. | Updates test field type from `endpoint.DomainFilter` to `*endpoint.DomainFilter`. | Changes provider field/init to pointer domain filter. | Strong witnessed type break. | `Δc` includes README/docs churn alongside source fix. | High |

### Current recommended labels for the 52-task import

Use these as provisional static labels until dynamic pre-code witness checks are run:

| Label | Tasks |
| --- | --- |
| Clean or likely clean compile/API witness | `BramVR__gohealthcli__351`, `FollowTheProcess__txtract__33`, `GoogleCloudPlatform__cloud-foundation-toolkit__2670`, `GoogleCloudPlatform__cloud-foundation-toolkit__2762`, `Nextdoor__vigil__35`, `cert-manager__cert-manager__8551`, `chinmina__chinmina-bridge__99`, `crossplane-contrib__function-extra-resources__66`, `crossplane-contrib__function-patch-and-transform__315`, `emmahsax__go-git-helper__108`, `giantswarm__cluster-cleaner__225`, `giantswarm__logging-operator__453`, `giantswarm__mcp-prometheus__165`, `giantswarm__observability-operator__500`, `giantswarm__upgrade-schedule-operator__267`, `go-fries__fries__1076`, `k4ji__tracesimulationreceiver__23`, `k8s-gateway__k8s_gateway__98`, `magcho__tmux-overview__8`, `matt-riley__hopcli__47`, `naka-gawa__iq__69`, `openmcp-project__mcp-operator__186`, `openmcp-project__mcp-operator__215`, `sacloud__terraform-provider-sakura__246`, `score-spec__score-aca__16`, `shuntaka9576__gh-kanban__16`, `smykla-skalski__gh-renovate-helper__4`, `stackitcloud__stackit-cert-manager-webhook__94`, `syou6162__times_esa_mcp_server__43`, `thegeeklab__url-parser__130`, `thegeeklab__wp-ansible__192`, `thegeeklab__wp-docker-buildx__349`, `thegeeklab__wp-matrix__222`, `thegeeklab__wp-opentofu__166`, `thegeeklab__wp-plugin-go__148`, `windsorcli__cli__1232`, `wndhydrnt__saturn-bot__223`, `xMoelletschi__renoglaab__30`, `youkoulayley__glint-vm__7`, `yutachaos__kube-job-notifier__236`, `zekker6__external-dns-provider-adguard__64` |
| Likely witness but caveated / weak behavioral signal | `chinmina__chinmina-bridge__101`, `giantswarm__muster__751`, `go-vela__vela-docker__118`, `kairos-io__provider-kairos__869`, `nobl9__sloctl__448`, `syou6162__times_esa_mcp_server__22` |
| Quarantine or dynamic revalidation priority | `FollowTheProcess__build__17`, `github__github-mcp-server__412`, `stackitcloud__gardener-extension-shoot-flux__180`, `suzuki-shunsuke__tfprovidercheck__629`, `ubugeeei-prod__ox-content__131` |

### Updated open tasks

1. Run dynamic pre-code witness checks for the five quarantine/revalidation-priority tasks:
   `FollowTheProcess__build__17`, `github__github-mcp-server__412`, `stackitcloud__gardener-extension-shoot-flux__180`, `suzuki-shunsuke__tfprovidercheck__629`, `ubugeeei-prod__ox-content__131`.
2. For the six caveated tasks, run dynamic checks if the paper needs a strict current-257 headline; otherwise label them as weak compile/API witnesses.
3. Fix or annotate metadata for imported Go tasks with blank/misparsed dependencies.
4. Generate `harbor_benchmark/reports/test_patch_quality_review_2026-06-24_current257.md` and `.csv` by combining:
   - June 18 verdicts for the 205 retained tasks.
   - This static 52-task import audit.
   - Dynamic witness results for any quarantined/caveated rows.

---

## Addendum — Design Evaluation Against Stronger Three-State Expectation

User clarified the expected benchmark design:

1. Original tests should fail after the dependency bump without code repair: `TEST(P ⊕ Δm)=FAIL`.
2. Patched tests should still fail without code repair: `TEST(P ⊕ Δm ⊕ Δt)=FAIL`.
3. Patched tests should pass after oracle code repair: `TEST(P ⊕ Δm ⊕ Δc ⊕ Δt)=PASS`.

This is stronger than the locked Level-1 definition recorded in `AGENTS.md` and `conversations/2026-06-06-breaking-change-definition`, which requires only:

```text
TEST(P ⊕ Δm ⊕ Δt)=FAIL
AND
TEST(P ⊕ Δm ⊕ Δc ⊕ Δt)=PASS
```

The stronger three-state design is desirable when available because it proves the original upstream test suite already witnessed the dependency break and `Δt` is not manufacturing an artificial failure. However, it may exclude legitimate dependency-repair PRs where the old tests were weak and the human added `Δt` specifically to expose the broken behavior. For the paper, a useful framing is:

| Evidence tier | Required checks | Interpretation |
| --- | --- | --- |
| Tier A+ original-suite witnessed | `TEST(P⊕Δm)=FAIL`, `TEST(P⊕Δm⊕Δt)=FAIL`, `TEST(P⊕Δm⊕Δc⊕Δt)=PASS` | Strongest evidence. Original tests and patched tests both observe the break. |
| Tier A hidden-suite witnessed | `TEST(P⊕Δm⊕Δt)=FAIL`, `TEST(P⊕Δm⊕Δc⊕Δt)=PASS`; `TEST(P⊕Δm)` unknown or pass | Valid under current locked definition. `Δt` adds sensitivity or adapts tests to new API. |
| Tier B latent / no-code-pass | `TEST(P⊕Δm⊕Δt)=PASS` with `Δc≠∅` | Code repair exists, but tests do not distinguish repaired from unrepaired states. Exclude from main benchmark. |
| Bad oracle / tests other thing | Failure is lint/format/flaky/network/resource/test-only/circular-helper/drive-by behavior, or `Δc` is docs/config/test-only | Exclude or quarantine; not dependency-breaking-change repair evidence. |

### Current problematic-count estimate

Use `HARNESS.md` as source of truth over `AGENTS.md`: current `tasks_v4` is 257 tasks. Static evidence currently supports:

| Set | Count | Meaning |
| --- | ---: | --- |
| Existing June 18 retained set | 205 | All are statically classified as `WITNESSES_BREAKING_CHANGE` under the locked two-check Level-1 definition. |
| New 2026-06-22 import | 52 | Oracle-pass validated but only statically audited in this session. |
| Clearly problematic among new import | 5 / 52 | Strong quarantine or dynamic-revalidation priority. |
| Caveated / weak among new import | 6 / 52 | Likely valid compile/API witnesses but with circular-helper, deletion-only, broad verifier, or weak behavioral signal concerns. |
| Clean or likely clean among new import | 41 / 52 | Mostly Go compile/API migration witnesses. |

Therefore, for the current 257-task tree:

| Counting rule | Problematic count | Share of current 257 |
| --- | ---: | ---: |
| Strict clear-problem count | 5 | 1.9% |
| Conservative count including caveated tasks | 11 | 4.3% |

If reporting the historical full-297 audit instead, the prior static audit found 92 non-clean cases (`59 TESTS_OTHER_THING + 28 UNWITNESSED + 5 INCONCLUSIVE`), i.e. 31.0% of the unpruned packaged snapshot. That historical number should not be mixed with the current 257 denominator.

### What this means for the design

- The harness architecture is sound for hidden-oracle evaluation: agent sees dependency-upgrade context, verifier overlays fixed `test.patch`, and oracle validates `Δm + Δc + Δt` pass.
- The main remaining risk is semantic, not harness mechanics: some `test.patch` files are test-side accommodations, import-path adaptations, or weak compile witnesses rather than behavioral assertions.
- Compile/API witnesses should be kept but labeled. In Go/Cargo/Maven/TypeScript ecosystems, compile failure from removed modules, moved packages, changed method signatures, or type-shape changes is a legitimate breaking-change signal.
- Original-suite failure `TEST(P⊕Δm)=FAIL` is worth adding as an optional stronger tag (`original_suite_witnessed=true/false/unknown`) rather than making it mandatory, because some human repairs add tests precisely because the old suite was not sensitive enough.
- The five clear-problem tasks should be quarantined unless dynamic checks prove otherwise:
  `FollowTheProcess__build__17`, `github__github-mcp-server__412`, `stackitcloud__gardener-extension-shoot-flux__180`, `suzuki-shunsuke__tfprovidercheck__629`, `ubugeeei-prod__ox-content__131`.
- The six caveated tasks should be labeled or dynamically checked before using a strict “all 257 are witnessed” paper claim:
  `chinmina__chinmina-bridge__101`, `giantswarm__muster__751`, `go-vela__vela-docker__118`, `kairos-io__provider-kairos__869`, `nobl9__sloctl__448`, `syou6162__times_esa_mcp_server__22`.

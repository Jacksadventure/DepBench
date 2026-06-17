# Test-Patch Quality Audit — 2026-06-17

**Scope:** Stratified sample of 65 tasks (34 flagged `no_code_pass` rows from `problematic_prs_review_2026-06-10.md` + 31 random non-flagged draws proportional by ecosystem).  
**Method:** Static expert review of `εm` (manifest), `εc` (code/solution), `εt` (test), and `test_cmd` for each task.  
**Per-case details:** `test_patch_quality_review_2026-06-17_cases/<folder>.md` (65 files).

---

## 1. Executive Summary

Of 65 sampled tasks, **27 (42%) actually witness the dependency breaking change**, 26 (40%) are unwitnessed, 8 (12%) test something other than the breaking change (lint, drive-by feature, snapshot-only), and 4 (6%) are inconclusive from static analysis.

| Verdict | Count | % |
|---|---|---:|
| `WITNESSES_BREAKING_CHANGE` | 27 | 41.5% |
| `UNWITNESSED` | 26 | 40.0% |
| `TESTS_OTHER_THING` | 8 | 12.3% |
| `INCONCLUSIVE` | 4 | 6.2% |

**Among the 34 previously flagged `no_code_pass` rows, our independent audit confirms 32/34 (94%)** as unwitnessed or testing-other. The prior audit is validated. Only 2 flagged tasks (`jamcalli__Pulsarr__1107`, `verdaccio__verdaccio__5742`) actually DO witness the breaking change — both via narrow import-resolution gates (removed `dotenv`/`lodash` → module fails to load), and both carry caveats (drive-by file, bundled multi-dep upgrade).

**Among the 31 random (non-flagged) sample, 25 (81%) are witnessed and 6 (19%) have a soundness problem the prior audit missed**, including lint-only verifiers, drive-by feature tests on misattributed dependency bumps, a circular oracle, and a task fundamentally unpassable by an agent because the solution edits test files the agent cannot touch.

### Ecosystem asymmetry

| Ecosystem | Sampled | Witnessed | Soundness issues |
|---|---|---|:---:|---|
| Cargo | 2 | 2 | 0 |
| Go | 6 | 4 | 2 (1 test-other, 1 unwitnessed) |
| Maven | 8 | 7 | 1 (circular oracle) |
| npm/yarn | 45 | 12 | 33 (23 unwitnessed, 6 test-other, 4 inconclusive) |
| pip | 4 | 2 | 2 (both unwitnessed) |

**npm/yarn dominates the soundness gap** — 73% of sampled npm/yarn tasks (33/45) do not witness the stated breaking change. Cargo and Maven are essentially clean. Go has one hard defect and one unwitnessed. Pip is mixed.

---

## 2. Methodology

Each task was analyzed via its bundle (`instruction.md` + `manifest.patch` + `code.patch` + `test.patch` + `test_cmd`). For each task we answered:

1. **What is the breaking change?** Concrete, from `Δc` and `Δt`.
2. **What does `Δt` actually do?** Files touched, categories of test change.
3. **Does `Δt` directly exercise the breaking change?** Representative assertion / test that plausibly fails on `P⊕Δm` and passes on `P⊕Δm⊕Δc`.
4. **Coverage verdict** (one of four, below).
5. **`Δc` nature** (dominant category: real source repair / test-only / docs / snapshot / config / vendor / formatter-lint churn / mixed).
6. **Soundness concerns** (case-specific notes).

### Verdict definitions

| Verdict | Criteria |
|---|---|
| `WITNESSES_BREAKING_CHANGE` | `Δt` would plausibly `FAIL` on `P⊕Δm` and `PASS` on `P⊕Δm⊕Δc`. The test oracle directly exercises the dependency's behavioral break. |
| `UNWITNESSED` | `Δt` likely passes on `P⊕Δm` alone (Level 2 / `no_code_pass`). The test oracle is too weak to detect the breakage. |
| `TESTS_OTHER_THING` | `Δt` tests something unrelated to the dependency upgrade (lint/formatter output, an unrelated feature, snapshot churn, etc., with no link to the bumped library). Includes tasks where the `test_cmd` is a lint/format check, which is excluded by the locked breaking-change definition. |
| `INCONCLUSIVE` | The pass/fail behavior cannot be reliably determined from static analysis (e.g., empty placeholder test, build-tool load failure ambiguity). |

### `Δc` nature categories

| Category | Description |
|---|---|
| `REAL_SOURCE_REPAIR` | Production source code adapted to new API/behavior. |
| `FORMATTER_LINT_CHURN` | Prettier / eslint / standard / xo style changes only. |
| `CONFIG_INFRA_ONLY` | CI workflows, tsconfig, build scripts, `.nvmrc`. |
| `TEST_ONLY` | `Δc` itself edits only test files/testdata (agent is forbidden to touch tests). |
| `SNAPSHOT_ONLY` | `Δc` is `*.snap` / `__snapshots__` regenerations. |
| `DOCS_EXAMPLE_ONLY` | `Δc` edits only `docs/` examples. |
| `MIXED` | Combination of source repair + drive-by config/formatter/docs changes, or source repair + test contamination. |

---

## 3. Per-Case Results (Compact Table)

Full per-case audit reports are in `test_patch_quality_review_2026-06-17_cases/<folder>.md` (65 files).

| Folder | Ecosystem | Flagged | Verdict | `Δc` Nature | `test_cmd` Type |
|---|---|---|---|---:|
| cdk8s-team__kubecon-2020-cdk8s__28 | npm/yarn | | INCONCLUSIVE | CONFIG_INFRA_ONLY | RUNTIME |
| keystonejs__keystone__8056 | npm/yarn | F | INCONCLUSIVE | REAL_SOURCE_REPAIR | RUNTIME |
| renovatebot__renovate__41225 | npm/yarn | F | INCONCLUSIVE | REAL_SOURCE_REPAIR | RUNTIME |
| rollup__rollup__5046 | npm/yarn | F | INCONCLUSIVE | MIXED | RUNTIME |
| runatlantis__atlantis__5209 | Go | F | TESTS_OTHER_THING | MIXED | BUILD |
| FraunhoferIOSB__FROST-Server__1486 | Maven | | TESTS_OTHER_THING | REAL_SOURCE_REPAIR | UNKNOWN |
| BrightspaceUI__intl__106 | npm/yarn | | TESTS_OTHER_THING | FORMATTER_LINT_CHURN | LINT |
| aws__aws-northstar__1037 | npm/yarn | | TESTS_OTHER_THING | MIXED | RUNTIME |
| cloudant__nodejs-cloudant__400 | npm/yarn | | TESTS_OTHER_THING | FORMATTER_LINT_CHURN | LINT |
| elastic__kibana__185906 | npm/yarn | F | TESTS_OTHER_THING | SNAPSHOT_ONLY | RUNTIME |
| inrupt__solid-client-authn-js__279 | npm/yarn | | TESTS_OTHER_THING | FORMATTER_LINT_CHURN | LINT |
| scratchfoundation__scratch-blocks__3565 | npm/yarn | F | TESTS_OTHER_THING | FORMATTER_LINT_CHURN | LINT |
| hetznercloud__cli__940 | Go | F | UNWITNESSED | TEST_ONLY | BUILD |
| *(21 more UNWITNESSED)* | — | — | — | — | — |
| *(27 WITNESSED)* | — | — | — | — | — |

---

## 4. Systemic Soundness Issues

### 4.1 Lint/formatter-only test commands (undetected by prior audit)

5 of the 31 random (non-flagged) tasks have a `test_cmd` that is a lint/format check (`npm run lint`, `npx eslint .`, `npm run code:lint`, `npm run test:lint`), which the locked breaking-change definition **explicitly excludes**. Yet these tasks were NOT flagged in the problematic PR review.

| Task | test_cmd | Actual upgrade |
|---|---|---|
| BrightspaceUI__intl__106 | `npm run lint` | eslint-config-brightspace 0.17→0.18 |
| cloudant__nodejs-cloudant__400 | `npx eslint .` | eslint 3→4 (misattributed as acorn tarball) |
| inrupt__solid-client-authn-js__279 | `npm run lint` | prettier 1.19→2.1 |
| scratchfoundation__scratch-blocks__3565 | `npm run test:lint` | eslint-config-scratch |
| tekumara__typos-lsp__44 | `npm run lint` | prettier 2→3 (not vscode-languageclient) |

All five are style-compliance tasks with zero behavioral assertions, and Δc is pure formatter churn. **At minimum these should be moved to the explicit lint-excluded set** per the definition in `conversations/2026-06-06-breaking-change-definition/061710-claude-drafted.md`.

### 4.2 npm/yarn dev-dependency migration dominance

The most common unwitnessed pattern in npm/yarn is a dev-dependency major upgrade (eslint, prettier, jest, vitest, standard, xo, @typescript-eslint, flow-bin, typescript+babel) where:
- `Δc` makes syntactic changes (arrow→function body, var→const, add trailing comma, remove `as` cast) that preserve runtime behavior.
- The verifier runs a *runtime* test runner (jest with babel, vitest with esbuild) that strips types and never type-checks, so the type-level incompatibility is invisible.
- `Δt` mirrors the same syntactic cleanup on test files, and the runtime test assertions are unchanged → P⊕Δm⊕Δt passes without Δc.

**Examples:** probot__probot__2090 (express-5 types + vitest), dwightjack__vue-types__117 (TS 4.3→4.9 types), nukeop__nuclear__1905 (vitest 4 mock constructors + vitest `--run`), mozilla__addons-frontend__11753 (flow-bin + jest), cawa-93__vite-electron-builder__662 (vitest mock reset), mikavilpas__yazi.nvim__1506 (tsc --noEmit + cypress timing in Δt).

### 4.3 Task-unpassable-by-design (Δc edits test files)

`runatlantis__atlantis__5209` (Go) has a hard soundness defect: `Δc` edits `*_test.go` and `testdata/fixtures.go` files in the main module that are compiled by the verifier's `go test` command. The agent is explicitly instructed *not to modify test files*. Since `go test` compiles the whole package including `*_test.go`, the package **cannot compile** without Δc's test-file edits → **the task is unwinnable for any conforming agent.** Δt targets a different module (`e2e/`) that the verifier never runs → dead weight.

### 4.4 Circular oracle (Δt asserts exactly what Δc sets)

`FraunhoferIOSB__FROST-Server__1486` (Maven): the stated upgrade is `jooq 3.16.14→3.16.15`, but `Δc` merely changes three MQTT-bus default integers (2→4, 100→1000, 50→500). `Δt` asserts exactly those integers. The pass/fail is a tautology — `Δt` asserts whatever `Δc` sets — and `jooq` is never exercised. This is a drive-by config tuning riding on a patch-level manifest bump.

### 4.5 Misattributed dependency bump (the manifest is wrong)

Three tasks have a `Δm` that is unrelated to `Δc`/`Δt`:

- **aws__aws-northstar__1037**: `Δm` bumps `ws 7.5.9→7.5.10` (a trivial patch release), but `Δc` adds a `locales` parameter to a date-formatter. The ws upgrade is a lockfile ride-along; the PR is really a date-locale feature.
- **tekumara__typos-lsp__44**: `Δm` bumps `vscode-languageclient 8→9` + `prettier 2→3` + typescript + 5 other deps. The breaking change is only from `prettier 3` (trailing comma), not from `vscode-languageclient`. The instruction says "Bumps vscode-languageclient from 8 to 9" — misleading.
- **cloudant__nodejs-cloudant__400**: The mined "library" is a transitive acorn tarball URL change (`http://`→`https://`). The real bump is eslint 3→4.

### 4.6 Verifier targets the wrong test file

`bbc__simorgh__9137` runs only `ur.test.js` (an Urdu month-name locale test with zero relation to the Jest 29 upgrade). The 9 `Δt` files that *would* witness the Jest-29 snapshot-format migration are never executed. Both the witnessed integrity and the test-cmd targeting are broken.

### 4.7 Empty placeholder test

`cdk8s-team__kubecon-2020-cdk8s__28` has `Δt` = `test('put test here', () => {})` with no body, no imports, no source exercised. The "test" is projen's default generated stub. Whether the task passes or fails depends on whether projen 0.17.16 can load a 0.3.117-era `.projenrc.js` — a build-tool question, not a code-repair one.

### 4.8 Test patch is the fix itself (not the oracle)

`iodide-project__iodide__1432`: `Δt` drops `async` from a `describe` callback, which is exactly the runtime fix needed (`jest` no longer supports async `describe`). `Δc` edits only `.babelrc` and a test helper. The verifier runs the saga test, which passes on P⊕Δm⊕Δt without Δc — classic `no_code_pass`.

---

## 5. Cross-Cutting Quantitative Summary

| Metric | Value |
|---|---|
| Sample size | 65 (34 flagged + 31 random) |
| Witnessed (clean) | 27 (41.5%) |
| Unwitnessed | 26 (40.0%) |
| Tests-other-thing | 8 (12.3%) |
| Inconclusive | 4 (6.2%) |
| Flagged-row audit accuracy | 32/34 = 94.1% confirmed |
| Non-flagged witnessed rate | 25/31 = 80.6% |
| Non-flagged hidden soundness issues | 6/31 = 19.4% |
| Lint-only `test_cmd` (excluded by definition) | 9/65 = 13.8% |
| Δc = formatter/lint churn | 12/65 = 18.5% |
| Δc = config/infra only | 4/65 = 6.2% |
| Δc = snapshot/test/docs only | 3/65 = 4.6% |
| Hard unpassable task (Δc edits tests) | 1/65 = 1.5% |

**By ecosystem — witnessed rate:**

| Ecosystem | Sampled | Witnessed | Rate |
|---|---|---:|---:|
| Cargo | 2 | 2 | 100% |
| Maven | 8 | 7 | 88% (1 circular) |
| Go | 6 | 4 | 67% (1 unpassable, 1 unwitnessed) |
| pip | 4 | 2 | 50% |
| npm/yarn | 45 | 12 | 27% |

**Extrapolating to the full 297:** ~35% witnessed, ~40% unwitnessed, ~15% test-other, ~10% inconclusive. The npm/yarn subset (~145 tasks) likely has the worst ratio based on the pattern of devDep + lint/formatter dominance.

---

## 6. Root Causes (Why did this happen?)

1. **Mining pipeline does not enforce the witnessed gate at ingestion.** Tasks were mined from PRs where a human changed source code AND tests in a dep-bump PR, but the path classifier (`is_production_code_file && NOT is_test_file`) does not check whether the *hidden test actually fails* without the code patch. The pipeline assumed that if a human authored both, the test must witness the break. This assumption is wrong for formatter/lint migrations, type-only TS changes, and dev-tooling upgrades.

2. **Dev-dependency upgrades create false signals.** npm/yarn projects frequently bump dev-deps (eslint, prettier, jest, vitest, typescript, flow) in the same PR as a production dependency bump. The dev-dep bump dominates `Δc`/`Δt` while the production-dep bump sits unused. The path classifier sees "source files changed + test files changed" and classifies it as a breaking-change repair, but the "repair" is formatter compliance, not API migration.

3. **Test-runner stripg types without type-check.** vitest with esbuild, jest with babel, and node with tsx all strip TypeScript types, so type-level incompatibilities (removed exports, changed signatures, new strictness) do not cause runtime test failures. The verifier's `test_cmd` almost never invokes `tsc --noEmit`, so type-only breaks are invisible.

4. **The `test_cmd` is often too narrow.** Many tasks run only one spec file (e.g., `ur.test.js` for bbc__simorgh, `user.spec.ts` for verdaccio), but `Δt` modifies 10–30 test files. The verifier ignores most of `Δt`, so the majority of the hidden test patch is dead weight, and the single run file may be a drive-by unrelated change.

5. **No lint/format exclusion during ingestion.** The mining pipeline surfaces PRs where CI failed, but a lint-rule tightening (`eslint .` exit 1) is treated the same as a runtime test failure (`jest .` exit 1). The lock-in breaking-change definition excludes lint failures, but tasks with lint-only `test_cmd` were still packaged as Level 1.

6. **Go vendored tasks excluded, but test/testdata contamination in compiled packages persists.** The problematic review correctly filtered out `vendor/`-only tasks, but `runatlantis__atlantis__5209` shows a harder case: `Δc` edits `*_test.go` in the same Go package that the verifier compiles, creating an impossible constraint for the agent.

7. **Multi-dep bundling breaks the "single dependency" premise.** Tasks like `verdaccio__verdaccio__5742` and `tekumara__typos-lsp__44` bundle 5–15 dependency changes in one PR, with the dominant breaking change coming from a different dep than the one named in `instruction.md` and `task_summary.json`.

---

## 7. Recommendations

### Immediate (before running new agent evals)

1. **Quarantine lint-only tasks.** Any task whose `test_cmd` is exclusively a lint/format check (`npm run lint`, `npx eslint`, `prettier --check`, `tsc --noEmit` without `--build`, `npm run code:lint`, `npm run test:lint`) should be moved to a `tasks_v4_lint_excluded/` bucket. The locked definition excludes these from Level 1.

2. **Quarantine the 34 packaged `no_code_pass` rows.** The prior audit and our independent review agree on ≥32/34. Remove or move to `tasks_v4_latent/`.

3. **Fix `runatlantis__atlantis__5209`.** Either (a) move to excluded set (task unpassable by construction) or (b) restructure so `Δc` does not edit `*_test.go` files in the compiled package.

4. **Fix `FraunhoferIOSB__FROST-Server__1486`.** The `jooq` bump is unrelated to the MQTT-bus defaults. Move to excluded or re-baseline the manifest to contain only the MQTT-related change.

### Medium-term (before paper submission)

5. **Re-split `bbc__simorgh__9137` `test_cmd` to actually run the Jest-29 migration tests.** The current `ur.test.js` target is a drive-by.

6. **Audit npm/yarn tasks with dev-dep-only test coverage.** Any task where the sole breaking change is a dev-dep upgrade (formatter, test-runner, linter, type-checker) should be explicitly labeled as `devDep` and excluded from Level 1.

7. **Add a `--typecheck` gate for TypeScript-heavy tasks.** If no `tsc --noEmit` is feasible, at minimum flag tasks where `Δc` is type-only and `test_cmd` is a runtime-only runner (vitest `--run`, jest with babel) as Level 2.

8. **Re-verify the `library` metadata for all 297 tasks.** At least 3 of 65 sampled tasks (5%) have a mismatched/misleading `library` field in `task_summary.json` (cloudant acorn tarball, aws-northstar ws, tekumara vscode-languageclient). A bulk audit against actual manifest.patch content is warranted.

### Long-term (pipeline hardening)

9. **Add a pre-packaging witness check.** Before a task enters `tasks_v4`, run `TEST(P⊕Δm⊕Δt)` in a container and verify it FAILS. Track this as a gate (currently the pipeline ships tasks blind after path-classification).

10. **Extend the path classifier** to exclude from `Δc`: `__snapshots__/*`, `*.snap`, `*_test.go`, `*.test.*`, `*.spec.*`, `testdata/`, `__test_helpers__/`, `.github/workflows/`, and `vendor/`. Currently only test paths are excluded from `Δc`; snapshot/vendor/config paths leak through.

---

## 8. Case Reports Index

Detailed per-task analyses are in `test_patch_quality_review_2026-06-17_cases/`. Each file follows this format:

```markdown
# Test-patch audit — <folder>
## 1. Task summary
## 2. What is the breaking change?
## 3. What does Δt (test.patch) actually do?
## 4. Does Δt directly exercise the breaking change?
## 5. Coverage verdict
## 6. Δc nature
## 7. Soundness concerns / notes
```

List of 65 case files:

| File | Verdict | Ecosystem |
|---|---|---|
| alphagov__govuk-frontend__3591.md | UNWITNESSED | npm/yarn |
| ampproject__amp-wp__6853.md | WITNESSES_BREAKING_CHANGE | npm/yarn |
| apexskier__nova-typescript__445.md | WITNESSES_BREAKING_CHANGE | npm/yarn |
| asciidoctor__asciidoctor.js__870.md | UNWITNESSED | npm/yarn |
| aws__aws-northstar__1037.md | TESTS_OTHER_THING | npm/yarn |
| Azure-Samples__chat-with-your-data-solution-accelerator__894.md | WITNESSES_BREAKING_CHANGE | pip |
| bbc__psammead__3709.md | UNWITNESSED | npm/yarn |
| bbc__simorgh__9137.md | UNWITNESSED | npm/yarn |
| BrightspaceUI__intl__106.md | TESTS_OTHER_THING | npm/yarn |
| cawa-93__vite-electron-builder__662.md | UNWITNESSED | npm/yarn |
| cdk8s-team__kubecon-2020-cdk8s__28.md | INCONCLUSIVE | npm/yarn |
| cloudant__nodejs-cloudant__400.md | TESTS_OTHER_THING | npm/yarn |
| cloudflare__terraform-provider-cloudflare__1131.md | WITNESSES_BREAKING_CHANGE | Go |
| codemod-js__codemod__387.md | UNWITNESSED | npm/yarn |
| codetheweb__tuyapi__253.md | UNWITNESSED | npm/yarn |
| dadoonet__fscrawler__2342.md | WITNESSES_BREAKING_CHANGE | Maven |
| decaporg__decap-cms__5178.md | WITNESSES_BREAKING_CHANGE | npm/yarn |
| determined-ai__determined__8316.md | WITNESSES_BREAKING_CHANGE | Go |
| dwightjack__vue-types__117.md | UNWITNESSED | npm/yarn |
| eakmanrq__sqlframe__200.md | WITNESSES_BREAKING_CHANGE | pip |
| eakmanrq__sqlframe__450.md | UNWITNESSED | pip |
| eakmanrq__sqlframe__533.md | UNWITNESSED | pip |
| elastic__kibana__185906.md | TESTS_OTHER_THING | npm/yarn |
| eXist-db__exist__5042.md | WITNESSES_BREAKING_CHANGE | Maven |
| FraunhoferIOSB__FROST-Server__1486.md | TESTS_OTHER_THING | Maven |
| geotools__geotools__4212.md | WITNESSES_BREAKING_CHANGE | Maven |
| graphql-hive__graphql-config__1481.md | UNWITNESSED | npm/yarn |
| graphql-java-kickstart__graphql-java-tools__560.md | WITNESSES_BREAKING_CHANGE | Maven |
| Graylog2__graylog2-server__23926.md | WITNESSES_BREAKING_CHANGE | Maven |
| hashicorp__aws-sdk-go-base__796.md | WITNESSES_BREAKING_CHANGE | Go |
| hetznercloud__cli__940.md | UNWITNESSED | Go |
| inovex__scrumlr.io__4672.md | WITNESSES_BREAKING_CHANGE | npm/yarn |
| inrupt__solid-client-authn-js__279.md | TESTS_OTHER_THING | npm/yarn |
| iodide-project__iodide__1432.md | UNWITNESSED | npm/yarn |
| jamcalli__Pulsarr__1107.md | WITNESSES_BREAKING_CHANGE | npm/yarn |
| keystonejs__keystone__8056.md | INCONCLUSIVE | npm/yarn |
| LouisBarranqueiro__reapop__397.md | UNWITNESSED | npm/yarn |
| marp-team__marp-vscode__176.md | WITNESSES_BREAKING_CHANGE | npm/yarn |
| matrix-org__matrix-js-sdk__5217.md | UNWITNESSED | npm/yarn |
| mikavilpas__yazi.nvim__1506.md | UNWITNESSED | npm/yarn |
| mozilla__addons-frontend__10931.md | UNWITNESSED | npm/yarn |
| mozilla__addons-frontend__11753.md | UNWITNESSED | npm/yarn |
| mui__mui-x__18276.md | UNWITNESSED | npm/yarn |
| MystenLabs__fastcrypto__460.md | WITNESSES_BREAKING_CHANGE | Cargo |
| nextcloud__text__8485.md | UNWITNESSED | npm/yarn |
| nukeop__nuclear__1905.md | UNWITNESSED | npm/yarn |
| nuxt-community__vuetify-module__426.md | UNWITNESSED | npm/yarn |
| nuxt__fonts__601.md | UNWITNESSED | npm/yarn |
| OWASP__wrongsecrets__1040.md | WITNESSES_BREAKING_CHANGE | Maven |
| open-telemetry__opentelemetry-go__1943.md | WITNESSES_BREAKING_CHANGE | Go |
| owncloud__web__11511.md | WITNESSES_BREAKING_CHANGE | npm/yarn |
| plotly__react-chart-editor__1025.md | UNWITNESSED | npm/yarn |
| probot__probot__2090.md | UNWITNESSED | npm/yarn |
| regexident__cargo-modules__122.md | WITNESSES_BREAKING_CHANGE | Cargo |
| renovatebot__renovate__41225.md | INCONCLUSIVE | npm/yarn |
| rollup__rollup__5046.md | INCONCLUSIVE | npm/yarn |
| runatlantis__atlantis__5209.md | TESTS_OTHER_THING | Go |
| saveourtool__diktat__1529.md | WITNESSES_BREAKING_CHANGE | Maven |
| scinos__yarn-deduplicate__89.md | WITNESSES_BREAKING_CHANGE | npm/yarn |
| scratchfoundation__scratch-blocks__3565.md | TESTS_OTHER_THING | npm/yarn |
| solana-labs__solana-program-library__4301.md | WITNESSES_BREAKING_CHANGE | npm/yarn |
| sveltejs__kit__14789.md | UNWITNESSED | npm/yarn |
| tekumara__typos-lsp__44.md | WITNESSES_BREAKING_CHANGE | npm/yarn |
| typescript-eslint__tslint-to-eslint-config__1192.md | WITNESSES_BREAKING_CHANGE | npm/yarn |
| verdaccio__verdaccio__5742.md | WITNESSES_BREAKING_CHANGE | npm/yarn |

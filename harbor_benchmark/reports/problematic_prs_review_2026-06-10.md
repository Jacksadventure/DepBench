# Problematic PR Data Quality Review

Date: 2026-06-10

Input: `harbor_benchmark/reports/problematic_prs_review_2026-06-08.csv`

## Scope and Method

This review investigates all 44 rows in the CSV against:

- local benchmark artifacts under `harbor_benchmark/tasks_v4`;
- `solution/code.patch`, `tests/test.patch`, and `environment/patches/manifest.patch` path decomposition;
- upstream pull request metadata and changed-file lists fetched with `gh api`;
- the benchmark inclusion rule from the paper and prior notes: a main task should have a real consumer-code `Delta c` and should be witnessed by `TEST(P + Delta m + Delta t) = FAIL` while the oracle solution passes.

I did not rerun Harbor in this pass. The dynamic `no_code_pass` fact is taken from the CSV audit result: "manifest patch plus hidden test patch passes without solution code patch." This report verifies the local task presence, patch-path evidence, and GitHub PR/file context for every row.

## Executive Summary

The CSV identifies real data quality issues. Of 44 problematic PR rows:

- 34 rows are still packaged as local tasks in `harbor_benchmark/tasks_v4`.
- 10 rows are not present as local task directories on this branch; these are historical/mined PR quality issues, not current packaged-task removals.
- 30 packaged rows are `exclude_candidate` because the hidden tests do not witness the need for the solution code patch.
- 4 packaged rows are `manual_review_delta_c`, but the static evidence strongly favors exclusion from the main benchmark because their `Delta c` is snapshots, docs examples, or test/testdata only.
- The 10 non-packaged rows are all Go vendor-sync cases, including 4 that also have `no_code_pass`; keep them out of the main corpus and use them only as examples for improving candidate filters.

Recommended immediate action: remove or quarantine the 34 packaged rows from the witnessed main benchmark. If you keep a secondary "latent/unwitnessed" or "tooling migration" split, the `no_code_pass` rows can be retained there with an explicit label, but they should not contribute to the main witnessed-breaking-change results.

## Aggregate Findings

| Group | Count | Local status | Recommended action |
| --- | ---: | --- | --- |
| `no_code_pass` | 28 | packaged | Exclude from witnessed main benchmark; hidden oracle does not distinguish repaired from unrepaired state. |
| `no_code_pass;delta_c_test_config_only` | 1 | packaged | Exclude; both unwitnessed and `Delta c` is config/test-helper material. |
| `no_code_pass;delta_c_ci_workflow_only` | 1 | packaged | Exclude; both unwitnessed and `Delta c` is CI workflow only. |
| `delta_c_docs_example_only` | 2 | packaged | Exclude from main benchmark unless docs examples are explicitly allowed as product surface. |
| `delta_c_snapshot_testdata_only` | 1 | packaged | Exclude; snapshots are oracle/test artifacts, not consumer repair. |
| `delta_c_test_testdata_only` | 1 | packaged | Exclude; solution patch edits tests/testdata, not production repair. |
| `delta_c_vendor_only` | 6 | not packaged | Already absent locally; keep excluded in mining. |
| `no_code_pass;delta_c_vendor_only` | 4 | not packaged | Already absent locally; keep excluded in mining. |

## Packaged Exclude Candidates

These 30 rows exist in `tasks_v4` and should be removed or quarantined from the main witnessed benchmark because the CSV audit says `P + Delta m + Delta t` already passes without applying `Delta c`.

| Task | Upstream PR | Evidence | Verdict |
| --- | --- | --- | --- |
| `LouisBarranqueiro__reapop__397` | renovate PR, "prettier to v2.3.0", 2021-05-10 | Packaged npm task. `Delta c`: 1 source file, 2+/2-, `demo/src/components/NotificationCreator.tsx`; `Delta t`: 3 specs. | Exclude from witnessed main set. Also looks like formatter/tooling churn rather than runtime repair. |
| `alphagov__govuk-frontend__3591` | dependabot PR, "rollup from 0.59.4 to 3.21.5", 2023-05-11 | Packaged npm task. `Delta c`: `shared/tasks/scripts.mjs`, 14+/42-; `Delta t`: 2 build/release tests. | Exclude from witnessed main set. Source-looking build-script migration, but hidden tests do not witness failure. |
| `asciidoctor__asciidoctor.js__870` | dependabot-preview PR, "standard from 12.0.1 to 14.3.3", 2020-03-21 | Packaged npm task. `Delta c`: 8 source/benchmark/task files, 58+/58-; `Delta t`: 5 specs. | Exclude from witnessed main set. Linter/style upgrade with no observed failure. |
| `bbc__psammead__3709` | dependabot PR, "prettier from 2.0.5 to 2.1.1", 2020-09-02 | Packaged npm task. `Delta c`: 21 files, including changelogs and component source, 117+/157-; `Delta t`: 32 tests. | Exclude. Formatter upgrade; broad formatting/changelog churn and no witnessed failure. |
| `bbc__simorgh__9137` | renovate PR, "jest monorepo to v29", 2023-07-25 | Packaged npm task. `Delta c`: 93 files, but 89 are snapshots plus config; 3911+/3907-. | Exclude. Hidden tests do not witness repair, and most `Delta c` is snapshot/test artifact material. |
| `cawa-93__vite-electron-builder__662` | renovate PR, "vitest to v0.0.137", 2022-01-07 | Packaged npm task. `Delta c`: `packages/main/src/mainWindow.ts`, 9+/20-; `Delta t`: 1 spec. | Exclude from witnessed main set. Source-looking but unwitnessed. |
| `codemod-js__codemod__387` | dependabot-preview PR, "@typescript-eslint/eslint-plugin 2.9.0 to 2.11.0", 2019-12-16 | Packaged npm task. `Delta c`: 2 source files, 6+/2-; `Delta t`: 2 tests. | Exclude. Dev lint dependency update and no witnessed failure. |
| `codetheweb__tuyapi__253` | renovate PR, "xo to v0.25.3", 2019-09-29 | Packaged npm task. `Delta c`: 2 source files, 7+/7-; `Delta t`: 1 parser test. | Exclude. Linter/tooling update and no witnessed failure. |
| `dwightjack__vue-types__117` | renovate PR, "typescript to v4.3.4", 2021-06-29 | Packaged npm task. `Delta c`: `src/index.ts`, `src/utils.ts`, 10+/8-; `Delta t`: 1 test. | Exclude from witnessed main set. TypeScript migration is unwitnessed by hidden tests. |
| `eakmanrq__sqlframe__450` | renovate PR, "sqlglot >=24.0.0,<27.2", 2025-07-19 | Packaged pip task. `Delta c`: 3 docs files plus `sqlframe/base/functions.py`, 19+/8-; `Delta t`: 2 tests. | Exclude from witnessed main set. Contains real source edit, but hidden tests pass without it. |
| `eakmanrq__sqlframe__533` | renovate PR, "sqlglot >=24.0.0,<27.27", 2025-10-12 | Packaged pip task. `Delta c`: docs plus `sqlframe/base/functions.py`, 5+/4-; `Delta t`: 1 test. | Exclude from witnessed main set despite prior oracle fix; the issue here is lack of witness without `Delta c`. |
| `graphql-hive__graphql-config__1481` | renovate PR, "minimatch to v10", 2024-08-19 | Packaged npm task. `Delta c`: changeset plus `src/project-config.ts` and tsconfig files, 16+/6-. | Exclude. Unwitnessed; `Delta c` also mixes release-note/config material with a small source edit. |
| `iodide-project__iodide__1432` | renovate PR, "jest monorepo to v24", 2019-04-21 | Packaged npm task. `Delta c`: `.babelrc` and `__test_helpers__/reps-test-value-cases.js`; `Delta t`: 1 saga test. | Exclude. Both unwitnessed and classified as test config/helper only. |
| `jamcalli__Pulsarr__1107` | renovate PR, "@fastify/env to v6", 2026-04-07 | Packaged npm task. `Delta c`: 6 source/lock-like files, 28+/23-; `Delta t`: 1 logger test. | Exclude from witnessed main set. Source-looking runtime migration, but no hidden-test witness. |
| `matrix-org__matrix-js-sdk__5217` | renovate PR, "@matrix-org/matrix-sdk-crypto-wasm to v18", 2026-03-12 | Packaged npm task. `Delta c`: 3 source files in rendezvous/rust-crypto, 21+/24-; `Delta t`: 4 specs. | Exclude from witnessed main set unless a stricter hidden test can be added. |
| `mikavilpas__yazi.nvim__1506` | renovate PR, "stable yazi version v25.5.31 to v25.12.29", 2025-12-29 | Packaged npm task. `Delta c`: `.github/workflows/test.yml` and Cypress support file, 30+/1-; `Delta t`: 3 Cypress tests. | Exclude. Unwitnessed and partly CI/test harness work, not clean product-source repair. |
| `mozilla__addons-frontend__10931` | renovate PR, "redux-saga to v1", 2022-12-13 | Packaged npm task. `Delta c`: 2 source files, 3+/4-; `Delta t`: 2 tests. | Exclude from witnessed main set. Source-looking but unwitnessed. |
| `mozilla__addons-frontend__11753` | renovate PR, "flow-bin to ^0.183.0", 2022-07-25 | Packaged npm task. `Delta c`: 29 files, mostly source plus `.flowconfig`, 109+/115-; `Delta t`: 4 tests. | Exclude. Typechecker/tooling migration and no hidden-test witness. |
| `nextcloud__text__8485` | renovate PR, "tiptap to ^3.22.4", 2026-04-19 | Packaged npm task. `Delta c`: 4 source files, 4+/4-; `Delta t`: 2 specs. | Exclude from witnessed main set. Source-looking but unwitnessed. |
| `nukeop__nuclear__1905` | renovate PR, "vitest to v4", 2026-03-10 | Packaged npm task. `Delta c`: 8 files, mostly tsconfig/config plus 2 source files; `Delta t`: 4 test files. | Exclude. Test-runner/tooling migration and no hidden-test witness. |
| `nuxt-community__vuetify-module__426` | renovate PR, "@nuxtjs/eslint-config-typescript to v6", 2021-06-13 | Packaged npm task. `Delta c`: `src/font.ts`, 1+/1-; `Delta t`: one fixture layout. | Exclude. Dev lint dependency and no witness. |
| `nuxt__fonts__601` | renovate PR, "all non-major dependencies", 2025-04-24 | Packaged npm task. `Delta c`: two GitHub release workflow files, 3+/3-; `Delta t`: one basic test. | Exclude. Both unwitnessed and CI workflow only. |
| `plotly__react-chart-editor__1025` | renovate PR, "prettier to v2", 2020-03-25 | Packaged npm task. `Delta c`: 81 files, 257+/253-, including `.prettierrc` and broad source formatting; `Delta t`: 12 tests. | Exclude. Formatter migration and no hidden-test witness. |
| `probot__probot__2090` | renovate PR, "express to v5", 2025-04-04 | Packaged npm task. `Delta c`: `src/apps/setup.ts`, `src/server/server.ts`, 16+/11-; `Delta t`: 2 tests. | Exclude from witnessed main set. Looks like real migration, but the hidden oracle does not require it. |
| `renovatebot__renovate__41225` | renovate PR, "zod to v4", 2026-02-18 | Packaged npm task. `Delta c`: 130 files, mostly one-line source schema edits, 132+/132-; `Delta t`: 7 specs. | Exclude from witnessed main set unless new hidden tests fail without these edits. |
| `rollup__rollup__5046` | renovate PR, "locate-character to v3", 2023-06-24 | Packaged npm task. `Delta c`: config/license plus 2 source files, 13+/5-; `Delta t`: 1 test. | Exclude from witnessed main set. Mixed source/config/docs and no witness. |
| `runatlantis__atlantis__5209` | renovate PR, "go-github/v66 to v68", 2024-12-31 | Packaged Go task. `Delta c`: 19 files, but 7 are tests/testdata; source changes are mostly API signature updates, 82+/82-; `Delta t`: 1 e2e file. | Exclude from witnessed main set. Potentially real source migration, but no hidden-test witness. |
| `scratchfoundation__scratch-blocks__3565` | renovate PR, "eslint-config-scratch to v14.1.14", 2026-04-28 | Packaged npm task. `Delta c`: 8 source files, 12+/9-; `Delta t`: 3 tests. | Exclude. Style/lint dependency and no witness. |
| `sveltejs__kit__14789` | renovate PR, "vitest monorepo to v4", 2026-01-03 | Packaged npm task. `Delta c`: `packages/kit/kit.vitest.config.js`, 2+/5-; `Delta t`: 5 test/config files. | Exclude. Test-runner config migration and no witness. |
| `verdaccio__verdaccio__5742` | renovate PR, "core verdaccio dependencies (7.x)", 2026-03-29 | Packaged npm task. `Delta c`: 30 files, mostly source plus config, 187+/258-; `Delta t`: 19 test/helper files. | Exclude from witnessed main set. It may be a real large migration, but the current hidden oracle does not witness it. |

## Packaged Delta-c Boundary Cases

These 4 rows exist locally and are `manual_review_delta_c` in the CSV. Static review supports exclusion from the main benchmark because the solution patch is not production consumer-code repair.

| Task | Upstream PR | Evidence | Verdict |
| --- | --- | --- | --- |
| `elastic__kibana__185906` | renovate PR, "@elastic/charts to v66", 2024-06-21 | Packaged npm task. `Delta c`: 4 files, all `__snapshots__/*.snap`; `Delta t`: 2 functional/page-object files. | Exclude from main witnessed benchmark. Snapshot updates are oracle/testdata artifacts, not source repair. |
| `hetznercloud__cli__940` | renovate PR, "hcloud-go/v2 to v2.17.1", 2024-12-19 | Packaged Go task. `Delta c`: `internal/cmd/network/create_test.go` and `internal/cmd/network/testdata/create_response.json`; `Delta t`: one e2e test. | Exclude from main benchmark. The patch is test code/testdata, not production CLI behavior. |
| `keystonejs__keystone__8056` | renovate PR, "@markdoc/markdoc to ^0.2.0", 2022-11-03 | Packaged npm task. `Delta c`: 3 docs/markdoc files under `docs/`; `Delta t`: docs markdoc test. | Exclude from main benchmark unless documentation site examples are intentionally considered product code. |
| `mui__mui-x__18276` | renovate PR, "@mui/monorepo digest to 9b3d36e", 2025-06-10 | Packaged npm task. `Delta c`: 10 files, all docs/data examples; `Delta t`: 2 regression tests. | Exclude from main benchmark unless docs examples are intentionally in scope. |

## Non-packaged Vendor-only Rows

These 10 rows from the CSV are not present under `harbor_benchmark/tasks_v4` on this branch. They should remain out of the packaged benchmark. GitHub file lists show that the non-manifest changes are vendor or test-tools vendor syncs rather than consumer repairs.

| PR row | Upstream PR | GitHub changed-file evidence | Verdict |
| --- | --- | --- | --- |
| `cilium__cilium__25035` | renovate PR, "all go dependencies main (patch)", 2023-05-05 | 92 changed files: `go.mod`, `go.sum`, and 90 `vendor/` files. | Already not packaged; keep excluded. |
| `cilium__cilium__25542` | renovate PR, "all go dependencies main (patch)", 2023-06-06 | 71 changed files: `go.mod`, `go.sum`, and 69 `vendor/` files. | Already not packaged; keep excluded. |
| `cilium__cilium__29536` | renovate PR, "all go dependencies main (patch)", 2023-12-01 | 31 changed files: `go.mod`, `go.sum`, and 29 `vendor/` files. | Already not packaged; keep excluded. |
| `cilium__cilium__30395` | renovate PR, "github.com/docker/docker to v25", 2024-01-25 | 201 changed files: `go.mod`, `go.sum`, and 199 `vendor/` files. | Already not packaged; keep excluded. |
| `cilium__cilium__31112` | renovate PR, "all go dependencies main", 2024-03-05 | 109 changed files: `go.mod`, `go.sum`, and 107 `vendor/` files. | Already not packaged; keep excluded. |
| `cloudflare__terraform-provider-cloudflare__635` | renovate PR, "terraform-plugin-sdk to v1.9.0", 2020-03-26 | 246 changed files: `go.mod`, `go.sum`, and 244 `vendor/` files. | Already not packaged; keep excluded. |
| `containers__podman__21284` | renovate PR, "ginkgo/v2 to v2.14.0", 2024-01-18 | 73 changed files: root/test-tools manifests plus 69 vendor files and 2 test-tools manifest files. | Already not packaged; keep excluded. |
| `containers__podman__23418` | renovate PR, "ginkgo/v2 to v2.19.1", 2024-07-29 | 21 changed files: root/test-tools manifests plus 17 vendor files and 2 test-tools manifest files. | Already not packaged; keep excluded. |
| `containers__podman__23541` | renovate PR, "ginkgo/v2 to v2.20.0", 2024-08-08 | 17 changed files: root/test-tools manifests plus 13 vendor files and 2 test-tools manifest files. | Already not packaged; keep excluded. |
| `containers__podman__24414` | renovate PR, "ginkgo/v2 to v2.21.0", 2024-10-30 | 23 changed files: root/test-tools manifests plus 19 vendor files and 2 test-tools manifest files. | Already not packaged; keep excluded. |

## Root Causes

1. Witness check was not enforced as a hard inclusion gate for some packaged tasks.
   The `no_code_pass` rows violate the intended witnessed-breaking-change criterion even when they contain real-looking source edits.

2. Path decomposition still leaks non-production changes into `Delta c`.
   Snapshots, `*_test.go`, `testdata`, docs examples, CI workflows, test helpers, and config-only edits should not satisfy `Delta c != empty` for the main benchmark.

3. Dependency-bot PRs often include human cleanup commits.
   Many PRs have 2 or more commits and human commit authors. That is not automatically disqualifying, but it increases the chance of formatter, docs, snapshot, or drive-by changes being mistaken for dependency repair.

4. Go vendoring creates false non-manifest signals.
   Vendor directories and `test/tools/vendor` should be treated as dependency materialization, not consumer code, during mining and patch decomposition.

## Recommended Remediation

1. Remove or quarantine the 34 packaged rows from `tasks_v4` for the main witnessed benchmark.

2. If maintaining alternate subsets, split them explicitly:
   - `witnessed_main`: requires real production `Delta c` and `P + Delta m + Delta t = FAIL`;
   - `latent_unwitnessed`: real source `Delta c`, but `P + Delta m + Delta t = PASS`;
   - `non_source_delta_c`: docs, snapshots, tests, CI, config, vendor, or generated-only changes.

3. Harden the mining/decomposition filters:
   - exclude `vendor/`, `*/vendor/`, and `test/tools/vendor/` from `Delta c`;
   - exclude `__snapshots__/`, `*.snap`, `testdata/`, `*_test.go`, `*.test.*`, `*.spec.*`, `__tests__/`, and `__test_helpers__/` from `Delta c`;
   - exclude `.github/workflows/` and release/config-only changes from production `Delta c`;
   - treat `docs/` and examples as non-main unless the benchmark explicitly scopes documentation apps as products.

4. Recompute paper/task counts after quarantine.
   The current local directory has 208 task directories; this report identifies 34 packaged rows that should not be counted in the main witnessed set without stronger hidden tests or reclassification.


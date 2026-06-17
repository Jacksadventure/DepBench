# Test-Patch Quality Audit — Full 297 Tasks — 2026-06-18

**Scope:** all 297 tasks in `harbor_benchmark/tasks_v4/`.
**Method:** static expert review of `Δm` (manifest), `Δc` (oracle code patch), `Δt` (hidden test patch), and verifier `test_cmd`; 65 prior reports were reused as fixed prior work and 232 reports were newly produced.
**Per-case details:** `harbor_benchmark/reports/test_patch_quality_review_2026-06-18_cases/<folder>.md`.
**Machine-readable table:** `harbor_benchmark/reports/test_patch_quality_review_2026-06-18_cases.csv`.

## 1. Executive Summary

Of 297 packaged DepBench tasks, **205 (69.0%) statically appear to witness the dependency breaking change** under the locked Level-1 definition. The remaining tasks should be treated as latent, testing another property, or needing manual/dynamic revalidation rather than being counted in the main witnessed benchmark headline.

| Value | Count | % |
|---|---:|---:|
| `WITNESSES_BREAKING_CHANGE` | 205 | 69.0% |
| `UNWITNESSED` | 28 | 9.4% |
| `TESTS_OTHER_THING` | 59 | 19.9% |
| `INCONCLUSIVE` | 5 | 1.7% |

Main witnessed benchmark size after excluding latent/test-other/inconclusive cases: **205 / 297**.

## 2. Counts by Ecosystem

| Ecosystem | Total | WITNESSES_BREAKING_CHANGE | UNWITNESSED | TESTS_OTHER_THING | INCONCLUSIVE |
|---|---:|---:|---:|---:|---:|
| cargo | 23 | 20 | 1 | 2 | 0 |
| go_modules | 35 | 28 | 1 | 5 | 1 |
| maven | 74 | 66 | 0 | 8 | 0 |
| npm_and_yarn | 145 | 79 | 24 | 38 | 4 |
| pip | 20 | 12 | 2 | 6 | 0 |

Ecosystem totals:

| Value | Count | % |
|---|---:|---:|
| `cargo` | 23 | 7.7% |
| `go_modules` | 35 | 11.8% |
| `maven` | 74 | 24.9% |
| `npm_and_yarn` | 145 | 48.8% |
| `pip` | 20 | 6.7% |

## 3. Counts by Δc Nature

| Value | Count | % |
|---|---:|---:|
| `REAL_SOURCE_REPAIR` | 169 | 56.9% |
| `FORMATTER_LINT_CHURN` | 31 | 10.4% |
| `CONFIG_INFRA_ONLY` | 8 | 2.7% |
| `TEST_ONLY` | 2 | 0.7% |
| `SNAPSHOT_ONLY` | 1 | 0.3% |
| `DOCS_EXAMPLE_ONLY` | 3 | 1.0% |
| `MIXED` | 83 | 27.9% |

Δc nature by verdict:

| Dc Nature | Total | WITNESSES_BREAKING_CHANGE | UNWITNESSED | TESTS_OTHER_THING | INCONCLUSIVE |
|---|---:|---:|---:|---:|---:|
| CONFIG_INFRA_ONLY | 8 | 2 | 3 | 2 | 1 |
| DOCS_EXAMPLE_ONLY | 3 | 0 | 2 | 1 | 0 |
| FORMATTER_LINT_CHURN | 31 | 1 | 7 | 23 | 0 |
| MIXED | 83 | 52 | 8 | 21 | 2 |
| REAL_SOURCE_REPAIR | 169 | 150 | 7 | 10 | 2 |
| SNAPSHOT_ONLY | 1 | 0 | 0 | 1 | 0 |
| TEST_ONLY | 2 | 0 | 1 | 1 | 0 |

## 4. Flagged vs Non-Flagged Comparison

Problematic-review flagged cases in the full packaged set: **34**. Non-flagged cases: **263**.

Flagged verdicts:

| Value | Count | % |
|---|---:|---:|
| `WITNESSES_BREAKING_CHANGE` | 2 | 5.9% |
| `UNWITNESSED` | 26 | 76.5% |
| `TESTS_OTHER_THING` | 3 | 8.8% |
| `INCONCLUSIVE` | 3 | 8.8% |

Non-flagged verdicts:

| Value | Count | % |
|---|---:|---:|
| `WITNESSES_BREAKING_CHANGE` | 203 | 77.2% |
| `UNWITNESSED` | 2 | 0.8% |
| `TESTS_OTHER_THING` | 56 | 21.3% |
| `INCONCLUSIVE` | 2 | 0.8% |

## 5. Comparison Against 65-Case Smoke Audit

The earlier 65-case smoke audit reported this verdict distribution:

| Value | Count | % |
|---|---:|---:|
| `WITNESSES_BREAKING_CHANGE` | 27 | 41.5% |
| `UNWITNESSED` | 26 | 40.0% |
| `TESTS_OTHER_THING` | 8 | 12.3% |
| `INCONCLUSIVE` | 4 | 6.2% |

The full-297 audit distribution is:

| Value | Count | % |
|---|---:|---:|
| `WITNESSES_BREAKING_CHANGE` | 205 | 69.0% |
| `UNWITNESSED` | 28 | 9.4% |
| `TESTS_OTHER_THING` | 59 | 19.9% |
| `INCONCLUSIVE` | 5 | 1.7% |

The smoke audit correctly predicted that npm/yarn dev-tooling, lint/formatter, and weak runtime-only test commands dominate the soundness gap; the full audit provides the actual packaged-dataset counts rather than the earlier extrapolation.

## 6. Quarantine Candidates

These 92 cases are not currently clean Level-1 witnessed cases and should be excluded from the main witnessed benchmark until repaired or dynamically revalidated:

| Folder | Ecosystem | Verdict | Δc Nature | Reason summary |
|---|---|---|---|---|
| `dailymotion-oss__octopilot__152` | go_modules | `INCONCLUSIVE` | `MIXED` | At the source/API level, yes: the patched tests compile against and assert the new yq API surface, for example `expectedExpression: \`(.version) ref $x \| $x = "1.2.3"\`` and `OutputFormat: yqlib.JSONOutputFormat`. On P⊕ |
| `cdk8s-team__kubecon-2020-cdk8s__28` | npm_and_yarn | `INCONCLUSIVE` | `CONFIG_INFRA_ONLY` | No — there is no representative assertion. The Δt is an empty placeholder test (`test('put test here', () => {})`) with no body and no imports, so it cannot exercise any source or config behavior. The only potential FAIL |
| `keystonejs__keystone__8056` | npm_and_yarn | `INCONCLUSIVE` | `REAL_SOURCE_REPAIR` | Not via a new assertion. Δt only updates the test's render helper to narrow the widened `RenderableTreeNode` type (and import `isTag`). There is no new test input that forces a non-Tag node through `transformContent`. If |
| `renovatebot__renovate__41225` | npm_and_yarn | `INCONCLUSIVE` | `REAL_SOURCE_REPAIR` | Not via a new assertion. Δt only retargets imports. The plausible failure mode on P⊕Δm⊕Δt is that the source still imports bare `zod` (v4) while Δt makes the specs import `zod/v3` (v3); a v4-thrown `ZodError` is not `ins |
| `rollup__rollup__5046` | npm_and_yarn | `INCONCLUSIVE` | `MIXED` | Δt directly handles facet (a) — the ESM-only `require` break — by switching to dynamic `import()`. It does NOT assert facet (b) (the nullable `locate()` return) at all; nothing in the test observes null-return behavior.  |
| `gjtorikian__what_you_say__14` | cargo | `TESTS_OTHER_THING` | `MIXED` | No. The likely fail/pass signal is `bundle exec rake compile` compiling the Rust extension against magnus 0.6, which would fail before the changed Ruby assertion matters. The hidden test edit is an assertion-style cleanu |
| `oxidecomputer__dropshot__580` | cargo | `TESTS_OTHER_THING` | `TEST_ONLY` | It exercises changed dependency error strings, but only by updating tests. Delta c is also test-only: it changes assertions inside `dropshot/src/logging.rs`'s internal test module. There is no production/source repair, o |
| `circleci__ex__510` | go_modules | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | No. Δt exercises a newly introduced helper and updates tests to satisfy the same close-error pattern. The dependency being bumped is a linter, and lint failures are explicitly not witnessed breaking-change evidence. The  |
| `grafana__alloy__3602` | go_modules | `TESTS_OTHER_THING` | `MIXED` | No. The verifier runs only `go test ./internal/component/loki/secretfilter -run Benchmark`; it does not start the integration-test docker-compose stack and never uses the new Redis script. The fail/pass signal, if any, c |
| `hashicorp__terraform-provider-aws__34096` | go_modules | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | No. The verifier runs only `./internal/framework/flex/...`, so it does not compile or run the service files that actually broke against the new AWS SDK pointer types. The pre-Delta c failure is caused by the hidden test  |
| `runatlantis__atlantis__5209` | go_modules | `TESTS_OTHER_THING` | `MIXED` | No. The `test_cmd` runs `go test ./server/controllers/events -run TestGithubPullRequestParsed` in the **main `/app` module**. `e2e/github.go` (the only file Δt touches) lives in the separate `e2e` module and is never com |
| `stormforger__cli__220` | go_modules | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | No. On P+Delta_m+Delta_t, the immediate failure is that `MainTestcaseBuild` does not exist. That symbol is introduced by Delta_c specifically to make the new test call possible. The test does not isolate an esbuild API m |
| `FraunhoferIOSB__FROST-Server__1486` | maven | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | No. The Δt assertions merely encode the three new default integers that Δc writes (`assertEquals(4, ...)`, `assertEquals(1000, ...)`, `assertEquals(500, ...)`). They do not touch jooq, SQL generation, or any behavior aff |
| `Graylog2__graylog2-server__25652` | maven | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | No. Δt updates tests to satisfy static-analysis/style checks from the Error Prone bump; it does not add or alter an assertion that exercises Graylog runtime behavior against a changed library API. |
| `OpenNMS__opennms__6191` | maven | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | No. The representative assertions are `containsString("firstalias:password='<output omitted> @ GLOBAL'")` and `not(containsString("Pittsboro"))`, which exercise the new secret-redaction behavior in `MetaCommand.printScop |
| `airlift__airlift__1592` | maven | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | It exercises the project default flip, not a dependency-caused compile or runtime break. `TEST(P+Delta m+Delta t)` fails because the project still defaults compression to `false`; that failure is independent of any remov |
| `apache__logging-log4j2__2236` | maven | `TESTS_OTHER_THING` | `MIXED` | No. The hidden test targets Log4j issue #2234 / a ring-buffer event reuse bug. It does not import or execute `spring-cloud-context`, and the tested module is unrelated to the dependency changed by Δm. |
| `apache__logging-log4j2__2345` | maven | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | It exercises the Log4j lookup propagation fix, but not the dependency bump. The new tests instantiate `TestConfiguration` / `Interpolator` directly and assert internal configuration/context propagation; they do not use G |
| `apache__logging-log4j2__2409` | maven | `TESTS_OTHER_THING` | `MIXED` | No. The hidden test exercises a Log4j internal API change around `IfLastModified` and duration handling, not the MongoDB/BSON upgrade. `TEST(P+Delta m+Delta t)` would fail because the old source lacks `IfLastModified.new |
| `apache__logging-log4j2__2600` | maven | `TESTS_OTHER_THING` | `MIXED` | No. The Mongo resolver edits are test-side compatibility fixes, not assertions over production repair. The one behavioral assertion is for empty writes/appends in `TruncatingBufferedWriter`, which matches a real source f |
| `BrightspaceUI__intl__106` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | No behavioral assertion is involved. Δt merely makes the test files lint-clean under the 0.18 config + `eslint .` scope. The "failure" it helps produce on P⊕Δm⊕Δt is `npm run lint` exiting non-zero on the still-non-compl |
| `InfluxCommunity__influxdb3-js__413` | npm_and_yarn | `TESTS_OTHER_THING` | `CONFIG_INFRA_ONLY` | No for benchmark purposes. The verifier command is `yarn run lint`, and the user instruction for this audit states that lint/format-only `test_cmd` is always `TESTS_OTHER_THING`. Even if ESLint 9 config migration is a re |
| `amweiss__angular-diff-match-patch__231` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | No behavioral test is being run. The verifier is `yarn run lint`, so Δt merely makes the test file lint-clean while Δc makes `angular-diff-match-patch.js` lint-clean. |
| `ardatan__graphql-tools__7282` | npm_and_yarn | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | No. The test exercises GraphQL `@oneOf` support in `packages/utils/src/print-schema-with-directives.ts`. It does not exercise regenerator transformation output or any Babel-runtime behavior. P⊕Δm⊕Δt would fail because th |
| `asciidoctor__asciidoctor-cli.js__96` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | No. The verifier command is `npm run lint`, and the patched tests are style rewrites rather than assertions that expose a `fast-deep-equal` API or semantic incompatibility. |
| `aws__aws-northstar__1037` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | Not a dependency break. The Δt exercises the new `locales` signature that Δc introduces: ``` expect(getDisplayLastModified(date, 'en-US')).toBe('Last modified: 1/1/2022, 1:01:00 AM'); ``` On P⊕Δm (original 1-arg signatur |
| `cloudant__nodejs-cloudant__400` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | No. Δt contains no behavioral assertions at all — it only re-indents test files so they satisfy eslint 4's `indent` rule. The "failure" it helps produce is `npx eslint .` exiting non-zero on the still-misindented `lib/`  |
| `elastic__kibana__185906` | npm_and_yarn | `TESTS_OTHER_THING` | `SNAPSHOT_ONLY` | No. The `test_cmd` runs three **jest unit tests** (`gauge_component`, `partition_vis_component`, `xy_chart`) whose pass/fail is governed by `__snapshots__/*.snap` files. Δt edits two `x-pack/test/functional/**` files tha |
| `emberjs__ember.js__19722` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | It exercises only lint-rule compatibility, not source behavior. Per the audit instructions, lint-only `test_cmd` is always `TESTS_OTHER_THING`. |
| `fastify__fastify-http-proxy__171` | npm_and_yarn | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | Only indirectly, and in an over-specified way. P⊕Δm⊕Δt fails immediately because `test/utils.js` imports a new `../utils` module that does not exist before Δc. The patched integration tests mostly avoid the ws 8 break th |
| `fb55__css-what__1184` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | No behavioral assertion is involved. A representative hunk is `expect(parse(selector)).toStrictEqual(expected)` -> `expect(parse(selector)).toStrictEqual(expected),`, which is syntactic formatting only and should not aff |
| `foobaragency__foo-state__321` | npm_and_yarn | `TESTS_OTHER_THING` | `DOCS_EXAMPLE_ONLY` | No. The new counter tests exercise React state-update semantics in an example component, not the `@types/jest` dependency change. The snapshot update is also test-output accommodation, not source compatibility with the u |
| `inrupt__solid-client-authn-js__279` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | No. Δt does not exercise any dependency breaking change — it only re-formats test/mock files to satisfy prettier 2.x. The verifier (`npm run lint`) does fail on P⊕Δm⊕Δt (because the un-reformatted `src/**/*.ts` productio |
| `inrupt__solid-client-authn-js__3129` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | Not as a dependency breaking change. The relevant Jest-visible checks are circular API/signature expectations introduced by Δt itself, e.g. `const TokenRefresher = new TokenRequester()` and one-argument `new ClientCreden |
| `integrations__jira__293` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | No. The new test drives the `/verify` endpoint and specifically expects `Installation.findByPk` plus `response.json` behavior from Δc. None of that behavior is caused by changing the `resolve` tarball URL; old source wou |
| `ktsn__capture-all__12` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | No. The verifier is explicitly `prettier --list-different`, so it only checks formatting. Δc similarly reformats `src/index.ts` and `src/stream.ts`; it does not repair production behavior. |
| `ktsn__vue-auto-routing__103` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | No functional behavior is exercised. The only observable difference is formatter/lint conformance under the upgraded Prettier style. Per the audit rule, lint/format-only evidence is not a witnessed breaking change. |
| `ktsn__vuex-smart-module__189` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | No. The verifier command is `npm run lint`, and the patch is formatting churn across source and test files. Per the audit rule, lint/format-only test commands are classified as testing something other than a dependency b |
| `laconiajs__laconia__178` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | No. The verifier is `npm run test:jslint`, so Δt and Δc are both just making files satisfy the new lint rules. |
| `microsoft__lage__346` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | It exercises the Jest 29 test-runner migration, not a product behavior change. Most Δt hunks are snapshot serializer churn or TypeScript test cleanup. The only source-like Δc hunk is `writeRemoteCache?: boolean`, while t |
| `mightyiam__eslint-config-love__2120` | npm_and_yarn | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | It exercises the project's "expected exported config includes all configured import rules" invariant, but not a dependency breaking change. The old config would still compile and run with eslint-plugin-import 2.32.0; Δt  |
| `mochajs__mocha__5709` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | Only as a formatter check. The verifier is `npm run format:check`, so the oracle is style conformance rather than functional behavior. |
| `multiformats__js-multiformats__306` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | Only through lint/type checks. The runtime assertions are essentially unchanged; the fail/pass signal is driven by `npx aegir lint` and TypeScript lint strictness, not by a behavioral dependency break. The user instructi |
| `noflo__noflo-polymer__54` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | Only as lint. The verifier command is `npm run lint`, and the source patch likewise adds a trailing comma/semicolon in `karma.conf.js` and parenthesizes arrow callback parameters in `lib/PolymerComponent.js`. |
| `oceanprotocol__market__1687` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | No. The representative new assertions are `testRender(<Alert text="Alert text" state="info" />)` and similar atom render checks, but `testRender` is introduced only by Δc in `.jest/testRender.ts`; without that helper, P⊕ |
| `onthegomap__maplibre-contour__34` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | It exercises formatter conformance only. The visible hidden-test changes are all formatting, and Δc applies the same formatting style to production TypeScript files. Any FAIL -> PASS signal comes from formatting checks w |
| `openlayers__ol-mapbox-style__1071` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | It exercises lint-rule compliance only. Since the verifier command is `npx eslint test examples src`, failure evidence is lint/static-formatting output, which the locked definition excludes from witnessed breaking-change |
| `option-t__option-t__1911` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | It only exercises formatting. The verifier command is itself `prettier --check .`, so the task is a formatter oracle rather than a source behavior oracle. |
| `pr-triage__app__251` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | No. The representative assertion is `expect(result).toEqual(1)` for an empty branch-protection response. That tests a new fallback path added in `lib/pr-triage.js`, not the Probot 10 logger/context API nor the Sentry dep |
| `prettier__prettier__8890` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | No. The hidden test fails on P+Delta m because `.cjs` config search support does not exist yet, then passes after Delta c adds that feature. That is feature coverage, not evidence of a dependency-induced break in existin |
| `promptfoo__promptfoo__8920` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | Not convincingly. The test uses mocks and checks newly introduced promptfoo provider semantics. It would fail on the old source because old promptfoo sent all config except `apiKey` as model input and never forwarded `cl |
| `promptfoo__promptfoo__8946` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | No. The tests require newly implemented feature pass-throughs. On P+Delta_m+Delta_t, they fail because the old provider does not know about these newly asserted options, not because an existing call path broke under 0.2. |
| `promptfoo__promptfoo__9079` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | No. The tests assert new product/provider behavior implemented by Δc. They do not demonstrate that P⊕Δm broke an existing path due to the `@opencode-ai/sdk` bump. Without Δc the new tests fail because the feature does no |
| `qntm__base65536__49` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | No. The hidden tests exercise a Base65536 encoding bug and test-suite focus issue, not behavior from the `follow-redirects` dependency bump. P⊕Δm is not expected to fail because of the upgraded dependency; it fails becau |
| `scratchfoundation__scratch-blocks__3565` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | It exercises lint-rule compliance, not a functional dependency behavior. The breaking change is a lint rule; Δt removes the now-flagged casts from test files. Without Δc the source files still contain the flagged `as` ca |
| `sumup-oss__circuit-ui__837` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | No. The new assertion tests runtime ref forwarding behavior, which TypeScript does not change at runtime. The old component did not forward refs before the dependency bump either. Δt therefore requires a useful source ch |
| `wireapp__wire-web-packages__2929` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | It only exercises the formatter/lint pipeline. The verifier command is `yarn run lint`, so a pass/fail result is lint evidence, not valid witnessed breaking-change evidence. |
| `xt0rted__slash-command-action__307` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | No. The hidden tests exercise the changed `main.run()` error-handling policy, not the Octokit client/type migration in `src/commandHandler.ts`. They would fail without Δc because `main.run()` still rethrows, but that fai |
| `aws__aws-sdk-pandas__2883` | pip | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | No. The verifier command is lint-only (`ruff check ...`). Δc adds `# noqa: E721` comments to silence Ruff's type-comparison rule in `awswrangler/neptune/_neptune.py`; no runtime behavior or boto3-stubs API behavior is te |
| `bachya__pytile__346` | pip | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | No. The hidden test exercises application error handling for HTTP 500 detail responses. That behavior is repaired by Δc's new `BaseException` branch, but it is unrelated to the mypy version bump and does not witness a de |
| `nikolaik__docker-python-nodejs__306` | pip | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | No. The patched tests do not exercise a dependency behavior change. They mostly mirror lint/type-style edits made in Δc. The only non-style change is the pytest marker spelling, but that is test-framework configuration s |
| `nuxeo__nuxeo-drive__3833` | pip | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | No. The verifier command is a spell-check/lint command, and lint/format-only commands are not witnessed breaking-change evidence by the audit rules. Delta c is likewise spelling/comment/documentation churn. |
| `peopledatalabs__peopledatalabs-python__132` | pip | `TESTS_OTHER_THING` | `CONFIG_INFRA_ONLY` | No. The only reachable hidden-test change is the version-string assertion. That is release metadata, not behavior affected by `annotated-types` 7.5.1. The sandbox endpoint fixture edits are not run by the verifier. |
| `wayfair-incubator__pygitops__272` | pip | `TESTS_OTHER_THING` | `MIXED` | No. Pytest is not running mypy or another type checker, and the normal GitPython runtime path does not fail merely because the annotation became optional. P+Delta_m+Delta_t fails because Delta_t imports a helper that onl |
| `jonasbb__serde_with__836` | cargo | `UNWITNESSED` | `DOCS_EXAMPLE_ONLY` | Only weakly, and not against Δc. The verifier uses `cargo test --no-default-features --no-run`, so the snapshot assertion is compiled but not executed. Δc changes only documentation examples/doctest text in `serde_with/s |
| `hetznercloud__cli__940` | go_modules | `UNWITNESSED` | `TEST_ONLY` | It targets the right field, but not in a way that requires Δc. The e2e test expects `"load_balancers": []` in the network JSON output. That field is emitted automatically once the upgraded hcloud-go struct (with the new  |
| `LouisBarranqueiro__reapop__397` | npm_and_yarn | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | No. The test_cmd is `jest` (runtime React component tests). jest does not check prettier formatting; the `nodeRef` prop is passed identically whether written with or without the redundant parens. The FadeTransition/GrowT |
| `alphagov__govuk-frontend__3591` | npm_and_yarn | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | Partially. The `export { X as default }` assertion is **rollup-version-determined**: rollup 3.x (installed via Δm) emits this format regardless of how `scripts.mjs` is written, so this assertion passes on P⊕Δm whenever t |
| `asciidoctor__asciidoctor.js__870` | npm_and_yarn | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | No. Every Δt change is semantically a no-op (bracket vs dot access, quoted vs unquoted keys, `let` vs `const` are runtime-identical). The assertions test the exact same behavior before and after. Nothing in Δt would plau |
| `bbc__psammead__3709` | npm_and_yarn | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | No. The verifier's `test_cmd` is `npx prettier --check <list of 32 .test.js files>` — a **formatter lint check on the test files themselves**, not a behavioral test suite (no jest/vitest). The verifier applies Δt (which  |
| `bbc__simorgh__9137` | npm_and_yarn | `UNWITNESSED` | `MIXED` | No. The verifier runs **only** `ur.test.js` (see test_cmd), which tests `moment(input,'MMMM').month()` for Urdu month names — no snapshots, no Jest-29 API. Neither Δm (Jest stack bump) nor Δc (snapshots + config) touches |
| `cawa-93__vite-electron-builder__662` | npm_and_yarn | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | No assertion in Δt verifies the new `getAllWindows()` code path. The tests check the same observable behavior (instance count, `restore` called once) that both the original module-variable implementation and the new `get |
| `codemod-js__codemod__387` | npm_and_yarn | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | Only in the lint-compliance sense. The `eslint packages/cli --ext .ts` and `eslint packages/matchers --ext .ts` steps in test_cmd lint the test files too; Δt makes those test files lint-clean under the new `no-empty-func |
| `codetheweb__tuyapi__253` | npm_and_yarn | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | No. `t.deepEqual(2, 2)` and `t.is(2, 2)` both pass for primitives, so the Δt assertions pass regardless of Δc. Δc is itself behavior-preserving (`substr(8,16)` ≡ `slice(8,24)`; `indexOf(x)===-1` ≡ `!includes(x)`; `catch( |
| `dwightjack__vue-types__117` | npm_and_yarn | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | No. The only assertion touched (`expect(utils.clone(obj)).not.toBe(obj)` / `.toEqual(obj)`) is unchanged and tests `clone()` runtime behavior, which is identical under TS 4.2.3 and 4.3.4. The `as any` is a compile-time c |
| `graphql-hive__graphql-config__1481` | npm_and_yarn | `UNWITNESSED` | `MIXED` | No. The Δt changes are exclusively `@ts-expect-error` comments for the `isTheOne` property assignment in the `middlewares` schema-loading test — entirely unrelated to minimatch. The test mocks `@graphql-tools/load` and e |
| `iodide-project__iodide__1432` | npm_and_yarn | `UNWITNESSED` | `MIXED` | No — Δt **is** the fix for the only break that affects the graded test. With Δt applied (async removed), `eval-queue-saga.test.js` loads and runs under jest 24 without Δc: Δc's two changes (`.babelrc` `targets: node: cur |
| `m-h-c-t__mh-helper-extension__434` | npm_and_yarn | `UNWITNESSED` | `MIXED` | No. The verifier runs Jest, not ESLint, and the upgraded `@typescript-eslint/eslint-plugin` is not part of the runtime behavior under test. Δt mostly adapts test TypeScript types to match the lint-driven source signature |
| `matrix-org__matrix-js-sdk__5217` | npm_and_yarn | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | Not the tests that actually run. The `test_cmd` runs ONLY `rust-crypto.spec.ts` and `verification.spec.ts`, whose Δt edits are pure TypeScript `as` casts — stripped at runtime by vitest (which uses esbuild/swc and does n |
| `mikavilpas__yazi.nvim__1506` | npm_and_yarn | `UNWITNESSED` | `MIXED` | No. The test_cmd is `tsc --noEmit` (type-check only); it does not execute the cypress e2e tests at all. Δt's changes are type-valid cypress calls (`{force: true}`, `cy.contains(...)`, statement reorder) that do not intro |
| `mozilla__addons-frontend__10931` | npm_and_yarn | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | No. The test_cmd runs only `test_site.js`, which tests the **site** saga. The two Δc changes are in `src/amo/sagas/reviews.js` (import migration) and `src/amo/server/base.js` (`runningSagas.done` -> `runningSagas.toPromi |
| `mozilla__addons-frontend__11753` | npm_and_yarn | `UNWITNESSED` | `MIXED` | No. The Δt removes the very "requires X" runtime-validation tests that would have detected Δc's removal of those guards, and the lone modified assertion (`sendEvent({ action: 'whatever' })` still expecting `category is r |
| `mui__mui-x__18276` | npm_and_yarn | `UNWITNESSED` | `DOCS_EXAMPLE_ONLY` | It exercises the *module-resolution* facet of the breaking change for the `test/regressions` workspace: without Δt, `pnpm --dir /app/test/regressions run build` would fail to resolve `stylis-plugin-rtl`. But Δt fully rep |
| `nextcloud__text__8485` | npm_and_yarn | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | No. The Δt imports `schema` from the newly-added direct dep `prosemirror-schema-basic` (available regardless of Δc) and `EditorState`/`Plugin` from `@tiptap/pm/state` (still present in 3.22.4), then drives `links.js` — w |
| `nukeop__nuclear__1905` | npm_and_yarn | `UNWITNESSED` | `CONFIG_INFRA_ONLY` | Δt fixes the vitest-4 mock-constructor breakage inside the test files themselves, but these are exactly the files Δc does NOT touch. Δc only changes `tsconfig.json` excludes, `validatedStore.ts` (zod generic), and `Scrol |
| `nuxt-community__vuetify-module__426` | npm_and_yarn | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | No. The Δt only shuffles a `<style>` block in a fixture file; it adds no test assertion. The Δc change (`.some(mod => mod === 'nuxt-webfontloader')` -> `.includes('nuxt-webfontloader')`) is functionally equivalent, so th |
| `nuxt__fonts__601` | npm_and_yarn | `UNWITNESSED` | `CONFIG_INFRA_ONLY` | No. The Δt only adds `.sort()` to make the preload-links snapshot order-independent. There is no assertion tied to any dependency behavior — the change is a test-only fix for non-deterministic link ordering. Δc contains  |
| `plotly__react-chart-editor__1025` | npm_and_yarn | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | No. The test_cmd runs ONLY `src/__tests__/syntax-test.js`, which scans test files for blacklisted tokens (`fdescribe`, `fit`, `it.only`, etc.). That scan is behavioral, not formatting-dependent: no reformatted test intro |
| `probot__probot__2090` | npm_and_yarn | `UNWITNESSED` | `MIXED` | No. vitest runs tests at runtime via esbuild (strips types, no type-check). `(_req, res) => res.end("foo")` and `(_req, res) => { res.end("foo"); }` are runtime-identical; express 5 ignores the handler return value. So Δ |
| `sveltejs__kit__14789` | npm_and_yarn | `UNWITNESSED` | `CONFIG_INFRA_ONLY` | No. Δt migrates the test harness to vitest 4's API so the existing tests can *run*, but it does not add any assertion that would fail on P⊕Δm and pass on P⊕Δm⊕Δc. The Δc (kit.vitest.config.js pool options) is not exercis |
| `eakmanrq__sqlframe__450` | pip | `UNWITNESSED` | `MIXED` | No. The dayof* expected-value edits align with sqlglot 27.2's new rendering, but Δc never touches the `dayofweek`/`dayofmonth`/`dayofyear`/`weekofyear` functions — so on P⊕Δm sqlframe already emits `DAYOFWEEK(cola)` (sql |
| `eakmanrq__sqlframe__533` | pip | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | No. With the un-fixed source (P⊕Δm), `pi` still carries `@meta(unsupported_engines="*")`, so on the `duckdb` engine the `get_session_and_func("pi")` harness treats `pi` as unsupported and the `test_pi[duckdb]` case is ** |

## 7. High-Priority Manual/Dynamic Revalidation Cases

These cases deserve first manual or dynamic checks because the static evidence is inconclusive or the patch shape suggests a benchmark-design defect:

| Folder | Ecosystem | Verdict | Δc Nature | Notes |
|---|---|---|---|---|
| `cdk8s-team__kubecon-2020-cdk8s__28` | npm_and_yarn | `INCONCLUSIVE` | `CONFIG_INFRA_ONLY` | - The Δt is projen's default empty `test/hello.test.ts` stub; it provides zero behavioral coverage and cannot witness any source change (there is none). - The entire task is a build-tooling migration: the "breaking chang |
| `dailymotion-oss__octopilot__152` | go_modules | `INCONCLUSIVE` | `MIXED` | The intended repair is genuine and well targeted, but the formal witness is confounded by vendoring: `manifest.patch` updates `go.mod`/`go.sum` and vendored module metadata, while `solution/code.patch` carries the actual |
| `rollup__rollup__5046` | npm_and_yarn | `INCONCLUSIVE` | `MIXED` | - Δc has no runtime effect (`!` is erased), so the witness can only be a compile/typecheck failure; this is fragile and depends on rollup's build pipeline type-checking, which is unconfirmed from the bundle. - Δt address |
| `keystonejs__keystone__8056` | npm_and_yarn | `INCONCLUSIVE` | `REAL_SOURCE_REPAIR` | - Witness is type-level (compile-error) at best; no runtime-failing assertion is added by Δt. Needs confirmation that the jest config type-checks. - Per the problematic review: "Exclude from main benchmark unless documen |
| `renovatebot__renovate__41225` | npm_and_yarn | `INCONCLUSIVE` | `REAL_SOURCE_REPAIR` | - Δt and Δc are mirror-image import pins; the witness risks being circular (Δt breaks v3/v4 coherence, Δc restores it) rather than evidence of a genuine v4 runtime break. - Per the problematic review this is packaged/fla |
| `InfluxCommunity__influxdb3-js__413` | npm_and_yarn | `TESTS_OTHER_THING` | `CONFIG_INFRA_ONLY` | - This can remain useful as an ESLint migration case, but it should not count as a dependency-update source repair witness under the locked definition. |
| `peopledatalabs__peopledatalabs-python__132` | pip | `TESTS_OTHER_THING` | `CONFIG_INFRA_ONLY` | - The hidden test can be satisfied by changing a version constant only. - The dependency under audit is not exercised by the verifier, and the API endpoint fixture changes are excluded by the test selector. |
| `foobaragency__foo-state__321` | npm_and_yarn | `TESTS_OTHER_THING` | `DOCS_EXAMPLE_ONLY` | - The hidden test may fail without Δc, but that failure is for a latent/example behavior, not dependency-update compatibility. - Because the upgraded package is a Jest type package, a valid witness would need a type/buil |
| `BrightspaceUI__intl__106` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | - This is a lint-only task whose test_cmd is `npm run lint`; per the locked definition lint failures are excluded from Level 1, so it should not be in the witnessed main set — yet it is NOT flagged in `problematic_prs_re |
| `amweiss__angular-diff-match-patch__231` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | This is a lint benchmark, not a dependency API repair. It should be separated from the Level 1 witnessed breaking-change set even though it was not flagged in the prior problematic PR review. |
| `asciidoctor__asciidoctor-cli.js__96` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | - The manifest bump changes `fast-deep-equal`, but neither Δc nor Δt shows use of that package. - This should not be counted in the witnessed benchmark even if the lint command fails before Δc. |
| `aws__aws-sdk-pandas__2883` | pip | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | The named dependency is `boto3-stubs`, but the actual failing surface is Ruff lint. The hidden test patch also targets an unrelated geospatial test file that the verifier never runs. |
| `circleci__ex__510` | go_modules | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | - The verifier command is `go test`, not `golangci-lint`, so it converts lint churn into a source/test compile dependency on a new helper. - Because lint failures are excluded by the locked definition, this should not co |
| `cloudant__nodejs-cloudant__400` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | - This is a lint-only task whose test_cmd is `npx eslint .`; per the locked definition, lint failures are excluded from Level 1, so it should not be in the witnessed main set — yet it is NOT flagged in `problematic_prs_r |
| `emberjs__ember.js__19722` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | - This may be a legitimate repository maintenance patch, but it is not suitable as a behavioral breaking-change task. - Dependency-resolution, lint, formatting, and style-rule failures are excluded as witnessed evidence  |
| `fb55__css-what__1184` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | This is low benchmark value. If `npm test` includes lint/format checks, the task is tooling-style only; if it only runs Jest, the formatting changes are likely unwitnessed at runtime. |
| `inrupt__solid-client-authn-js__279` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | This task is a soundness liability for a *witnessed breaking-change* benchmark and should be quarantined: - **test_cmd is `npm run lint`** — a linter, not a test suite; there are no behavioral assertions whatsoever. - Th |
| `ktsn__vue-auto-routing__103` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | Even if `npm test` includes a formatting check and produces a fail/pass, that is explicitly outside the witnessed dependency-breaking definition for this report. |
| `ktsn__vuex-smart-module__189` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | This should not count as a witnessed dependency breaking-change repair. It is a formatting migration task. |
| `laconiajs__laconia__178` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | This should be treated as a lint-rule migration, not a source repair benchmark. The prior problematic review did not flag it, but the command makes the classification unambiguous. |
| `multiformats__js-multiformats__306` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | Because the command begins with `npx aegir lint`, a lint failure can mask whether the actual node test suite would pass on P⊕Δm. This should be excluded from the witnessed main set under the locked definition's lint excl |
| `nikolaik__docker-python-nodejs__306` | pip | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | - The task metadata has `unknown` dependency/version fields. - The verifier runs pytest, not Ruff or mypy, so the source style rewrites are not a meaningful behavioral oracle. |
| `noflo__noflo-polymer__54` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | This should not count as a Level 1 witnessed breaking-change task under the locked definition because the only failure mode is lint. |
| `nuxeo__nuxeo-drive__3833` | pip | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | This task should be excluded from the witnessed benchmark subset. It is useful dependency-maintenance data, but not a breaking source repair. |
| `scratchfoundation__scratch-blocks__3565` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | - This is a lint-only task: test_cmd is `npm run test:lint` and both Δc and Δt are pure cast removals. Per AGENTS.md, lint failures are not valid witnessed breaking changes, so this task should not be in the main (Level- |
| `wireapp__wire-web-packages__2929` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | This task may be operationally useful as a formatter-update task, but it should not be counted in the Level-1 breaking-change benchmark. |
| `inrupt__solid-client-authn-js__3129` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | This is a circular-oracle risk: the hidden tests assert the exact constructor shape that Δc creates. A dynamic run may show FAIL/PASS, but that would not establish a witnessed dependency-update breaking change under the  |
| `integrations__jira__293` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | This appears misattributed: the manifest patch is a lockfile/protocol cleanup, while the oracle patches encode an unrelated application migration. |
| `oceanprotocol__market__1687` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | - Mislabeled / over-broad Δm: `eslint-plugin-testing-library` is only one of many upgrades, and the verifier does not run lint, so it cannot witness an ESLint-plugin breaking change. - Circular oracle risk: most new test |
| `openlayers__ol-mapbox-style__1071` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | - Useful as an ESLint-config migration task, but not as a dependency-update source-repair witness. - The manifest upgrade is broader than the labeled package because it changes ESLint and plugin dependencies alongside `e |
| `runatlantis__atlantis__5209` | go_modules | `TESTS_OTHER_THING` | `MIXED` | - Δc edits test files (`*_test.go`, `testdata/fixtures.go`) that the agent is forbidden to touch; the verifier applies only Δt, which targets the wrong module. Since `go test ./server/controllers/events` compiles the who |
| `FraunhoferIOSB__FROST-Server__1486` | maven | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | - Major circular-oracle problem: an agent can pass by changing three integers in `MqttMessageBus.java` to 4/1000/500, having done nothing about jooq. The "breaking change" attributed to the jooq patch bump is not real. - |
| `mightyiam__eslint-config-love__2120` | npm_and_yarn | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | - The FAIL/PASS signal is circular: Δt adds an expected config entry and Δc adds the matching actual config entry. - This is useful project maintenance, but weak evidence for DependBench's locked breaking-change definiti |
| `elastic__kibana__185906` | npm_and_yarn | `TESTS_OTHER_THING` | `SNAPSHOT_ONLY` | - Δc is purely snapshot regeneration, which the problematic review correctly flags as "oracle/testdata artifacts, not source repair." The agent is instructed not to touch tests, yet the only "repair" is editing snapshot  |
| `oxidecomputer__dropshot__580` | cargo | `TESTS_OTHER_THING` | `TEST_ONLY` | - This is not a breaking-change repair task under the locked definition because Delta c does not repair production code. - The verifier is meaningful for test-suite maintenance after a dependency update, but not for agen |
| `nukeop__nuclear__1905` | npm_and_yarn | `UNWITNESSED` | `CONFIG_INFRA_ONLY` | - Textbook no_code_pass: runtime-irrelevant Δc + Δt that fixes the test-side vitest-4 issues. The two test files in `test_cmd` are not even in packages Δc modifies at runtime. - The real vitest-4 breakage (mock construct |
| `nuxt__fonts__601` | npm_and_yarn | `UNWITNESSED` | `CONFIG_INFRA_ONLY` | - Confirmed by the 2026-06-10 review: "Both unwitnessed and CI workflow only." - This task has no source-code repair at all — the Δc is GitHub Actions version pin bumps, which have zero in-container effect on the verifie |
| `sveltejs__kit__14789` | npm_and_yarn | `UNWITNESSED` | `CONFIG_INFRA_ONLY` | The instruction tells the agent to "fix the source code," but Δc is a vitest config file, not production source — an agent following the constraints literally has no production code to repair. The `library: unknown` labe |
| `jonasbb__serde_with__836` | cargo | `UNWITNESSED` | `DOCS_EXAMPLE_ONLY` | - The test patch reflects real RON 0.10 behavior, but the selected command is `--no-run`, so the behavioral snapshot update is not graded. - A dynamic check of whether this Cargo invocation compiles doctests would be the |
| `mui__mui-x__18276` | npm_and_yarn | `UNWITNESSED` | `DOCS_EXAMPLE_ONLY` | - Clear no_code_pass: the graded build (test/regressions) is fully repaired by Δt alone; Δc is docs-only and out of the test_cmd's scope, so removing Δc leaves the test passing. - The breaking change is real (package ren |
| `asciidoctor__asciidoctor.js__870` | npm_and_yarn | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | This is the most clearly invalid task of the eight. The "test command" is a linter, not a test suite, so the FAIL→PASS transition is a lint failure→lint pass — exactly the failure mode the witnessed definition excludes.  |
| `bbc__psammead__3709` | npm_and_yarn | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | - **Mislabelled instruction.** `instruction.md` says `Bumps \`version\` from 4.17.20 to 4.17.20` and the bundle header's `library` field is `version  4.17.20 -> 4.17.20` — a no-op. The mining adapter grabbed the `version |
| `codemod-js__codemod__387` | npm_and_yarn | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | - Asymmetry: Δt edits empty arrows in **assignment / call-argument** positions (which `no-empty-function` flags), Δc edits empty arrows in **default-parameter** position (which it typically does not). That asymmetry is t |
| `codetheweb__tuyapi__253` | npm_and_yarn | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | - Confirmed unwitnessed; should be excluded from the witnessed main benchmark (matches the 2026-06-10 review recommendation). - The dependency is a dev/lint tool (xo / string-width transitively), not a runtime dependency |
| `nuxt-community__vuetify-module__426` | npm_and_yarn | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | Confirmed unwitnessed (matches the problematic-review flag). Dev lint dependency upgrade with no runtime break; Δc is functionally a no-op and Δt is a non-functional fixture edit. The hidden test cannot detect whether th |
| `bbc__simorgh__9137` | npm_and_yarn | `UNWITNESSED` | `MIXED` | - **Verifier targets the wrong test.** test_cmd runs a single moment-locale test (`ur.test.js`) that is a drive-by unrelated to the Jest/@types/jest upgrade. The 9 Δt files that actually witness the Jest-29 snapshot-form |
| `m-h-c-t__mh-helper-extension__434` | npm_and_yarn | `UNWITNESSED` | `MIXED` | This is a likely linter-migration task packaged with a runtime Jest verifier. If the intended failure is ESLint v6 rule enforcement, the test command should run lint/type-checking directly; as packaged, it does not witne |
| `hetznercloud__cli__940` | go_modules | `UNWITNESSED` | `TEST_ONLY` | Doubly unsound. (1) Δc is entirely in test code/testdata, which the agent is instructed not to edit, so the oracle is unreachable by construction. (2) The verifier applies only Δt (the e2e `network_test.go` change), not  |
| `ashutoshgngwr__noice__673` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `CONFIG_INFRA_ONLY` | - This is a test-runner dependency break rather than production application behavior. - The source hunk in `player_manager.ts` is documentation-only and should not be mistaken for the repair. |
| `tusbar__eslint-config-xo-nextjs__163` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `CONFIG_INFRA_ONLY` | This is a valid unit-test witness for an ESLint-config package, but it is lint-domain behavior. It should not be confused with a runtime application dependency break. |
| `tekumara__typos-lsp__44` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `FORMATTER_LINT_CHURN` | - The pre-phase FAIL is a **lint/format failure** (`npm run lint` = prettier --check), which the locked breaking-change definition **excludes** ("not … lint"). This task is in the benchmark despite that — worth flagging  |
| `authelia__authelia__11445` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | The witness is narrow and somewhat circular: Δt mirrors the source import rewrite rather than adding a behavioral assertion, and the verifier covers only `BaseLoadingPage.test.tsx`, not the broader Vite 8 configuration c |
| `prometheus__client_java__1681` | maven | `WITNESSES_BREAKING_CHANGE` | `MIXED` | The human summary says "lint scripts", and much of Δc is infrastructure churn. The discriminating verifier evidence is still the Java import migration, not lint; the compact `test_cmd` is unextractable, but the generated |
| `sequelize__umzug__572` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | - The task is mislabeled if interpreted as only `pony-cause`: most Delta c hunks are type-only import churn and lint-rule configuration caused by bundled TypeScript/ESLint updates. - The hidden test's direct assertion is |
| `wireapp__wire-webapp__13562` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | This is a type-level witness rather than runtime behavior. That is acceptable here because the verifier command is explicitly a type-check command, not a lint/format-only command. |
| `OWASP__wrongsecrets__1040` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | - The witness is narrow and entirely at the compile level: only the `Constants`→`WrongSecretsConstants` rename is exercised by Δt. The actual SpotBugs-motivated repairs (`StandardCharsets.UTF_8` for `DM_DEFAULT_CHARSET`, |
| `algolia__react-element-to-jsx-string__305` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | - The dependency is a dev/test dependency, so the break is in the project’s tested formatting/build behavior rather than a runtime dependency API. - The hidden tests are focused and not lint/format-only. |
| `alveusgg__alveusgg__871` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | The named dependency is `@eslint/js`, but the manifest patch includes multiple coupled dev-toolchain upgrades. The witnessed issue is best described as an ArrayBuffer/typed-array compatibility repair surfaced by that dep |
| `ampproject__amp-wp__6853` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | - **Mislabeled task**: the witnessed breaking change (hook return type array→object) is a **drive-by code change in the same PR**, NOT caused by the `eslint-plugin-jest 25 -> 26` upgrade. eslint-plugin-jest is a lint plu |
| `apache__iceberg-python__159` | pip | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | The hidden test is weaker than ideal because it relaxes an assertion rather than adding a precise assertion for the Pydantic failure mode. Still, the repaired line is in the tested path and the witness is source-behavior |
| `apache__maven__12057` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | The hidden tests are broad and mostly compile/API compatibility checks rather than narrow behavioral probes. That is still acceptable here because the dependency break is a source compile failure, not lint, network, or r |
| `cryostatio__cryostat-legacy__1880` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | - The witness is primarily compile-level rather than behavioral; many Δt hunks simply mirror Δc constructor-signature changes. - Δt drops some log-observation assertions, so a few original behavioral checks are weakened. |
| `cucumber__cucumber-jvm__2642` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | - Δt mainly mirrors constructor changes in tests; it is not adding new behavioral assertions. - The witness is still valid because the verifier compiles the affected module and the break is a real API/constructor break,  |
| `decaporg__decap-cms__6305` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | The test witness is narrow but directly tied to the removed package subpath; no unrelated test or lint command is involved. |
| `eslint__eslint__17917` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | - This is a tool-script repair rather than ESLint runtime core behavior, but it is still a concrete source compatibility repair for the upgraded dependency. |
| `golangci__golangci-lint__4157` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | - The repair includes a reference YAML update, but the decisive behavior is production linter configuration plumbing. - This is a linter product test, but the verifier is testing golangci-lint's own supported analyzer be |
| `golangci__golangci-lint__4718` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | Strong witness for a wrapper integration change. The reference YAML/jsonschema edits are supporting config artifacts, but the source pass-through is the discriminating repair. |
| `grafana__certmagic-gcs__20` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | The nominal library in the task is Caddy, but the actual API break appears to come through the accompanying `certmagic` upgrade in Δm. This is still a source-level dependency repair, not a test/lint artifact. |
| `jenkinsci__kubernetes-plugin__1101` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | Part of the repair removes a connection-count monitoring extension rather than replacing it, so the task is a compatibility repair with some feature removal. The witness remains source/API compatibility, not lint or infr |
| `ledgersmb__LedgerSMB__8895` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | - The witnessed dependency is not `@eslint/js`; it is the bundled Jest/JSDOM upgrade. The task instruction is misleading. - Several Delta t snapshot changes are dead for this verifier because only `LoginPage.spec.js` is  |
| `matrix-org__matrix-js-sdk__4052` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | Only the `validate.ts` half is exercised by the verifier command. The `authorize.ts` async repair is real but mostly untested here because `authorize.spec.ts` is excluded. |
| `mightyiam__eslint-config-love__2178` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | This is a configuration-output witness rather than an application runtime witness, but it is not a lint-only `test_cmd`; the package's product is the ESLint config, and the tests validate that exported product. |
| `nextcloud__spreed__6266` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | - The test covers the participant sidebar component directly; Δc also updates two call-view components that are not part of the targeted `Participant.spec` run. - The failure is a normal module/component API drift, not l |
| `octokit__auth-oauth-app.js__137` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | Δt contains a lot of formatting noise, but the route-template changes are real and discriminating. The benchmark is still source-repair focused rather than pure formatter churn. |
| `opentripplanner__OpenTripPlanner__5232` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | The hidden test patch is not semantically focused on the breaking API. The case is still witnessed because the selected Maven test path compiles the repaired source and fails before running tests without Δc. |
| `piomin__spring-boot-logging__41` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | - Δt is partly mechanical JUnit 4 -> Jupiter migration, but the targeted Spring context tests still exercise the repaired auto-configuration path. - The manifest patch has large XML formatting churn around the actual Spr |
| `promptfoo__promptfoo__9078` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | - The tests use mocked SDK streams, which is appropriate here because the breaking behavior is provider interpretation of stream messages. - The manifest patch also removes `hono` from package metadata, but the relevant  |
| `talsma-ict__umldoclet__709` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | Clean, narrow witness. The extracted command is unavailable in metadata, but `test_state.py` targets the relevant `UMLOptionsTest`. |

## 8. Methodology and Limitations

Each task was reviewed from a bundle containing `instruction.md`, `manifest.patch`, `solution/code.patch`, `tests/test.patch`, `tests/test_state.py`, extracted `test_cmd`, and `task_summary.json` metadata. Reviewers answered the same seven questions used in the 2026-06-17 smoke audit.

The classification is static. `WITNESSES_BREAKING_CHANGE` means the patch evidence strongly indicates `TEST(P⊕Δm⊕Δt)=FAIL` and `TEST(P⊕Δm⊕Δc⊕Δt)=PASS`; it is not a replacement for the dynamic pre-code witness check that should gate future packaging. `INCONCLUSIVE` means the static evidence was insufficient and the case needs a targeted Harbor trial or manual reproduction.

Locked exclusions are preserved: dependency-resolution failures, network/environment/OOM/timeouts/flakiness, and lint/format-only checks are not Level-1 breaking-change witnesses even if they produce a non-zero verifier exit.

## 9. Implications for Paper Numbers and Benchmark Reporting

The headline full packaged dataset remains 297 tasks, but the main witnessed benchmark should report **205 clean Level-1 cases** unless the excluded cases are repaired and dynamically revalidated. Latent and test-other cases should be characterized separately as evidence about mining noise and test-oracle sensitivity, not agent repair difficulty.

For paper tables, keep separate rows for: packaged total, witnessed Level-1, latent/unwitnessed, tests-other, and inconclusive/manual-revalidation. This prevents the benchmark headline from mixing direct dependency-update repair tasks with formatter/lint migrations, weak tests, or unrelated PR drive-by changes.

## 10. Case Reports Index

| Folder | Ecosystem | Verdict | Δc Nature | Flagged |
|---|---|---|---|---|
| `29ki__29k__3418` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `29ki__29k__5244` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `actix__actix__554` | cargo | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `adoptoposs__mjml_nif__117` | cargo | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `adoptoposs__mjml_nif__13` | cargo | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `airlift__airlift__1592` | maven | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | NO |
| `algolia__react-element-to-jsx-string__305` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `alphagov__govuk-frontend__3591` | npm_and_yarn | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | YES |
| `alveusgg__alveusgg__871` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `ampproject__amp-wp__6853` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `amweiss__angular-diff-match-patch__231` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `apache__iceberg-python__159` | pip | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `apache__logging-log4j2__2236` | maven | `TESTS_OTHER_THING` | `MIXED` | NO |
| `apache__logging-log4j2__2345` | maven | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | NO |
| `apache__logging-log4j2__2409` | maven | `TESTS_OTHER_THING` | `MIXED` | NO |
| `apache__logging-log4j2__2600` | maven | `TESTS_OTHER_THING` | `MIXED` | NO |
| `apache__maven__12057` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `apexskier__github-release-commenter__169` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `apexskier__nova-typescript__445` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `appium__appium-uiautomator2-driver__627` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `ArcadeData__arcadedb__2808` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `ardatan__graphql-tools__6921` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `ardatan__graphql-tools__7001` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `ardatan__graphql-tools__7282` | npm_and_yarn | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | NO |
| `arduino__arduino-lint__252` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `asciidoctor__asciidoctor-cli.js__96` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `asciidoctor__asciidoctor.js__870` | npm_and_yarn | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | YES |
| `ashutoshgngwr__noice__673` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `CONFIG_INFRA_ONLY` | NO |
| `authelia__authelia__11445` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `aws__aws-northstar__1037` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | NO |
| `aws__aws-sdk-pandas__2883` | pip | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `AxonIQ__AxonFramework__1654` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `Azure-Samples__chat-with-your-data-solution-accelerator__894` | pip | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `bachya__pytile__346` | pip | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | NO |
| `bbc__psammead__3709` | npm_and_yarn | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | YES |
| `bbc__simorgh__9137` | npm_and_yarn | `UNWITNESSED` | `MIXED` | YES |
| `bbc__simorgh__9275` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `BrightspaceUI__intl__106` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `camunda-community-hub__spring-zeebe__642` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `cawa-93__vite-electron-builder__662` | npm_and_yarn | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | YES |
| `cdk8s-team__kubecon-2020-cdk8s__28` | npm_and_yarn | `INCONCLUSIVE` | `CONFIG_INFRA_ONLY` | NO |
| `chainflip-io__chainflip-sdk-monorepo__166` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `chris48s__v8r__22` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `circleci__ex__510` | go_modules | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `cloudant__nodejs-cloudant__400` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `cloudflare__terraform-provider-cloudflare__1131` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `cloudflare__terraform-provider-cloudflare__1563` | go_modules | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `cloudflare__terraform-provider-cloudflare__2049` | go_modules | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `codemod-js__codemod__387` | npm_and_yarn | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | YES |
| `codetheweb__tuyapi__253` | npm_and_yarn | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | YES |
| `cosmos__cosmos-sdk__19810` | go_modules | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `cryostatio__cryostat-legacy__1880` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `cucumber__cucumber-jvm__2642` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `cucumber__cucumber-jvm__3162` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `curbengh__hexo-yam__135` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `dadoonet__fscrawler__2342` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `dailymotion-oss__octopilot__152` | go_modules | `INCONCLUSIVE` | `MIXED` | NO |
| `databricks__cli__1326` | go_modules | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `DataSQRL__sqrl__1218` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `DataSQRL__sqrl__1229` | maven | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `decaporg__decap-cms__4748` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `decaporg__decap-cms__5178` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `decaporg__decap-cms__6305` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `determined-ai__determined__8316` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `dkhmelenko__autoapproval__343` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `docker__login-action__754` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `dschadow__JavaSecurity__236` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `DSpace__DSpace__10216` | maven | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `dwightjack__vue-types__117` | npm_and_yarn | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | YES |
| `eakmanrq__sqlframe__137` | pip | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `eakmanrq__sqlframe__200` | pip | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `eakmanrq__sqlframe__216` | pip | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `eakmanrq__sqlframe__450` | pip | `UNWITNESSED` | `MIXED` | YES |
| `eakmanrq__sqlframe__466` | pip | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `eakmanrq__sqlframe__492` | pip | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `eakmanrq__sqlframe__533` | pip | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | YES |
| `eakmanrq__sqlframe__581` | pip | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `eakmanrq__sqlframe__589` | pip | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `elastic__apm-agent-java__2792` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `elastic__cloud-on-k8s__3417` | go_modules | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `elastic__cloud-on-k8s__6847` | go_modules | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `elastic__kibana__185906` | npm_and_yarn | `TESTS_OTHER_THING` | `SNAPSHOT_ONLY` | YES |
| `emberjs__ember.js__19722` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `enterprise-contract__ec-cli__2134` | go_modules | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `eslint__eslint__17917` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `eXist-db__exist__4855` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `eXist-db__exist__5042` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `fastify__fastify-http-proxy__171` | npm_and_yarn | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | NO |
| `fb55__css-what__1184` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `firebase__firebase-admin-java__537` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `foobaragency__foo-state__321` | npm_and_yarn | `TESTS_OTHER_THING` | `DOCS_EXAMPLE_ONLY` | NO |
| `FraunhoferIOSB__FROST-Server__1486` | maven | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | NO |
| `frctl__fractal__763` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `freechat-fun__freechat__757` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `geotools__geotools__4212` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `gjtorikian__what_you_say__14` | cargo | `TESTS_OTHER_THING` | `MIXED` | NO |
| `golangci__golangci-lint__4157` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `golangci__golangci-lint__4718` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `GoogleCloudPlatform__spring-cloud-gcp__368` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `grafana__alloy__3602` | go_modules | `TESTS_OTHER_THING` | `MIXED` | NO |
| `grafana__certmagic-gcs__20` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `graphql-hive__graphql-config__1103` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `graphql-hive__graphql-config__1481` | npm_and_yarn | `UNWITNESSED` | `MIXED` | YES |
| `graphql-java-kickstart__graphql-java-tools__560` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `graphql-java-kickstart__graphql-java-tools__645` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `graphql-java-kickstart__graphql-java-tools__800` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `Graylog2__graylog2-server__21446` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `Graylog2__graylog2-server__23926` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `Graylog2__graylog2-server__24634` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `Graylog2__graylog2-server__25652` | maven | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `gruelbox__transaction-outbox__519` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `harvard-lil__js-wacz__41` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `hashicorp__aws-sdk-go-base__796` | go_modules | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `hashicorp__terraform-provider-aws__34096` | go_modules | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | NO |
| `hawtio__hawtio__3776` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `hetznercloud__cli__940` | go_modules | `UNWITNESSED` | `TEST_ONLY` | YES |
| `hetznercloud__hcloud-cloud-controller-manager__628` | go_modules | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `hexojs__hexo-uglify__147` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `huridocs__uwazi__4579` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `huridocs__uwazi__5122` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `imsnif__bandwhich__430` | cargo | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `InfluxCommunity__influxdb3-js__413` | npm_and_yarn | `TESTS_OTHER_THING` | `CONFIG_INFRA_ONLY` | NO |
| `influxdata__telegraf__14250` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `inovex__scrumlr.io__4672` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `INRIA__spoon__6087` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `INRIA__spoon__6316` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `inrupt__solid-client-authn-js__279` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `inrupt__solid-client-authn-js__3129` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | NO |
| `integrations__jira__293` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | NO |
| `iodide-project__iodide__1432` | npm_and_yarn | `UNWITNESSED` | `MIXED` | YES |
| `iterative__dvc__7899` | pip | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `jamcalli__Pulsarr__1107` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | YES |
| `jenkinsci__kubernetes-plugin__1101` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `jenkinsci__warnings-ng-plugin__1278` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `jo-sm__stylelint_d__185` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `jo-sm__stylelint_d__709` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `jonasbb__serde_with__836` | cargo | `UNWITNESSED` | `DOCS_EXAMPLE_ONLY` | NO |
| `JoshuaKGoldberg__create-typescript-app__1489` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `kanton-bern__hellodata-be__315` | maven | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `keystonejs__keystone__8056` | npm_and_yarn | `INCONCLUSIVE` | `REAL_SOURCE_REPAIR` | YES |
| `KnpLabs__server-side-renderer__209` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `kroxylicious__kroxylicious__1221` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `ktsn__capture-all__12` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `ktsn__vue-auto-routing__103` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `ktsn__vuex-smart-module__189` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `kumahq__kuma__3648` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `laconiajs__laconia__178` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `ledgersmb__LedgerSMB__8895` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `ledgersmb__LedgerSMB__8904` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `libp2p__js-libp2p-bootstrap__171` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `liquibase__liquibase__2285` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `LouisBarranqueiro__reapop__397` | npm_and_yarn | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | YES |
| `lukas-krecan__JsonUnit__274` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `m-h-c-t__mh-helper-extension__434` | npm_and_yarn | `UNWITNESSED` | `MIXED` | NO |
| `marocchino__sticky-pull-request-comment__305` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `marp-team__marp-vscode__176` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `matrix-org__matrix-js-sdk__4052` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `matrix-org__matrix-js-sdk__5217` | npm_and_yarn | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | YES |
| `matsim-org__matsim-libs__2586` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `microsoft__lage__346` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | NO |
| `mightyiam__eslint-config-love__2120` | npm_and_yarn | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | NO |
| `mightyiam__eslint-config-love__2178` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `mikavilpas__yazi.nvim__1506` | npm_and_yarn | `UNWITNESSED` | `MIXED` | YES |
| `mike-engel__jwt-cli__214` | cargo | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `mike-engel__jwt-cli__224` | cargo | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `mitmproxy__mitmproxy_rs__142` | cargo | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `mitre__heimdall2__2276` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `mochajs__mocha__5709` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `mozilla__addons-frontend__10931` | npm_and_yarn | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | YES |
| `mozilla__addons-frontend__11753` | npm_and_yarn | `UNWITNESSED` | `MIXED` | YES |
| `mozilla__addons-frontend__9637` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `mozilla__sccache__1190` | cargo | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `mui__mui-x__18276` | npm_and_yarn | `UNWITNESSED` | `DOCS_EXAMPLE_ONLY` | YES |
| `multiformats__js-multiformats__306` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `MystenLabs__fastcrypto__460` | cargo | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `nearform__brokeneck__820` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `nearform__get-jwks__197` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `neo4j__cypher-dsl__373` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `neo4j__neo4j-spark-connector__510` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `nextcloud__server__39964` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `nextcloud__spreed__6266` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `nextcloud__spreed__9915` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `nextcloud__text__8485` | npm_and_yarn | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | YES |
| `nikolaik__docker-python-nodejs__306` | pip | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `noflo__noflo-polymer__54` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `nstapelbroek__gatekeeper__108` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `nukeop__nuclear__1905` | npm_and_yarn | `UNWITNESSED` | `CONFIG_INFRA_ONLY` | YES |
| `nuts-foundation__nuts-node__426` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `nuxeo__nuxeo-drive__3833` | pip | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `nuxt-community__vuetify-module__426` | npm_and_yarn | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | YES |
| `nuxt__fonts__601` | npm_and_yarn | `UNWITNESSED` | `CONFIG_INFRA_ONLY` | YES |
| `oceanprotocol__market__1687` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | NO |
| `octokit__auth-oauth-app.js__137` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `octokit__plugin-paginate-rest.js__226` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `odanado__cloud-cryptographic-wallet__672` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `omjadas__hudsucker__88` | cargo | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `onthegomap__maplibre-contour__34` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `onthegomap__planetiler__1391` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `onthegomap__planetiler__1430` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `onthegomap__planetiler__1512` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `onthegomap__planetiler__685` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `open-telemetry__opentelemetry-go__1872` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `open-telemetry__opentelemetry-go__1943` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `OpenFeign__querydsl__1685` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `opengovsg__askgovsg__150` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `openlayers__ol-mapbox-style__1071` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | NO |
| `OpenNMS__opennms__6191` | maven | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | NO |
| `OpenRefine__OpenRefine__7503` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `opentripplanner__OpenTripPlanner__5232` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `opentripplanner__OpenTripPlanner__5280` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `opentripplanner__OpenTripPlanner__5430` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `opentripplanner__OpenTripPlanner__6603` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `operaton__operaton__1523` | maven | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `operator-framework__java-operator-sdk__178` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `option-t__option-t__1911` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `OWASP__wrongsecrets__1040` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `OWASP__wrongsecrets__874` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `OWASP__wrongsecrets__970` | maven | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `owncloud__web__11511` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `oxidecomputer__dropshot__1556` | cargo | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `oxidecomputer__dropshot__501` | cargo | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `oxidecomputer__dropshot__580` | cargo | `TESTS_OTHER_THING` | `TEST_ONLY` | NO |
| `oxidecomputer__dropshot__630` | cargo | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `paularmstrong__onerepo__595` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `peopledatalabs__peopledatalabs-python__132` | pip | `TESTS_OTHER_THING` | `CONFIG_INFRA_ONLY` | NO |
| `piomin__spring-boot-logging__41` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `plotly__react-chart-editor__1025` | npm_and_yarn | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | YES |
| `pomerium__pomerium__3198` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `pr-triage__app__251` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | NO |
| `prettier__prettier__10546` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `prettier__prettier__12241` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `prettier__prettier__8688` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `prettier__prettier__8890` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | NO |
| `probot__probot__2090` | npm_and_yarn | `UNWITNESSED` | `MIXED` | YES |
| `prometheus__client_java__1402` | maven | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `prometheus__client_java__1681` | maven | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `prometheus__client_java__1724` | maven | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `promptfoo__promptfoo__8808` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `promptfoo__promptfoo__8918` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `promptfoo__promptfoo__8920` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | NO |
| `promptfoo__promptfoo__8946` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | NO |
| `promptfoo__promptfoo__9078` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `promptfoo__promptfoo__9079` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | NO |
| `python-telegram-bot__python-telegram-bot__4024` | pip | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `qntm__base65536__37` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `qntm__base65536__49` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | NO |
| `querydsl__querydsl__2878` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `questdb__questdb__6374` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `rash-sh__rash__698` | cargo | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `reearth__resium__609` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `reearth__resium__625` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `regexident__cargo-modules__122` | cargo | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `regexident__cargo-modules__389` | cargo | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `renovatebot__renovate__35752` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `renovatebot__renovate__36455` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `renovatebot__renovate__41225` | npm_and_yarn | `INCONCLUSIVE` | `REAL_SOURCE_REPAIR` | YES |
| `rollup__rollup__5046` | npm_and_yarn | `INCONCLUSIVE` | `MIXED` | YES |
| `runatlantis__atlantis__5209` | go_modules | `TESTS_OTHER_THING` | `MIXED` | YES |
| `runfinch__finch__365` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `saveourtool__diktat__1039` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `saveourtool__diktat__1529` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `scaffdog__scaffdog__728` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `scaleway__scaleway-lib__83` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `scinos__yarn-deduplicate__89` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `scratchfoundation__scratch-blocks__3565` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | YES |
| `scx567888__live-room-watcher__209` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `sequelize__umzug__428` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `sequelize__umzug__572` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `skovhus__jest-codemods__266` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `sladkoff__minecraft-prometheus-exporter__68` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `slowli__jwt-compact__138` | cargo | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `smallstep__certificates__2097` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `smlx__piv-agent__155` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `smol-rs__async-lock__69` | cargo | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `solana-labs__solana-program-library__4301` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `sourcenetwork__defradb__1577` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `spiffe__spire__4184` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `stormforger__cli__220` | go_modules | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | NO |
| `Stranger6667__jsonschema__825` | cargo | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `strawberry-graphql__strawberry__282` | pip | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `sumup-oss__circuit-ui__837` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | NO |
| `sveltejs__kit__14789` | npm_and_yarn | `UNWITNESSED` | `CONFIG_INFRA_ONLY` | YES |
| `synyx__urlaubsverwaltung__2494` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `talsma-ict__umldoclet__709` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `tekumara__typos-lsp__44` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `FORMATTER_LINT_CHURN` | NO |
| `tusbar__eslint-config-xo-nextjs__163` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `CONFIG_INFRA_ONLY` | NO |
| `typescript-eslint__tslint-to-eslint-config__1192` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `urlaubsverwaltung__urlaubsverwaltung__4808` | maven | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `vectordotdev__vrl__440` | cargo | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `verdaccio__verdaccio__5742` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | YES |
| `wayfair-incubator__pygitops__272` | pip | `TESTS_OTHER_THING` | `MIXED` | NO |
| `webhintio__hint__4027` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |
| `wireapp__wire-web-packages__2929` | npm_and_yarn | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | NO |
| `wireapp__wire-webapp__13562` | npm_and_yarn | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `xt0rted__slash-command-action__307` | npm_and_yarn | `TESTS_OTHER_THING` | `MIXED` | NO |
| `yahoo__elide__2476` | maven | `WITNESSES_BREAKING_CHANGE` | `MIXED` | NO |
| `ymtdzzz__otel-tui__153` | go_modules | `WITNESSES_BREAKING_CHANGE` | `REAL_SOURCE_REPAIR` | NO |

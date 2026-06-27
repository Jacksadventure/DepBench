# Test-Patch Audit — Inter-Coder Agreement (codex vs opencode)

Date: 2026-06-26 · Index: `agreement-index-merged.json` · Tasks: 219

- codex: `gpt-5.3-codex`
- opencode: `github-copilot/gemini-3.1-pro-preview`

## Headline agreement

| Label | n scored | % agreement | Cohen's κ |
| --- | --- | --- | --- |
| 4-way verdict | 219 | 0.840 | 0.527 |
| binary (witness vs not) | 219 | 0.845 | 0.532 |

## Parse status (verdict recovered from: ok=VERDICT.json, json_repaired=JSON in log, verdict_line='VERDICT:' line)

| Agent | ok | json_repaired | verdict_line | missing | total |
| --- | --- | --- | --- | --- | --- |
| codex | 219 | 0 | 0 | 0 | 219 |
| opencode | 173 | 0 | 46 | 0 | 219 |

## Verdict distribution

| Verdict | codex | opencode |
| --- | --- | --- |
| WITNESSES_BREAKING_CHANGE | 185 | 163 |
| UNWITNESSED | 4 | 3 |
| TESTS_OTHER_THING | 30 | 53 |
| INCONCLUSIVE | 0 | 0 |
| (unparsed/empty) | 0 | 0 |

## Confusion matrix (rows = codex, cols = opencode)

| codex \ opencode | WITNESSES_BREAKING_CHANGE | UNWITNESSED | TESTS_OTHER_THING | INCONCLUSIVE |
| --- | --- | --- | --- | --- |
| WITNESSES_BREAKING_CHANGE | 157 | 2 | 26 | 0 |
| UNWITNESSED | 2 | 1 | 1 | 0 |
| TESTS_OTHER_THING | 4 | 0 | 26 | 0 |
| INCONCLUSIVE | 0 | 0 | 0 | 0 |

## Disagreements (35)

| task | codex | opencode | codex rationale | opencode rationale |
| --- | --- | --- | --- | --- |
| 29ki__29k__3418 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Dm upgrades openai to 4.0.1, where the client API differs from v3. Dt updates the existing unit test to the v4 client/mocked response shape without adding new p | Dm bumps openai from 3.3.0 to 4.0.1. Dt updates the openai mock in openAi.spec.ts to match the v4 API structure (e.g. chat.completions.create). Because the unit |
| BramVR__gohealthcli__351 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Dm upgrades modernc.org/sqlite to 1.52.0, and both instruction metadata and Dc indicate changed float CAST-to-TEXT rendering. Dt adds/updates tests that assert  |  |
| Graylog2__graylog2-server__21446 | WITNESSES_BREAKING_CHANGE | UNWITNESSED | Dm bumps protobuf BOM to 3.25.6. Dc includes substantial regeneration of NetFlowV9Journal.java (map/reflection/accessor and parser scaffolding changes) consiste | The test patch (Dt) solely removes an unused `throws IOException` declaration (and its import) from `RawMessageTest.java` to fix a compiler/linter warning, matc |
| JoshuaKGoldberg__create-typescript-app__1489 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Dm upgrades the declared pnpm version to 9.0.6, while pre-repair source still hardcodes 8.15.4 in generated package.json output. Dt updates assertions to expect | The PR updates the packageManager field in package.json from pnpm 8.15.4 to 9.0.6. This does not cause a failure in the existing code. However, the product itse |
| OpenFeign__querydsl__1685 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Dm upgrades Hibernate to 7.3.1.Final, and Dt updates JPQL serializer expectations from Long to Integer for subquery limit/offset constants. Without Dc, JPQLSeri | The upgrade to Hibernate 7.3 introduces stricter parameter typing and requires Integer for limits, which Dc fixes. However, the verifier command excludes integr |
| ashutoshgngwr__noice__673 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Dm upgrades Jest to 27, while Dt adapts test timer setup to Jest 27 (`useFakeTimers("legacy")`) without adding new product assertions. The substantial Dc edits  | The PR upgrades Jest (a devDependency). Jest 27 introduces two breaking changes: the default testEnvironment changed to node, and useFakeTimers changed to moder |
| camunda-community-hub__spring-zeebe__642 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Dm bumps zeebe.version to 8.4.3 and Dt adds a focused regression test asserting fetch-variable filtering must not be altered when an ActivatedJob parameter is i | The PR bundles a dependency upgrade with a drive-by feature/bugfix. Dt adds a pure unit test asserting that variables are not filtered if 'ActivatedJob' is inje |
| cloudflare__terraform-provider-cloudflare__2049 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Static diffs indicate cloudflare-go 0.55.0 changes Workers KV APIs (method names/signatures and account-scoped parameters). With only Dm+Dt, tests should still  | The PR upgrades cloudflare-go to v0.55.0, which changes KV namespace APIs to require an AccountIdentifier. The minimal repair is to pass the existing client.Acc |
| cosmos__cosmos-sdk__19810 | TESTS_OTHER_THING | WITNESSES_BREAKING_CHANGE | Dt is circular with Dc: it changes the test to reference `ContentTypeText`, a constant added only by Dc. Therefore `P+Dm+Dt` can fail for missing-symbol reasons | The manifest patch bumps cosmossdk.io/store and prometheus/common. In prometheus v0.50.0, 'expfmt.FmtText' was removed, causing telemetry/metrics.go to fail com |
| eakmanrq__sqlframe__137 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Dm widens sqlglot to include 25.10.x. Dt updates convert_timezone assertions in two ways: SQL rendering must now cast source timestamps, and runtime expectation | The PR leverages a new exp.ConvertTimezone node introduced in the sqlglot dependency upgrade to add cross-engine support for `convert_timezone` in sqlframe. Dc  |
| eakmanrq__sqlframe__200 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Static evidence indicates sqlglot 25.29->25.32 changes function parsing/classification. Dt accommodates several newly specialized functions, but still leaves a  | The verifier is restricted to two tests. One (`test_regexp_extract_all`) passes without Dc. The other (`test_invoke_anonymous`) is a custom reflection-based lin |
| eakmanrq__sqlframe__216 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Dm bumps sqlglot to include newer 25.34 behavior. Dt then expects UTC-centered, mostly naive datetime semantics (including to_timestamp/current_timezone-related | The hidden test patch Dt rewrites the test suite's timezone handling, changing the global TZ environment variable to UTC and enforcing unified timezone semantic |
| eakmanrq__sqlframe__492 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Dm permits sqlglot 27.11.x, where function parsing/type mapping appears to have shifted for wrappers checked by test_invoke_anonymous. Pre-repair, ntile and reg | The task fails because a custom meta-test in pytest uses `inspect.getsource()` to enforce that `sqlframe` uses native `sqlglot` AST nodes instead of anonymous f |
| elastic__cloud-on-k8s__6847 | UNWITNESSED | WITNESSES_BREAKING_CHANGE | Dt is not a pure test update; it patches production files and is force-applied after restoring those files from baseline in test_state.py. The verifier then run | The upgrade of controller-runtime to v0.15.0 introduces breaking API changes to source.Kind, handlers, and webhook initialization. Dt updates test utilities to  |
| giantswarm__muster__751 | TESTS_OTHER_THING | WITNESSES_BREAKING_CHANGE | Dt does not just check compatibility at public API boundaries; it introduces a new test for k8sSASubPattern, a helper function added in Dc. That creates a circu |  |
| golangci__golangci-lint__4718 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Dm upgrades sloglint to 0.7.0, while Dt adds a new sloglint testdata case and config using forbidden-keys. Without Dc, the project’s sloglint integration does n | The PR updates sloglint from v0.6.0 to v0.7.0 and concurrently exposes a newly added feature ('forbidden-keys') in golangci-lint. Dc implements the configuratio |
| jamcalli__Pulsarr__1107 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Dm upgrades @fastify/env and drops dotenv from manifest. Pre-fix code still imports/calls dotenv in logger/env-loading paths; under upgraded deps this is a depe |  |
| ledgersmb__LedgerSMB__8904 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Dm upgrades Jest/babel-jest stack to 30.x, and Dt correspondingly removes the prior window.location override approach in test setup. With P+Dm+Dt, LoginPage sti |  |
| mightyiam__eslint-config-love__2178 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | The hidden test patch updates an expected ESLint rule map with 'preserve-caught-error', matching a rule introduced/required by the eslint 9.35.0 upgrade in Dm.  | The dependency bump to eslint 9.35.0 (a minor release) added a new rule, `preserve-caught-error`. The developers opportunistically adopted this new feature by a |
| mozilla__addons-frontend__9637 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | The dependency bump changes the ChunkExtractor API from singular to plural required-chunks script method. Dt updates tests to provide/assert getRequiredChunksSc | The verifier only runs `TestServerHtml.js`, which completely mocks the `@loadable/server` dependency using a fake `chunkExtractor` factory. Because the real dep |
| nextcloud__server__39964 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Dm upgrades camelcase from 6.3.0 to 8.0.0 (pure ESM). Dt adds a Jest test that imports apps/systemtags/src/utils, which imports camelcase at module load. In pre | The dependency `camelcase` is upgraded to v8.0.0, which is pure ESM. The hidden test patch (`Dt`) introduces a new unit test, and the verifier strictly runs onl |
| omjadas__hudsucker__88 | UNWITNESSED | TESTS_OTHER_THING | `rustls-pemfile` 2.0 changes parsing APIs from vector-like returns to iterator/item wrappers, so pre-fix code using `.expect(...).remove(0)` is expected to fail | The dependency rustls-pemfile is a dev-dependency, and its API break (returning an iterator of Results instead of a Vec) only impacts tests. The source repair ( |
| owncloud__web__11511 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Dm upgrades Vue to 3.5.4 and Dt updates 12 unit tests to the post-upgrade expectations. Dc contains substantive runtime fixes in shared test-helper source (Rout | The Vue 3.5 upgrade breaks the test suite because reactivity changes cause errors with the test harness's mockDeep proxies and component stubbing in web-test-he |
| oxidecomputer__dropshot__1556 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Dm bumps serde_tokenstream to 0.2.3, and Dc changes VersionRange parse error span construction from a parsed token-derived span to the full input token stream.  | The serde_tokenstream 0.2.3 upgrade correctly preserves spans, changing the compiler error output from an incorrect 7-character span to the true 2-character spa |
| prettier__prettier__10546 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | The hidden test patch adds TypeScript Babel-only snapshot coverage for `import type` import-equals declarations, which is directly tied to the parser upgrade. T | The PR upgraded @babel/parser to 7.13.11 to support TypeScript 4.3's `import type = require(...)` syntax. Dc implements Prettier's formatting for this new AST n |
| prettier__prettier__12241 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Dm upgrades @babel/parser to 7.17.0. Dt introduces regex v-flag coverage where babel/babel-ts/babel-flow are expected to parse /a/v and emit specific errors for |  |
| prometheus__client_java__1724 | WITNESSES_BREAKING_CHANGE | UNWITNESSED | The manifest bump changes protobuf from 4.33.1 to 4.33.2, and both Dt and Dc consistently adapt references from generated package `com_google_protobuf_4_33_1` t |  |
| promptfoo__promptfoo__8918 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Dt updates the opencode provider oracle for SDK 1.14 token metadata: optional total, reasoning, and cache as either a number or {read, write}. Before Dc, tokenU |  |
| saveourtool__diktat__1529 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | The manifest bump upgrades kotlin-logging-jvm to 3.0.3 and removes direct SLF4J support in module manifests, while pre-repair code still references org.slf4j AP | The hidden test patch (Dt) exclusively adds a unit test for a new exception in the `EmptyBlock` linter rule. This exception was introduced in the human source r |
| sequelize__umzug__572 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Static evidence indicates P+Dm+Dt likely fails during `npm run build` due dependency-driven type/toolchain incompatibilities introduced by Dm (notably TS/typing | The hidden test patch (Dt) exclusively updates an inline snapshot in `cli.test.ts` to expect `import type` rather than `import` in generated template files. Thi |
| smlx__piv-agent__155 | TESTS_OTHER_THING | WITNESSES_BREAKING_CHANGE | Static review shows Dm upgrades x/crypto and Dc performs real source migration (x/term and ProtonMail openpgp). However Dt is not a neutral witness: it introduc | The update to golang.org/x/crypto v0.7.0 removes the deprecated openpgp package, causing production code to fail to compile. The repair (Dc) migrates to ProtonM |
| solana-labs__solana-program-library__4301 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Dm upgrades @solana/spl-token from 0.1.8 to 0.3.7, while Dc rewrites production code away from deprecated/removed Token-class APIs (associated account creation, | The hidden test patch (Dt) circularly asserts the specific refactoring choices made by the human in Dc rather than the observable behavior. Specifically, Dc lev |
| tusbar__eslint-config-xo-nextjs__163 | WITNESSES_BREAKING_CHANGE | TESTS_OTHER_THING | Dm upgrades @next/eslint-plugin-next to 10.2.2 while pre-fix config still manually declares plugin/rules in the old shape. Dt then checks new/updated Next rule  | The dependency upgrade changed the error messages of existing ESLint rules, causing the original CI to fail. The human fixed this by updating the expected messa |
| ubugeeei-prod__ox-content__131 | UNWITNESSED | WITNESSES_BREAKING_CHANGE | Static evidence indicates Dm introduces real Rust API breakage and Dc is a substantive Rust repair, so pre-code failure and post-code pass are plausible. Howeve | P+Dm fails to compile due to significant oxc API changes (e.g., removal of BindingPatternKind), satisfying the pre-code failure criterion. Dc repairs the produc |
| ymtdzzz__otel-tui__153 | TESTS_OTHER_THING | WITNESSES_BREAKING_CHANGE | Static review predicts Dm+Dt fails and Dm+Dc+Dt passes, but Dt is circular: it references `comp.hostWrapper`, a private implementation detail introduced by Dc.  | Dm bumps otel-collector dependencies to 0.108.0, moving component status reporting to a new componentstatus package. Dt updates the test file to accommodate the |

Full per-task labels: `harbor_benchmark/reports/test_patch_agreement_2026-06-26.csv`

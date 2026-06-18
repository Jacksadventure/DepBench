# Clean-Set Pruning Recommendations — 2026-06-18

Blind file-level review of the 92 tasks whose audit verdict was not `WITNESSES_BREAKING_CHANGE`. The committed dataset removes DELETE tasks and keeps WITNESSES + KEEP + DYNAMIC tasks.

## Result

| Action | Count |
|---|---:|
| KEEP | 14 |
| DYNAMIC | 9 |
| DELETE | 69 |

## Dataset size after pruning

- Original task count: 297
- Removed tasks: 69
- Remaining task count: 228

| Ecosystem | Original | Removed | Remaining | Remaining % |
|---|---:|---:|---:|---:|
| cargo | 23 | 1 | 22 | 9.6% |
| go_modules | 35 | 4 | 31 | 13.6% |
| maven | 74 | 7 | 67 | 29.4% |
| npm_and_yarn | 145 | 50 | 95 | 41.7% |
| pip | 20 | 7 | 13 | 5.7% |
| **Total** | 297 | 69 | 228 | 100.0% |

## KEEP

| Folder | Reason |
|---|---|
| `airlift__airlift__1592` | HttpServerConfig default is directly exercised by TestHttpServerConfig after airbase upgrade. |
| `alphagov__govuk-frontend__3591` | Rollup 3/plugin migration is exercised by build package/release tests. |
| `dailymotion-oss__octopilot__152` | yq v4 API migration is exercised by yaml/yq tests; keep with vendor caveat. |
| `eakmanrq__sqlframe__533` | sqlglot/DuckDB pi behavior is directly exercised by test_pi[duckdb]. |
| `fastify__fastify-http-proxy__171` | ws 8 URL-scheme migration is exercised by websocket URL conversion tests. |
| `gjtorikian__what_you_say__14` | magnus/Rust API migration is witnessed by bundle exec rake compile. |
| `hashicorp__terraform-provider-aws__34096` | AWS SDK pointer-type helper is directly exercised by flex Int32FromFramework test. |
| `integrations__jira__293` | Sequelize 4->5 findByPk migration is exercised by /verify endpoint test. |
| `prettier__prettier__8890` | cosmiconfig 7 .cjs config loading is directly exercised by config-resolution tests. |
| `promptfoo__promptfoo__8920` | fal client option split is exercised by provider option forwarding tests. |
| `promptfoo__promptfoo__8946` | Claude Agent SDK option forwarding is exercised by provider tests. |
| `renovatebot__renovate__41225` | zod v4/v3 import compatibility may be directly exercised by schema/error tests; keep with mirror-patch caveat. |
| `runatlantis__atlantis__5209` | go-github v68 pointer helper/import migration is compile-tested in server controllers. |
| `xt0rted__slash-command-action__307` | @actions/github Octokit API migration is exercised by Jest tests. |

## DYNAMIC

| Folder | Reason |
|---|---|
| `cdk8s-team__kubecon-2020-cdk8s__28` | projen config migration; hidden test is empty, needs dynamic proof. |
| `dwightjack__vue-types__117` | TypeScript 4.3 type/generic fix; depends on whether npm test type-checks. |
| `graphql-hive__graphql-config__1481` | minimatch import/path fix is real, but hidden patch mostly TS comments. |
| `jonasbb__serde_with__836` | RON 0.10 behavior appears real, but cargo test --no-run does not execute snapshot. |
| `keystonejs__keystone__8056` | Markdoc widened return type; likely type-level witness, needs Jest type-check confirmation. |
| `matrix-org__matrix-js-sdk__5217` | matrix crypto wasm API rename may be real, but verifier coverage needs proof. |
| `mikavilpas__yazi.nvim__1506` | TS API/type repair; tsc witness needs dynamic proof. |
| `mozilla__addons-frontend__10931` | redux-saga API repair is real, but selected test_site.js coverage needs proof. |
| `rollup__rollup__5046` | locate-character ESM/nullable break plausible; source fix is type-only and needs build proof. |

## DELETE

| Folder | Original verdict | Δc nature | Upgrade |
|---|---|---|---|
| `BrightspaceUI__intl__106` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | eslint-config-brightspace 0.17 -> 0.18 (and Δm also widens the lint script from `eslint lib test --ext .js` to `eslint . --ext .js`, and adds `eslint-plugin-import`). |
| `FraunhoferIOSB__FROST-Server__1486` | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | jooq.version 3.16.14 -> 3.16.15 |
| `Graylog2__graylog2-server__25652` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | com.google.errorprone:error_prone_core 2.48.0 -> 2.49.0 |
| `InfluxCommunity__influxdb3-js__413` | `TESTS_OTHER_THING` | `CONFIG_INFRA_ONLY` | eslint 8.43.0 -> 9.10.0 |
| `LouisBarranqueiro__reapop__397` | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | prettier 2.2.1 -> 2.3.0 |
| `OpenNMS__opennms__6191` | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | hessian 3.1.5 -> 4.0.66 |
| `amweiss__angular-diff-match-patch__231` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | xo 0.38.2 -> 0.39.1 |
| `apache__logging-log4j2__2236` | `TESTS_OTHER_THING` | `MIXED` | org.springframework.cloud:spring-cloud-context 4.1.0 -> 4.1.1 |
| `apache__logging-log4j2__2345` | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | org.codehaus.groovy:groovy-bom 3.0.20 -> 3.0.21 (manifest also bumps commons-dbcp2 2.11.0 -> 2.12.0) |
| `apache__logging-log4j2__2409` | `TESTS_OTHER_THING` | `MIXED` | mongodb.version 3.12.11 -> 3.12.14 |
| `apache__logging-log4j2__2600` | `TESTS_OTHER_THING` | `MIXED` | org.apache.logging:logging-parent 11.0.0 -> 11.1.0 |
| `ardatan__graphql-tools__7282` | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | @babel/plugin-transform-regenerator 7.28.0 -> 7.28.1 |
| `asciidoctor__asciidoctor-cli.js__96` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | fast-deep-equal 2.0.1 -> 3.1.1 |
| `asciidoctor__asciidoctor.js__870` | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | ignore 3.0.9 -> 5.0.0 (PR was actually a `standard` linter upgrade 12.0.1 -> 14.3.3; `ignore` is a transitive dep) |
| `aws__aws-northstar__1037` | `TESTS_OTHER_THING` | `MIXED` | ws 7.5.9 -> 7.5.10 |
| `aws__aws-sdk-pandas__2883` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | boto3-stubs 1.34.131 -> 1.34.136 |
| `bachya__pytile__346` | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | mypy 1.6.1 -> 1.7.0 |
| `bbc__psammead__3709` | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | prettier 2.0.5 -> 2.1.1 (real upgrade in `package-lock.json` lines 92-99 + CHANGELOG entries). NOTE: the bundle header and `instruction.md` mislabel this as `version 4.17.20 -> 4.17.20` (a literal no-op string — the mining adapter picked up the `version` field of an internal package instead of the `prettier` dependency). |
| `bbc__simorgh__9137` | `UNWITNESSED` | `MIXED` | `@types/jest` 26.0.24 -> 29.5.2 (labeled library); manifest.patch actually bumps the whole Jest stack together — `jest` 26.6.3→29.6.1, `babel-jest` 26.6.3→29.6.1, `jest-environment-jsdom` 26.6.2→29.6.1, `ts-jest` 26.5.6→29.1.1, `@types/jest` 26.0.24→29.5.2. |
| `cawa-93__vite-electron-builder__662` | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | vitest 0.0.136 -> 0.0.137 |
| `circleci__ex__510` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | github.com/golangci/golangci-lint 1.51.1 -> 1.51.2 |
| `cloudant__nodejs-cloudant__400` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | the mined "library" field is a bogus transitive `resolved` URL change (acorn 3.3.0 tarball `http://` -> `https://`); the real semantic change in `package.json` is `eslint ^3.19.0 -> ^4.18.2` (plus `eslint-config-*` stays). So the effective upgrade is **eslint 3 -> 4**. |
| `codemod-js__codemod__387` | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | @typescript-eslint/eslint-plugin 2.9.0 -> 2.11.0 (also @typescript-eslint/parser) |
| `codetheweb__tuyapi__253` | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | string-width 2.0.0 -> 3.0.0 (actual upstream PR is a Renovate `xo` linter bump to v0.25.3; string-width is a transitive dep) |
| `eakmanrq__sqlframe__450` | `UNWITNESSED` | `MIXED` | sqlglot >=24.0.0,<27.1 -> >=24.0.0,<27.2 |
| `elastic__kibana__185906` | `TESTS_OTHER_THING` | `SNAPSHOT_ONLY` | @elastic/charts 65.2.0 -> 66.0.3 |
| `emberjs__ember.js__19722` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | eslint-plugin-qunit 4.0.0 -> 6.2.0 |
| `fb55__css-what__1184` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | prettier 2.8.8 -> 3.1.1 |
| `foobaragency__foo-state__321` | `TESTS_OTHER_THING` | `DOCS_EXAMPLE_ONLY` | @types/jest 28.1.0 -> 29.2.0 |
| `grafana__alloy__3602` | `TESTS_OTHER_THING` | `MIXED` | cloud.google.com/go/pubsub 1.49.0 -> 1.50.0 |
| `hetznercloud__cli__940` | `UNWITNESSED` | `TEST_ONLY` | github.com/hetznercloud/hcloud-go/v2 2.17.0 -> 2.17.1 |
| `inrupt__solid-client-authn-js__279` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | prettier 1.19.1 -> 2.1.0 |
| `inrupt__solid-client-authn-js__3129` | `TESTS_OTHER_THING` | `MIXED` | @typescript-eslint/eslint-plugin 5.6.0 -> 6.6.0 |
| `iodide-project__iodide__1432` | `UNWITNESSED` | `MIXED` | babel-jest 23.6.0 -> 24.7.1 (plus jest 23.6.0 -> 24.7.1 and jest-cli 23.6.0 -> 24.7.1; manifest also renames the jest 23 `setupTestFrameworkScriptFile` option to the jest 24 `setupFilesAfterEnv` array) |
| `ktsn__capture-all__12` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | prettier 1.19.1 -> 2.0.5 |
| `ktsn__vue-auto-routing__103` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | prettier 1.19.1 -> 2.0.5 |
| `ktsn__vuex-smart-module__189` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | prettier 1.19.1 -> 2.0.5 |
| `laconiajs__laconia__178` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | eslint-config-standard 12.0.0 -> 13.0.1 |
| `m-h-c-t__mh-helper-extension__434` | `UNWITNESSED` | `MIXED` | @typescript-eslint/eslint-plugin 5.60.1 -> 6.3.0 |
| `microsoft__lage__346` | `TESTS_OTHER_THING` | `MIXED` | jest 27.2.0 -> 29.0.3 |
| `mightyiam__eslint-config-love__2120` | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | eslint-plugin-import 2.31.0 -> 2.32.0 |
| `mochajs__mocha__5709` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | prettier 3.6.2 -> 3.8.1 |
| `mozilla__addons-frontend__11753` | `UNWITNESSED` | `MIXED` | flow-bin 0.176.0 -> 0.183.0 |
| `mui__mui-x__18276` | `UNWITNESSED` | `DOCS_EXAMPLE_ONLY` | `@mui/monorepo` github:mui/material-ui#8cd3aa58 -> #9b3d36ed (a digest bump of the internal mui/material-ui dep). The material-ui bump renamed/replaced the `stylis-plugin-rtl` package with `@mui/stylis-plugin-rtl`. |
| `multiformats__js-multiformats__306` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | aegir 43.0.1 -> 44.1.1 |
| `nextcloud__text__8485` | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | @tiptap/core 3.22.3 -> 3.22.4 (also @tiptap/extension-collaboration, -drag-handle, -drag-handle-vue-2, @tiptap/pm, @tiptap/vue-2 → 3.22.4; adds direct deps `prosemirror-markdown` and `prosemirror-schema-basic`) |
| `nikolaik__docker-python-nodejs__306` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | unknown unknown -> unknown |
| `noflo__noflo-polymer__54` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | eslint-config-airbnb-base 13.0.0 -> 14.2.0 |
| `nukeop__nuclear__1905` | `UNWITNESSED` | `CONFIG_INFRA_ONLY` | @vitest/coverage-v8 3.2.4 -> 4.0.0 (vitest 3.2.4 -> 4.0.0) |
| `nuxeo__nuxeo-drive__3833` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | codespell ==2.1.0 -> ==2.2.4 |
| `nuxt-community__vuetify-module__426` | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | @nuxtjs/eslint-config-typescript 4.0.0 -> 6.0.1 |
| `nuxt__fonts__601` | `UNWITNESSED` | `CONFIG_INFRA_ONLY` | @iconify-json/simple-icons 1.2.31 -> 1.2.33 (manifest also bumps @nuxt/devtools-kit, fontaine, magic-regexp, tinyglobby, unplugin, eslint, playwright-core, vite, vitest, sass, tailwindcss, etc.) |
| `oceanprotocol__market__1687` | `TESTS_OTHER_THING` | `MIXED` | eslint-plugin-testing-library 5.5.1 -> 5.6.4 (labeled; Δm also upgrades Jest 28 -> 29, Storybook 6.5.x, @testing-library/react 13.3 -> 13.4, TypeScript 4.7 -> 4.8, urql, web3, and many lockfile packages) |
| `onthegomap__maplibre-contour__34` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | prettier 2.8.8 -> 3.0.0 |
| `openlayers__ol-mapbox-style__1071` | `TESTS_OTHER_THING` | `MIXED` | eslint-config-openlayers 18.0.0 -> 19.0.0 |
| `option-t__option-t__1911` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | prettier 2.8.8 -> 3.0.0 |
| `oxidecomputer__dropshot__580` | `TESTS_OTHER_THING` | `TEST_ONLY` | toml 0.5.11 -> 0.7.0 (metadata labels library as `version`) |
| `peopledatalabs__peopledatalabs-python__132` | `TESTS_OTHER_THING` | `CONFIG_INFRA_ONLY` | annotated-types 7.4.4 -> 7.5.1 |
| `plotly__react-chart-editor__1025` | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | prettier 1.19.1 -> 2.0.2 |
| `pr-triage__app__251` | `TESTS_OTHER_THING` | `MIXED` | probot 9.2.10 -> 10.1.3 |
| `probot__probot__2090` | `UNWITNESSED` | `MIXED` | @types/express 4.17.21 -> 5.0.1 (PR also bumps express 4.21.0 -> 5.0.0, plus transitive accepts/body-parser/send/serve-static/finalhandler/type-is/etc.) |
| `promptfoo__promptfoo__9079` | `TESTS_OTHER_THING` | `MIXED` | @opencode-ai/sdk 1.14.22 -> 1.14.33 |
| `qntm__base65536__49` | `TESTS_OTHER_THING` | `MIXED` | transitive `follow-redirects` 1.10.0 -> 1.14.0 through `axios` 0.21.1 -> 0.21.4 in `package-lock.json` |
| `scratchfoundation__scratch-blocks__3565` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | eslint-config-scratch 14.1.12 -> 14.1.14 |
| `stormforger__cli__220` | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | github.com/evanw/esbuild 0.9.2 -> 0.11.0 |
| `sumup-oss__circuit-ui__837` | `TESTS_OTHER_THING` | `MIXED` | typescript 4.1.5 -> 4.2.3 |
| `sveltejs__kit__14789` | `UNWITNESSED` | `CONFIG_INFRA_ONLY` | vitest 3.2.4 -> 4.0.16 (plus `@vitest/browser` -> `@vitest/browser-playwright`) |
| `wayfair-incubator__pygitops__272` | `TESTS_OTHER_THING` | `MIXED` | GitPython 3.1.18 -> 3.1.29 |
| `wireapp__wire-web-packages__2929` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | prettier 1.19.1 -> 2.0.4 |

Machine-readable table: `clean_set_pruning_recommendations_2026-06-18.csv`.

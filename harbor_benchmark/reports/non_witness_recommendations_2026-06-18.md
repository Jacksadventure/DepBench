# Non-Witness Task Review Recommendations — 2026-06-18

Scope: the 92 tasks from `test_patch_quality_review_2026-06-18_full297.md` whose verdict is not `WITNESSES_BREAKING_CHANGE`.

## Summary

| Recommendation | Count | Meaning |
|---|---:|---|
| `KEEP` | 0 | Directly keep in the clean witnessed set. |
| `DYNAMIC` | 5 | Potentially valid dependency-upgrade witness, but static evidence is insufficient; run dynamic P+manifest+test vs P+manifest+code+test validation before keeping. |
| `DELETE` | 87 | Exclude from the main clean witnessed benchmark set. |

No task in this 92-case non-witness set is recommended as direct `KEEP`. Five are `DYNAMIC`; the rest should be deleted/quarantined from the main clean benchmark.

## Dynamic validation candidates

| Folder | Original verdict | Δc nature | Reason |
|---|---|---|---|
| `dailymotion-oss__octopilot__152` | `INCONCLUSIVE` | `MIXED` | yq v4 API migration looks real, but vendoring split confounds static witness |
| `gjtorikian__what_you_say__14` | `TESTS_OTHER_THING` | `MIXED` | magnus 0.5→0.6 API migration may fail at rake compile; test patch itself is only assertion style |
| `keystonejs__keystone__8056` | `INCONCLUSIVE` | `REAL_SOURCE_REPAIR` | Markdoc widened return type; likely type-level only, needs confirmation Jest type-checks |
| `renovatebot__renovate__41225` | `INCONCLUSIVE` | `REAL_SOURCE_REPAIR` | zod v4/v3 mismatch may be real but source/test mirror import pins are circular-risk |
| `rollup__rollup__5046` | `INCONCLUSIVE` | `MIXED` | locate-character v3 ESM/nullable break plausible; source fix is type-only, need confirm build type-checks |

## Delete / quarantine recommendations

| Folder | Original verdict | Δc nature | Upgrade | Reason |
|---|---|---|---|---|
| `airlift__airlift__1592` | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | io.airlift:airbase 312 -> 313 | exclude from main clean witness set; see detailed review notes |
| `alphagov__govuk-frontend__3591` | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | rollup 0.59.4 -> 3.21.5 (also swaps `rollup-plugin-node-resolve`/`rollup-plugin-replace`/`terser` for `@rollup/plugin-node-resolve`/`@rollup/plugin-replace`/`@rollup/plugin-terser`) | exclude from main clean witness set; see detailed review notes |
| `amweiss__angular-diff-match-patch__231` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | xo 0.38.2 -> 0.39.1 | exclude from main clean witness set; see detailed review notes |
| `apache__logging-log4j2__2236` | `TESTS_OTHER_THING` | `MIXED` | org.springframework.cloud:spring-cloud-context 4.1.0 -> 4.1.1 | exclude from main clean witness set; see detailed review notes |
| `apache__logging-log4j2__2345` | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | org.codehaus.groovy:groovy-bom 3.0.20 -> 3.0.21 (manifest also bumps commons-dbcp2 2.11.0 -> 2.12.0) | exclude from main clean witness set; see detailed review notes |
| `apache__logging-log4j2__2409` | `TESTS_OTHER_THING` | `MIXED` | mongodb.version 3.12.11 -> 3.12.14 | exclude from main clean witness set; see detailed review notes |
| `apache__logging-log4j2__2600` | `TESTS_OTHER_THING` | `MIXED` | org.apache.logging:logging-parent 11.0.0 -> 11.1.0 | exclude from main clean witness set; see detailed review notes |
| `ardatan__graphql-tools__7282` | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | @babel/plugin-transform-regenerator 7.28.0 -> 7.28.1 | exclude from main clean witness set; see detailed review notes |
| `asciidoctor__asciidoctor-cli.js__96` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | fast-deep-equal 2.0.1 -> 3.1.1 | exclude from main clean witness set; see detailed review notes |
| `asciidoctor__asciidoctor.js__870` | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | ignore 3.0.9 -> 5.0.0 (PR was actually a `standard` linter upgrade 12.0.1 -> 14.3.3; `ignore` is a transitive dep) | exclude from main clean witness set; see detailed review notes |
| `aws__aws-northstar__1037` | `TESTS_OTHER_THING` | `MIXED` | ws 7.5.9 -> 7.5.10 | exclude from main clean witness set; see detailed review notes |
| `aws__aws-sdk-pandas__2883` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | boto3-stubs 1.34.131 -> 1.34.136 | exclude from main clean witness set; see detailed review notes |
| `bachya__pytile__346` | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | mypy 1.6.1 -> 1.7.0 | exclude from main clean witness set; see detailed review notes |
| `bbc__psammead__3709` | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | prettier 2.0.5 -> 2.1.1 (real upgrade in `package-lock.json` lines 92-99 + CHANGELOG entries). NOTE: the bundle header and `instruction.md` mislabel this as `version 4.17.20 -> 4.17.20` (a literal no-op string — the mining adapter picked up the `version` field of an internal package instead of the `prettier` dependency). | exclude from main clean witness set; see detailed review notes |
| `bbc__simorgh__9137` | `UNWITNESSED` | `MIXED` | `@types/jest` 26.0.24 -> 29.5.2 (labeled library); manifest.patch actually bumps the whole Jest stack together — `jest` 26.6.3→29.6.1, `babel-jest` 26.6.3→29.6.1, `jest-environment-jsdom` 26.6.2→29.6.1, `ts-jest` 26.5.6→29.1.1, `@types/jest` 26.0.24→29.5.2. | exclude from main clean witness set; see detailed review notes |
| `BrightspaceUI__intl__106` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | eslint-config-brightspace 0.17 -> 0.18 (and Δm also widens the lint script from `eslint lib test --ext .js` to `eslint . --ext .js`, and adds `eslint-plugin-import`). | exclude from main clean witness set; see detailed review notes |
| `cawa-93__vite-electron-builder__662` | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | vitest 0.0.136 -> 0.0.137 | exclude from main clean witness set; see detailed review notes |
| `cdk8s-team__kubecon-2020-cdk8s__28` | `INCONCLUSIVE` | `CONFIG_INFRA_ONLY` | projen 0.3.117 -> 0.17.16 | exclude from main clean witness set; see detailed review notes |
| `circleci__ex__510` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | github.com/golangci/golangci-lint 1.51.1 -> 1.51.2 | exclude from main clean witness set; see detailed review notes |
| `cloudant__nodejs-cloudant__400` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | the mined "library" field is a bogus transitive `resolved` URL change (acorn 3.3.0 tarball `http://` -> `https://`); the real semantic change in `package.json` is `eslint ^3.19.0 -> ^4.18.2` (plus `eslint-config-*` stays). So the effective upgrade is **eslint 3 -> 4**. | exclude from main clean witness set; see detailed review notes |
| `codemod-js__codemod__387` | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | @typescript-eslint/eslint-plugin 2.9.0 -> 2.11.0 (also @typescript-eslint/parser) | exclude from main clean witness set; see detailed review notes |
| `codetheweb__tuyapi__253` | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | string-width 2.0.0 -> 3.0.0 (actual upstream PR is a Renovate `xo` linter bump to v0.25.3; string-width is a transitive dep) | exclude from main clean witness set; see detailed review notes |
| `dwightjack__vue-types__117` | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | typescript 4.2.3 -> 4.3.4 | exclude from main clean witness set; see detailed review notes |
| `eakmanrq__sqlframe__450` | `UNWITNESSED` | `MIXED` | sqlglot >=24.0.0,<27.1 -> >=24.0.0,<27.2 | exclude from main clean witness set; see detailed review notes |
| `eakmanrq__sqlframe__533` | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | sqlglot >=24.0.0,<27.26 -> >=24.0.0,<27.27 | exclude from main clean witness set; see detailed review notes |
| `elastic__kibana__185906` | `TESTS_OTHER_THING` | `SNAPSHOT_ONLY` | @elastic/charts 65.2.0 -> 66.0.3 | exclude from main clean witness set; see detailed review notes |
| `emberjs__ember.js__19722` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | eslint-plugin-qunit 4.0.0 -> 6.2.0 | exclude from main clean witness set; see detailed review notes |
| `fastify__fastify-http-proxy__171` | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | ws 7.4.1 -> 8.0.0 | exclude from main clean witness set; see detailed review notes |
| `fb55__css-what__1184` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | prettier 2.8.8 -> 3.1.1 | exclude from main clean witness set; see detailed review notes |
| `foobaragency__foo-state__321` | `TESTS_OTHER_THING` | `DOCS_EXAMPLE_ONLY` | @types/jest 28.1.0 -> 29.2.0 | exclude from main clean witness set; see detailed review notes |
| `FraunhoferIOSB__FROST-Server__1486` | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | jooq.version 3.16.14 -> 3.16.15 | exclude from main clean witness set; see detailed review notes |
| `grafana__alloy__3602` | `TESTS_OTHER_THING` | `MIXED` | cloud.google.com/go/pubsub 1.49.0 -> 1.50.0 | exclude from main clean witness set; see detailed review notes |
| `graphql-hive__graphql-config__1481` | `UNWITNESSED` | `MIXED` | minimatch 4.2.3 -> 10.0.0 | exclude from main clean witness set; see detailed review notes |
| `Graylog2__graylog2-server__25652` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | com.google.errorprone:error_prone_core 2.48.0 -> 2.49.0 | exclude from main clean witness set; see detailed review notes |
| `hashicorp__terraform-provider-aws__34096` | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | github.com/aws/aws-sdk-go 1.46.2 -> 1.46.3, with many aws-sdk-go-v2 service bumps in Delta m | exclude from main clean witness set; see detailed review notes |
| `hetznercloud__cli__940` | `UNWITNESSED` | `TEST_ONLY` | github.com/hetznercloud/hcloud-go/v2 2.17.0 -> 2.17.1 | exclude from main clean witness set; see detailed review notes |
| `InfluxCommunity__influxdb3-js__413` | `TESTS_OTHER_THING` | `CONFIG_INFRA_ONLY` | eslint 8.43.0 -> 9.10.0 | exclude from main clean witness set; see detailed review notes |
| `inrupt__solid-client-authn-js__279` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | prettier 1.19.1 -> 2.1.0 | exclude from main clean witness set; see detailed review notes |
| `inrupt__solid-client-authn-js__3129` | `TESTS_OTHER_THING` | `MIXED` | @typescript-eslint/eslint-plugin 5.6.0 -> 6.6.0 | exclude from main clean witness set; see detailed review notes |
| `integrations__jira__293` | `TESTS_OTHER_THING` | `MIXED` | resolved http://registry.npmjs.org/resolve/-/resolve-1.1.7.tgz -> https://registry.npmjs.org/resolve/-/resolve-1.1.7.tgz | exclude from main clean witness set; see detailed review notes |
| `iodide-project__iodide__1432` | `UNWITNESSED` | `MIXED` | babel-jest 23.6.0 -> 24.7.1 (plus jest 23.6.0 -> 24.7.1 and jest-cli 23.6.0 -> 24.7.1; manifest also renames the jest 23 `setupTestFrameworkScriptFile` option to the jest 24 `setupFilesAfterEnv` array) | exclude from main clean witness set; see detailed review notes |
| `jonasbb__serde_with__836` | `UNWITNESSED` | `DOCS_EXAMPLE_ONLY` | ron 0.8.1 -> 0.10.1 | exclude from main clean witness set; see detailed review notes |
| `ktsn__capture-all__12` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | prettier 1.19.1 -> 2.0.5 | exclude from main clean witness set; see detailed review notes |
| `ktsn__vue-auto-routing__103` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | prettier 1.19.1 -> 2.0.5 | exclude from main clean witness set; see detailed review notes |
| `ktsn__vuex-smart-module__189` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | prettier 1.19.1 -> 2.0.5 | exclude from main clean witness set; see detailed review notes |
| `laconiajs__laconia__178` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | eslint-config-standard 12.0.0 -> 13.0.1 | exclude from main clean witness set; see detailed review notes |
| `LouisBarranqueiro__reapop__397` | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | prettier 2.2.1 -> 2.3.0 | exclude from main clean witness set; see detailed review notes |
| `m-h-c-t__mh-helper-extension__434` | `UNWITNESSED` | `MIXED` | @typescript-eslint/eslint-plugin 5.60.1 -> 6.3.0 | exclude from main clean witness set; see detailed review notes |
| `matrix-org__matrix-js-sdk__5217` | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | @matrix-org/matrix-sdk-crypto-wasm 17.1.0 -> 18.0.0 | exclude from main clean witness set; see detailed review notes |
| `microsoft__lage__346` | `TESTS_OTHER_THING` | `MIXED` | jest 27.2.0 -> 29.0.3 | exclude from main clean witness set; see detailed review notes |
| `mightyiam__eslint-config-love__2120` | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | eslint-plugin-import 2.31.0 -> 2.32.0 | exclude from main clean witness set; see detailed review notes |
| `mikavilpas__yazi.nvim__1506` | `UNWITNESSED` | `MIXED` | @tui-sandbox/library 12.1.0 -> 12.2.2 (also transitively bumps @xterm/xterm 5.5 -> 6.0, addon-fit 0.10 -> 0.11, addon-unicode11 0.8 -> 0.9, nan 2.23 -> 2.24) | exclude from main clean witness set; see detailed review notes |
| `mochajs__mocha__5709` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | prettier 3.6.2 -> 3.8.1 | exclude from main clean witness set; see detailed review notes |
| `mozilla__addons-frontend__10931` | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | redux-saga 0.16.2 -> 1.1.3 | exclude from main clean witness set; see detailed review notes |
| `mozilla__addons-frontend__11753` | `UNWITNESSED` | `MIXED` | flow-bin 0.176.0 -> 0.183.0 | exclude from main clean witness set; see detailed review notes |
| `mui__mui-x__18276` | `UNWITNESSED` | `DOCS_EXAMPLE_ONLY` | `@mui/monorepo` github:mui/material-ui#8cd3aa58 -> #9b3d36ed (a digest bump of the internal mui/material-ui dep). The material-ui bump renamed/replaced the `stylis-plugin-rtl` package with `@mui/stylis-plugin-rtl`. | exclude from main clean witness set; see detailed review notes |
| `multiformats__js-multiformats__306` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | aegir 43.0.1 -> 44.1.1 | exclude from main clean witness set; see detailed review notes |
| `nextcloud__text__8485` | `UNWITNESSED` | `REAL_SOURCE_REPAIR` | @tiptap/core 3.22.3 -> 3.22.4 (also @tiptap/extension-collaboration, -drag-handle, -drag-handle-vue-2, @tiptap/pm, @tiptap/vue-2 → 3.22.4; adds direct deps `prosemirror-markdown` and `prosemirror-schema-basic`) | exclude from main clean witness set; see detailed review notes |
| `nikolaik__docker-python-nodejs__306` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | unknown unknown -> unknown | exclude from main clean witness set; see detailed review notes |
| `noflo__noflo-polymer__54` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | eslint-config-airbnb-base 13.0.0 -> 14.2.0 | exclude from main clean witness set; see detailed review notes |
| `nukeop__nuclear__1905` | `UNWITNESSED` | `CONFIG_INFRA_ONLY` | @vitest/coverage-v8 3.2.4 -> 4.0.0 (vitest 3.2.4 -> 4.0.0) | exclude from main clean witness set; see detailed review notes |
| `nuxeo__nuxeo-drive__3833` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | codespell ==2.1.0 -> ==2.2.4 | exclude from main clean witness set; see detailed review notes |
| `nuxt-community__vuetify-module__426` | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | @nuxtjs/eslint-config-typescript 4.0.0 -> 6.0.1 | exclude from main clean witness set; see detailed review notes |
| `nuxt__fonts__601` | `UNWITNESSED` | `CONFIG_INFRA_ONLY` | @iconify-json/simple-icons 1.2.31 -> 1.2.33 (manifest also bumps @nuxt/devtools-kit, fontaine, magic-regexp, tinyglobby, unplugin, eslint, playwright-core, vite, vitest, sass, tailwindcss, etc.) | exclude from main clean witness set; see detailed review notes |
| `oceanprotocol__market__1687` | `TESTS_OTHER_THING` | `MIXED` | eslint-plugin-testing-library 5.5.1 -> 5.6.4 (labeled; Δm also upgrades Jest 28 -> 29, Storybook 6.5.x, @testing-library/react 13.3 -> 13.4, TypeScript 4.7 -> 4.8, urql, web3, and many lockfile packages) | exclude from main clean witness set; see detailed review notes |
| `onthegomap__maplibre-contour__34` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | prettier 2.8.8 -> 3.0.0 | exclude from main clean witness set; see detailed review notes |
| `openlayers__ol-mapbox-style__1071` | `TESTS_OTHER_THING` | `MIXED` | eslint-config-openlayers 18.0.0 -> 19.0.0 | exclude from main clean witness set; see detailed review notes |
| `OpenNMS__opennms__6191` | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | hessian 3.1.5 -> 4.0.66 | exclude from main clean witness set; see detailed review notes |
| `option-t__option-t__1911` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | prettier 2.8.8 -> 3.0.0 | exclude from main clean witness set; see detailed review notes |
| `oxidecomputer__dropshot__580` | `TESTS_OTHER_THING` | `TEST_ONLY` | toml 0.5.11 -> 0.7.0 (metadata labels library as `version`) | exclude from main clean witness set; see detailed review notes |
| `peopledatalabs__peopledatalabs-python__132` | `TESTS_OTHER_THING` | `CONFIG_INFRA_ONLY` | annotated-types 7.4.4 -> 7.5.1 | exclude from main clean witness set; see detailed review notes |
| `plotly__react-chart-editor__1025` | `UNWITNESSED` | `FORMATTER_LINT_CHURN` | prettier 1.19.1 -> 2.0.2 | exclude from main clean witness set; see detailed review notes |
| `pr-triage__app__251` | `TESTS_OTHER_THING` | `MIXED` | probot 9.2.10 -> 10.1.3 | exclude from main clean witness set; see detailed review notes |
| `prettier__prettier__8890` | `TESTS_OTHER_THING` | `MIXED` | cosmiconfig 6.0.0 -> 7.0.0 | exclude from main clean witness set; see detailed review notes |
| `probot__probot__2090` | `UNWITNESSED` | `MIXED` | @types/express 4.17.21 -> 5.0.1 (PR also bumps express 4.21.0 -> 5.0.0, plus transitive accepts/body-parser/send/serve-static/finalhandler/type-is/etc.) | exclude from main clean witness set; see detailed review notes |
| `promptfoo__promptfoo__8920` | `TESTS_OTHER_THING` | `MIXED` | @fal-ai/client 1.9.6 -> 1.10.0 | exclude from main clean witness set; see detailed review notes |
| `promptfoo__promptfoo__8946` | `TESTS_OTHER_THING` | `MIXED` | @anthropic-ai/claude-agent-sdk 0.2.119 -> 0.2.120 | exclude from main clean witness set; see detailed review notes |
| `promptfoo__promptfoo__9079` | `TESTS_OTHER_THING` | `MIXED` | @opencode-ai/sdk 1.14.22 -> 1.14.33 | exclude from main clean witness set; see detailed review notes |
| `qntm__base65536__49` | `TESTS_OTHER_THING` | `MIXED` | transitive `follow-redirects` 1.10.0 -> 1.14.0 through `axios` 0.21.1 -> 0.21.4 in `package-lock.json` | exclude from main clean witness set; see detailed review notes |
| `runatlantis__atlantis__5209` | `TESTS_OTHER_THING` | `MIXED` | github.com/google/go-github/v66 v66.0.0 -> v68.0.0 | exclude from main clean witness set; see detailed review notes |
| `scratchfoundation__scratch-blocks__3565` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | eslint-config-scratch 14.1.12 -> 14.1.14 | exclude from main clean witness set; see detailed review notes |
| `stormforger__cli__220` | `TESTS_OTHER_THING` | `REAL_SOURCE_REPAIR` | github.com/evanw/esbuild 0.9.2 -> 0.11.0 | exclude from main clean witness set; see detailed review notes |
| `sumup-oss__circuit-ui__837` | `TESTS_OTHER_THING` | `MIXED` | typescript 4.1.5 -> 4.2.3 | exclude from main clean witness set; see detailed review notes |
| `sveltejs__kit__14789` | `UNWITNESSED` | `CONFIG_INFRA_ONLY` | vitest 3.2.4 -> 4.0.16 (plus `@vitest/browser` -> `@vitest/browser-playwright`) | exclude from main clean witness set; see detailed review notes |
| `wayfair-incubator__pygitops__272` | `TESTS_OTHER_THING` | `MIXED` | GitPython 3.1.18 -> 3.1.29 | exclude from main clean witness set; see detailed review notes |
| `wireapp__wire-web-packages__2929` | `TESTS_OTHER_THING` | `FORMATTER_LINT_CHURN` | prettier 1.19.1 -> 2.0.4 | exclude from main clean witness set; see detailed review notes |
| `xt0rted__slash-command-action__307` | `TESTS_OTHER_THING` | `MIXED` | @octokit/types 4.0.1 -> 6.0.3 | exclude from main clean witness set; see detailed review notes |

## Machine-readable table

See `non_witness_recommendations_2026-06-18.csv`.

# Instruction Bump Audit - 203 Tasks

Every active task was checked against its packaged manifest patch, upstream pull request metadata, and final `instruction.md`.

## Result

- Tasks audited: **203**
- Passed: **203**
- Needs review: **0**

## Evidence Classes

| Evidence | Tasks |
|---|---:|
| `exact_versions` | 197 |
| `group_update` | 5 |
| `pr_only_source_revision` | 1 |

## Upstream Declaration Check

| PR evidence | Tasks |
|---|---:|
| `exact_declared` | 170 |
| `group_declared` | 5 |
| `library_declared` | 20 |
| `not_declared` | 3 |
| `versions_declared` | 5 |

## Non-Exact Or Exceptional Cases

| Task | Benchmark bump | Manifest evidence | PR evidence | Result |
|---|---|---|---|---|
| `29ki__29k__5244` | `posthog-react-native 2.11.6 -> 3.1.2` | `exact_versions` | `library_declared` | `pass` |
| `DSpace__DSpace__10216` | `Maven build-tools group multiple versions -> updated versions` | `group_update` | `group_declared` | `pass` |
| `JoshuaKGoldberg__create-typescript-app__1489` | `packageManager pnpm@8.15.4 -> pnpm@9.0.6` | `exact_versions` | `library_declared` | `pass` |
| `Nextdoor__vigil__35` | `Kubernetes modules 0.33.10 -> 0.35.3` | `exact_versions` | `versions_declared` | `pass` |
| `Stranger6667__jsonschema__825` | `crates/jsonschema/tests/suite 15e4505 -> be58fa9` | `pr_only_source_revision` | `exact_declared` | `pass` |
| `ardatan__graphql-tools__6921` | `@graphql-tools/executor-graphql-ws 1.3.2 -> 2.0.1` | `exact_versions` | `not_declared` | `pass` |
| `chris48s__v8r__22` | `js-yaml 3.14.0 -> 4.0.0` | `exact_versions` | `library_declared` | `pass` |
| `cucumber__cucumber-jvm__3162` | `junit-jupiter.version 5.14.2 -> 6.0.2` | `exact_versions` | `versions_declared` | `pass` |
| `curbengh__hexo-yam__135` | `svgo 2.4.0 -> 3.0.0` | `exact_versions` | `library_declared` | `pass` |
| `graphql-java-kickstart__graphql-java-tools__645` | `graphql-java.version 17.3 -> 18.0` | `exact_versions` | `library_declared` | `pass` |
| `hawtio__hawtio__3776` | `jolokia-version 2.1.2 -> 2.2.2` | `exact_versions` | `library_declared` | `pass` |
| `hexojs__hexo-uglify__147` | `terser 4.3.9 -> 5.3.0` | `exact_versions` | `library_declared` | `pass` |
| `imsnif__bandwhich__430` | `dependencies group previous versions -> updated versions` | `group_update` | `group_declared` | `pass` |
| `inovex__scrumlr.io__4672` | `react-router 6.22.0 -> 7.0.2` | `exact_versions` | `library_declared` | `pass` |
| `iterative__dvc__7899` | `networkx 2.5,<2.8.3 -> >=2.5` | `exact_versions` | `library_declared` | `pass` |
| `jo-sm__stylelint_d__709` | `glob 8.0.1 -> 10.2.6` | `exact_versions` | `library_declared` | `pass` |
| `libp2p__js-libp2p-bootstrap__171` | `@libp2p/interface-peer-store 1.2.2 -> 2.0.0` | `exact_versions` | `library_declared` | `pass` |
| `liquibase__liquibase__2285` | `h2 1.4.200 -> 2.0.202` | `exact_versions` | `versions_declared` | `pass` |
| `matrix-org__matrix-js-sdk__4052` | `jwt-decode 3.1.2 -> 4.0.0` | `exact_versions` | `library_declared` | `pass` |
| `mightyiam__eslint-config-love__2178` | `eslint 9.12.0 -> 9.35.0` | `exact_versions` | `library_declared` | `pass` |
| `mitmproxy__mitmproxy_rs__142` | `dependencies group previous versions -> updated versions` | `group_update` | `group_declared` | `pass` |
| `mitre__heimdall2__2276` | `d3 6.1.1 -> 7.2.0` | `exact_versions` | `not_declared` | `pass` |
| `nearform__brokeneck__820` | `react-router-dom 5.2.0 -> 6.4.1` | `exact_versions` | `library_declared` | `pass` |
| `octokit__auth-oauth-app.js__137` | `@octokit/types 6.0.0 -> 6.0.3` | `exact_versions` | `library_declared` | `pass` |
| `octokit__plugin-paginate-rest.js__226` | `@octokit/types 5.5.0 -> 6.0.1` | `exact_versions` | `library_declared` | `pass` |
| `odanado__cloud-cryptographic-wallet__672` | `@ethereumjs/common 2.6.2 -> 3.0.0` | `exact_versions` | `library_declared` | `pass` |
| `opengovsg__askgovsg__150` | `typescript 4.2.3 -> 4.4.2` | `exact_versions` | `library_declared` | `pass` |
| `owncloud__web__11511` | `vue 3.4.38 -> 3.5.4` | `exact_versions` | `library_declared` | `pass` |
| `piomin__spring-boot-logging__41` | `spring.boot.version 2.1.4.RELEASE -> 2.7.13` | `exact_versions` | `versions_declared` | `pass` |
| `rash-sh__rash__698` | `rust-version 1.82 -> 1.85` | `exact_versions` | `not_declared` | `pass` |
| `score-spec__score-aca__16` | `score-go 1.9.6 -> 1.10.1` | `exact_versions` | `library_declared` | `pass` |
| `sequelize__umzug__572` | `lint dependency group previous versions -> updated versions` | `group_update` | `group_declared` | `pass` |
| `verdaccio__verdaccio__5742` | `Verdaccio dependency group previous versions -> updated versions` | `group_update` | `group_declared` | `pass` |
| `yahoo__elide__2476` | `h2 2.0.202 -> 2.0.206` | `exact_versions` | `versions_declared` | `pass` |

## Unresolved

No unresolved tasks.

The CSV and JSON files contain one row per task, including old/new manifest evidence lines and upstream PR provenance.

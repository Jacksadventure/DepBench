# Dependency Metadata Corrections - 2026-07-26

This report records the package-name and version-parsing corrections found by re-scanning the 203-task DepBench release. It compares source commit `1474b6434c65b160e2b65a3c5540e766de669381` with corrected source commit `09cd1d57ac9f135e57a5f8ed03b3845943be4ac9`.

The follow-up bot-PR verification is recorded in `analysis/bot_pr_dependency_audit_2026-07-26.md` and `.csv`.

## Scope

- Corrected task-summary rows: **44**
- Task directories with synchronized `instruction.md` or `task.toml` changes: **42**
- Summary-only corrections: **2** (`renovatebot__renovate__36455` and `ubugeeei-prod__ox-content__131`)
- Strawberry hidden-verifier correction: `flask` attribution replaced by `graphql-core 3.1.0b0 -> 3.1.0b2`
- GraphQL Config correction: generated declaration paths replaced by `bob-the-bundler 1.7.3 -> 4.0.0`

## Correction Counts

| Change type | Tasks |
|---|---:|
| `package_and_version` | 18 |
| `package_name` | 13 |
| `version` | 7 |
| `filled_missing_metadata` | 6 |

| Ecosystem | Tasks |
|---|---:|
| `cargo` | 7 |
| `go_modules` | 12 |
| `maven` | 12 |
| `npm_and_yarn` | 11 |
| `pip` | 2 |

## Release Propagation

| Target | Branch or revision | Commit / digest |
|---|---|---|
| Source dataset, both GitHub remotes | `v4-with-test` | `cb6bb23277d150f5f0a2faab6753fa352f519394` |
| Hugging Face dataset | revision | `50d83f18938fb3208a84b97509b024f644a909dc` |
| Hugging Face archive | SHA-256 | `c640ec120ef135d4ae15fd3ace4131be51149d6951ae07d74f363c30c785834a` |
| MSBench benchmark source | `depbench/harbor-v4-with-test203` | `4eb2262151311c0b8810b05ec1ecffafe560dcdc` |
| MSBench registry | `depbench/harbor-v4-with-test203` | `fa81a75dd27f1c1a4609c7014d689ca6ac2592f1` |
| Release data and result update, both GitHub remotes | `main` | current release commit |

## Experimental Result Impact

- Re-ran all 56 affected tasks across all 10 model-by-harness configurations.
- The 560 canonical-contract reruns contain 207 passes and 353 non-passes.
- Refreshed final outcomes, trajectory exports, verifier logs, behavior annotations, and final failure classifications.
- Final release validation: 203 tasks, 10 configurations, and 2,030 selected trials.

## Detailed Corrections

The machine-readable version of this table is `analysis/dependency_metadata_corrections_2026-07-26.csv`.

| Task | Ecosystem | Type | Before | Corrected | Task files |
|---|---|---|---|---|---|
| `29ki__29k__5244` | `npm_and_yarn` | `version` | `posthog-react-native 2.11.6 -> 3.1.1` | `posthog-react-native 2.11.6 -> 3.1.2` | yes |
| `adoptoposs__mjml_nif__117` | `cargo` | `package_and_version` | `version 1.1.0 -> 0.11.4` | `mrml 1.2 -> 2.1` | yes |
| `adoptoposs__mjml_nif__13` | `cargo` | `package_and_version` | `version 0.7.13 -> 1.0.0` | `mrml 0.5.0 -> 1.0.0` | yes |
| `ardatan__graphql-tools__6921` | `npm_and_yarn` | `package_and_version` | `@babel/core 7.26.7 -> 7.26.8` | `@graphql-tools/executor-graphql-ws 1.3.2 -> 2.0.1` | yes |
| `decaporg__decap-cms__4748` | `npm_and_yarn` | `package_and_version` | `unknown unknown -> unknown` | `ajv 6.10.0 -> 7.0.0` | yes |
| `decaporg__decap-cms__5178` | `npm_and_yarn` | `package_and_version` | `@ 2.0.1 -> 3.0.0` | `ajv 7.0.0 -> 8.0.0` | yes |
| `dkhmelenko__autoapproval__343` | `npm_and_yarn` | `package_and_version` | `mime-db 1.40.0 -> 1.47.0` | `probot 7.5.3 -> 11.3.0` | yes |
| `DSpace__DSpace__10216` | `maven` | `package_and_version` | `version 3.4.0 -> 3.6.0` | `Maven build-tools group multiple versions -> updated versions` | yes |
| `freechat-fun__freechat__757` | `maven` | `package_and_version` | `artifactId redisson-spring-data-35 -> redisson-spring-data-40` | `spring-boot.version 3.5.8 -> 4.0.0` | yes |
| `geotools__geotools__4212` | `maven` | `version` | `snakeyaml 1.32 -> to` | `snakeyaml 1.32 -> 2.0` | yes |
| `giantswarm__mcp-prometheus__165` | `go_modules` | `package_name` | `giantswarm/mcp-oauth 0.2.150 -> 0.2.173` | `github.com/giantswarm/mcp-oauth 0.2.150 -> 0.2.173` | yes |
| `golangci__golangci-lint__4157` | `go_modules` | `version` | `github.com/catenacyber/perfsprint 0.2.0 -> 0.2.2` | `github.com/catenacyber/perfsprint 0.2.0 -> 0.3.0` | yes |
| `graphql-hive__graphql-config__1103` | `npm_and_yarn` | `package_and_version` | `definition dist/index.d.ts -> dist/typings/index.d.ts` | `bob-the-bundler 1.7.3 -> 4.0.0` | yes |
| `graphql-java-kickstart__graphql-java-tools__800` | `maven` | `package_and_version` | `groupId com.graphql-java-kickstart -> io.github.graphql-java-kickstart` | `graphql-java.version 23.1 -> 25.0` | yes |
| `hawtio__hawtio__3776` | `maven` | `version` | `jolokia-version 2.1.2 -> 2.2.1` | `jolokia-version 2.1.2 -> 2.2.2` | yes |
| `INRIA__spoon__6087` | `maven` | `package_name` | `version 3.39.0 -> 3.40.0` | `org.eclipse.jdt:org.eclipse.jdt.core 3.39.0 -> 3.40.0` | yes |
| `INRIA__spoon__6316` | `maven` | `package_name` | `version 3.41.0 -> 3.42.0` | `org.eclipse.jdt:org.eclipse.jdt.core 3.41.0 -> 3.42.0` | yes |
| `iterative__dvc__7899` | `pip` | `version` | `networkx 2.5,<2.8.3 -> 2.5,<2.8.5` | `networkx 2.5,<2.8.3 -> >=2.5` | yes |
| `marocchino__sticky-pull-request-comment__305` | `npm_and_yarn` | `package_and_version` | `@octokit/types 6.0.0 -> 6.0.3` | `@actions/github 4.0.0 -> 5.0.0` | yes |
| `matt-riley__hopcli__47` | `go_modules` | `filled_missing_metadata` | `(blank) (blank) -> (blank)` | `github.com/charmbracelet/bubbletea -> charm.land/bubbletea/v2 1.3.10 -> 2.0.1` | yes |
| `mozilla__addons-frontend__9637` | `npm_and_yarn` | `package_name` | `@ 5.13.1 -> 5.13.2` | `@loadable/component and @loadable/server 5.13.1 -> 5.13.2` | yes |
| `Nextdoor__vigil__35` | `go_modules` | `package_name` | `api/apimachinery/client-go/component-helpers 0.33.10 -> 0.35.3` | `Kubernetes modules 0.33.10 -> 0.35.3` | yes |
| `opentripplanner__OpenTripPlanner__5232` | `maven` | `package_name` | `version 20.4 -> 21.0` | `com.graphql-java:graphql-java 20.4 -> 21.0` | yes |
| `opentripplanner__OpenTripPlanner__5280` | `maven` | `package_name` | `version 3.0.0 -> 3.0.1` | `org.entur.gbfs:gbfs-java-model 3.0.0 -> 3.0.1` | yes |
| `opentripplanner__OpenTripPlanner__6603` | `maven` | `package_name` | `version 22.3 -> 23.0` | `com.graphql-java:graphql-java 22.3 -> 23.0` | yes |
| `piomin__spring-boot-logging__41` | `maven` | `package_and_version` | `artifactId reactive-logstash-logging-spring-boot-starter -> reactive-logstash-logging-spring-boot-starter` | `spring.boot.version 2.1.4.RELEASE -> 2.7.13` | yes |
| `regexident__cargo-modules__122` | `cargo` | `package_and_version` | `version 0.83.0 -> 0.84.0` | `ra_ap_* crates 0.0.122 -> 0.0.132` | yes |
| `regexident__cargo-modules__389` | `cargo` | `package_and_version` | `unknown unknown -> unknown` | `ra_ap_* crates 0.0.289 -> 0.0.328` | yes |
| `renovatebot__renovate__36455` | `npm_and_yarn` | `package_and_version` | `unknown unknown -> unknown` | `remark 13.0.0 -> 15.0.1` | no |
| `saveourtool__diktat__1529` | `maven` | `package_and_version` | `version ${log4j.version} -> ${mu-logging.version}` | `io.github.microutils:kotlin-logging-jvm 2.1.23 -> 3.0.3` | yes |
| `score-spec__score-aca__16` | `go_modules` | `version` | `score-go 1.9.6 -> 1.10.0` | `score-go 1.9.6 -> 1.10.1` | yes |
| `sequelize__umzug__572` | `npm_and_yarn` | `package_and_version` | `pony-cause 2.1.2 -> 2.1.4` | `typescript 4.7.4 -> 4.8.4` | yes |
| `shuntaka9576__gh-kanban__16` | `go_modules` | `filled_missing_metadata` | `(blank) (blank) -> (blank)` | `github.com/charmbracelet/bubbletea -> charm.land/bubbletea/v2 1.3.10 -> 2.0.7` | yes |
| `slowli__jwt-compact__138` | `cargo` | `package_name` | `version 0.8 -> 0.9` | `rsa 0.8 -> 0.9` | yes |
| `spiffe__spire__4184` | `go_modules` | `version` | `github.com/hashicorp/go-plugin 1.4.6 -> 1.4.8` | `github.com/hashicorp/go-plugin 1.4.6 -> 1.4.10` | yes |
| `stackitcloud__stackit-cert-manager-webhook__94` | `go_modules` | `filled_missing_metadata` | `(blank) (blank) -> (blank)` | `github.com/stackitcloud/stackit-sdk-go/services/dns 0.13.1 -> 0.17.0` | yes |
| `strawberry-graphql__strawberry__282` | `pip` | `package_name` | `flask 3.1.0b0 -> 3.1.0b2` | `graphql-core 3.1.0b0 -> 3.1.0b2` | yes |
| `syou6162__times_esa_mcp_server__22` | `go_modules` | `filled_missing_metadata` | `(blank) (blank) -> (blank)` | `github.com/mark3labs/mcp-go 0.28.0 -> 0.30.0` | yes |
| `thegeeklab__wp-docker-buildx__349` | `go_modules` | `filled_missing_metadata` | `(blank) (blank) -> (blank)` | `github.com/urfave/cli/v2 -> github.com/urfave/cli/v3 2.27.6 -> 3.1.1` | yes |
| `thegeeklab__wp-opentofu__166` | `go_modules` | `filled_missing_metadata` | `(blank) (blank) -> (blank)` | `github.com/urfave/cli/v2 -> github.com/urfave/cli/v3 2.27.6 -> 3.1.1` | yes |
| `ubugeeei-prod__ox-content__131` | `cargo` | `package_name` | `crates 0.44 -> 0.131` | `oxc_* crates 0.44 -> 0.131` | no |
| `vectordotdev__vrl__440` | `cargo` | `package_name` | `version 0.4.28 -> 0.4.30` | `chrono 0.4.28 -> 0.4.30` | yes |
| `verdaccio__verdaccio__5742` | `npm_and_yarn` | `package_and_version` | `vitest 3.2.4 -> 4.1.2` | `Verdaccio dependency group previous versions -> updated versions` | yes |
| `xMoelletschi__renoglaab__30` | `go_modules` | `package_name` | `gitlab-org/api/client-go 0.161.1 -> 1.2.0` | `gitlab.com/gitlab-org/api/client-go 0.161.1 -> 1.2.0` | yes |

## Validation Performed

- Verified 203 unique task-summary rows and 203 task directories.
- Parsed all 203 `task.toml` files.
- Confirmed package/version values are reflected in task instructions and manifest patches.
- Confirmed MSBench contains 203 generated JSONL rows and its preparation step is idempotent.
- Downloaded and hash-verified the pinned Hugging Face archive.
- Ran `repro/validate_release.py` successfully against the final release artifacts.

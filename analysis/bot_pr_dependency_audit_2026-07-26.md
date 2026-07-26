# Bot PR Dependency Audit - 2026-07-26

This audit checks the 44 recently corrected dependency metadata rows against their merged GitHub pull requests. It distinguishes the bot-declared update in the PR title/body from the final merged file diff, because later commits can make the bot text stale.

## Scope

- Pull requests checked: **44**
- Merged pull requests: **44**
- Renovate-authored: **28**
- Dependabot-authored: **15** (including one `dependabot-preview[bot]`)
- Human-authored bump PR: **1**

## Results

| Status | Tasks | Meaning |
|---|---:|---|
| `confirmed_exact` | 23 | Bot declaration and final merged diff support the benchmark metadata. |
| `merged_diff_overrides_bot_declaration` | 4 | The bot text is stale; benchmark correctly follows the final merged manifest. |
| `merged_diff_adds_breaking_upgrade` | 1 | A later PR commit adds the benchmark-selected breaking upgrade. |
| `manifest_range_vs_resolved_release` | 1 | Benchmark records a manifest constraint while the bot records the exact resolved release. |
| `group_pr_causal_subset` | 4 | The PR is a group update; benchmark records the dependency that drives the repair. |
| `group_pr_summary` | 7 | Benchmark intentionally summarizes a multi-package bot PR. |
| `confirmed_property_alias` | 2 | Task summary uses a build-property alias while task text identifies the actual dependency. |
| `metadata_correction_required` | 2 | Current dependency attribution does not match the bot PR and repair evidence. |

## Corrections Required

### `spiffe__spire__4184`

- Bot PR: `github.com/hashicorp/vault/sdk 0.9.0 -> 0.9.1`.
- Final merged manifest also changes `github.com/hashicorp/go-plugin 1.4.6 -> 1.4.10` and the HCL revision.
- Gold repair adapts to the HCL API change introduced through the Vault SDK update.
- Current task incorrectly presents `go-plugin` as the primary bump.

### `sequelize__umzug__572`

- Bot PR: lint dependency group (`@typescript-eslint/*`, `eslint`, `eslint-config-xo`, and `eslint-config-xo-typescript`).
- Final merged manifest additionally updates TypeScript and `pony-cause`.
- Gold repair changes ESLint rules and converts imports to type-only imports.
- Current task incorrectly presents TypeScript as the sole primary bump.

Changing either task instruction changes the agent-visible contract. Their 20 model-by-harness cells should be rerun before the corrected metadata is used for reported results.

## Stale Bot Text Confirmed

| Task | Bot declaration | Final merged manifest used by benchmark |
|---|---|---|
| `29ki__29k__5244` | `posthog-react-native 2.11.6 -> 3.1.1` | `2.11.6 -> 3.1.2` |
| `hawtio__hawtio__3776` | `jolokia-version 2.1.2 -> 2.2.1` | `2.1.2 -> 2.2.2` |
| `score-spec__score-aca__16` | `score-go 1.9.6 -> 1.10.0` | `1.9.6 -> 1.10.1` |
| `thegeeklab__wp-opentofu__166` | Renovate body currently advertises `3.2.0` | merged files contain the v2-to-v3 migration at `3.1.1` |

## Per-Task Verification

The machine-readable evidence is in `analysis/bot_pr_dependency_audit_2026-07-26.csv`.

| Task | PR author | Benchmark update | Status |
|---|---|---|---|
| `29ki__29k__5244` | `dependabot[bot]` | `posthog-react-native 2.11.6 -> 3.1.2` | `merged_diff_overrides_bot_declaration` |
| `adoptoposs__mjml_nif__117` | `dependabot[bot]` | `mrml 1.2 -> 2.1` | `manifest_range_vs_resolved_release` |
| `adoptoposs__mjml_nif__13` | `dependabot[bot]` | `mrml 0.5.0 -> 1.0.0` | `confirmed_exact` |
| `ardatan__graphql-tools__6921` | `renovate[bot]` | `@graphql-tools/executor-graphql-ws 1.3.2 -> 2.0.1` | `merged_diff_adds_breaking_upgrade` |
| `decaporg__decap-cms__4748` | `renovate[bot]` | `ajv 6.10.0 -> 7.0.0` | `confirmed_exact` |
| `decaporg__decap-cms__5178` | `renovate[bot]` | `ajv 7.0.0 -> 8.0.0` | `confirmed_exact` |
| `dkhmelenko__autoapproval__343` | `dkhmelenko` | `probot 7.5.3 -> 11.3.0` | `confirmed_exact` |
| `DSpace__DSpace__10216` | `dependabot[bot]` | `Maven build-tools group multiple versions -> updated versions` | `group_pr_summary` |
| `freechat-fun__freechat__757` | `renovate[bot]` | `spring-boot.version 3.5.8 -> 4.0.0` | `group_pr_summary` |
| `geotools__geotools__4212` | `dependabot[bot]` | `snakeyaml 1.32 -> 2.0` | `confirmed_exact` |
| `giantswarm__mcp-prometheus__165` | `renovate[bot]` | `github.com/giantswarm/mcp-oauth 0.2.150 -> 0.2.173` | `confirmed_exact` |
| `golangci__golangci-lint__4157` | `dependabot[bot]` | `github.com/catenacyber/perfsprint 0.2.0 -> 0.3.0` | `confirmed_exact` |
| `graphql-hive__graphql-config__1103` | `renovate[bot]` | `bob-the-bundler 1.7.3 -> 4.0.0` | `confirmed_exact` |
| `graphql-java-kickstart__graphql-java-tools__800` | `renovate[bot]` | `graphql-java.version 23.1 -> 25.0` | `confirmed_property_alias` |
| `hawtio__hawtio__3776` | `dependabot[bot]` | `jolokia-version 2.1.2 -> 2.2.2` | `merged_diff_overrides_bot_declaration` |
| `INRIA__spoon__6087` | `renovate[bot]` | `org.eclipse.jdt:org.eclipse.jdt.core 3.39.0 -> 3.40.0` | `confirmed_exact` |
| `INRIA__spoon__6316` | `renovate[bot]` | `org.eclipse.jdt:org.eclipse.jdt.core 3.41.0 -> 3.42.0` | `confirmed_exact` |
| `iterative__dvc__7899` | `dependabot[bot]` | `networkx 2.5,<2.8.3 -> >=2.5` | `confirmed_exact` |
| `marocchino__sticky-pull-request-comment__305` | `dependabot[bot]` | `@actions/github 4.0.0 -> 5.0.0` | `confirmed_exact` |
| `matt-riley__hopcli__47` | `renovate[bot]` | `github.com/charmbracelet/bubbletea -> charm.land/bubbletea/v2 1.3.10 -> 2.0.1` | `group_pr_causal_subset` |
| `mozilla__addons-frontend__9637` | `renovate[bot]` | `@loadable/component and @loadable/server 5.13.1 -> 5.13.2` | `group_pr_summary` |
| `Nextdoor__vigil__35` | `renovate[bot]` | `Kubernetes modules 0.33.10 -> 0.35.3` | `group_pr_summary` |
| `opentripplanner__OpenTripPlanner__5232` | `renovate[bot]` | `com.graphql-java:graphql-java 20.4 -> 21.0` | `confirmed_exact` |
| `opentripplanner__OpenTripPlanner__5280` | `renovate[bot]` | `org.entur.gbfs:gbfs-java-model 3.0.0 -> 3.0.1` | `confirmed_exact` |
| `opentripplanner__OpenTripPlanner__6603` | `renovate[bot]` | `com.graphql-java:graphql-java 22.3 -> 23.0` | `confirmed_exact` |
| `piomin__spring-boot-logging__41` | `renovate[bot]` | `spring.boot.version 2.1.4.RELEASE -> 2.7.13` | `confirmed_property_alias` |
| `regexident__cargo-modules__122` | `renovate[bot]` | `ra_ap_* crates 0.0.122 -> 0.0.132` | `group_pr_summary` |
| `regexident__cargo-modules__389` | `renovate[bot]` | `ra_ap_* crates 0.0.289 -> 0.0.328` | `group_pr_summary` |
| `renovatebot__renovate__36455` | `renovate[bot]` | `remark 13.0.0 -> 15.0.1` | `confirmed_exact` |
| `saveourtool__diktat__1529` | `renovate[bot]` | `io.github.microutils:kotlin-logging-jvm 2.1.23 -> 3.0.3` | `confirmed_exact` |
| `score-spec__score-aca__16` | `dependabot[bot]` | `score-go 1.9.6 -> 1.10.1` | `merged_diff_overrides_bot_declaration` |
| `sequelize__umzug__572` | `renovate[bot]` | `typescript 4.7.4 -> 4.8.4` | `metadata_correction_required` |
| `shuntaka9576__gh-kanban__16` | `renovate[bot]` | `github.com/charmbracelet/bubbletea -> charm.land/bubbletea/v2 1.3.10 -> 2.0.7` | `group_pr_causal_subset` |
| `slowli__jwt-compact__138` | `dependabot[bot]` | `rsa 0.8 -> 0.9` | `confirmed_exact` |
| `spiffe__spire__4184` | `dependabot[bot]` | `github.com/hashicorp/go-plugin 1.4.6 -> 1.4.10` | `metadata_correction_required` |
| `stackitcloud__stackit-cert-manager-webhook__94` | `renovate[bot]` | `github.com/stackitcloud/stackit-sdk-go/services/dns 0.13.1 -> 0.17.0` | `group_pr_causal_subset` |
| `strawberry-graphql__strawberry__282` | `dependabot-preview[bot]` | `graphql-core 3.1.0b0 -> 3.1.0b2` | `confirmed_exact` |
| `syou6162__times_esa_mcp_server__22` | `renovate[bot]` | `github.com/mark3labs/mcp-go 0.28.0 -> 0.30.0` | `confirmed_exact` |
| `thegeeklab__wp-docker-buildx__349` | `renovate[bot]` | `github.com/urfave/cli/v2 -> github.com/urfave/cli/v3 2.27.6 -> 3.1.1` | `confirmed_exact` |
| `thegeeklab__wp-opentofu__166` | `renovate[bot]` | `github.com/urfave/cli/v2 -> github.com/urfave/cli/v3 2.27.6 -> 3.1.1` | `merged_diff_overrides_bot_declaration` |
| `ubugeeei-prod__ox-content__131` | `dependabot[bot]` | `oxc_* crates 0.44 -> 0.131` | `group_pr_causal_subset` |
| `vectordotdev__vrl__440` | `dependabot[bot]` | `chrono 0.4.28 -> 0.4.30` | `confirmed_exact` |
| `verdaccio__verdaccio__5742` | `renovate[bot]` | `Verdaccio dependency group previous versions -> updated versions` | `group_pr_summary` |
| `xMoelletschi__renoglaab__30` | `renovate[bot]` | `gitlab.com/gitlab-org/api/client-go 0.161.1 -> 1.2.0` | `confirmed_exact` |

## Method

- Read each merged PR title, author, body, merge metadata, and changed-file diff through the GitHub API.
- Parsed Dependabot and Renovate package/version tables where available.
- Compared bot-declared updates with the final merged manifest diff and the packaged benchmark manifest patch.
- Used the gold code patch only to identify which dependency in a group caused the required source repair.
- Did not change benchmark tasks or reported results as part of this audit.

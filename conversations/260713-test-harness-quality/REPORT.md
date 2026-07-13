# DepBench Harness Quality — Complete Problem-Case Inventory

Date: 2026-07-13  
Scope: checked-out `v4-with-test` 219-task corpus and July 13 219x10 final pass matrix.

This inventory expands `131554-gpt-diagnosed-harness.md`. It lists every task identified by at least one concrete quality screen. A task being listed does **not** always mean the task itself should be deleted:

- `ORACLE` means the reconciled two-coder audit classified the task as `TESTS_OTHER_THING` or `UNWITNESSED`; these are candidate quarantine tasks pending dynamic adjudication.
- `NOP passes` means the verifier rewarded a no-edit agent, so the runtime harness did not enforce the dependency upgrade.
- `JAVA_HOME xN` means `N` preserved guarded rerun cells were verifier-invalid. This invalidates those trial results, not necessarily the underlying task.
- `STRUCTURAL` means the task is confirmed unsolvable or hidden-scaffolding-limited under the current information regime.
- `ADVERSARIAL` means visible and hidden tests encode conflicting pre/post-upgrade choices; retain only as an explicitly labeled oracle-direction task.

## Headline counts

| Screen | Tasks | Meaning |
| --- | ---: | --- |
| Reconciled non-witness oracle | 50 | 46 `TESTS_OTHER_THING`, 4 `UNWITNESSED` |
| NOP agent passes | 37 | Confirmed no-edit reward; incomplete screen because only 37 suspects were run |
| Guarded `JAVA_HOME` contamination | 57 | 166 invalid verifier cells |
| Confirmed structural/scaffolding hazard | 2 | nuts-node and actix |
| Confirmed adversarial visible/hidden semantics | 3 | brokeneck, Solana, JavaSecurity |
| Unique tasks flagged by any screen | **122/219** | Categories overlap; this is an investigation inventory, not a 122-task deletion list |
| Zero-pass tasks requiring immediate qualification | **44/93** | Union of 33 non-witness, 12 tainted Maven, and 2 structural/scaffolding tasks |

Overlap among the 122 flagged tasks:

| Flag combination | Tasks |
| --- | ---: |
| Oracle only | 39 |
| `JAVA_HOME` only | 34 |
| NOP only | 19 |
| NOP + `JAVA_HOME` | 14 |
| Oracle + `JAVA_HOME` | 7 |
| Oracle + NOP | 3 |
| Structural only | 2 |
| Adversarial only | 2 |
| `JAVA_HOME` + adversarial | 1 |
| Oracle + NOP + `JAVA_HOME` | 1 |

## Remediation status — 2026-07-13

The 57 `JAVA_HOME`-flagged Maven tasks now restore the Java environment in
their verifier before launching Maven:

- `JAVA_HOME=/opt/java/openjdk`;
- `PATH` begins with the JDK, Maven, and standard system binary directories;
- commands use `bash -c` rather than a login shell that can discard the
  container environment;
- the verifier fails explicitly if `/opt/java/openjdk/bin/java` is absent.

The corresponding 57 DockerHub task-image tags were also repaired in place by
publishing new image configs with `JAVA_HOME`, `PATH`, `MAVEN_HOME`, and
`MAVEN_CONFIG`. Existing filesystem layers were reused; no source/dependency
layers were rebuilt. The old and new manifest digests are recorded in
`harbor_benchmark/reports/java_home_image_repair_2026-07-13.csv`.

Runtime smoke checks covered ArcadeDB (JDK 21), DSpace (JDK 17),
WrongSecrets (JDK 17), and JavaSecurity (JDK 21). A verifier-helper smoke also
passed after deliberately stripping `JAVA_HOME` and Java from the inherited
`PATH`.

The environment defect is repaired for future runs. The 166 historical guarded
cells remain invalid historical observations and still require replay before
the aggregate result matrix is updated.

## P0: all 44 questioned zero-pass tasks

These are the zero-pass tasks that cannot currently support a “consensus-hard” claim.

| Task | Ecosystem | Finding | Required action |
| --- | --- | --- | --- |
| `actix__actix__554` | Cargo | Hidden `trybuild`/`rustversion` dependencies and dead `.stderr` gate | Repackage or quarantine |
| `algolia__react-element-to-jsx-string__305` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `alveusgg__alveusgg__871` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `ampproject__amp-wp__6853` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `apache__maven__12057` | Maven | `JAVA_HOME` invalidated 1 cell | Reverify |
| `ardatan__graphql-tools__7001` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `camunda-community-hub__spring-zeebe__642` | Maven | `TESTS_OTHER_THING`; `JAVA_HOME` invalidated 5 cells | Adjudicate and reverify |
| `chris48s__v8r__22` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `cryostatio__cryostat-legacy__1880` | Maven | `JAVA_HOME` invalidated 2 cells | Reverify |
| `dschadow__JavaSecurity__236` | Maven | `JAVA_HOME` invalidated 1 cell; visible 1M vs hidden 50k Shiro iterations | Reverify and label adversarial |
| `eakmanrq__sqlframe__137` | Python | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `eakmanrq__sqlframe__216` | Python | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `graphql-hive__graphql-config__1103` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `Graylog2__graylog2-server__23926` | Maven | `JAVA_HOME` invalidated 1 cell | Reverify |
| `jenkinsci__warnings-ng-plugin__1278` | Maven | `TESTS_OTHER_THING`; `JAVA_HOME` invalidated 7 cells | Adjudicate and reverify |
| `jo-sm__stylelint_d__185` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `kanton-bern__hellodata-be__315` | Maven | `JAVA_HOME` invalidated 2 cells | Reverify |
| `KnpLabs__server-side-renderer__209` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `ledgersmb__LedgerSMB__8895` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `ledgersmb__LedgerSMB__8904` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `lukas-krecan__JsonUnit__274` | Maven | `JAVA_HOME` invalidated 4 cells | Reverify |
| `mightyiam__eslint-config-love__2178` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `nextcloud__server__39964` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `Nextdoor__vigil__35` | Go | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `nuts-foundation__nuts-node__426` | Go | Random hidden EC key, DID, signatures, and fixtures are unknowable | Quarantine or repackage |
| `onthegomap__planetiler__1430` | Maven | `JAVA_HOME` invalidated 4 cells | Reverify |
| `owncloud__web__11511` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `oxidecomputer__dropshot__1556` | Cargo | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `paularmstrong__onerepo__595` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `promptfoo__promptfoo__8808` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `promptfoo__promptfoo__8918` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `qntm__base65536__37` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `reearth__resium__609` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `reearth__resium__625` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `scinos__yarn-deduplicate__89` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `sladkoff__minecraft-prometheus-exporter__68` | Maven | `TESTS_OTHER_THING`; `JAVA_HOME` invalidated 1 cell | Adjudicate and reverify |
| `smlx__piv-agent__155` | Go | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `synyx__urlaubsverwaltung__2494` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `tekumara__typos-lsp__44` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `tusbar__eslint-config-xo-nextjs__163` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `typescript-eslint__tslint-to-eslint-config__1192` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `urlaubsverwaltung__urlaubsverwaltung__4808` | Maven | `JAVA_HOME` invalidated 2 cells | Reverify |
| `webhintio__hint__4027` | npm | `TESTS_OTHER_THING` | Dynamic three-state adjudication |
| `yahoo__elide__2476` | Maven | `JAVA_HOME` invalidated 6 cells | Reverify |

Two additional zero-pass tasks are confirmed adversarial but are not in the 44-task union above because their oracle audit currently calls them witnesses and they have no `JAVA_HOME` flag:

| Task | Problem |
| --- | --- |
| `nearform__brokeneck__820` | Visible v5 router mocks/prop inputs conflict with hidden canonical v6 hooks/propless components. |
| `solana-labs__solana-program-library__4301` | Visible and hidden tests require mutually exclusive error wrapping, RPC call counts, and instruction counts. |

## Complete 122-task flagged inventory

`Passes` is the July 13 final count out of ten configurations. `JAVA_HOME xN` is the number of preserved invalid guarded cells.

| Task | Ecosystem | Passes | Flags |
| --- | --- | ---: | --- |
| `actix__actix__554` | Cargo | 0/10 | STRUCTURAL: hidden-only trybuild/rustversion deps; dead stderr gate |
| `algolia__react-element-to-jsx-string__305` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `alveusgg__alveusgg__871` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `ampproject__amp-wp__6853` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `apache__maven__12057` | Maven | 0/10 | `JAVA_HOME x1` |
| `ArcadeData__arcadedb__2808` | Maven | 4/10 | `JAVA_HOME x3` |
| `ardatan__graphql-tools__7001` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `arduino__arduino-lint__252` | Go | 10/10 | NOP passes |
| `ashutoshgngwr__noice__673` | npm | 9/10 | ORACLE: `TESTS_OTHER_THING`; NOP passes |
| `AxonIQ__AxonFramework__1654` | Maven | 7/10 | `JAVA_HOME x1` |
| `camunda-community-hub__spring-zeebe__642` | Maven | 0/10 | ORACLE: `TESTS_OTHER_THING`; `JAVA_HOME x5` |
| `chris48s__v8r__22` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `cloudflare__terraform-provider-cloudflare__1131` | Go | 10/10 | NOP passes |
| `cryostatio__cryostat-legacy__1880` | Maven | 0/10 | `JAVA_HOME x2` |
| `cucumber__cucumber-jvm__2642` | Maven | 2/10 | `JAVA_HOME x5` |
| `cucumber__cucumber-jvm__3162` | Maven | 9/10 | NOP passes; `JAVA_HOME x1` |
| `DataSQRL__sqrl__1218` | Maven | 8/10 | NOP passes; `JAVA_HOME x2` |
| `DataSQRL__sqrl__1229` | Maven | 3/10 | NOP passes; `JAVA_HOME x1` |
| `dschadow__JavaSecurity__236` | Maven | 0/10 | `JAVA_HOME x1`; ADVERSARIAL: visible 1M vs hidden 50k Shiro iteration default |
| `DSpace__DSpace__10216` | Maven | 4/10 | NOP passes; `JAVA_HOME x5` |
| `eakmanrq__sqlframe__137` | Python | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `eakmanrq__sqlframe__200` | Python | 9/10 | NOP passes |
| `eakmanrq__sqlframe__216` | Python | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `eakmanrq__sqlframe__466` | Python | 8/10 | NOP passes |
| `eakmanrq__sqlframe__492` | Python | 8/10 | ORACLE: `TESTS_OTHER_THING`; NOP passes |
| `elastic__apm-agent-java__2792` | Maven | 9/10 | NOP passes |
| `enterprise-contract__ec-cli__2134` | Go | 6/10 | NOP passes |
| `eXist-db__exist__4855` | Maven | 1/10 | `JAVA_HOME x3` |
| `eXist-db__exist__5042` | Maven | 6/10 | `JAVA_HOME x2` |
| `firebase__firebase-admin-java__537` | Maven | 1/10 | ORACLE: `TESTS_OTHER_THING`; `JAVA_HOME x5` |
| `frctl__fractal__763` | npm | 8/10 | NOP passes |
| `freechat-fun__freechat__757` | Maven | 6/10 | `JAVA_HOME x2` |
| `giantswarm__mcp-prometheus__165` | Go | 2/10 | ORACLE: `TESTS_OTHER_THING` |
| `github__github-mcp-server__412` | Go | 6/10 | ORACLE: `UNWITNESSED` |
| `golangci__golangci-lint__4718` | Go | 4/10 | ORACLE: `TESTS_OTHER_THING` |
| `GoogleCloudPlatform__spring-cloud-gcp__368` | Maven | 4/10 | `JAVA_HOME x4` |
| `graphql-hive__graphql-config__1103` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `graphql-java-kickstart__graphql-java-tools__560` | Maven | 4/10 | NOP passes; `JAVA_HOME x3` |
| `graphql-java-kickstart__graphql-java-tools__645` | Maven | 1/10 | NOP passes; `JAVA_HOME x5` |
| `graphql-java-kickstart__graphql-java-tools__800` | Maven | 8/10 | NOP passes; `JAVA_HOME x2` |
| `Graylog2__graylog2-server__21446` | Maven | 5/10 | ORACLE: `UNWITNESSED`; NOP passes; `JAVA_HOME x2` |
| `Graylog2__graylog2-server__23926` | Maven | 0/10 | `JAVA_HOME x1` |
| `Graylog2__graylog2-server__24634` | Maven | 8/10 | `JAVA_HOME x1` |
| `gruelbox__transaction-outbox__519` | Maven | 1/10 | `JAVA_HOME x5` |
| `hawtio__hawtio__3776` | Maven | 3/10 | `JAVA_HOME x1` |
| `hetznercloud__hcloud-cloud-controller-manager__628` | Go | 8/10 | NOP passes |
| `INRIA__spoon__6087` | Maven | 5/10 | `JAVA_HOME x3` |
| `INRIA__spoon__6316` | Maven | 4/10 | NOP passes; `JAVA_HOME x6` |
| `jamcalli__Pulsarr__1107` | npm | 10/10 | NOP passes |
| `jenkinsci__kubernetes-plugin__1101` | Maven | 3/10 | `JAVA_HOME x5` |
| `jenkinsci__warnings-ng-plugin__1278` | Maven | 0/10 | ORACLE: `TESTS_OTHER_THING`; `JAVA_HOME x7` |
| `jo-sm__stylelint_d__185` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `JoshuaKGoldberg__create-typescript-app__1489` | npm | 4/10 | ORACLE: `TESTS_OTHER_THING` |
| `kanton-bern__hellodata-be__315` | Maven | 0/10 | `JAVA_HOME x2` |
| `KnpLabs__server-side-renderer__209` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `kroxylicious__kroxylicious__1221` | Maven | 5/10 | `JAVA_HOME x3` |
| `ledgersmb__LedgerSMB__8895` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `ledgersmb__LedgerSMB__8904` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `liquibase__liquibase__2285` | Maven | 5/10 | NOP passes; `JAVA_HOME x3` |
| `lukas-krecan__JsonUnit__274` | Maven | 0/10 | `JAVA_HOME x4` |
| `marp-team__marp-vscode__176` | npm | 4/10 | ORACLE: `TESTS_OTHER_THING` |
| `mightyiam__eslint-config-love__2178` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `mitre__heimdall2__2276` | npm | 8/10 | NOP passes |
| `mozilla__addons-frontend__9637` | npm | 5/10 | ORACLE: `TESTS_OTHER_THING` |
| `nearform__brokeneck__820` | npm | 0/10 | ADVERSARIAL: visible v5 mocks vs hidden canonical v6 hooks |
| `nearform__get-jwks__197` | npm | 7/10 | NOP passes |
| `neo4j__cypher-dsl__373` | Maven | 8/10 | NOP passes; `JAVA_HOME x1` |
| `neo4j__neo4j-spark-connector__510` | Maven | 5/10 | `JAVA_HOME x3` |
| `nextcloud__server__39964` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `Nextdoor__vigil__35` | Go | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `nuts-foundation__nuts-node__426` | Go | 0/10 | STRUCTURAL: random hidden key/fixture; structurally unsolvable |
| `odanado__cloud-cryptographic-wallet__672` | npm | 8/10 | NOP passes |
| `omjadas__hudsucker__88` | Cargo | 1/10 | ORACLE: `TESTS_OTHER_THING` |
| `onthegomap__planetiler__1391` | Maven | 7/10 | `JAVA_HOME x1` |
| `onthegomap__planetiler__1430` | Maven | 0/10 | `JAVA_HOME x4` |
| `onthegomap__planetiler__1512` | Maven | 5/10 | `JAVA_HOME x2` |
| `OpenFeign__querydsl__1685` | Maven | 1/10 | ORACLE: `TESTS_OTHER_THING`; `JAVA_HOME x2` |
| `opengovsg__askgovsg__150` | npm | 10/10 | NOP passes |
| `opentripplanner__OpenTripPlanner__5232` | Maven | 6/10 | NOP passes; `JAVA_HOME x3` |
| `opentripplanner__OpenTripPlanner__5280` | Maven | 6/10 | `JAVA_HOME x1` |
| `opentripplanner__OpenTripPlanner__5430` | Maven | 7/10 | NOP passes; `JAVA_HOME x2` |
| `opentripplanner__OpenTripPlanner__6603` | Maven | 4/10 | `JAVA_HOME x3` |
| `operaton__operaton__1523` | Maven | 1/10 | `JAVA_HOME x5` |
| `operator-framework__java-operator-sdk__178` | Maven | 6/10 | `JAVA_HOME x2` |
| `OWASP__wrongsecrets__1040` | Maven | 1/10 | ORACLE: `TESTS_OTHER_THING`; `JAVA_HOME x3` |
| `OWASP__wrongsecrets__874` | Maven | 5/10 | NOP passes; `JAVA_HOME x4` |
| `OWASP__wrongsecrets__970` | Maven | 5/10 | NOP passes; `JAVA_HOME x5` |
| `owncloud__web__11511` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `oxidecomputer__dropshot__1556` | Cargo | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `paularmstrong__onerepo__595` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `piomin__spring-boot-logging__41` | Maven | 4/10 | `JAVA_HOME x5` |
| `prettier__prettier__10546` | npm | 1/10 | ORACLE: `TESTS_OTHER_THING` |
| `prettier__prettier__12241` | npm | 2/10 | ORACLE: `TESTS_OTHER_THING` |
| `prometheus__client_java__1681` | Maven | 5/10 | `JAVA_HOME x2` |
| `prometheus__client_java__1724` | Maven | 6/10 | ORACLE: `UNWITNESSED`; `JAVA_HOME x2` |
| `promptfoo__promptfoo__8808` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `promptfoo__promptfoo__8918` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `qntm__base65536__37` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `querydsl__querydsl__2878` | Maven | 5/10 | `JAVA_HOME x2` |
| `questdb__questdb__6374` | Maven | 2/10 | `JAVA_HOME x4` |
| `reearth__resium__609` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `reearth__resium__625` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `saveourtool__diktat__1039` | Maven | 8/10 | `JAVA_HOME x1` |
| `saveourtool__diktat__1529` | Maven | 3/10 | `JAVA_HOME x4` |
| `scaleway__scaleway-lib__83` | npm | 4/10 | NOP passes |
| `scinos__yarn-deduplicate__89` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `sequelize__umzug__428` | npm | 9/10 | NOP passes |
| `sladkoff__minecraft-prometheus-exporter__68` | Maven | 0/10 | ORACLE: `TESTS_OTHER_THING`; `JAVA_HOME x1` |
| `smallstep__certificates__2097` | Go | 4/10 | NOP passes |
| `smlx__piv-agent__155` | Go | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `solana-labs__solana-program-library__4301` | npm | 0/10 | ADVERSARIAL: mutually contradictory visible/hidden call/error semantics |
| `stackitcloud__stackit-cert-manager-webhook__94` | Go | 9/10 | NOP passes |
| `synyx__urlaubsverwaltung__2494` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `tekumara__typos-lsp__44` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `tusbar__eslint-config-xo-nextjs__163` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `typescript-eslint__tslint-to-eslint-config__1192` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `ubugeeei-prod__ox-content__131` | Cargo | 9/10 | ORACLE: `UNWITNESSED`; NOP passes |
| `urlaubsverwaltung__urlaubsverwaltung__4808` | Maven | 0/10 | `JAVA_HOME x2` |
| `verdaccio__verdaccio__5742` | npm | 9/10 | NOP passes |
| `webhintio__hint__4027` | npm | 0/10 | ORACLE: `TESTS_OTHER_THING` |
| `wireapp__wire-webapp__13562` | npm | 9/10 | NOP passes |
| `yahoo__elide__2476` | Maven | 0/10 | `JAVA_HOME x6` |

## Interpretation and action boundaries

- **Immediate quarantine/repackage:** nuts-node and actix.
- **Candidate oracle quarantine:** all 50 `ORACLE` tasks. Run the locked three-state check before final removal; prioritize the 33 zero-pass rows and the 22 both-coder agreements.
- **Invalid results, not automatic task deletion:** all 57 `JAVA_HOME` tasks. Repair the guarded environment and reverify all 166 affected cells.
- **Harness exploit:** all 37 NOP-pass tasks. Run NOP across all 219 after adding manifest/version enforcement; the current 37-task list is a lower bound.
- **Separate construct:** brokeneck, Solana, and JavaSecurity. If retained, report them as stale-visible-test/re-baselining tasks, not ordinary hidden-test coverage.

No textual hidden-patch application failure was found in the 405 preserved guarded verifier logs, so this inventory does not label tasks merely because `test.patch` is large or snapshot-based.

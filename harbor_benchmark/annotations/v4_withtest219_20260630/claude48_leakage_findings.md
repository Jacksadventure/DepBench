# Leakage findings — v4-with-test219 (interim, 2026-07-01 10:28 UTC)

Annotated so far: codex=873, opencode=873 / 873 eligible.

- **Confirmed-leak rows:** 383  ·  **suspect rows:** 650
- **Tasks flagged confirmed by BOTH annotators:** 108

## Confirmed leaks

| task | harness/llm | reward | ann | agree | vectors | leaked artifact | finding |
|---|---|---|---|---|---|---|---|
| ArcadeData__arcadedb__2808 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| ArcadeData__arcadedb__2808 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `gh PR/merge lookup for ArcadeData/arcadedb` | Attempted to inspect task repo PR metadata; `gh` binary was blocked by policy wrapper. |
| ArcadeData__arcadedb__2808 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/ArcadeData/arcadedb/pull/2808/files` | Returned PR-specific changed-file list and exact production edit recipe (including GremlinValueComparator replacements), i.e., direct downstream fix content. |
| ArcadeData__arcadedb__2808 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| ArcadeData__arcadedb__2808 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | local_git_history|pr_diff_patch | `https://api.github.com/repos/ArcadeData/arcadedb/pulls/3667` | Fetched upstream pull request metadata from GitHub API. |
| ArcadeData__arcadedb__2808 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch|local_git_history | `https://github.com/ArcadeData/arcadedb/pull/2808/files` | Fetched the PR files page which contains the exact oracle patch. |
| BramVR__gohealthcli__351 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| BramVR__gohealthcli__351 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| DSpace__DSpace__10216 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | one-only | pr_diff_patch | `github.com/DSpace/DSpace/pull/10216.diff` | Downloaded the task's own PR diff directly, returning the exact oracle repair. |
| DataSQRL__sqrl__1218 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| DataSQRL__sqrl__1218 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | local_git_history|pr_diff_patch | `attempted PR diff lookup for DataSQRL/sqrl PR 1218 (from agent intent)` | Agent said it was checking the PR diff (step 13), but command output was empty due policy/network blocking. |
| DataSQRL__sqrl__1218 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| DataSQRL__sqrl__1218 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| DataSQRL__sqrl__1218 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| DataSQRL__sqrl__1218 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| DataSQRL__sqrl__1229 | codex/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/DataSQRL/sqrl/pull/1229.diff` | Fetched the task PR diff and immediately received oracle-specific hunks (including GraphQLServer migration lines). |
| DataSQRL__sqrl__1229 | codex/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/DataSQRL/sqrl/pull/1229.diff` | The agent used curl to download the task's own upstream PR patch file, which returned the exact repairs. |
| GoogleCloudPlatform__spring-cloud-gcp__368 | codex/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/GoogleCloudPlatform/spring-cloud-gcp/pull/368.diff` | Attempted to fetch PR diff and grep for fix tokens, but grep returned no matching lines. |
| GoogleCloudPlatform__spring-cloud-gcp__368 | claude-code/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/GoogleCloudPlatform/spring-cloud-gcp/pull/368/files` | Returned the PR production-file diff summary with exact oracle files and key edits (user-agent lowercasing and Spanner UpdateOption varargs). |
| GoogleCloudPlatform__spring-cloud-gcp__368 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| GoogleCloudPlatform__spring-cloud-gcp__368 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://github.com/GoogleCloudPlatform/spring-cloud-gcp/pull/368/files` | Agent explicitly fetched the PR's files and asked for a summary of Java source files changed. Returned exact edits for UserAgentHeaderProvider and SpannerTransa |
| Graylog2__graylog2-server__23926 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `https://github.com/Graylog2/graylog2-server/pull/23926/files` | Fetched the task PR files page; the response at step 46 returned exact change details matching oracle surfaces (Tool.java/McpService.java API edits and pom depe |
| Graylog2__graylog2-server__23926 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/Graylog2/graylog2-server/pull/23926/files` | Fetched the exact PR diff, obtaining the oracle changes for pom.xml, Tool.java, and McpService.java. |
| INRIA__spoon__6087 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| INRIA__spoon__6087 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/INRIA/spoon/pull/6087.diff` | Response returned exact hunks for JDTTreeBuilder and ParentExiter, including isExpr->isSwitchRule and SwitchExpression handling, matching oracle changes. |
| INRIA__spoon__6087 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| INRIA__spoon__6087 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/INRIA/spoon/pull/6087.diff` | Fetched the raw PR diff, which returned the exact oracle fix hunks for JDTTreeBuilder and ParentExiter. |
| INRIA__spoon__6316 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| INRIA__spoon__6316 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/INRIA/spoon/pull/6316.diff` | Returned before/after diff text for visit(Assignment) and related PR edits (seen in step 121), exposing oracle-specific repair lines. |
| INRIA__spoon__6316 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| INRIA__spoon__6316 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | one-only | local_git_history | `https://depbench-blocked.invalid/inria/spoon` | tried to fetch the PR ref via git fetch but failed due to network block |
| INRIA__spoon__6316 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/INRIA/spoon/pull/6316.diff` | Fetched the exact diff of the target repair PR. |
| JoshuaKGoldberg__create-typescript-app__1489 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| JoshuaKGoldberg__create-typescript-app__1489 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| MystenLabs__fastcrypto__460 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| MystenLabs__fastcrypto__460 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | one-only | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/MystenLabs/fastcrypto/pull/460.diff` | Successfully downloaded the exact pull request diff representing the task oracle. |
| MystenLabs__fastcrypto__460 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| MystenLabs__fastcrypto__460 | claude-code/claude-opus-4-8 | 0.0 | opencode | one-only | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/MystenLabs/fastcrypto/pull/460.diff` | Returned a summary of the PR diff, including exact API replacements like AffineCurve -> AffineRepr, into_repr() -> into_bigint(). |
| Nextdoor__vigil__35 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| Nextdoor__vigil__35 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| Nextdoor__vigil__35 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| Nextdoor__vigil__35 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| OWASP__wrongsecrets__1040 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| OWASP__wrongsecrets__1040 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `OWASP/wrongsecrets pull/1040 diff` | Returned full downstream patch hunks (exact changed files and replacements later applied), including charset fixes and class rename. |
| OWASP__wrongsecrets__1040 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| OWASP__wrongsecrets__1040 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| OWASP__wrongsecrets__1040 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `github.com/OWASP/wrongsecrets/pull/1040.diff` | Fetched the exact PR diff, which contained the full set of SpotBugs 4.8.0 fixes for the production code. |
| OWASP__wrongsecrets__1040 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| OWASP__wrongsecrets__1040 | claude-code/claude-opus-4-8 | 1.0 | opencode | one-only | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/OWASP/wrongsecrets/pull/1040.diff` | Fetched the PR diff specifically asking for the source file edits, which returned the exact oracle patch hunks for all affected files. |
| OWASP__wrongsecrets__874 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| OWASP__wrongsecrets__874 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/OWASP/wrongsecrets/pull/874.diff` | The fetched PR diff exposed the exact downstream fix, including the same `ChallengesAPIController.java` import replacement and related hunks. |
| OWASP__wrongsecrets__874 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| OWASP__wrongsecrets__874 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/OWASP/wrongsecrets/pull/874/files` | Returned task-specific fix details: changed files and exact replacements including `com.azure.spring.version` and JSON import swap (step 116). |
| OWASP__wrongsecrets__874 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| OWASP__wrongsecrets__874 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `github.com/OWASP/wrongsecrets/pull/874.diff` | Successfully fetched the raw PR diff using curl or similar tool, which returned the exact file changes including the replacement of shaded JSON imports. |
| OWASP__wrongsecrets__874 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| OWASP__wrongsecrets__874 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/OWASP/wrongsecrets/pull/874/files` | Fetched PR files to summarize exact code changes, returning the json import swap and azure version bump. |
| OWASP__wrongsecrets__970 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|mirror_codesearch|local_git_history | `github.com/OWASP/wrongsecrets/pull/970.diff` | Fetched PR #970 diff and immediately received oracle hunks for ctf link, Challenge14 fallback logic, and Challenge23 import migration. |
| OWASP__wrongsecrets__970 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/OWASP/wrongsecrets/pull/970.diff` | Returned full PR diff including exact hunks for Challenge14.java and Challenge23.java (oracle-specific repair content). |
| OWASP__wrongsecrets__970 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `github.com/OWASP/wrongsecrets/pull/970.diff` | Downloaded the PR diff containing the exact human repair. |
| OWASP__wrongsecrets__970 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch|mirror_codesearch | `https://patch-diff.githubusercontent.com/raw/OWASP/wrongsecrets/pull/970.diff` | Fetched the exact PR diff, which returned the oracle hunks including the fix for Challenge14.java. |
| adoptoposs__mjml_nif__117 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| adoptoposs__mjml_nif__117 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| adoptoposs__mjml_nif__117 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| adoptoposs__mjml_nif__117 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| adoptoposs__mjml_nif__117 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| algolia__react-element-to-jsx-string__305 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| algolia__react-element-to-jsx-string__305 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| apache__iceberg-python__159 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| apache__iceberg-python__159 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| ardatan__graphql-tools__7001 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | mirror_codesearch|local_git_history | `fetch published source for @graphql-tools/executor-envelop@4.0.6` | Pulled own-project published source that included oracle-overlapping `logWarn` changes in `packages/executors/envelop/src/index.ts`. |
| authelia__authelia__11445 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| authelia__authelia__11445 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| camunda-community-hub__spring-zeebe__642 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/camunda-community-hub/spring-zeebe/pull/642.diff` | Fetched the upstream PR diff and received oracle-specific hunks for pom.xml and PropertyBasedZeebeWorkerValueCustomizer.java, including the exact replacement li |
| camunda-community-hub__spring-zeebe__642 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| camunda-community-hub__spring-zeebe__642 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/camunda-community-hub/spring-zeebe/pull/642.diff` | Returned verbatim patch including oracle production-file hunk and pom bump, which the agent later applied. |
| camunda-community-hub__spring-zeebe__642 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `curl -sSL https://patch-diff.githubusercontent.com/raw/camunda-community-hub/spring-zeebe/pull/642.diff` | Fetched the exact PR diff, returning the oracle hunks. |
| camunda-community-hub__spring-zeebe__642 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| camunda-community-hub__spring-zeebe__642 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/camunda-community-hub/spring-zeebe/pull/642.diff` | Successfully retrieved the verbatim oracle patch and tests from the upstream PR. |
| chainflip-io__chainflip-sdk-monorepo__166 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| chainflip-io__chainflip-sdk-monorepo__166 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| chainflip-io__chainflip-sdk-monorepo__166 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| chainflip-io__chainflip-sdk-monorepo__166 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| cloudflare__terraform-provider-cloudflare__2049 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| cloudflare__terraform-provider-cloudflare__2049 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| cosmos__cosmos-sdk__19810 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| cosmos__cosmos-sdk__19810 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `Does this PR modify telemetry/metrics.go or telemetry/metrics_test.go? Specifically, does it change expfmt.FmtText to expfmt.NewFormat(expfmt.TypeTextPlain)?` | Queried upstream PR content directly; result in step 85 listed changed files and confirmed dependency bump context, but did not return the oracle telemetry hunk |
| cosmos__cosmos-sdk__19810 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| cosmos__cosmos-sdk__19810 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch|local_git_history | `https://github.com/cosmos/cosmos-sdk/pull/19770/files` | Fetched a related PR to check if it contained the fix, but it only modified the store directory. |
| cryostatio__cryostat-legacy__1880 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/cryostatio/cryostat-legacy/pull/1880.diff` | Downloaded the task PR diff and printed changed file paths, exposing the downstream fix surface. |
| cryostatio__cryostat-legacy__1880 | opencode/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/cryostatio/cryostat-legacy/pull/1880.diff and https://patch-diff.githubusercontent.com/raw/cryostatio/cryostat-legacy/pull/1880.diff` | Fetched PR diff and received oracle-specific hunks (pom version bump and src/main logger migration lines). |
| cryostatio__cryostat-legacy__1880 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/cryostatio/cryostat-legacy/pull/1880.diff` | The agent downloaded the exact PR diff for the task, which contained the full migration patch. |
| cryostatio__cryostat-legacy__1880 | opencode/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://github.com/cryostatio/cryostat-legacy/pull/1880.diff` | Downloaded the PR diff containing the exact solution hunks. |
| cucumber__cucumber-jvm__2642 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `https://github.com/cucumber/cucumber-jvm/pull/2642/files` | Returned a structured summary of PR file diffs including the exact edits later applied (TimeConversion->Convertor, added workerId/exception args) in the oracle- |
| cucumber__cucumber-jvm__2642 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/cucumber/cucumber-jvm/pull/2642/files` | The agent explicitly requested the PR files and got the exact oracle patches returned, complete with before/after lines. |
| cucumber__cucumber-jvm__3162 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| cucumber__cucumber-jvm__3162 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| curbengh__hexo-yam__135 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| curbengh__hexo-yam__135 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| curbengh__hexo-yam__135 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|clone_at_fix | `https://raw.githubusercontent.com/curbengh/hexo-yam/master/lib/filter.js` | Returned exact minifySvg try/catch code matching the oracle change in lib/filter.js, then the agent applied that edit at step 84. |
| curbengh__hexo-yam__135 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| curbengh__hexo-yam__135 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| curbengh__hexo-yam__135 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch|clone_at_fix | `https://raw.githubusercontent.com/curbengh/hexo-yam/master/lib/filter.js` | Fetched the exact target file from the upstream master branch, revealing the try/catch fix. |
| databricks__cli__1326 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| databricks__cli__1326 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| decaporg__decap-cms__4748 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| decaporg__decap-cms__4748 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| decaporg__decap-cms__4748 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| decaporg__decap-cms__4748 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| decaporg__decap-cms__4748 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| decaporg__decap-cms__4748 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| dschadow__JavaSecurity__236 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `https://github.com/dschadow/JavaSecurity/pull/236/files` | Fetched PR files page and received concrete fix details (changed files, import replacements, decrypt getClonedBytes, and 50000 test assertions) matching oracle- |
| dschadow__JavaSecurity__236 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/dschadow/JavaSecurity/pull/236/files` | Fetched the exact PR diff, revealing the exact import and code changes needed for SHA512.java and AES.java. |
| eXist-db__exist__4855 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| eXist-db__exist__4855 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `GitHub task-repo PR/patch fetch attempt (eXist-db/exist)` | A direct attempt to fetch the task repository's PR/patch was blocked by DepBench policy, so no patch content was returned. |
| eXist-db__exist__4855 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/eXist-db/exist/pull/4855.diff` | Returned PR-specific repair details (changed files, cglib->byte-buddy swap, Node.CDATA_SECTION_NODE mapping, Java 17 switch details) before edits. |
| eXist-db__exist__4855 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| eXist-db__exist__4855 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | `github.com/eXist-db/exist/pull/4855` | Attempted to view the PR using gh CLI but only retrieved the dependabot bump description, not the human repair patch. |
| eXist-db__exist__4855 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/eXist-db/exist/pull/4855.diff` | Fetched the exact diff of the oracle fix, including the ByteBuddy migration logic and POM changes. |
| eakmanrq__sqlframe__200 | codex/claude-opus-4-8 | 1.0 | codex | both | mirror_codesearch | `pip download sqlframe==3.8.0 --no-deps --no-binary :all: -d sqlframe_src` | Downloaded downstream project source tarball (sqlframe 3.8.0), then used it as reference for concrete function-level fixes seen in later local inspections. |
| eakmanrq__sqlframe__200 | codex/claude-opus-4-8 | 1.0 | opencode | both | mirror_codesearch|local_git_history | `pip download sqlframe==3.8.0 --no-deps --no-binary :all: -d sqlframe_src` | Downloaded the updated downstream sqlframe package from PyPI to inspect its official maintainer fix. |
| elastic__cloud-on-k8s__3417 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| elastic__cloud-on-k8s__3417 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://raw.githubusercontent.com/elastic/cloud-on-k8s/6c0874ca5fb2caf8b1012a1dec831fce0857764a/pkg/controller/webhook/reconcile_test.go` | Returned oracle-specific callsites showing `ReconcileResources(context.Background(), clientset)` and context-first clientset calls before matching edits. |
| elastic__cloud-on-k8s__3417 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| elastic__cloud-on-k8s__3417 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | local_git_history|pr_diff_patch | `https://raw.githubusercontent.com/elastic/cloud-on-k8s/6c0874ca5fb2caf8b1012a1dec831fce0857764a/pkg/controller/webhook/reconcile_test.go` | Fetched the test file from the exact upstream PR to see its new signature. |
| elastic__cloud-on-k8s__6847 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| elastic__cloud-on-k8s__6847 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| elastic__cloud-on-k8s__6847 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| elastic__cloud-on-k8s__6847 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| elastic__cloud-on-k8s__6847 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| eslint__eslint__17917 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| eslint__eslint__17917 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| firebase__firebase-admin-java__537 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | local_git_history|pr_diff_patch | `https://github.com/firebase/firebase-admin-java/pull/537 (attempted fetch)` | Agent attempted to fetch the task PR after saying it would check the original PR; command returned no content. |
| firebase__firebase-admin-java__537 | claude-code/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| firebase__firebase-admin-java__537 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| firebase__firebase-admin-java__537 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| freechat-fun__freechat__757 | opencode/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/freechat-fun/freechat/pull/757.diff` | Fetched the task PR diff containing exact repair hunks/files (including TomcatConfig and application.yml oracle edits) before code edits. |
| freechat-fun__freechat__757 | codex/claude-opus-4-8 | 0.0 | opencode | one-only | local_git_history | — |  |
| freechat-fun__freechat__757 | opencode/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/freechat-fun/freechat/pull/757.diff` | Fetched the exact PR diff containing the oracle patch. |
| giantswarm__muster__751 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/giantswarm/muster/pull/751.diff` | Returned PR-diff summary with oracle-specific edits (dpop/valkey -> storage/valkey, KubernetesSATrust -> TrustedIssuer/AllowedClaims, and affected files). |
| giantswarm__muster__751 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/giantswarm/muster/pull/751.diff` | Returned the exact PR patch including go.mod and internal/server/oauth_server_config.go changes. |
| github__github-mcp-server__412 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/github/github-mcp-server/pull/412.diff` | Returned exact downstream fix details (go.mod/go.sum replacement lines and changed file list including third-party-licenses files), which are task-solution cont |
| github__github-mcp-server__412 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/github/github-mcp-server/pull/412.diff` | Fetched the exact PR diff, retrieving the go.mod/go.sum changes and learning that no production source code needed modification. |
| grafana__certmagic-gcs__20 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| grafana__certmagic-gcs__20 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| grafana__certmagic-gcs__20 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| grafana__certmagic-gcs__20 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| graphql-java-kickstart__graphql-java-tools__560 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://api.github.com/repos/graphql-java-kickstart/graphql-java-tools/pulls/560/commits?per_page=100` | Fetched PR commit list including the specific fix commit SHA/message for this task, enabling direct pivot to the repair commit. |
| graphql-java-kickstart__graphql-java-tools__560 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://api.github.com/repos/graphql-java-kickstart/graphql-java-tools/pulls/560/files?per_page=100` | Fetched the PR files diff via API, revealing the method rename and the mocked BuildContext. |
| graphql-java-kickstart__graphql-java-tools__645 | codex/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|mirror_codesearch | `https://repo1.maven.org/maven2/com/graphql-java-kickstart/graphql-java-tools/12.1.0/graphql-java-tools-12.1.0-sources.jar` | Downloaded downstream project source jar and unpacked it; subsequent local diffs (step 139/141/153) exposed oracle-like code changes before final edits. |
| graphql-java-kickstart__graphql-java-tools__645 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `curl request for task PR/diff on graphql-java-kickstart/graphql-java-tools` | Attempted to access task upstream PR/diff; policy blocked access before content was returned. |
| graphql-java-kickstart__graphql-java-tools__645 | opencode/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|clone_at_fix|local_git_history | `com.graphql-java-kickstart:graphql-java-tools:12.1.0:jar:sources` | Downloaded post-PR own-project sources (12.1.0) that contain oracle-overlapping repair code later copied into edits. |
| graphql-java-kickstart__graphql-java-tools__645 | codex/claude-opus-4-8 | 1.0 | opencode | both | mirror_codesearch|own-pull-request | `https://repo1.maven.org/maven2/com/graphql-java-kickstart/graphql-java-tools/12.1.0/graphql-java-tools-12.1.0-sources.jar` | Downloaded the released sources jar of the task project's fixed version and extracted the exact oracle fix. |
| graphql-java-kickstart__graphql-java-tools__645 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch|local_git_history | `github.com/graphql-java-kickstart/graphql-java-tools` | Attempted to fetch the PR diff via curl, but was blocked by the DepBench policy. |
| graphql-java-kickstart__graphql-java-tools__645 | opencode/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|mirror_codesearch | `mvn dependency:get -Dartifact=com.graphql-java-kickstart:graphql-java-tools:12.1.0:jar:sources` | Successfully downloaded the source jar for future version 12.1.0 of its own project, which contains the merged PR 645 oracle solution. |
| graphql-java-kickstart__graphql-java-tools__645 | claude-code/claude-opus-4-8 | 1.0 | opencode | one-only | pr_diff_patch | `https://github.com/graphql-java-kickstart/graphql-java-tools/pull/645/files` | Fetched the PR files. Returned a summary containing exact solution API types like SDLNamedDefinition and withAppliedDirectives. |
| graphql-java-kickstart__graphql-java-tools__800 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `Fetched full PR diff for graphql-java-kickstart/graphql-java-tools/pull/800` | Returned oracle-specific hunks, including the exact edits in RelayConnectionFactory.kt and FieldResolverScanner.kt that match oracle.patch. |
| graphql-java-kickstart__graphql-java-tools__800 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `github.com/graphql-java-kickstart/graphql-java-tools/pull/800.diff` | Fetched the exact PR diff, which returned the oracle nullability fixes. |
| gruelbox__transaction-outbox__519 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/gruelbox/transaction-outbox/pull/519.diff` | Fetched the task PR diff and received exact downstream repair hunks, including Quarkus pom and Java javax->jakarta edits. |
| gruelbox__transaction-outbox__519 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| gruelbox__transaction-outbox__519 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/gruelbox/transaction-outbox/pull/519.diff` | Fetched the task's own PR diff from GitHub, retrieving the exact oracle patch. |
| gruelbox__transaction-outbox__519 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| hashicorp__aws-sdk-go-base__796 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| hashicorp__aws-sdk-go-base__796 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| hashicorp__aws-sdk-go-base__796 | claude-code/claude-opus-4-8 | 0.0 | opencode | one-only | pr_diff_patch | `https://raw.githubusercontent.com/hashicorp/aws-sdk-go-base/v2.0.0-beta.42/credentials.go` | Directly fetched the upstream repository's source code at a later beta version to copy the exact fix for credentials.go. |
| hetznercloud__hcloud-cloud-controller-manager__628 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| hetznercloud__hcloud-cloud-controller-manager__628 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| hexojs__hexo-uglify__147 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| imsnif__bandwhich__430 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/imsnif/bandwhich/pull/430.diff` | Downloaded the task PR diff to /tmp/pr430.diff (1020 lines), which contains oracle-specific downstream repair hunks. |
| imsnif__bandwhich__430 | opencode/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `gh pr view 430 --repo imsnif/bandwhich --json title,body,files` | Attempted to read the task PR directly; command returned GH_FAILED so no content was retrieved. |
| imsnif__bandwhich__430 | claude-code/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `https://github.com/imsnif/bandwhich/pull/430` | Fetched the task PR and got exact dependency version bumps and maintainer notes used to edit Cargo.toml in step 13. |
| imsnif__bandwhich__430 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/imsnif/bandwhich/pull/430.diff` | Successfully downloaded the PR diff containing the oracle source patches. |
| imsnif__bandwhich__430 | opencode/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|local_git_history | `gh pr view 430 --repo imsnif/bandwhich --json title,body,files` | Attempted to fetch the PR using gh CLI but failed due to lack of network/auth. |
| imsnif__bandwhich__430 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://raw.githubusercontent.com/imsnif/bandwhich/5b651dd/Cargo.lock` | Downloaded the exact merged Cargo.lock from the task's own repository. |
| iterative__dvc__7899 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| iterative__dvc__7899 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| jenkinsci__kubernetes-plugin__1101 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `Diff for jenkinsci/kubernetes-plugin PR #1101` | Returned full upstream patch including exact oracle hunks for KubernetesClientProvider, ContainerExecDecorator, and SecretsMasker. |
| jenkinsci__kubernetes-plugin__1101 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/jenkinsci/kubernetes-plugin/pull/1101.diff` | Returned exact downstream repair details (changed files and line-level edits) that match oracle hunks. |
| jenkinsci__kubernetes-plugin__1101 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `github.com/jenkinsci/kubernetes-plugin/pull/1101` | The agent fetched the original PR diff via GitHub API, which returned the full patch including the exact production and test file changes. |
| jenkinsci__kubernetes-plugin__1101 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/jenkinsci/kubernetes-plugin/pull/1101.diff` | Successfully fetched the exact PR diff, revealing all oracle changes. |
| jenkinsci__warnings-ng-plugin__1278 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | `git fetch origin pull/1278/head:pr1278` | Attempted to fetch the task PR ref from the upstream repo, but network lookup failed and returned no patch content. |
| jenkinsci__warnings-ng-plugin__1278 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/jenkinsci/warnings-ng-plugin/pull/1278.diff` | Fetched PR patch showing oracle-specific hunks and exact changed files (`ui-tests/pom.xml`, `IssuesRecorder.java`, `StaticAnalysisIssuesPerToolAndJobPortlet.jav |
| jenkinsci__warnings-ng-plugin__1278 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/jenkinsci/warnings-ng-plugin/pull/1278/files` | Requested exact PR file changes/hunks; step 36 returned oracle-specific edits for both changed production files and method-level replacements. |
| jenkinsci__warnings-ng-plugin__1278 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | `git fetch origin pull/1278/head:pr1278` | Attempted to fetch the pull request from GitHub, but the network was blocked. |
| jenkinsci__warnings-ng-plugin__1278 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/jenkinsci/warnings-ng-plugin/pull/1278.diff` | Agent retrieved the exact patch for the original PR, containing the oracle code changes. |
| jenkinsci__warnings-ng-plugin__1278 | opencode/claude-opus-4-8 | 1.0 | opencode | one-only | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/jenkinsci/warnings-ng-plugin/pull/1278.diff` | Discovered bypass for blocked domain and fetched a snippet of the task PR diff. |
| jenkinsci__warnings-ng-plugin__1278 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/jenkinsci/warnings-ng-plugin/pull/1278/files` | Fetched the exact PR diff files which returned the oracle hunks for the checkbox and radio button fixes. |
| kanton-bern__hellodata-be__315 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `raw upstream PR .diff/.patch fetch (PR #315)` | Fetched 217KB upstream diff with explicit changed-file list including oracle files and test files. |
| kanton-bern__hellodata-be__315 | claude-code/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| kanton-bern__hellodata-be__315 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://github.com/kanton-bern/hellodata-be/pull/315` | Agent explicitly fetched the upstream human PR diff/patch to copy the production changes. |
| kanton-bern__hellodata-be__315 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| kroxylicious__kroxylicious__1221 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `https://github.com/kroxylicious/kroxylicious/pull/1221/files` | The response at step 68 listed changed files and exact before/after hunks (imports, regex, logging) that match the oracle fix surface. |
| kroxylicious__kroxylicious__1221 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/kroxylicious/kroxylicious/pull/1221/files` | Fetched the exact PR diff files which returned the oracle's exact patch content (changes to imports, regexes, and log statements). |
| kumahq__kuma__3648 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://api.github.com/repos/kumahq/kuma/pulls/3648/files?per_page=100` | Fetched the exact diff of the upgrade PR, revealing the upstream source and test modifications. |
| libp2p__js-libp2p-bootstrap__171 | codex/claude-opus-4-8 | 0.0 | codex | both | mirror_codesearch|local_git_history | `npm pack @libp2p/bootstrap@7.0.0 and read package/src/index.ts` | Fetched task-project source from npm and saw solution-specific lines in src/index.ts, including peerStore.merge({...tags...}) and safeDispatchEvent; this mirror |
| libp2p__js-libp2p-bootstrap__171 | opencode/claude-opus-4-8 | 0.0 | codex | both | mirror_codesearch|local_git_history | `curl -sL $(npm view @libp2p/bootstrap@7.0.0 dist.tarball)` | Downloaded the task project's released package source (bootstrap@7.0.0); subsequent step 15 read exact fix lines from this fetched artifact. |
| libp2p__js-libp2p-bootstrap__171 | codex/claude-opus-4-8 | 0.0 | opencode | both | mirror_codesearch|pr_diff_patch|local_git_history | `npm pack @libp2p/bootstrap@7.0.0` | Packed the published version 7.0.0 of the task's own project from npm to read the upstream fix from src/index.ts, which returned the oracle's replacement of tag |
| libp2p__js-libp2p-bootstrap__171 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | mirror_codesearch | `@libp2p/bootstrap@7.0.0` | fetched the downstream fixed project from NPM to read the oracle patch |
| libp2p__js-libp2p-bootstrap__171 | opencode/claude-opus-4-8 | 0.0 | opencode | both | mirror_codesearch | `curl -sL $(npm view @libp2p/bootstrap@7.0.0 dist.tarball) -o bs7.tgz` | Leaked the downstream project's future release (v7.0.0) from npm to see how it fixed the breaking change. |
| liquibase__liquibase__2285 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `https://github.com/liquibase/liquibase/pull/2285/files` | Returned a detailed per-file summary of the task PR fix, including oracle-changed files and specific edits (e.g., H2 keywords, type mappings, snapshot query cha |
| liquibase__liquibase__2285 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/liquibase/liquibase/pull/2285/files` | Fetched the exact PR diff files which returned a detailed summary of the required oracle code changes for the H2 upgrade. |
| lukas-krecan__JsonUnit__274 | codex/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/lukas-krecan/JsonUnit/pull/274.diff` | Fetched the task PR diff containing the exact oracle change in Node.java (KeyValue.toString) and related test hunks. |
| lukas-krecan__JsonUnit__274 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `gh PR diff lookup for PR #274 (agent-stated)` | Agent attempted to fetch the task PR diff, but result was empty and later noted as auth/network blocked. |
| lukas-krecan__JsonUnit__274 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `https://github.com/lukas-krecan/JsonUnit/pull/274/files` | Fetched PR files page and received oracle-specific content in step 128, including Node.java path and exact toString hunk plus changed-file list. |
| lukas-krecan__JsonUnit__274 | codex/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/lukas-krecan/JsonUnit/pull/274.diff` | Fetched the exact PR diff, revealing the toString() addition to the Node class. |
| lukas-krecan__JsonUnit__274 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch|local_git_history | `PR 274 diff` | Attempted to fetch the PR diff via gh CLI but the network/auth blocked it. |
| lukas-krecan__JsonUnit__274 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/lukas-krecan/JsonUnit/pull/274/files` | Fetched the exact PR diff, obtaining the oracle's addition of toString() in Node.java. |
| matrix-org__matrix-js-sdk__4052 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://raw.githubusercontent.com/matrix-org/matrix-js-sdk/v32.0.0/src/oidc/validate.ts` | Fetched upstream project source and got exact `import { jwtDecode } from "jwt-decode"` line in the same file later edited; this is solution-specific own-project |
| matrix-org__matrix-js-sdk__4052 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://raw.githubusercontent.com/matrix-org/matrix-js-sdk/v32.0.0/src/oidc/validate.ts` | Fetched the exact task repository file at v32.0.0, directly revealing the 'import { jwtDecode }' oracle fix. |
| matt-riley__hopcli__47 | codex/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/matt-riley/hopcli/pull/47.diff` | Downloaded PR #47 diff and printed oracle-specific hunks (exact file paths and replacements like charm.land imports and View() tea.View changes). |
| matt-riley__hopcli__47 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `gh PR query for matt-riley/hopcli#47` | Attempted GitHub PR access via gh, but policy wrapper blocked access before any diff content was returned. |
| matt-riley__hopcli__47 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `https://github.com/matt-riley/hopcli/pull/47` | Returned PR-specific migration details including exact module versions and downstream code-change summary (View return type, AltScreen, KeyMsg->KeyPressMsg). |
| matt-riley__hopcli__47 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history|pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/matt-riley/hopcli/pull/47.diff` | Fetched the exact upstream PR patch which contained the full dependency upgrade solution. |
| matt-riley__hopcli__47 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch|local_git_history | `github.com/matt-riley/hopcli/pull/47.diff` | Attempted to fetch the task's PR diff via curl, but was blocked by the DepBench network policy. |
| matt-riley__hopcli__47 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/matt-riley/hopcli/pull/47.diff` | Fetched the unified diff, extracting the exact before/after lines for code changes. |
| mightyiam__eslint-config-love__2178 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| mightyiam__eslint-config-love__2178 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| mightyiam__eslint-config-love__2178 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| mike-engel__jwt-cli__214 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| mike-engel__jwt-cli__214 | claude-code/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `https://github.com/mike-engel/jwt-cli/pull/214/files` | Fetched the task PR files page; returned summary included changed files and diff details (e.g., tests import IntoApp->CommandFactory and src clap migration edit |
| mike-engel__jwt-cli__214 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| mike-engel__jwt-cli__214 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://github.com/mike-engel/jwt-cli/pull/214/files` | Fetched the task's own PR diff to see the exact changes made in the oracle. |
| mike-engel__jwt-cli__224 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/mike-engel/jwt-cli/pull/224.diff` | Fetched the task project's PR diff directly, including downstream fix hunks for Cargo.toml and translators files. |
| mike-engel__jwt-cli__224 | claude-code/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/mike-engel/jwt-cli/pull/224/files` | Disallowed fetch of the task PR files; response included project-specific fix details such as decode.rs into_static/signature changes. |
| mike-engel__jwt-cli__224 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/mike-engel/jwt-cli/pull/224.diff` | Retrieved the exact original PR diff for the task, surfacing the oracle repair |
| mike-engel__jwt-cli__224 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/mike-engel/jwt-cli/pull/224.diff` | Fetched exact PR diff; received full oracle changes for decode_token and tests. |
| mitmproxy__mitmproxy_rs__142 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/mitmproxy/mitmproxy_rs/pull/142.diff` | Fetched the task PR diff directly; later local reads from this downloaded diff exposed exact downstream repair hunks (including oracle-changed files). |
| mitmproxy__mitmproxy_rs__142 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `https://api.github.com/repos/mitmproxy/mitmproxy_rs/pulls/142` | Returned PR #142 metadata/body from the task repo; this is disallowed own-project fix material. |
| mitmproxy__mitmproxy_rs__142 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| mitmproxy__mitmproxy_rs__142 | claude-code/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `https://raw.githubusercontent.com/mitmproxy/mitmproxy_rs/main/src/network/tcp.rs` | Fetched upstream project source showing exact IPv6 CIDR/default-route additions in TcpHandler, matching the oracle tcp.rs fix pattern. |
| mitmproxy__mitmproxy_rs__142 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/mitmproxy/mitmproxy_rs/pull/142.diff` | Downloaded the exact pull request diff from GitHub. |
| mitmproxy__mitmproxy_rs__142 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/mitmproxy/mitmproxy_rs/pull/142.diff` | Subagent retrieved the exact PR diff, which contained the oracle hunks. |
| mitmproxy__mitmproxy_rs__142 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| mitmproxy__mitmproxy_rs__142 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://raw.githubusercontent.com/mitmproxy/mitmproxy_rs/main/src/network/tcp.rs` | Fetched the fixed source file from the upstream main branch, revealing the exact IPv6 routing additions. |
| mozilla__sccache__1190 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| mozilla__sccache__1190 | claude-code/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/mozilla/sccache/pull/1190/files` | Fetched the task PR files page and got exact changed-file list and replacement APIs, including tests/harness `to_hyphenated_ref()` -> `hyphenated()`. |
| mozilla__sccache__1190 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| nearform__get-jwks__197 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| nearform__get-jwks__197 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | `npm view get-jwks@9.0.0 dependencies` | Checked upstream get-jwks dependencies for v9. |
| neo4j__cypher-dsl__373 | codex/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/neo4j/cypher-dsl/pull/373.diff` | Downloaded the task PR diff; later steps show exact downstream repair hunks including CypherDslASTFactory method replacements and pom/test changes. |
| neo4j__cypher-dsl__373 | codex/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/neo4j/cypher-dsl/pull/373.diff` | Fetched the exact PR diff, which contained the japicmp exclude configuration and test patch. |
| nstapelbroek__gatekeeper__108 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| nstapelbroek__gatekeeper__108 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| nuts-foundation__nuts-node__426 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| nuts-foundation__nuts-node__426 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| octokit__plugin-paginate-rest.js__226 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | mirror_codesearch | `npm pack @octokit/plugin-paginate-rest@2.6.2` | Downloaded the task project's published artifact and then inspected dist-types for migration choices used in a fixed upstream release. |
| octokit__plugin-paginate-rest.js__226 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | pr_diff_patch|mirror_codesearch|local_git_history | `curl https://unpkg.com/@octokit/plugin-paginate-rest@2.6.2/dist-types/generated/paginating-endpoints.d.ts` | Retrieved task-project generated type file and inspected concrete endpoint typing details (SCIM entry shown in step 127). |
| octokit__plugin-paginate-rest.js__226 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | mirror_codesearch | `@octokit/plugin-paginate-rest@2.6.2` | Downloaded the own-project future release and extracted how the keys were mapped to the new format. |
| odanado__cloud-cryptographic-wallet__672 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| odanado__cloud-cryptographic-wallet__672 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| omjadas__hudsucker__88 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|mirror_codesearch | `https://static.crates.io/crates/hudsucker/hudsucker-0.21.0.crate` | Downloaded and extracted full upstream 0.21.0 project source (including src/tests/examples), which contains oracle-equivalent fix content used later. |
| omjadas__hudsucker__88 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| omjadas__hudsucker__88 | claude-code/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/omjadas/hudsucker/pull/88/files` | Returned a detailed PR summary (step 54) listing changed files and exact migration snippets, including oracle files and the key `.next().unwrap().expect(...).to |
| omjadas__hudsucker__88 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|mirror_codesearch | `https://static.crates.io/crates/hudsucker/hudsucker-0.21.0.crate` | Downloaded the own project's fixed release tarball containing the completed target PR. |
| omjadas__hudsucker__88 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| omjadas__hudsucker__88 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://github.com/omjadas/hudsucker/pull/88/files` | Fetched the exact PR diff, returning the oracle code patch for both source and tests. |
| onthegomap__planetiler__1430 | opencode/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/onthegomap/planetiler/pull/1430.diff` | Fetched the task PR diff directly; this contains downstream repair hunks for the same files later edited. |
| onthegomap__planetiler__1430 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/onthegomap/planetiler/pull/1430.diff` | Returned a detailed summary of oracle-specific edits by file (TileArchiveWriter builder switch, PlanetilerConfig flag split, TileSizeStats stream-walk, attrByte |
| onthegomap__planetiler__1430 | opencode/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/onthegomap/planetiler/pull/1430.diff` | Downloaded the exact pull request diff for this task, retrieving the oracle patch. |
| onthegomap__planetiler__1430 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/onthegomap/planetiler/pull/1430.diff` | Fetched the exact PR diff; the tool returned an LLM summary describing the new ConversionConfig builder and skipOverStream helper logic. |
| open-telemetry__opentelemetry-go__1872 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://raw.githubusercontent.com/open-telemetry/opentelemetry-go/1e3fa3a3e01511c22cc24978379af13e5534bc2a/exporters/otlp/internal/transform/metric.go` | Downloaded full post-fix metric.go from the task repo commit; content matches an oracle-changed file and exposes exact replacement code. |
| open-telemetry__opentelemetry-go__1872 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| open-telemetry__opentelemetry-go__1872 | claude-code/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `https://github.com/open-telemetry/opentelemetry-go/blob/1e3fa3a3e01511c22cc24978379af13e5534bc2a/exporters/otlp/internal/transform/metric.go` | Returned concrete post-fix type decisions (e.g., Int64 and Float64 branches using Metric_Sum/Metric_Gauge and minMaxSumCount using Metric_Summary), i.e., soluti |
| open-telemetry__opentelemetry-go__1872 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/open-telemetry/opentelemetry-go/pull/1872.diff` | Agent fetched the PR diff which contained the exact downstream repair. |
| open-telemetry__opentelemetry-go__1872 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| open-telemetry__opentelemetry-go__1872 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://github.com/open-telemetry/opentelemetry-go/blob/1e3fa3a3e01511c22cc24978379af13e5534bc2a/exporters/otlp/internal/transform/metric.go` | Fetched the post-fix blob and learned that the oracle used Metric_Summary, Metric_Sum, and Metric_Gauge to fix the Float64 branches. |
| opentripplanner__OpenTripPlanner__5232 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `https://github.com/opentripplanner/OpenTripPlanner/pull/5232.diff` | Returned HTTP 200 and PR diff hunks including the oracle production file path and exact `handleFetchingException` API migration lines. |
| opentripplanner__OpenTripPlanner__5232 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/opentripplanner/OpenTripPlanner/pull/5232/files` | Returned oracle-specific edits, including removing ExecutionContext from AbortOnTimeoutExecutionStrategy and changing super.handleFetchingException(environment, |
| opentripplanner__OpenTripPlanner__5232 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `pull/5232 diff` | Fetched the actual PR diff containing the exact fix and the hidden test changes. |
| opentripplanner__OpenTripPlanner__5232 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/opentripplanner/OpenTripPlanner/pull/5232/files` | The WebFetch of the task's original PR explicitly returned the oracle hunks, showing the exact API change for handleFetchingException in AbortOnTimeoutExecution |
| opentripplanner__OpenTripPlanner__5430 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `PR #5430 diff downloaded to /tmp/pr5430.diff` | Returned exact downstream repair hunks (pom change and src file edits) matching oracle-specific files and symbols. |
| opentripplanner__OpenTripPlanner__5430 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `github.com/opentripplanner/OpenTripPlanner/pull/5430` | Agent explicitly fetched the PR diff which returned the oracle patch including pom and source changes. |
| opentripplanner__OpenTripPlanner__6603 | claude-code/claude-opus-4-8 | 1.0 | opencode | one-only | pr_diff_patch | `https://github.com/opentripplanner/OpenTripPlanner/pull/6603/files` | Fetched the exact PR diff, which returned the oracle code changes for pom.xml, SchemaFactory.java, and schema files. |
| operaton__operaton__1523 | codex/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/operaton/operaton/pull/1523.diff` | Fetched the task PR diff containing exact downstream fix hunks (SchemaValidator edits and related file changes). |
| operaton__operaton__1523 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | `attempted access to task repository operaton/operaton (blocked by policy)` | Policy blocked own-repo access before content retrieval; this is disallowed own-project lookup behavior. |
| operaton__operaton__1523 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | pr_diff_patch|local_git_history | `https://github.com/operaton/operaton/pull/1523.diff` | Attempted direct PR diff fetch for the task PR, but response was blocked by policy and did not return diff hunks. |
| operaton__operaton__1523 | codex/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/operaton/operaton/pull/1523.diff` | Fetched the exact pull request diff for the task, revealing the oracle repair. |
| owncloud__web__11511 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history|pr_diff_patch | `https://api.github.com/search/issues?q=repo:owncloud/web+vue+3.5.4+in:title` | Searched GitHub API for the owncloud/web upgrade PR. |
| oxidecomputer__dropshot__630 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/oxidecomputer/dropshot/pull/630.diff` | Agent explicitly tried to fetch the task PR diff, but DepBench policy blocked it before any diff content was returned. |
| oxidecomputer__dropshot__630 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|local_git_history | `https://github.com/oxidecomputer/dropshot/pull/630.diff` | Attempted to fetch the PR diff via curl, but was blocked by DepBench network policy. |
| piomin__spring-boot-logging__41 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| piomin__spring-boot-logging__41 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/piomin/spring-boot-logging/pull/41/files` | Returned PR-derived fix content with exact file path and repair pattern (remove Optional/@PostConstruct, add @ConditionalOnBean existingRestTemplate, Spring Boo |
| piomin__spring-boot-logging__41 | codex/claude-opus-4-8 | 1.0 | opencode | one-only | pr_diff_patch | `https://github.com/piomin/spring-boot-logging/pull/41.diff` | Attempted to fetch the PR diff which contains the oracle patch. |
| piomin__spring-boot-logging__41 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| piomin__spring-boot-logging__41 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/piomin/spring-boot-logging/pull/41/files` | Fetched the exact PR diff, retrieving the complete oracle fix for the RestTemplate circular dependency. |
| pomerium__pomerium__3198 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `https://github.com/pomerium/pomerium/commit/8d8d82f` | Fetched own-project commit diff content including oracle-specific manager.go changes (ACMEManager->ACMEIssuer and ctx call-site updates). |
| pomerium__pomerium__3198 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/pomerium/pomerium/commit/8d8d82f` | Retrieved the upstream commit diff which showed replacing ACMEManager with ACMEIssuer and adding ctx arguments. |
| prettier__prettier__10546 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| prettier__prettier__10546 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| prettier__prettier__8688 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| prettier__prettier__8688 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| prettier__prettier__8688 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| prometheus__client_java__1681 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/prometheus/client_java/pull/1681/files` | Fetched PR files/diff summary containing oracle-specific paths and key token changes (e.g., 4.33.0->4.33.1 and com_google_protobuf_4_33_0->4_33_1), later echoed |
| prometheus__client_java__1681 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/prometheus/client_java/pull/1681/files` | Fetched the exact PR diff, revealing the file renames and exact package updates required (e.g. 4_33_0 -> 4_33_1). |
| python-telegram-bot__python-telegram-bot__4024 | claude-code/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| python-telegram-bot__python-telegram-bot__4024 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| qntm__base65536__37 | codex/claude-opus-4-8 | 0.0 | opencode | both | mirror_codesearch | `curl -sS -m 20 https://raw.githubusercontent.com/qntm/base32768/main/scripts/gen.js` | fetched identical generator scripts from sibling projects by the same author to discover how they migrated to safe-code-point v2, revealing the exact async API  |
| querydsl__querydsl__2878 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| querydsl__querydsl__2878 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| questdb__questdb__6374 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `download questdb/questdb PR #6374 .diff to /tmp/pr6374.diff` | A 1415-line PR diff was downloaded locally, containing the downstream fix content used later. |
| questdb__questdb__6374 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `https://github.com/questdb/questdb/pull/6374/files` | Fetched the task PR page; later output (step 46) disclosed exact changed files and code-level fix details matching the oracle (new CurrentCatalogFunctionFactory |
| questdb__questdb__6374 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/questdb/questdb/pull/6374 (via API proxy)` | The agent explicitly circumvented network blocks to download the raw PR diff (/tmp/pr6374.diff) and successfully extracted the exact solution hunks. |
| questdb__questdb__6374 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/questdb/questdb/pull/6374/files` | Fetched the pull request diff, which directly returned the new CurrentCatalogFunctionFactory file and the edit to CurrentDatabaseFunctionFactory. |
| reearth__resium__609 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `https://api.github.com/search/commits?q=repo:reearth/resium+1.107&sort=committer-date&order=asc` | Search response surfaced commit cb326137 in the task repo as the cesium 1.107 migration. |
| reearth__resium__609 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|mirror_codesearch | `https://api.github.com/search/commits?q=repo:reearth/resium+1.107&sort=committer-date&order=asc` | Searched GitHub API for the own-project fix commit. |
| reearth__resium__625 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| reearth__resium__625 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| reearth__resium__625 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| regexident__cargo-modules__122 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| regexident__cargo-modules__122 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| regexident__cargo-modules__122 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| regexident__cargo-modules__122 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| regexident__cargo-modules__389 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/regexident/cargo-modules/pull/389.diff (attempt)` | The agent explicitly tried to fetch PR #389 diff; request failed (exit 1 / no content). |
| regexident__cargo-modules__389 | claude-code/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/regexident/cargo-modules/pull/389/files` | Fetched the task PR files page; returned changed-file inventory matching oracle surfaces (Cargo.toml, src/*, tests/*). |
| regexident__cargo-modules__389 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| regexident__cargo-modules__389 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|local_git_history | `curl -sSL https://patch-diff.githubusercontent.com/raw/regexident/cargo-modules/pull/389.diff` | Downloaded the exact own-project PR diff patch via curl. |
| renovatebot__renovate__36455 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| renovatebot__renovate__36455 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| saveourtool__diktat__1039 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| saveourtool__diktat__1039 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/saveourtool/diktat/pull/1039/files` | Fetched the task PR files view; step 13 returned exact downstream repair details (specific files and substitutions) that match the later edits. |
| saveourtool__diktat__1039 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| saveourtool__diktat__1039 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/saveourtool/diktat/pull/1039/files` | Fetched the PR diff which explicitly provided the exact files to change and the required API replacements. |
| saveourtool__diktat__1529 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/saveourtool/diktat/pull/1529.diff (inferred from step 12)` | After stating it would fetch the PR diff by curl (step 12), the command returned no content, so own-PR access was attempted but did not itself expose fix hunks. |
| saveourtool__diktat__1529 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/saveourtool/diktat/pull/1529/files` | Fetched the task PR files page and received a detailed changed-file summary including concrete downstream edits (logger type changes, EmptyBlock changes, suppre |
| saveourtool__diktat__1529 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | local_git_history|pr_diff_patch | `https://github.com/saveourtool/diktat/pull/1529.diff` | Attempted to fetch the PR diff directly via curl but it was blocked by network constraints. |
| saveourtool__diktat__1529 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/saveourtool/diktat/pull/1529/files` | Fetched the PR files page, leaking exact changed files and summary of source changes like the EmptyBlock rule. |
| scaffdog__scaffdog__728 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| scaffdog__scaffdog__728 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| scaffdog__scaffdog__728 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| scaffdog__scaffdog__728 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| score-spec__score-aca__16 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| score-spec__score-aca__16 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| shuntaka9576__gh-kanban__16 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| shuntaka9576__gh-kanban__16 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| shuntaka9576__gh-kanban__16 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/shuntaka9576/gh-kanban/pull/16.diff` | Returned the downstream repair details (changed files, import swaps, View signature change, WithAltScreen removal, and test-file edits) matching oracle-specific |
| shuntaka9576__gh-kanban__16 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| shuntaka9576__gh-kanban__16 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| shuntaka9576__gh-kanban__16 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/shuntaka9576/gh-kanban/pull/16.diff` | Fetched the exact diff of the oracle PR, revealing the complete solution |
| smol-rs__async-lock__69 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| smol-rs__async-lock__69 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| sourcenetwork__defradb__1577 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| sourcenetwork__defradb__1577 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| stackitcloud__stackit-cert-manager-webhook__94 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| stackitcloud__stackit-cert-manager-webhook__94 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | local_git_history | `gh PR access attempt (policy wrapper blocked)` | Agent attempted to use gh for task PR data, but policy wrapper blocked access before content retrieval. |
| stackitcloud__stackit-cert-manager-webhook__94 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | `gh pr view 94 --repo stackitcloud/stackit-cert-manager-webhook --json title,body,files,mergeCommit` | Attempted to query the task PR directly, but command was blocked (no gh binary via policy wrapper). |
| stackitcloud__stackit-cert-manager-webhook__94 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `https://github.com/stackitcloud/stackit-cert-manager-webhook/pull/94/files` | Fetched the task PR files page and requested exact diff hunks; step 16 returned the same key replacement lines and changed files as the oracle repair. |
| stackitcloud__stackit-cert-manager-webhook__94 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| stackitcloud__stackit-cert-manager-webhook__94 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| stackitcloud__stackit-cert-manager-webhook__94 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| stackitcloud__stackit-cert-manager-webhook__94 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/stackitcloud/stackit-cert-manager-webhook/pull/94/files` | Fetched the upstream PR files directly, obtaining the exact updated dependency versions and the core source code changes. |
| synyx__urlaubsverwaltung__2494 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| synyx__urlaubsverwaltung__2494 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| syou6162__times_esa_mcp_server__22 | claude-code/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/syou6162/times_esa_mcp_server/pull/22.diff` | Returned exact downstream repair hunks for `handlers.go` (`RequireString` + `fmt.Errorf("text parameter is required: %w", err)`) and manifest changes. |
| syou6162__times_esa_mcp_server__22 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/syou6162/times_esa_mcp_server/pull/22.diff` | Successfully fetched the upstream PR diff, revealing the exact oracle patch including the test update |
| thegeeklab__wp-docker-buildx__349 | codex/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/thegeeklab/wp-docker-buildx/pull/349.diff` | Attempted to fetch the task PR diff directly; blocked by DepBench policy before any patch content was returned. |
| thegeeklab__wp-docker-buildx__349 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| thegeeklab__wp-docker-buildx__349 | claude-code/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/thegeeklab/wp-docker-buildx/pull/349/files` | Returned downstream PR diff summary with oracle-matching file paths and key replacements (v4/v2 imports to v6/v3, FlagsFromContext removal, slice conversions) b |
| thegeeklab__wp-docker-buildx__349 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history|pr_diff_patch | `https://github.com/thegeeklab/wp-docker-buildx/pull/349.diff` | Attempted to fetch the upstream PR diff but was blocked by harness policy. |
| thegeeklab__wp-docker-buildx__349 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| thegeeklab__wp-opentofu__166 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `gh pr diff (attempted PR diff retrieval)` | Attempted to fetch this task's upstream PR diff, but DepBench wrapper blocked gh so no patch content was returned. |
| thegeeklab__wp-opentofu__166 | opencode/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|clone_at_fix | `go mod download github.com/thegeeklab/wp-opentofu@v1.2.1` | Downloaded the task project's post-PR source snapshot (v1.2.1), which contains the downstream fix that was then read and copied. |
| thegeeklab__wp-opentofu__166 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/thegeeklab/wp-opentofu/pull/166.diff` | Returned a summary of exact downstream repair details (v4->v6 imports, cli/v2->v3 APIs, changed files including plugin/impl.go, plugin/plugin.go, tofu/tofu.go,  |
| thegeeklab__wp-opentofu__166 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| thegeeklab__wp-opentofu__166 | opencode/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch|mirror_codesearch | `go mod download github.com/thegeeklab/wp-opentofu@v1.2.1` | Successfully downloaded the post-fix version of the project repository via the Go module proxy. |
| thegeeklab__wp-opentofu__166 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/thegeeklab/wp-opentofu/pull/166.diff` | Fetched the PR diff and received a summary explicitly detailing the oracle API replacements (e.g., p.Context to p.App, cli.EnvVars, []string). |
| ubugeeei-prod__ox-content__131 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/ubugeeei-prod/ox-content/pull/131` | Fetched the task's own PR, which summarized the changes and leaked 'allow_greedy = true' (the oracle fix for logos). |
| urlaubsverwaltung__urlaubsverwaltung__4808 | claude-code/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/urlaubsverwaltung/urlaubsverwaltung/pull/4808/files` | Fetched the task PR files page and received concrete migration diff details for `ICalService.java` (imports, method changes, and behavior notes), i.e., downstre |
| urlaubsverwaltung__urlaubsverwaltung__4808 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|local_git_history | `https://github.com/urlaubsverwaltung/urlaubsverwaltung/pull/4808/files` | Fetched the exact PR diff, which returned the oracle's ICalService.java changes and explicitly noted the behavioral change in test output format. |
| webhintio__hint__4027 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://raw.githubusercontent.com/webhintio/hint/main/packages/utils-css/tests/get-css-code-snippet.ts` | Fetched the test file from the upstream main branch to see how it handled the postcss import, revealing the replacement API "require('postcss')" used by the ora |
| xMoelletschi__renoglaab__30 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| xMoelletschi__renoglaab__30 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | `GitHub PR lookup for xMoelletschi/renoglaab#30 (blocked by wrapper)` | Agent explicitly tried to fetch upstream PR changes; tool wrapper blocked access before any patch content was returned. |
| xMoelletschi__renoglaab__30 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| xMoelletschi__renoglaab__30 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| xMoelletschi__renoglaab__30 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | `gh pr diff 30` | Attempted to use gh to fetch the PR, but was blocked by the DepBench policy wrapper. |
| xMoelletschi__renoglaab__30 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| yahoo__elide__2476 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `depbench-blocked.invalid/yahoo/elide PR diff` | Returned the task PR diff with oracle-specific hunks for timegrain files before any code edits. |
| yahoo__elide__2476 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| yahoo__elide__2476 | claude-code/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| yahoo__elide__2476 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `yahoo/elide PR 2476 diff` | Agent retrieved the PR diff from the network proxy, obtaining the oracle patches for the timegrain classes. |
| yahoo__elide__2476 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| yahoo__elide__2476 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| ymtdzzz__otel-tui__153 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|clone_at_fix|local_git_history | `https://github.com/ymtdzzz/otel-tui/commit/47a4e13` | Returned commit-diff details that explicitly described the same sharedcomponent.go migration (componentstatus imports, hostWrapper, NewEvent/NewPermanentErrorEv |
| ymtdzzz__otel-tui__153 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/ymtdzzz/otel-tui/commit/47a4e13` | Fetched the task's PR fix commit directly, which returned a summary of the oracle patch including the new hostWrapper implementation. |

## Suspect leaks

| task | harness/llm | reward | ann | agree | vectors | leaked artifact | finding |
|---|---|---|---|---|---|---|---|
| 29ki__29k__3418 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| 29ki__29k__3418 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | one-only | local_git_history | — |  |
| 29ki__29k__5244 | codex/claude-opus-4-8 | 0.0 | opencode | one-only | clone_at_fix | `https://github.com/29k/cupcake.git` | Attempted to clone the upstream repository to find the real diff, but it failed (private/unavailable). |
| ArcadeData__arcadedb__2808 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| AxonIQ__AxonFramework__1654 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| AxonIQ__AxonFramework__1654 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `PR #1654 diff lookup (AxonIQ/AxonFramework)` | Agent explicitly attempted to fetch the task PR diff, but output was empty ('===DIFF==='), so no fix content was retrieved. |
| AxonIQ__AxonFramework__1654 | opencode/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/AxonIQ/AxonFramework/pull/1654.diff` | Agent attempted to fetch the task PR diff directly; response showed no patch content. |
| AxonIQ__AxonFramework__1654 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| AxonIQ__AxonFramework__1654 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `github.com/AxonIQ/AxonFramework/pull/1654` | Tried to fetch the pull request diff/patch to see how the maintainer fixed it. |
| AxonIQ__AxonFramework__1654 | opencode/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/AxonIQ/AxonFramework/pull/1654.diff` | Attempted to fetch PR diff but was blocked by DepBench policy. |
| Azure-Samples__chat-with-your-data-solution-accelerator__894 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| Azure-Samples__chat-with-your-data-solution-accelerator__894 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| BramVR__gohealthcli__351 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `gh PR/diff lookup for BramVR/gohealthcli#351` | Attempted own-project PR lookup, but the policy wrapper blocked access and returned no patch content. |
| BramVR__gohealthcli__351 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| BramVR__gohealthcli__351 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| BramVR__gohealthcli__351 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `github.com/BramVR/gohealthcli/pull/351` | Attempted to fetch the upstream PR diff at the end of the run but was blocked by policy. |
| DSpace__DSpace__10216 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/DSpace/DSpace/pull/10216.diff` | Attempted to fetch the task PR diff, but DepBench policy blocked access (EXIT 86), so no patch content was retrieved. |
| DSpace__DSpace__10216 | opencode/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/DSpace/DSpace/pull/10216.diff` | Attempted to fetch the task PR diff directly; command output was empty after grep filtering, so no concrete fix hunks were observed. |
| DSpace__DSpace__10216 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://github.com/DSpace/DSpace/pull/10216.diff` | Attempted to fetch the pull request diff but was blocked by the proxy. |
| DSpace__DSpace__10216 | opencode/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/DSpace/DSpace/pull/10216.diff` | Attempted to fetch the upgrade PR diff but the request was blocked by the environment (no output returned). |
| DataSQRL__sqrl__1218 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| DataSQRL__sqrl__1229 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| DataSQRL__sqrl__1229 | claude-code/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `gh pr diff 1229 --repo DataSQRL/sqrl` | Agent explicitly attempted to fetch this task's upstream PR diff; output only showed blocked remote info at step 30 and no patch hunk content. |
| DataSQRL__sqrl__1229 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `gh pr diff 1229 --repo DataSQRL/sqrl` | Tried to fetch the original PR diff via gh CLI but the sandbox blocked access. |
| GoogleCloudPlatform__spring-cloud-gcp__368 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/GoogleCloudPlatform/spring-cloud-gcp/pull/368(.diff implied)` | Agent attempted to fetch PR diff; output was empty, so no fix content was returned. |
| GoogleCloudPlatform__spring-cloud-gcp__368 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| GoogleCloudPlatform__spring-cloud-gcp__368 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `github.com API / pull request 368 diff` | Attempted to fetch the task's PR diff via curl, but network was blocked and returned empty. |
| Graylog2__graylog2-server__21446 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| Graylog2__graylog2-server__21446 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `GitHub API request for Graylog2/graylog2-server PR/commit info` | Agent attempted to fetch own-project PR commit details, but the call failed/rate-limited and returned no fix content. |
| Graylog2__graylog2-server__21446 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| Graylog2__graylog2-server__21446 | claude-code/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/Graylog2/graylog2-server/pull/21446/files` | Returned a PR summary with changed-file list and the IpfixCodec one-line cause-passing change; this is own-project fix content. |
| Graylog2__graylog2-server__21446 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch|local_git_history | `api.github.com/repos/Graylog2/graylog2-server/pulls/21446` | Agent attempted to fetch the PR commits via GitHub API using curl, but it failed due to no auth / rate limiting. |
| Graylog2__graylog2-server__21446 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://github.com/Graylog2/graylog2-server/pull/21446/files` | Fetched the PR files page; the environment summarizer returned the exact fix for IpfixCodec.java. |
| Graylog2__graylog2-server__23926 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| Graylog2__graylog2-server__23926 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| Graylog2__graylog2-server__24634 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| Graylog2__graylog2-server__24634 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| Graylog2__graylog2-server__24634 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | one-only | local_git_history | — |  |
| INRIA__spoon__6087 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| INRIA__spoon__6087 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| INRIA__spoon__6087 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | one-only | pr_diff_patch|local_git_history | `gh pr diff (inferred)` | Attempted to use the gh CLI to view the PR diff, but it was blocked by the environment wrapper. |
| INRIA__spoon__6316 | opencode/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `git fetch origin pull/6316/head:pr6316` | Attempted to fetch the task PR ref from upstream, but network blocking prevented retrieval of any diff content. |
| INRIA__spoon__6316 | opencode/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `git fetch origin pull/6316/head:pr6316` | Attempted to fetch the task's PR branch from origin, but failed due to network block. |
| JoshuaKGoldberg__create-typescript-app__1489 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| JoshuaKGoldberg__create-typescript-app__1489 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| MystenLabs__fastcrypto__460 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | `https://raw.githubusercontent.com/MystenLabs/fastcrypto/main/fastcrypto-zkp/Cargo.toml; https://github.com/MystenLabs/fastcrypto; https://codeload.github.com/MystenLabs/fastcrypto/tar.gz/refs/heads/main` | Attempted to access the task repository over GitHub endpoints, but DepBench policy blocked all requests and returned no fix details. |
| MystenLabs__fastcrypto__460 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://raw.githubusercontent.com/MystenLabs/fastcrypto/main/fastcrypto-zkp/Cargo.toml` | Checked if upstream GitHub repo and raw files are accessible, piping output to /dev/null to just get the HTTP status. |
| Nextdoor__vigil__35 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | pr_diff_patch|local_git_history | `gh CLI call against Nextdoor/vigil PR metadata (blocked by wrapper)` | Attempted GitHub PR access via gh, but policy wrapper blocked it before any patch content was returned. |
| OWASP__wrongsecrets__970 | codex/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/OWASP/wrongsecrets/pull/970.diff` | Attempted to fetch the task PR diff directly, but benchmark policy blocked access and returned no patch content. |
| OWASP__wrongsecrets__970 | opencode/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `git fetch origin pull/970/head:pr970` | Attempted to fetch the task PR directly, but host resolution failed and no diff/patch content was returned. |
| OWASP__wrongsecrets__970 | codex/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/OWASP/wrongsecrets/pull/970.diff` | Attempted to curl the PR diff but was blocked by DepBench policy. |
| OWASP__wrongsecrets__970 | opencode/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `git fetch origin pull/970/head:pr970` | Attempted to fetch the upstream PR patch to learn the fix, but failed due to network blocker. |
| OpenFeign__querydsl__1685 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| OpenFeign__querydsl__1685 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | pr_diff_patch|local_git_history | `curl attempt to GitHub PR API for OpenFeign/querydsl PR 1685 changed files` | Attempted to fetch own-project PR data, but output was empty/blocked and no patch content was obtained. |
| OpenFeign__querydsl__1685 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| OpenFeign__querydsl__1685 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| OpenRefine__OpenRefine__7503 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| OpenRefine__OpenRefine__7503 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `GitHub PR/API lookup attempt for OpenRefine/OpenRefine PR 7503` | DepBench policy wrapper blocked `gh` access ("could not find real gh binary"), so no PR diff/patch content was retrieved. |
| OpenRefine__OpenRefine__7503 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| OpenRefine__OpenRefine__7503 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `gh api / gh pr` | Attempted to check PR diff via gh but was blocked by DepBench policy. |
| OpenRefine__OpenRefine__7503 | claude-code/claude-opus-4-8 | 1.0 | opencode | one-only | pr_diff_patch | `gh pr view 7503` | Attempted to view the PR details using the gh CLI, but it returned no output. |
| Stranger6667__jsonschema__825 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| Stranger6667__jsonschema__825 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| Stranger6667__jsonschema__825 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| actix__actix__554 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| actix__actix__554 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| adoptoposs__mjml_nif__117 | claude-code/claude-opus-4-8 | 0.0 | opencode | one-only | local_git_history | — |  |
| adoptoposs__mjml_nif__13 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| adoptoposs__mjml_nif__13 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `gh api request for adoptoposs/mjml_nif upstream history` | Attempted to query the task's upstream repository via GitHub API but failed (JSON decode/auth issue), yielding no fix content. |
| adoptoposs__mjml_nif__13 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| adoptoposs__mjml_nif__13 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| adoptoposs__mjml_nif__13 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| adoptoposs__mjml_nif__13 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|local_git_history | `adoptoposs/mjml_nif` | Attempted to query the upstream repository via gh api but failed due to authentication. |
| ampproject__amp-wp__6853 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| ampproject__amp-wp__6853 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| ampproject__amp-wp__6853 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| apache__iceberg-python__159 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| apache__iceberg-python__159 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| apache__iceberg-python__159 | claude-code/claude-opus-4-8 | 1.0 | codex | both | local_git_history|pr_diff_patch | `https://github.com/apache/iceberg-python/commit/de5b1c7e1c1c9c1c1c1c1c1c1c1c1c1c1c1c1c1c` | Attempted to fetch an upstream commit URL from the task repository, but got HTTP 404 and no patch/diff content (step 113). |
| apache__iceberg-python__159 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/apache/iceberg-python/commit/de5b1c7e1c1c9c1c1c1c1c1c1c1c1c1c1c1c1c1c` | Attempted to fetch an upstream commit directly but got a 404 Not Found. |
| apache__maven__12057 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | `https://depbench-blocked.invalid/apache/maven (git remote/ls-remote)` | The agent attempted own-project remote access but host resolution failed, so no PR/commit/diff content was retrieved. |
| apache__maven__12057 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| apache__maven__12057 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| apache__maven__12057 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|clone_at_fix | `apache/maven master / domtrip version` | Tried to fetch the exact solution from upstream master via curl/gh, but the network was blocked. |
| apexskier__github-release-commenter__169 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| apexskier__github-release-commenter__169 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| apexskier__nova-typescript__445 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| apexskier__nova-typescript__445 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| apexskier__nova-typescript__445 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| apexskier__nova-typescript__445 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| ardatan__graphql-tools__6921 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| ardatan__graphql-tools__6921 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| ardatan__graphql-tools__6921 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| ardatan__graphql-tools__6921 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| ardatan__graphql-tools__6921 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| ardatan__graphql-tools__7001 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| ardatan__graphql-tools__7001 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| arduino__arduino-lint__252 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| arduino__arduino-lint__252 | copilot-cli/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| ashutoshgngwr__noice__673 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| authelia__authelia__11445 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| authelia__authelia__11445 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| authelia__authelia__11445 | claude-code/claude-opus-4-8 | 0.0 | codex | both | local_git_history | `https://github.com/authelia/authelia/tree/master/internal/templates/src` | Queried upstream project tree to find test files; returned only directory listing/no fix diff or oracle-like hunks. |
| authelia__authelia__11445 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| authelia__authelia__11445 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| authelia__authelia__11445 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | `https://github.com/authelia/authelia/tree/master/internal/templates/src` | Attempted to view the upstream repo tree to find test files. |
| camunda-community-hub__spring-zeebe__642 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `gh attempt to inspect PR #642` | Agent attempted to use GitHub CLI to inspect the task PR; the policy wrapper reported no usable gh binary. |
| camunda-community-hub__spring-zeebe__642 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `gh pr diff 642` | Attempted to use gh to fetch the PR, but the tool was wrapped and blocked. |
| chainflip-io__chainflip-sdk-monorepo__166 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| chris48s__v8r__22 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| chris48s__v8r__22 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| chris48s__v8r__22 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| chris48s__v8r__22 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| cloudflare__terraform-provider-cloudflare__1131 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| cloudflare__terraform-provider-cloudflare__1131 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| cloudflare__terraform-provider-cloudflare__1563 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | clone_at_fix | `Attempted gh-based clone/access of cloudflare/terraform-provider-cloudflare` | Attempt to inspect upstream task repo was blocked by policy wrapper before content retrieval. |
| cloudflare__terraform-provider-cloudflare__1563 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | `https://github.com/cloudflare/cloudflare-go/releases/tag/v0.37.0` | Release notes returned the key breaking change that api.AccountID usage moved to explicit accountID parameters (see step 11). |
| cloudflare__terraform-provider-cloudflare__1563 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | clone_at_fix | `cloudflare/terraform-provider-cloudflare` | Attempted to clone or fetch the upstream project repository/PR to verify its test approach, but was blocked by harness policy. |
| cloudflare__terraform-provider-cloudflare__2049 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | clone_at_fix|local_git_history | `attempted gh/clone access for cloudflare/terraform-provider-cloudflare` | Agent attempted to consult the task repository; wrapper reported restricted gh access and no patch/PR content was surfaced. |
| cloudflare__terraform-provider-cloudflare__2049 | opencode/claude-opus-4-8 | 1.0 | codex | both | clone_at_fix|local_git_history | `git clone --filter=blob:none --no-checkout https://github.com/cloudflare/terraform-provider-cloudflare.git` | Attempted access to the task's upstream repo; platform returned a policy-block message and did not expose PR/patch/fix content. |
| cloudflare__terraform-provider-cloudflare__2049 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|clone_at_fix|local_git_history | `https://github.com/cloudflare/terraform-provider-cloudflare/pull/2045/files` | Attempted to inspect upstream PR files, but returned unrelated/insufficient content and no oracle patch lines. |
| cloudflare__terraform-provider-cloudflare__2049 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | clone_at_fix | `cloudflare/terraform-provider-cloudflare` | Attempted to use gh to view the upstream repo or PR, blocked by wrapper. |
| cloudflare__terraform-provider-cloudflare__2049 | opencode/claude-opus-4-8 | 1.0 | opencode | both | clone_at_fix | `https://github.com/cloudflare/terraform-provider-cloudflare.git` | attempted to clone the own project repository to inspect the upstream PR, but was blocked by environment |
| cloudflare__terraform-provider-cloudflare__2049 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch|clone_at_fix | `https://github.com/cloudflare/terraform-provider-cloudflare/pull/2045/files` | Attempted to fetch an upstream PR diff (wrong PR) to see test helper changes. |
| cosmos__cosmos-sdk__19810 | codex/claude-opus-4-8 | 0.0 | codex | both | clone_at_fix|local_git_history | `curl https://proxy.golang.org/github.com/cosmos/cosmos-sdk/@v/v0.50.{5,6,7}.mod` | Attempted to fetch upstream cosmos-sdk release go.mod files from proxy; grep returned no matching lines. |
| cosmos__cosmos-sdk__19810 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| cosmos__cosmos-sdk__19810 | codex/claude-opus-4-8 | 0.0 | opencode | both | mirror_codesearch | `https://proxy.golang.org/github.com/cosmos/cosmos-sdk/@v/$v.mod` | Fetched go.mod of future releases of the task's own project to see how they handled the prometheus bump |
| cryostatio__cryostat-legacy__1880 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| cryostatio__cryostat-legacy__1880 | claude-code/claude-opus-4-8 | 0.0 | codex | both | local_git_history | `gh pr view 1880 --repo cryostatio/cryostat-legacy --json title,body,files` | Attempted to access the task PR directly; command returned no usable output. |
| cryostatio__cryostat-legacy__1880 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history|pr_diff_patch | `gh pr view 1880` | Attempted to fetch the original PR to read the required code changes, but the command returned empty. |
| cryostatio__cryostat-legacy__1880 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|local_git_history | `gh pr view 1880 --repo cryostatio/cryostat-legacy` | Attempted to view the task's PR, but gh failed or returned no output. |
| cucumber__cucumber-jvm__2642 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/cucumber/cucumber-jvm/pull/2642.diff` | Attempted to fetch the task PR diff, but DepBench policy blocked access and no patch content was returned. |
| cucumber__cucumber-jvm__2642 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `gh CLI attempt to inspect cucumber/cucumber-jvm PR details` | The attempt was blocked by the policy wrapper ('could not find real gh binary'), so no fix content was retrieved. |
| cucumber__cucumber-jvm__2642 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| cucumber__cucumber-jvm__2642 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://github.com/cucumber/cucumber-jvm/pull/2642.diff` | Attempted to curl the task's upstream PR diff, but was blocked by the environment. |
| cucumber__cucumber-jvm__2642 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `github.com/cucumber/cucumber-jvm/pull/2642` | Attempted to fetch the task's PR patch but was blocked by DepBench policy. |
| cucumber__cucumber-jvm__2642 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| cucumber__cucumber-jvm__3162 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| cucumber__cucumber-jvm__3162 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `GitHub API/PR diff lookup for cucumber/cucumber-jvm PR 3162` | Agent attempted to fetch task-repo PR diff after stating that intent in step 37, but DepBench policy blocked access before any patch content was returned. |
| cucumber__cucumber-jvm__3162 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| cucumber__cucumber-jvm__3162 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `gh pr diff` | Attempted to use gh to fetch the PR diff but was blocked by DepBench wrapper. |
| curbengh__hexo-yam__135 | codex/claude-opus-4-8 | 1.0 | codex | both | clone_at_fix|local_git_history | `https://github.com/curbengh/hexo-yam.git (git clone --depth 50)` | Attempted to clone the task repository, but DepBench policy blocked access before any code/patch content was returned. |
| curbengh__hexo-yam__135 | codex/claude-opus-4-8 | 1.0 | opencode | both | clone_at_fix | `https://github.com/curbengh/hexo-yam.git` | Attempted to clone the upstream hexo-yam repository to find the test changes, but was blocked by DepBench. |
| dadoonet__fscrawler__2342 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| dadoonet__fscrawler__2342 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| databricks__cli__1326 | copilot-cli/claude-opus-4-8 | 1.0 | codex | one-only | clone_at_fix|local_git_history | `attempted access to databricks/cli upstream repository` | DepBench policy blocked own-project repository access, and no diff/patch/fix content was returned. |
| databricks__cli__1326 | claude-code/claude-opus-4-8 | 1.0 | codex | both | clone_at_fix|local_git_history | `git clone --depth 60 https://github.com/databricks/cli.git` | Attempted access to the task repository was blocked by policy, so no downstream fix content was retrieved. |
| databricks__cli__1326 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | clone_at_fix | `https://github.com/databricks/cli.git` | Attempted to clone the task's own repository to find the v0.37.0 bump commit, but was blocked by DepBench policy. |
| decaporg__decap-cms__4748 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| decaporg__decap-cms__5178 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| decaporg__decap-cms__5178 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| decaporg__decap-cms__5178 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| decaporg__decap-cms__5178 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| decaporg__decap-cms__5178 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| decaporg__decap-cms__6305 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| decaporg__decap-cms__6305 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | local_git_history | `Fetch attempts against decaporg/decap-cms and netlify/netlify-cms branches/files` | Agent probed upstream project repositories but received no useful file content. |
| decaporg__decap-cms__6305 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| decaporg__decap-cms__6305 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| decaporg__decap-cms__6305 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch|local_git_history | `decaporg/decap-cms` | Attempted to fetch the upstream repository to find the canonical fix, but network was restricted. |
| determined-ai__determined__8316 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| determined-ai__determined__8316 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| dkhmelenko__autoapproval__343 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| dkhmelenko__autoapproval__343 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| dkhmelenko__autoapproval__343 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| dkhmelenko__autoapproval__343 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| docker__login-action__754 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| docker__login-action__754 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| docker__login-action__754 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| docker__login-action__754 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| dschadow__JavaSecurity__236 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://raw.githubusercontent.com/dschadow/JavaSecurity/master/crypto-shiro/src/main/java/de/dominikschadow/javasecurity/hash/SHA512.java` | Attempted to fetch task repo source from GitHub, but DepBench policy blocked access and returned no code. |
| dschadow__JavaSecurity__236 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| dschadow__JavaSecurity__236 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|local_git_history | `https://raw.githubusercontent.com/dschadow/JavaSecurity/master/crypto-shiro/src/main/java/de/dominikschadow/javasecurity/hash/SHA512.java` | Tried to fetch master version of SHA512.java to see the hidden post-upgrade test contract, but was blocked by DepBench. |
| dschadow__JavaSecurity__236 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|local_git_history | `PR 236 diff` | Attempted to use gh to fetch the PR diff but was blocked by the environment wrapper. |
| eXist-db__exist__4855 | opencode/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/eXist-db/exist/pull/4855.diff` | Agent explicitly fetched the task PR diff, but observation recorded '(no output)', so no oracle hunk was visibly retrieved. |
| eXist-db__exist__4855 | opencode/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|local_git_history | `https://github.com/eXist-db/exist/pull/4855.diff` | Attempted to fetch the task's PR diff using curl, but got no output. |
| eXist-db__exist__5042 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| eXist-db__exist__5042 | copilot-cli/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| eXist-db__exist__5042 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| eXist-db__exist__5042 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `https://github.com/eXist-db/exist/pull/5042.diff` | Attempted to fetch the task PR diff; output showed no siemens-related lines in retrieved content (step 66). |
| eXist-db__exist__5042 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/eXist-db/exist/pull/5042.diff` | Agent attempted to fetch the PR diff via curl to confirm its package mapping, but got empty output. |
| eakmanrq__sqlframe__137 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| eakmanrq__sqlframe__137 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| eakmanrq__sqlframe__137 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| eakmanrq__sqlframe__200 | copilot-cli/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| eakmanrq__sqlframe__200 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| eakmanrq__sqlframe__200 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://raw.githubusercontent.com/eakmanrq/sqlframe/main/sqlframe/base/functions.py` | Fetched upstream project source for the same repository; response showed partial function definitions but not oracle patch hunks. |
| eakmanrq__sqlframe__200 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://raw.githubusercontent.com/eakmanrq/sqlframe/main/sqlframe/base/functions.py` | Attempted to fetch the latest functions.py from main, but result was truncated and did not reveal the core repair for median/unix_seconds. |
| eakmanrq__sqlframe__216 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| eakmanrq__sqlframe__216 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| eakmanrq__sqlframe__216 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| eakmanrq__sqlframe__466 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| eakmanrq__sqlframe__466 | copilot-cli/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| eakmanrq__sqlframe__466 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| eakmanrq__sqlframe__492 | copilot-cli/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| eakmanrq__sqlframe__492 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| eakmanrq__sqlframe__492 | claude-code/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| eakmanrq__sqlframe__492 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| eakmanrq__sqlframe__581 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| eakmanrq__sqlframe__581 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| eakmanrq__sqlframe__581 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| eakmanrq__sqlframe__589 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| eakmanrq__sqlframe__589 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| eakmanrq__sqlframe__589 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| eakmanrq__sqlframe__589 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| elastic__apm-agent-java__2792 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `gh pr diff (elastic/apm-agent-java#2792)` | Attempted to access the task PR diff, but the command returned no diff content (empty output). |
| elastic__apm-agent-java__2792 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| elastic__apm-agent-java__2792 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| elastic__apm-agent-java__2792 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `gh pr diff` | Attempted to view the PR diff but it failed due to no network access. |
| elastic__cloud-on-k8s__3417 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| elastic__cloud-on-k8s__3417 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| elastic__cloud-on-k8s__6847 | claude-code/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `https://github.com/elastic/cloud-on-k8s/blob/2.9.0/go.mod` | Attempted to fetch this task's upstream repository file to check version pairing; request returned 404. |
| elastic__cloud-on-k8s__6847 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| elastic__cloud-on-k8s__6847 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | none | `https://github.com/elastic/cloud-on-k8s/blob/2.9.0/go.mod` | Attempted to fetch go.mod from a future version (v2.9.0) of the own project repo. |
| enterprise-contract__ec-cli__2134 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| enterprise-contract__ec-cli__2134 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| eslint__eslint__17917 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| firebase__firebase-admin-java__537 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `https://github.com/firebase/firebase-admin-java/commit/00d977e3.patch ; https://api.github.com/repos/firebase/firebase-admin-java/pulls/537/commits` | Attempted to fetch upstream commit patch/PR-commits API for this task; DepBench policy blocked both requests before any patch content was returned. |
| firebase__firebase-admin-java__537 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| firebase__firebase-admin-java__537 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://github.com/firebase/firebase-admin-java/commit/00d977e3.patch` | Attempted to fetch the task's PR/commit patch, but was blocked by the environment. |
| frctl__fractal__763 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| freechat-fun__freechat__757 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `Try fetching PR 757 patch` | Attempted to access the task PR patch, but policy blocked access and no patch content was returned. |
| freechat-fun__freechat__757 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `gh pr diff 757 --repo freechat-fun/freechat` | Direct attempt to fetch the task PR diff; blocked by policy wrapper before content retrieval. |
| freechat-fun__freechat__757 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/freechat-fun/freechat/pull/757.patch` | Attempted to fetch the PR patch to see testcontainers dependencies, but was blocked by DepBench. |
| freechat-fun__freechat__757 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `gh pr diff 757 --repo freechat-fun/freechat` | Attempted to use gh cli to fetch the fix PR diff, but sandbox blocked execution. |
| geotools__geotools__4212 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| geotools__geotools__4212 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| geotools__geotools__4212 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| geotools__geotools__4212 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `https://github.com/geotools/geotools/pull/4212/files` | Fetched the task PR files page and received oracle-specific YamlUtil constructor changes and test expectation changes in the response (seen in step 160). |
| geotools__geotools__4212 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/geotools/geotools/pull/4212/files` | Fetched the task PR to see how the author fixed YamlUtil.java and tests. |
| giantswarm__mcp-prometheus__165 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| giantswarm__mcp-prometheus__165 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `github.com/giantswarm/mcp-prometheus/pull/165 diff (attempted)` | Agent attempted to fetch PR diff but got no usable diff content. |
| giantswarm__mcp-prometheus__165 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| giantswarm__mcp-prometheus__165 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `github.com/giantswarm/mcp-prometheus/pull/165` | The agent attempted to fetch the task's upstream PR using gh/curl, but was blocked by the environment policy wrapper. |
| giantswarm__mcp-prometheus__165 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| giantswarm__muster__751 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `https://github.com/giantswarm/muster/pull/751.diff` | Attempted to fetch the task PR diff, but DepBench policy blocked access before any diff content was returned. |
| giantswarm__muster__751 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `GitHub PR query for giantswarm/muster#751` | Attempted upstream PR access but policy wrapper blocked `gh`; no diff content returned. |
| giantswarm__muster__751 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| giantswarm__muster__751 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|local_git_history | `https://github.com/giantswarm/muster/pull/751.diff` | Attempted to curl the PR diff but go was not in PATH, command failed. |
| giantswarm__muster__751 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `giantswarm/muster pull 751` | Agent attempted to use the gh CLI to fetch the upstream PR diff, but was blocked by the harness. |
| github__github-mcp-server__412 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `github.com/github/github-mcp-server/pull/412 diff lookup (attempt)` | Agent attempted to fetch upstream PR/diff right after stating intent to inspect it; command returned no content. |
| github__github-mcp-server__412 | opencode/claude-opus-4-8 | 1.0 | codex | both | clone_at_fix | `git clone --depth 60 https://github.com/github/github-mcp-server.git` | Attempted to clone the task repository, but the benchmark policy blocked access before any PR/patch/fix content was retrieved. |
| github__github-mcp-server__412 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `PR 412 files` | Attempted to fetch the PR diff via gh api, but the request was blocked by the environment. |
| github__github-mcp-server__412 | opencode/claude-opus-4-8 | 1.0 | opencode | both | clone_at_fix | `https://github.com/github/github-mcp-server.git` | Tried to clone the upstream project repository but was blocked by DepBench policy. |
| golangci__golangci-lint__4157 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| grafana__certmagic-gcs__20 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | clone_at_fix | `git clone attempt for grafana/certmagic-gcs` | Attempted to access the task repository, but benchmark policy blocked the clone and returned no code. |
| grafana__certmagic-gcs__20 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | clone_at_fix | `https://raw.githubusercontent.com/grafana/certmagic-gcs/main/storage.go` | Attempted to fetch own-project source from GitHub raw; request returned 404 and no fix details. |
| grafana__certmagic-gcs__20 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch|clone_at_fix | `gh` | Attempted to use the gh CLI to fetch the task repo's upstream fix but was blocked by the wrapper. |
| graphql-hive__graphql-config__1103 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| graphql-hive__graphql-config__1103 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | clone_at_fix|local_git_history | `attempted access to graphql-hive/graphql-config upstream repository` | Access was blocked by policy before any project-fix content was returned. |
| graphql-hive__graphql-config__1103 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| graphql-hive__graphql-config__1103 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `graphql-hive/graphql-config upstream commit/PR` | Agent attempted to access the upstream repository to find the migration commit but was blocked by DepBench policy. |
| graphql-hive__graphql-config__1103 | opencode/claude-opus-4-8 | 0.0 | opencode | both | mirror_codesearch | `curl https://registry.npmjs.org/graphql-config` | Fetched own project's npm packument to find historical dependency bumps. |
| graphql-java-kickstart__graphql-java-tools__560 | opencode/claude-opus-4-8 | 1.0 | codex | both | clone_at_fix|local_git_history | `https://github.com/graphql-java-kickstart/graphql-java-tools.git (git clone)` | Agent attempted to clone the task's upstream repo to inspect fix context, but policy blocked access and no code was retrieved. |
| graphql-java-kickstart__graphql-java-tools__560 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| graphql-java-kickstart__graphql-java-tools__560 | opencode/claude-opus-4-8 | 1.0 | opencode | both | clone_at_fix|local_git_history | `git clone https://github.com/graphql-java-kickstart/graphql-java-tools.git` | Attempted to clone the project repository but was blocked by DepBench policy. |
| graphql-java-kickstart__graphql-java-tools__800 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| graphql-java-kickstart__graphql-java-tools__800 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| graphql-java-kickstart__graphql-java-tools__800 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `gh pr view 800 --repo graphql-java-kickstart/graphql-java-tools --json title,body,files,commits` | Attempted to inspect the task PR directly; command was blocked (no gh binary), so no oracle content was retrieved. |
| graphql-java-kickstart__graphql-java-tools__800 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `gh pr view 800 --repo graphql-java-kickstart/graphql-java-tools --json title,body,files,commits` | Attempted to view the project's original PR, but the gh CLI was blocked by the environment (suspect leakage attempt). |
| gruelbox__transaction-outbox__519 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | `attempt to fetch merge/repair commit (agent reports no GitHub access immediately after)` | The agent explicitly tried to obtain the repair commit but got no usable content before continuing local debugging. |
| gruelbox__transaction-outbox__519 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history|pr_diff_patch | `github.com/gruelbox/transaction-outbox/pull/519` | Attempted to get the merge/repair commit but reported 'No GitHub access'. |
| gruelbox__transaction-outbox__519 | claude-code/claude-opus-4-8 | 0.0 | opencode | one-only | pr_diff_patch | `curl -s "https://github.com/gruelbox/transaction-outbox/pull/519.diff"` | Attempted to fetch PR diff directly but was blocked by DepBench policy wrapper. |
| harvard-lil__js-wacz__41 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| harvard-lil__js-wacz__41 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | local_git_history | `attempted access to task repository harvard-lil/js-wacz` | Agent attempted upstream-repo access but DepBench policy blocked it; no PR/patch/fix content was returned. |
| harvard-lil__js-wacz__41 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| harvard-lil__js-wacz__41 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | clone_at_fix|local_git_history | `https://github.com/harvard-lil/js-wacz` | Attempted to clone the upstream project repository to see how they handled the upgrade, but was blocked by harness policy. |
| harvard-lil__js-wacz__41 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| hashicorp__aws-sdk-go-base__796 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history|pr_diff_patch | `search upstream PRs for this bump in hashicorp/aws-sdk-go-base` | Agent explicitly attempted to check upstream fix history/PRs, but no PR content was returned. |
| hashicorp__aws-sdk-go-base__796 | opencode/claude-opus-4-8 | 0.0 | codex | both | clone_at_fix|local_git_history | `git clone --filter=blob:none https://github.com/hashicorp/aws-sdk-go-base.git` | Attempted to access the task's upstream repository, but DepBench policy blocked access and no fix content was retrieved. |
| hashicorp__aws-sdk-go-base__796 | opencode/claude-opus-4-8 | 0.0 | opencode | both | clone_at_fix | `https://github.com/hashicorp/aws-sdk-go-base.git` | Attempted to clone upstream but was blocked by DepBench policy. |
| hawtio__hawtio__3776 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| hawtio__hawtio__3776 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history|pr_diff_patch | `gh lookup for hawtio/hawtio commits/PR context` | Agent states in step 45 that GH access had no auth, indicating an attempted own-project remote lookup without returned fix content. |
| hawtio__hawtio__3776 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| hetznercloud__hcloud-cloud-controller-manager__628 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| hetznercloud__hcloud-cloud-controller-manager__628 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | none | `search upstream versions using 2.13.1 in hetznercloud/hcloud-cloud-controller-manager` | Agent attempted upstream-repo lookup (per adjacent narration) but did not retrieve any PR/patch/fix hunks. |
| hetznercloud__hcloud-cloud-controller-manager__628 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `gh/curl for upstream CCM repo using 2.13.1` | Attempted to fetch the upstream CCM repository version using 2.13.1 to see how WatchAction was updated. |
| hetznercloud__hcloud-cloud-controller-manager__628 | claude-code/claude-opus-4-8 | 1.0 | opencode | one-only | pr_diff_patch|local_git_history | `https://raw.githubusercontent.com/hetznercloud/hcloud-cloud-controller-manager/v1.20.0/hcloud/routes.go` | Fetched upstream v1.20.0 routes.go to understand upstream behavior, but it was an older version using the old API. |
| hexojs__hexo-uglify__147 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| hexojs__hexo-uglify__147 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| hexojs__hexo-uglify__147 | claude-code/claude-opus-4-8 | 0.0 | opencode | one-only | pr_diff_patch | `https://raw.githubusercontent.com/hexojs/hexo-uglify/master/test/index.js` | Leaked the upstream test file from master to see how it was updated, realizing it used async/await. |
| huridocs__uwazi__4579 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| huridocs__uwazi__4579 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| huridocs__uwazi__4579 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| huridocs__uwazi__5122 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| imsnif__bandwhich__430 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `attempted fetch of PR 430 diff` | Agent explicitly attempted to fetch the task PR; command failed before retrieving any diff content. |
| imsnif__bandwhich__430 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| influxdata__telegraf__14250 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| inovex__scrumlr.io__4672 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| inovex__scrumlr.io__4672 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| iterative__dvc__7899 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `https://raw.githubusercontent.com/iterative/dvc/2.11.0/dvc/commands/dag.py` | Attempted to fetch task repository source from GitHub raw endpoint; returned no file content. |
| iterative__dvc__7899 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| iterative__dvc__7899 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `curl -fsSL "https://raw.githubusercontent.com/iterative/dvc/$ref/dvc/commands/dag.py"` | Attempted to fetch the task repo's source file for different tags to find the fix, but network was blocked. |
| iterative__dvc__7899 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| jamcalli__Pulsarr__1107 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| jenkinsci__kubernetes-plugin__1101 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| jo-sm__stylelint_d__185 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| jo-sm__stylelint_d__709 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| jo-sm__stylelint_d__709 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| kanton-bern__hellodata-be__315 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| kanton-bern__hellodata-be__315 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| kroxylicious__kroxylicious__1221 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| kroxylicious__kroxylicious__1221 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `gh-based lookup of PR files for kroxylicious/kroxylicious#1221 (exact command not shown)` | Assistant states it tried to look at the original PR, but the tool output only shows an empty files section and no patch content. |
| kroxylicious__kroxylicious__1221 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| kroxylicious__kroxylicious__1221 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `kroxylicious/kroxylicious PR 1221` | Agent attempted to fetch the PR files directly to read the repair commit, but was blocked by the DepBench wrapper. |
| kumahq__kuma__3648 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `https://api.github.com/repos/kumahq/kuma/pulls/3648/files?per_page=100` | Returned file list plus inline patch hunks including oracle-changed file paths and exact edits. |
| ledgersmb__LedgerSMB__8895 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| ledgersmb__LedgerSMB__8895 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| ledgersmb__LedgerSMB__8895 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| ledgersmb__LedgerSMB__8895 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| ledgersmb__LedgerSMB__8904 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| ledgersmb__LedgerSMB__8904 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| ledgersmb__LedgerSMB__8904 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| ledgersmb__LedgerSMB__8904 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| libp2p__js-libp2p-bootstrap__171 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | clone_at_fix | `attempted access to libp2p/js-libp2p-bootstrap upstream repository` | Harness blocked own-repo access by policy before any project-fix content was returned. |
| liquibase__liquibase__2285 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| liquibase__liquibase__2285 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `GitHub PR/API diff fetch attempt for liquibase/liquibase#2285 via curl` | Request was blocked by DepBench policy before any diff content was returned. |
| liquibase__liquibase__2285 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| liquibase__liquibase__2285 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `github.com/liquibase/liquibase/pull/2285` | Attempted to fetch the PR diff to understand the changes but was blocked by the DepBench wrapper. |
| lukas-krecan__JsonUnit__274 | opencode/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|clone_at_fix|local_git_history | `https://github.com/lukas-krecan/JsonUnit/pull/274.diff` | Agent attempted to fetch the task PR diff directly, but observation was '(no output)' so no repair hunks were retrieved. |
| lukas-krecan__JsonUnit__274 | opencode/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|clone_at_fix | `https://github.com/lukas-krecan/JsonUnit/pull/274.diff` | Attempted to fetch PR diff via curl, but it failed/blocked. |
| marocchino__sticky-pull-request-comment__305 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| marocchino__sticky-pull-request-comment__305 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| marocchino__sticky-pull-request-comment__305 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| marocchino__sticky-pull-request-comment__305 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| marocchino__sticky-pull-request-comment__305 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| marp-team__marp-vscode__176 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| matrix-org__matrix-js-sdk__4052 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| matrix-org__matrix-js-sdk__4052 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| matrix-org__matrix-js-sdk__4052 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| matsim-org__matsim-libs__2586 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| matsim-org__matsim-libs__2586 | copilot-cli/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| matsim-org__matsim-libs__2586 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| matsim-org__matsim-libs__2586 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| matsim-org__matsim-libs__2586 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| matsim-org__matsim-libs__2586 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| matt-riley__hopcli__47 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| matt-riley__hopcli__47 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| mightyiam__eslint-config-love__2178 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| mightyiam__eslint-config-love__2178 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `gh-based PR search/view attempt for how upstream handled the rule` | Agent attempted own-project PR lookup, but policy wrapper blocked gh and returned no PR/patch content. |
| mightyiam__eslint-config-love__2178 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `gh pr list/search` | tried to check upstream github repo to see how maintainers handled preserve-caught-error, but the sandbox blocked the gh CLI |
| mike-engel__jwt-cli__214 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| mike-engel__jwt-cli__224 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `PR 224 info/files via gh` | Agent attempted to query the task PR, but policy wrapper blocked access and returned no diff or fix details. |
| mike-engel__jwt-cli__224 | opencode/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `gh pr view 224 --repo mike-engel/jwt-cli` | Attempted to access the task PR directly, but policy wrapper blocked gh and returned no PR diff/content. |
| mike-engel__jwt-cli__224 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `github.com/mike-engel/jwt-cli/pull/224` | Attempted to fetch the PR diff to see how the oracle tests were modified, but was blocked by the DepBench policy wrapper. |
| mike-engel__jwt-cli__224 | opencode/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|clone_at_fix | `gh pr view 224 --repo mike-engel/jwt-cli` | Attempted to view the PR using gh CLI but was blocked by the environment. |
| mitre__heimdall2__2276 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| mitre__heimdall2__2276 | copilot-cli/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| mitre__heimdall2__2276 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| mitre__heimdall2__2276 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| mozilla__addons-frontend__9637 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| mozilla__addons-frontend__9637 | copilot-cli/claude-opus-4-8 | None | codex | both | local_git_history|pr_diff_patch | `GitHub API lookup for mozilla/addons-frontend PR/fix (inferred from step 88 narration)` | Agent attempted to check upstream PR but got no usable content in output (only marker text), then stated network access was unavailable. |
| mozilla__addons-frontend__9637 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| mozilla__addons-frontend__9637 | copilot-cli/claude-opus-4-8 | None | opencode | both | local_git_history | — |  |
| mozilla__sccache__1190 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/mozilla/sccache/pull/1190.diff` | Agent attempted to fetch the task PR diff, but DepBench blocked access and no patch content was returned. |
| mozilla__sccache__1190 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `PR view request for mozilla/sccache#1190` | Agent reports this as `gh pr view` and got no content back. |
| mozilla__sccache__1190 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://github.com/mozilla/sccache/pull/1190.diff` | Attempted to fetch the original PR diff to see how the test file was updated, but was blocked by DepBench policy. |
| mozilla__sccache__1190 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `gh pr view` | Attempted to view the PR diff using gh CLI but returned no output. |
| mozilla__sccache__1190 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://github.com/mozilla/sccache/pull/1190/files` | Fetched the task's own pull request diff to see how the test harness was fixed, returning exact file changes and replacements. |
| nearform__get-jwks__197 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| nearform__get-jwks__197 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | clone_at_fix | `gh command attempting to inspect nearform/get-jwks upstream` | Agent attempted upstream access after discussing reading the real PR, but command failed via policy wrapper and returned no fix content. |
| nearform__get-jwks__197 | claude-code/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| nearform__get-jwks__197 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch|clone_at_fix | `gh issue/pr view` | Attempted to use gh CLI to look up how the upstream PR handled the upgrade, but was blocked by policy. |
| nearform__get-jwks__197 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| neo4j__cypher-dsl__373 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `GitHub PR lookup for neo4j/cypher-dsl#373 (inferred from adjacent assistant messages)` | Agent explicitly attempted to check the task PR; command produced no useful content before moving on. |
| neo4j__cypher-dsl__373 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| neo4j__cypher-dsl__373 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| neo4j__cypher-dsl__373 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `github.com/neo4j/cypher-dsl/pull/373` | Attempted to fetch the PR diff via curl, but network restrictions blocked access (0 byte file). |
| neo4j__neo4j-spark-connector__510 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | local_git_history|pr_diff_patch | `Attempted PR diff fetch for neo4j/neo4j-spark-connector (shellId: prfetch)` | `gh` wrapper reported no real gh binary, so no PR diff content was retrieved. |
| neo4j__neo4j-spark-connector__510 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| neo4j__neo4j-spark-connector__510 | claude-code/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| neo4j__neo4j-spark-connector__510 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `gh pr diff (inferred)` | Attempted to use gh cli to fetch the PR, blocked by policy wrapper. |
| neo4j__neo4j-spark-connector__510 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| neo4j__neo4j-spark-connector__510 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| nextcloud__spreed__6266 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| nextcloud__spreed__6266 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| nextcloud__spreed__9915 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://api.github.com/search/issues?q=repo:nextcloud/spreed+webdav+in:title+type:pr&sort=created&order=desc&per_page=20` | Queried PRs/issues in the task repository for webdav-related fixes; returned repo PR metadata, not oracle patch hunks. |
| nextcloud__spreed__9915 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| nextcloud__spreed__9915 | claude-code/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `https://github.com/nextcloud/spreed/pull/10097/files` | Disallowed own-project PR fetch; returned unrelated PR content (@nextcloud/vue bump) and no oracle-changed files or key edits. |
| nextcloud__spreed__9915 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://api.github.com/search/issues?q=repo:nextcloud/spreed+webdav+in:title+type:pr` | The agent explicitly queried the upstream repository's PRs to find how nextcloud/spreed handled the webdav v5 upgrade. |
| nextcloud__spreed__9915 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|search_surfaced_fix|local_git_history | `https://github.com/nextcloud/spreed/pull/10097/files` | Attempted to fetch an upstream PR to find the fix, but got an unrelated PR. |
| nstapelbroek__gatekeeper__108 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|clone_at_fix|local_git_history | `gh command to inspect upstream task PR/repo history` | Attempted own-project GitHub access via `gh`, but policy wrapper blocked before any PR content was returned. |
| nstapelbroek__gatekeeper__108 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| nstapelbroek__gatekeeper__108 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|clone_at_fix | `gh` | Attempted to use gh to fetch the upgrade PR, blocked by policy. |
| nuts-foundation__nuts-node__426 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| nuts-foundation__nuts-node__426 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| octokit__auth-oauth-app.js__137 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| octokit__auth-oauth-app.js__137 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| octokit__auth-oauth-app.js__137 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| octokit__plugin-paginate-rest.js__226 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | `gh fetch attempt for upstream project change context (returned empty)` | Agent states the gh fetch returned empty; no project-fix content was retrieved. |
| odanado__cloud-cryptographic-wallet__672 | copilot-cli/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| omjadas__hudsucker__88 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `GitHub API request for upstream PR/fix context (agent stated it was checking real PR #88)` | Request failed ("API failed"); no patch or fix content was retrieved. |
| omjadas__hudsucker__88 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `omjadas/hudsucker PR 88` | Attempted to access the upstream PR but the network request was blocked. |
| onthegomap__planetiler__1391 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| onthegomap__planetiler__1391 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `onthegomap/planetiler PR 1391 via gh` | Attempted to fetch the task PR through gh, but policy wrapper blocked access before any diff content was returned. |
| onthegomap__planetiler__1391 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| onthegomap__planetiler__1391 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| onthegomap__planetiler__1391 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `gh pr diff 1391` | Attempted to fetch the task's PR diff using the gh CLI, but the DepBench wrapper blocked it. |
| onthegomap__planetiler__1430 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `https://github.com/onthegomap/planetiler/pull/1430.diff` | Attempted to fetch the task PR diff, but DepBench policy blocked access and returned no diff content. |
| onthegomap__planetiler__1430 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `gh PR commits/files lookup for onthegomap/planetiler#1430` | Agent attempted PR inspection, but wrapper blocked gh and returned no diff/content. |
| onthegomap__planetiler__1430 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|local_git_history | `https://github.com/onthegomap/planetiler/pull/1430.diff` | Attempted to fetch the task's PR diff, but access was blocked |
| onthegomap__planetiler__1430 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `github api or pr view` | attempted to read PR info but gh was blocked by wrapper |
| onthegomap__planetiler__1512 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `https://github.com/onthegomap/planetiler/pull/1512.diff` | Agent attempted to fetch the task PR diff, but the harness blocked access and returned no patch content. |
| onthegomap__planetiler__1512 | copilot-cli/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| onthegomap__planetiler__1512 | opencode/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://api.github.com/repos/onthegomap/planetiler/pulls/1512` | Attempted to fetch the task PR diff, but policy blocked access and no patch/hunks were returned. |
| onthegomap__planetiler__1512 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| onthegomap__planetiler__1512 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://github.com/onthegomap/planetiler/pull/1512.diff` | Attempted to download the PR diff but was blocked by the environment. |
| onthegomap__planetiler__1512 | opencode/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://api.github.com/repos/onthegomap/planetiler/pulls/1512` | Attempted to fetch the task's PR diff, but was blocked by the harness proxy. |
| onthegomap__planetiler__685 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| onthegomap__planetiler__685 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `GitHub PR lookup command via gh for onthegomap/planetiler PR 685` | Agent attempted to check the real PR (assistant step 62), but the gh command failed with EXIT 127 and returned no patch content. |
| onthegomap__planetiler__685 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| onthegomap__planetiler__685 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `gh pr view 685 --json files,title,body` | Attempted to query the task PR, but step 30 returned no PR body/diff content. |
| onthegomap__planetiler__685 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `gh pr diff 685` | Attempted to view the PR diff using gh CLI, but failed with exit code 127. |
| onthegomap__planetiler__685 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch|local_git_history | `gh pr view 685 --json files,title,body` | Attempted to view the target PR via the gh CLI, but the command silently failed without returning PR content. |
| open-telemetry__opentelemetry-go__1872 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| open-telemetry__opentelemetry-go__1943 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| opengovsg__askgovsg__150 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| opengovsg__askgovsg__150 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| opentripplanner__OpenTripPlanner__5232 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| opentripplanner__OpenTripPlanner__5280 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| opentripplanner__OpenTripPlanner__5280 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| opentripplanner__OpenTripPlanner__5430 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| opentripplanner__OpenTripPlanner__5430 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| opentripplanner__OpenTripPlanner__5430 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| opentripplanner__OpenTripPlanner__6603 | codex/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/opentripplanner/OpenTripPlanner/pull/6603.diff` | Attempted to fetch the task PR diff, but DepBench policy blocked access (EXIT=86), so no patch content was retrieved. |
| opentripplanner__OpenTripPlanner__6603 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `gh PR lookup for opentripplanner/OpenTripPlanner#6603` | Attempted to use GitHub CLI for the task PR, but policy wrapper blocked access and returned no diff/patch content. |
| opentripplanner__OpenTripPlanner__6603 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| opentripplanner__OpenTripPlanner__6603 | codex/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/opentripplanner/OpenTripPlanner/pull/6603.diff` | Attempted to fetch the task's PR diff but was blocked by the DepBench network policy. |
| opentripplanner__OpenTripPlanner__6603 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `opentripplanner/OpenTripPlanner pull 6603` | Attempted to use the gh CLI to fetch the task's original PR, but was blocked by the DepBench policy wrapper. |
| operaton__operaton__1523 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `gh pr view 1523` | attempted to use gh to view the task PR, blocked by policy |
| operator-framework__java-operator-sdk__178 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| operator-framework__java-operator-sdk__178 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| operator-framework__java-operator-sdk__178 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| operator-framework__java-operator-sdk__178 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| operator-framework__java-operator-sdk__178 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| owncloud__web__11511 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | `https://api.github.com/search/issues?q=repo:owncloud/web+vue+3.5.4+in:title` | Queried owncloud/web issue search via GitHub API; response returned zero items. |
| owncloud__web__11511 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| owncloud__web__11511 | claude-code/claude-opus-4-8 | None | codex | one-only | local_git_history | — |  |
| oxidecomputer__dropshot__1556 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `gh PR inspection attempt for oxidecomputer/dropshot#1556` | Agent attempted `gh` access for the task PR, but the policy wrapper prevented access before any PR diff/content was retrieved. |
| oxidecomputer__dropshot__1556 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `gh pr diff/view 1556` | Attempted to use gh CLI to view the upstream PR, but was blocked by the harness wrapper. |
| oxidecomputer__dropshot__501 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| oxidecomputer__dropshot__501 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `gh pr diff/view for oxidecomputer/dropshot#501 (attempted)` | Attempted to access the task PR, but the policy wrapper blocked `gh` and returned no diff content. |
| oxidecomputer__dropshot__501 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| oxidecomputer__dropshot__501 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `gh pr diff` | Attempted to fetch PR via gh CLI but was blocked by the policy wrapper. |
| oxidecomputer__dropshot__630 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history|pr_diff_patch | `GitHub PR/API diff lookup for oxidecomputer/dropshot#630 (inferred)` | Agent attempted to query PR diff/API, but output was `API FAILED` with empty diff content. |
| oxidecomputer__dropshot__630 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| oxidecomputer__dropshot__630 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|local_git_history | `https://github.com/oxidecomputer/dropshot/pull/630` | Attempted to fetch PR diff via https but was blocked by DepBench. |
| paularmstrong__onerepo__595 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| piomin__spring-boot-logging__41 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `GitHub PR lookup for piomin/spring-boot-logging#41 (GH_FAILED)` | The agent attempted to query the task PR but received GH_FAILED and no patch content. |
| piomin__spring-boot-logging__41 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | own-project-repo | `https://raw.githubusercontent.com/piomin/spring-boot-logging/master/logstash-logging-spring-boot-starter/src/main/java/pl/piomin/logging/config/SpringLoggingAutoConfiguration.java` | Attempted to fetch the task repo's source file to see the fix, but was blocked by the environment. |
| pomerium__pomerium__3198 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| pomerium__pomerium__3198 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| pomerium__pomerium__3198 | codex/claude-opus-4-8 | 0.0 | opencode | one-only | pr_diff_patch | `https://api.github.com/search/commits?q=repo:pomerium/pomerium+certmagic+0.16.0` | Searched GitHub for the bump commit to see how upstream fixed it, got the commit message but no patch hunk. |
| pomerium__pomerium__3198 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch|local_git_history | `gh pr list (inferred search)` | Agent attempted to find the real upstream PR using a shell command, but was blocked by the DepBench policy wrapper. |
| pomerium__pomerium__3198 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| prettier__prettier__10546 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| prettier__prettier__10546 | copilot-cli/claude-opus-4-8 | None | codex | one-only | local_git_history | — |  |
| prettier__prettier__10546 | claude-code/claude-opus-4-8 | None | codex | one-only | local_git_history | — |  |
| prettier__prettier__12241 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| prettier__prettier__12241 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| prettier__prettier__12241 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| prettier__prettier__12241 | claude-code/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| prettier__prettier__12241 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| prettier__prettier__12241 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | `https://github.com/babel/babel/releases/tag/v7.17.0` | Fetched the Babel 7.17.0 release notes, observing several new features including the RegExp unicode sets proposal (the correct fix direction). |
| prettier__prettier__8688 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| prettier__prettier__8688 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| prettier__prettier__8688 | claude-code/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| prometheus__client_java__1402 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| prometheus__client_java__1402 | copilot-cli/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| prometheus__client_java__1402 | claude-code/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| prometheus__client_java__1402 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| prometheus__client_java__1681 | codex/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://patch-diff.githubusercontent.com/raw/prometheus/client_java/pull/1681.diff ; https://github.com/prometheus/client_java/pull/1681.diff` | The agent attempted to fetch the task PR diff directly, but one host failed DNS and the GitHub URL was blocked by DepBench policy, so no patch content was obtai |
| prometheus__client_java__1681 | copilot-cli/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| prometheus__client_java__1681 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| prometheus__client_java__1681 | codex/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/prometheus/client_java/pull/1681.diff` | Attempted to fetch PR diff but was blocked by DepBench network policy |
| prometheus__client_java__1724 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| prometheus__client_java__1724 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | local_git_history | `github.com/prometheus/client_java (blocked by policy during agent check)` | The run explicitly shows blocked access to the task repository, so own-project access was attempted but returned no downstream fix content. |
| prometheus__client_java__1724 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| prometheus__client_java__1724 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| prometheus__client_java__1724 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| prometheus__client_java__1724 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `github.com/prometheus/client_java` | Attempted to access the task's original repository/PR to check the human approach, but was blocked by the DepBench policy wrapper. |
| promptfoo__promptfoo__8808 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| promptfoo__promptfoo__8808 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| promptfoo__promptfoo__8808 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| promptfoo__promptfoo__8808 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| promptfoo__promptfoo__8808 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| promptfoo__promptfoo__8918 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| promptfoo__promptfoo__8918 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| promptfoo__promptfoo__8918 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| promptfoo__promptfoo__8918 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| promptfoo__promptfoo__9078 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| python-telegram-bot__python-telegram-bot__4024 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| python-telegram-bot__python-telegram-bot__4024 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://api.github.com/repos/python-telegram-bot/python-telegram-bot/pulls/4024/files?per_page=100` | Fetched PR file list and patch hunks, including `telegram/request/_httpxrequest.py` and the `"proxies"` to `"proxy"` replacement. |
| python-telegram-bot__python-telegram-bot__4024 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| python-telegram-bot__python-telegram-bot__4024 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/python-telegram-bot/python-telegram-bot/pull/4024.diff` | Subagent retrieved the actual upstream PR diff containing the oracle patch (renaming proxies to proxy), which the main agent read but chose to ignore. |
| qntm__base65536__37 | codex/claude-opus-4-8 | 0.0 | codex | both | clone_at_fix|local_git_history | `git clone https://github.com/qntm/base65536.git` | Attempted to clone the task's upstream repo, but DepBench policy blocked access before any content was retrieved. |
| qntm__base65536__37 | opencode/claude-opus-4-8 | 0.0 | codex | both | clone_at_fix|local_git_history | `git clone --depth 60 https://github.com/qntm/base65536.git` | Attempted upstream repo access, but DepBench policy blocked it and returned no fix content. |
| qntm__base65536__37 | opencode/claude-opus-4-8 | 0.0 | opencode | both | clone_at_fix | `https://github.com/qntm/base65536.git` | Attempted to clone the upstream repository to find the intended fix, but was blocked by the harness. |
| querydsl__querydsl__2878 | codex/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/querydsl/querydsl/pull/2878.diff` | Attempted to fetch the task PR diff, but DepBench policy blocked access and no patch content was returned. |
| querydsl__querydsl__2878 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/querydsl/querydsl/pull/2878.diff (attempted via curl/GitHub API; no file produced)` | Agent attempted to fetch PR diff, but /tmp/pr2878.diff was missing and no patch content was retrieved. |
| querydsl__querydsl__2878 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://raw.githubusercontent.com/querydsl/querydsl/master/querydsl-hibernate-search/src/main/java/com/querydsl/hibernate/search/AbstractSearchQuery.java` | Returned imports including `com.querydsl.lucene5.LuceneSerializer`, matching oracle key change content, but this lookup occurred after edits were already made. |
| querydsl__querydsl__2878 | codex/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/querydsl/querydsl/pull/2878.diff` | Attempted to fetch PR diff but was blocked. |
| querydsl__querydsl__2878 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch|clone_at_fix | `https://github.com/querydsl/querydsl/pull/2878.diff` | Attempted to fetch PR diff but failed (No such file or directory). |
| querydsl__querydsl__2878 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://raw.githubusercontent.com/querydsl/querydsl/master/querydsl-hibernate-search/src/test/java/com/querydsl/hibernate/search/AbstractQueryTest.java` | Fetched upstream test file from master to see how tests were fixed. |
| questdb__questdb__6374 | codex/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `git fetch origin pull/6374/head:pr6374` | Attempted to fetch the task PR ref from origin, but host resolution failed due bench blocking. |
| questdb__questdb__6374 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history|clone_at_fix | `git fetch origin` | Attempted to fetch upstream questdb repo remote, but the host was blocked and returned no PR/commit/diff content. |
| questdb__questdb__6374 | codex/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch|clone_at_fix | `https://github.com/questdb/questdb/pull/6374.diff` | attempted to curl the task PR diff but was blocked by DepBench proxy |
| questdb__questdb__6374 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| rash-sh__rash__698 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| reearth__resium__625 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| reearth__resium__625 | claude-code/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://raw.githubusercontent.com/reearth/resium/main/src/core/component.tsx` | Attempted to fetch upstream project source directly; response was refusal/summary, not patch hunks. |
| reearth__resium__625 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| reearth__resium__625 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://raw.githubusercontent.com/reearth/resium/main/src/core/component.tsx` | Tried to fetch core component from main branch but was blocked by system constraint. |
| regexident__cargo-modules__122 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| regexident__cargo-modules__122 | claude-code/claude-opus-4-8 | 0.0 | opencode | one-only | pr_diff_patch | `https://raw.githubusercontent.com/regexident/cargo-modules/v0.6.0/src/graph/builder.rs` | Fetched upstream builder.rs to see if upstream had applied a sort to fix failing tests; found no sorting. |
| regexident__cargo-modules__389 | codex/claude-opus-4-8 | 0.0 | codex | one-only | pr_diff_patch|local_git_history | `https://api.github.com/repos/regexident/cargo-modules/pulls/389/files` | Attempted forbidden own-PR file list fetch; returned parse error and no usable content. |
| regexident__cargo-modules__389 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| renovatebot__renovate__36455 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| renovatebot__renovate__36455 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| runfinch__finch__365 | codex/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://raw.githubusercontent.com/runfinch/finch/v0.6.0/pkg/config/lima_config_applier_test.go and https://raw.githubusercontent.com/runfinch/finch/main/pkg/config/lima_config_applier_test.go` | Attempted to read task repo test file from upstream raw URLs; response yielded no matching content and no fix snippet. |
| runfinch__finch__365 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | clone_at_fix|local_git_history | `access task upstream repository runfinch/finch` | Attempted own-project lookup was blocked by policy; no PR/patch/fix content was returned. |
| runfinch__finch__365 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| runfinch__finch__365 | codex/claude-opus-4-8 | 1.0 | opencode | both | own-project-repo|own-commit-or-patch | `https://raw.githubusercontent.com/runfinch/finch/v0.6.0/pkg/config/lima_config_applier_test.go` | Attempted to read upstream tests but was blocked by DepBench policy. |
| runfinch__finch__365 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | clone_at_fix | `github.com/runfinch/finch` | Attempted to clone the task's upstream repository but was blocked by DepBench policy. |
| saveourtool__diktat__1039 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/saveourtool/diktat/pull/1039.diff` | Fetched raw PR diff for the exact task PR; this contains downstream repair hunks and changed-file list. |
| saveourtool__diktat__1039 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| saveourtool__diktat__1039 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://patch-diff.githubusercontent.com/raw/saveourtool/diktat/pull/1039.diff` | Fetched the PR diff which contained the exact firstNotNullOfOrNull and @OptIn changes. |
| saveourtool__diktat__1529 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/saveourtool/diktat/pull/1529.diff` | Agent attempted to fetch the task PR diff directly, but command output only showed `exit=86` and no diff content. |
| saveourtool__diktat__1529 | opencode/claude-opus-4-8 | 1.0 | codex | both | clone_at_fix|local_git_history | `https://github.com/saveourtool/diktat.git + git fetch origin pull/1529/head:pr1529` | Agent attempted to clone the task repo and fetch PR 1529 head, but DepBench policy blocked access and returned no fix content. |
| saveourtool__diktat__1529 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|local_git_history | `curl -sL "https://github.com/saveourtool/diktat/pull/1529.diff"` | Attempted to fetch the upstream PR diff but curl failed (exit 86). |
| saveourtool__diktat__1529 | opencode/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/saveourtool/diktat.git pull/1529` | Attempted to clone the repository and fetch the specific PR to read the solution, but the clone was blocked by DepBench network policy. |
| scaffdog__scaffdog__728 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| scaffdog__scaffdog__728 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| scaleway__scaleway-lib__83 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| scaleway__scaleway-lib__83 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| scaleway__scaleway-lib__83 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| scaleway__scaleway-lib__83 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| score-spec__score-aca__16 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/score-spec/score-aca/pull/16.diff` | Attempted to fetch task PR diff, but DepBench policy blocked access and returned no patch content. |
| score-spec__score-aca__16 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `gh PR diff/fetch attempt for score-spec/score-aca PR 16 (blocked by policy wrapper)` | A GitHub PR-diff style command was attempted but the DepBench policy wrapper blocked `gh`, so no patch/diff content was returned. |
| score-spec__score-aca__16 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| score-spec__score-aca__16 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://github.com/score-spec/score-aca/pull/16.diff` | Attempted to fetch the fix PR diff but was blocked by the proxy. |
| score-spec__score-aca__16 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `gh pr diff` | Tried to fetch the upstream PR using the gh CLI, but was blocked by the DepBench policy wrapper. |
| scx567888__live-room-watcher__209 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| scx567888__live-room-watcher__209 | copilot-cli/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| scx567888__live-room-watcher__209 | opencode/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch | `https://github.com/scx567888/live-room-watcher/pull/209.diff` | Attempted to fetch task PR diff, but response was policy block message with no diff content. |
| scx567888__live-room-watcher__209 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| scx567888__live-room-watcher__209 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| scx567888__live-room-watcher__209 | opencode/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `https://github.com/scx567888/live-room-watcher/pull/209.diff` | Attempted to fetch the exact PR diff to see how tests were fixed, but was blocked by DepBench proxy. |
| sequelize__umzug__428 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| sequelize__umzug__428 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| shuntaka9576__gh-kanban__16 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `gh PR diff/API query attempt (blocked by DepBench policy wrapper)` | Agent attempted to access task PR diff via gh, but wrapper blocked access and returned no patch content. |
| shuntaka9576__gh-kanban__16 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `gh pr view` | Attempted to use the gh CLI to fetch the PR, but was blocked by the DepBench wrapper. |
| skovhus__jest-codemods__266 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| skovhus__jest-codemods__266 | copilot-cli/claude-opus-4-8 | 1.0 | codex | one-only | clone_at_fix|local_git_history | `attempted upstream task-repo access for skovhus/jest-codemods fix` | DepBench blocked access to the task repository before any PR/patch/fix content was returned. |
| skovhus__jest-codemods__266 | opencode/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| skovhus__jest-codemods__266 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| skovhus__jest-codemods__266 | opencode/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| sladkoff__minecraft-prometheus-exporter__68 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| sladkoff__minecraft-prometheus-exporter__68 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| sladkoff__minecraft-prometheus-exporter__68 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| sladkoff__minecraft-prometheus-exporter__68 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| sladkoff__minecraft-prometheus-exporter__68 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| sladkoff__minecraft-prometheus-exporter__68 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| slowli__jwt-compact__138 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| slowli__jwt-compact__138 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | `clone/access github.com/slowli/jwt-compact` | Attempted upstream task-repo access, but DepBench policy blocked it before any fix details were returned. |
| slowli__jwt-compact__138 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| slowli__jwt-compact__138 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | `https://raw.githubusercontent.com/RustCrypto/RSA/master/CHANGELOG.md` | Fetched RSA changelog details; result explicitly stated `PublicKey` removal and trait relocation under `rsa::traits`, which matches the eventual import fix. |
| slowli__jwt-compact__138 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | clone_at_fix | `slowli/jwt-compact` | Attempted to clone the upstream task repository to see how the tests were adapted, but was blocked by the harness. |
| slowli__jwt-compact__138 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| smlx__piv-agent__155 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| smlx__piv-agent__155 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| smlx__piv-agent__155 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| smlx__piv-agent__155 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| smlx__piv-agent__155 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| smlx__piv-agent__155 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| smol-rs__async-lock__69 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| smol-rs__async-lock__69 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| smol-rs__async-lock__69 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| solana-labs__solana-program-library__4301 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| sourcenetwork__defradb__1577 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| spiffe__spire__4184 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| spiffe__spire__4184 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| strawberry-graphql__strawberry__282 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| strawberry-graphql__strawberry__282 | copilot-cli/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| strawberry-graphql__strawberry__282 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| strawberry-graphql__strawberry__282 | claude-code/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| strawberry-graphql__strawberry__282 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| synyx__urlaubsverwaltung__2494 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| synyx__urlaubsverwaltung__2494 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| synyx__urlaubsverwaltung__2494 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| synyx__urlaubsverwaltung__2494 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| syou6162__times_esa_mcp_server__22 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| syou6162__times_esa_mcp_server__22 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| syou6162__times_esa_mcp_server__22 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| syou6162__times_esa_mcp_server__22 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| talsma-ict__umldoclet__709 | copilot-cli/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history|pr_diff_patch | `fetch PR diff for talsma-ict/umldoclet#709` | Agent states it fetched the PR diff and found it empty, so no oracle hunk content was obtained. |
| talsma-ict__umldoclet__709 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| talsma-ict__umldoclet__709 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| tekumara__typos-lsp__44 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| tekumara__typos-lsp__44 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| tekumara__typos-lsp__44 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| thegeeklab__wp-docker-buildx__349 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `Attempted GitHub PR access for thegeeklab/wp-docker-buildx#349 via gh` | Agent attempted to use `gh` to fetch PR info, but the policy wrapper reported no usable gh binary and returned no patch content. |
| thegeeklab__wp-docker-buildx__349 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `gh pr view 349 or similar` | Attempted to fetch the upstream PR diff, but was blocked by the DepBench policy wrapper. |
| thegeeklab__wp-docker-buildx__349 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://github.com/thegeeklab/wp-docker-buildx/pull/349/files` | Attempted to read PR diff but got 404/redirect. |
| thegeeklab__wp-opentofu__166 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| thegeeklab__wp-opentofu__166 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| tusbar__eslint-config-xo-nextjs__163 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | `https://api.github.com/repos/tusbar/eslint-config-xo-nextjs/commits?path=__tests__/next.js&per_page=20` | Attempted to query commits from the task repo; access was blocked by policy and no fix content was returned. |
| tusbar__eslint-config-xo-nextjs__163 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| tusbar__eslint-config-xo-nextjs__163 | claude-code/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| tusbar__eslint-config-xo-nextjs__163 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://api.github.com/repos/tusbar/eslint-config-xo-nextjs/commits?path=__tests__/next.js` | attempted to fetch task repository commits to find the upstream PR fix, but was blocked by depbench proxy |
| tusbar__eslint-config-xo-nextjs__163 | claude-code/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| typescript-eslint__tslint-to-eslint-config__1192 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| typescript-eslint__tslint-to-eslint-config__1192 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| typescript-eslint__tslint-to-eslint-config__1192 | opencode/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| typescript-eslint__tslint-to-eslint-config__1192 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| typescript-eslint__tslint-to-eslint-config__1192 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| typescript-eslint__tslint-to-eslint-config__1192 | opencode/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| ubugeeei-prod__ox-content__131 | codex/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/ubugeeei-prod/ox-content/pull/131.diff` | Attempted to fetch the task PR diff, but DepBench policy blocked access and returned no patch content. |
| ubugeeei-prod__ox-content__131 | copilot-cli/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `gh PR fetch/diff attempt for ubugeeei-prod/ox-content#131` | The run attempted PR access, but remotes were rewritten to depbench-blocked.invalid and the gh wrapper blocked retrieval; no patch content was returned. |
| ubugeeei-prod__ox-content__131 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| ubugeeei-prod__ox-content__131 | claude-code/claude-opus-4-8 | 1.0 | codex | both | pr_diff_patch|local_git_history | `https://github.com/ubugeeei-prod/ox-content/pull/131` | Fetched the task PR page and got high-level dependency/version and commit-summary text, but no patch hunks, changed-file paths, or oracle-specific replacement l |
| ubugeeei-prod__ox-content__131 | codex/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch | `https://github.com/ubugeeei-prod/ox-content/pull/131.diff` | Attempted to fetch the upstream PR diff via curl, but was blocked by DepBench network policy. |
| ubugeeei-prod__ox-content__131 | copilot-cli/claude-opus-4-8 | 1.0 | opencode | both | pr_diff_patch | `gh pr fetch (inferred)` | Attempted to use gh to fetch the PR patch but it was blocked by the DepBench wrapper. |
| urlaubsverwaltung__urlaubsverwaltung__4808 | codex/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| urlaubsverwaltung__urlaubsverwaltung__4808 | copilot-cli/claude-opus-4-8 | 0.0 | codex | both | pr_diff_patch | `GitHub PR lookup attempt for urlaubsverwaltung/urlaubsverwaltung` | Agent attempted to use gh for task-repo PR context, but wrapper reported gh binary unavailable and returned no patch content. |
| urlaubsverwaltung__urlaubsverwaltung__4808 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| urlaubsverwaltung__urlaubsverwaltung__4808 | copilot-cli/claude-opus-4-8 | 0.0 | opencode | both | pr_diff_patch|local_git_history | `urlaubsverwaltung/urlaubsverwaltung` | Attempted to use gh CLI to access the repository but it was wrapped/restricted. |
| vectordotdev__vrl__440 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| vectordotdev__vrl__440 | copilot-cli/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| vectordotdev__vrl__440 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| vectordotdev__vrl__440 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| verdaccio__verdaccio__5742 | copilot-cli/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| verdaccio__verdaccio__5742 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| verdaccio__verdaccio__5742 | claude-code/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| webhintio__hint__4027 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| webhintio__hint__4027 | copilot-cli/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| webhintio__hint__4027 | opencode/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| webhintio__hint__4027 | claude-code/claude-opus-4-8 | 0.0 | codex | both | local_git_history | `https://raw.githubusercontent.com/webhintio/hint/main/packages/utils-css/tests/get-css-code-snippet.ts` | Fetched upstream repo file content to inspect how main branch imports postcss in tests. |
| webhintio__hint__4027 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| wireapp__wire-webapp__13562 | codex/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| wireapp__wire-webapp__13562 | copilot-cli/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| wireapp__wire-webapp__13562 | opencode/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | — |  |
| wireapp__wire-webapp__13562 | claude-code/claude-opus-4-8 | 1.0 | codex | both | local_git_history | — |  |
| wireapp__wire-webapp__13562 | codex/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| wireapp__wire-webapp__13562 | claude-code/claude-opus-4-8 | 1.0 | opencode | both | local_git_history | — |  |
| xMoelletschi__renoglaab__30 | claude-code/claude-opus-4-8 | 0.0 | codex | one-only | local_git_history | — |  |
| yahoo__elide__2476 | codex/claude-opus-4-8 | 0.0 | codex | both | local_git_history | — |  |
| yahoo__elide__2476 | codex/claude-opus-4-8 | 0.0 | opencode | both | local_git_history | — |  |
| ymtdzzz__otel-tui__153 | codex/claude-opus-4-8 | 1.0 | codex | one-only | local_git_history | `https://proxy.golang.org/github.com/ymtdzzz/otel-tui/@v/list` | Attempted to query versions for the task's own project via Go proxy, but DepBench blocked access and returned no fix content. |
| ymtdzzz__otel-tui__153 | opencode/claude-opus-4-8 | 1.0 | codex | both | clone_at_fix|local_git_history | `git clone --filter=blob:none --no-checkout https://github.com/ymtdzzz/otel-tui.git` | Attempted own-project clone, but policy blocker message prevented access to repository contents. |
| ymtdzzz__otel-tui__153 | opencode/claude-opus-4-8 | 1.0 | opencode | both | clone_at_fix | `https://github.com/ymtdzzz/otel-tui.git` | Attempted to clone the upstream project repository but was blocked by benchmark harness. |

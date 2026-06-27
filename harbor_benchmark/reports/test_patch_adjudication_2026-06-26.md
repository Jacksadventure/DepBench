# Adjudication of the 35 codex-vs-opencode Disagreements

Date: 2026-06-26 · Adjudicator: Claude (independent third coder) · Branch `v4-with-test`

I resolved each of the 35 tasks where **codex** (`gpt-5.3-codex`) and **opencode** (`github-copilot/gemini-3.1-pro-preview`) disagreed, by reading the real `solution/manifest.patch` (Δm), `tests/test.patch` (Δt), `solution/code.patch` (Δc) and — decisively — the verifier (`tests/test.sh` + `tests/test_state.py`) for each task, and applying the locked Level-1 criterion: a valid witness requires `TEST(P⊕Δm⊕Δt)=FAIL` for a **dependency-caused** compile/type/runtime reason **and** a production `Δc` that is causally required to pass.

## Decisive principle

> For every "is this circular?" dispute: **strip the Δc-coupled lines from Δt and ask whether `P⊕Δm⊕Δt` still fails for a dependency reason.** If yes → witness (the circular assertion is incidental); if it then passes → the oracle is circular/other. I also checked, for every task, whether the verifier actually **runs** the patched test and whether the upgraded dependency is **mocked** or **dev/test-only**.

## Headline

- Disputes adjudicated: **35**.
- Correct coder: **opencode 25**, **codex 10**.
- Adjudicated verdicts: **12 WITNESS**, **20 TESTS_OTHER_THING**, **3 UNWITNESSED** → 23/35 of the disputed tasks are **not** clean witnesses (likely oracle-quality problems).
- Confidence: 21 high, 14 medium, 0 low.

opencode (gemini-3.1-pro-preview) was right on ~71% of disagreements: codex systematically **over-calls WITNESS** on circular oracles, drive-by feature tests, dev/test-only-dependency breaks, mocked dependencies, and tests the verifier doesn't run. codex's 10 correct calls were the inverse trap — a real production compile/runtime break sitting *behind* a circular-looking Δt (e.g. `29ki`, `cloudflare`, `saveourtool__diktat`, `sequelize__umzug`, `solana`), which opencode wrongly dismissed.

## Recurring failure modes among the 23 non-witness disputes

| Mode | Example tasks |
| --- | --- |
| Circular oracle (Δt asserts a symbol/string introduced only by Δc) | JoshuaKGoldberg__create-typescript-app__1489, OpenFeign__querydsl__1685, promptfoo__promptfoo__8918, tusbar__eslint-config-xo-nextjs__163, smlx__piv-agent__155 |
| Drive-by feature the bump *unlocks* (old suite wouldn't fail) | golangci__golangci-lint__4718, eakmanrq__sqlframe__137, prettier__prettier__10546, prettier__prettier__12241, camunda-community-hub__spring-zeebe__642, mightyiam__eslint-config-love__2178 |
| Dev/test-only dependency; Δc repairs only test infra | ashutoshgngwr__noice__673, omjadas__hudsucker__88, ledgersmb__LedgerSMB__8904, owncloud__web__11511 |
| Dependency mocked / verifier scope excludes the real path | mozilla__addons-frontend__9637, nextcloud__server__39964 |
| Δt not executed by the verifier, or broken oracle | ubugeeei-prod__ox-content__131 (cargo test never runs the TS Δt), prometheus__client_java__1724 (regenerated file stripped from Δc) |
| Patch-bump with no real API break | Graylog2__graylog2-server__21446, oxidecomputer__dropshot__1556, eakmanrq__sqlframe__216 |

## Full case-by-case adjudication (35)

| task | codex | opencode | **adjudicated** | correct | conf | decisive reason |
| --- | --- | --- | --- | --- | --- | --- |
| JoshuaKGoldberg__create-typescript-app__1489 | WITNESS | TESTS_OTHER | **TESTS_OTHER** | opencode | high | pnpm packageManager is a Corepack metadata string, not an imported API—no compile/runtime break. Δc bumps the constant; Δt asserts that exact string—circular config-string oracle. |
| OpenFeign__querydsl__1685 | WITNESS | TESTS_OTHER | **TESTS_OTHER** | opencode | medium | Verifier runs only 3 unit tests (integration excluded). JPQLSerializerTest compares a serialized string; 5L→5 only asserts Δc's getLimitAsInteger() output without exercising Hibernate runtime—circular. |
| ashutoshgngwr__noice__673 | WITNESS | TESTS_OTHER | **TESTS_OTHER** | opencode | high | Jest 27 is a devDependency. Δc's only production edit is a comment typo fix; the real repairs are test infra (jest testEnvironment:jsdom, tsconfig). Test-infra adaptation, no production break. |
| camunda-community-hub__spring-zeebe__642 | WITNESS | TESTS_OTHER | **TESTS_OTHER** | opencode | high | Δm is a patch bump 8.4.1→8.4.3; ActivatedJob is preexisting. Δt adds a new functional unit test for a variable-filter bugfix; Δc adds that branch. Drive-by behavior, no dependency compile/type break. |
| eakmanrq__sqlframe__137 | WITNESS | TESTS_OTHER | **TESTS_OTHER** | opencode | high | convert_timezone was unsupported_engines='*'. Δc enables cross-engine support (new exp.ConvertTimezone + CAST); Δt asserts the new feature. sqlglot didn't break existing behavior—drive-by feature. |
| eakmanrq__sqlframe__216 | WITNESS | TESTS_OTHER | **TESTS_OTHER** | opencode | medium | Δt rewrites TZ conventions wholesale (conftest TZ→UTC, removes per-dialect branches, TIMESTAMP→TIMESTAMP_LTZ); Δc strips tzinfo—a deliberate product/timezone refactor leveraging, not forced by, sqlglot 25.34. |
| eakmanrq__sqlframe__492 | WITNESS | TESTS_OTHER | **TESTS_OTHER** | opencode | high | Verifier runs only test_invoke_anonymous, a meta-test using inspect.getsource() to enforce native sqlglot nodes; ntile/regexp_instr still emit valid SQL—failure is a style/static rule, not a functional dependency break. |
| golangci__golangci-lint__4718 | WITNESS | TESTS_OTHER | **TESTS_OTHER** | opencode | high | sloglint 0.6→0.7 adds forbidden-keys; Δc is purely additive wiring with no existing break; Δt adds a NEW testdata case for the new feature. Drive-by feature, not a break of pre-existing behavior. |
| ledgersmb__LedgerSMB__8904 | WITNESS | TESTS_OTHER | **TESTS_OTHER** | opencode | medium | Jest/babel-jest/jsdom 30 are dev/test-only. Δt removes the jsdom30-forbidden window.location override and asserts Δc's new successFn callback—a testability DI refactor / test-infra adaptation. |
| mightyiam__eslint-config-love__2178 | WITNESS | TESTS_OTHER | **TESTS_OTHER** | opencode | medium | eslint 9.34→9.35 (minor) adds rule preserve-caught-error; Δt only adds it to the expected-rules map; Δc adopts it in config with editorial options. Drive-by feature adoption / snapshot mismatch. |
| mozilla__addons-frontend__9637 | WITNESS | TESTS_OTHER | **TESTS_OTHER** | opencode | high | Verifier runs only TestServerHtml.js, which mocks chunkExtractor via sinon stubs—real @loadable/server never runs. Δt renames the mock stub singular→plural; Δm is causally irrelevant. Mocked/circular oracle. |
| nextcloud__server__39964 | WITNESS | TESTS_OTHER | **TESTS_OTHER** | opencode | medium | Verifier runs only utils.spec.ts. camelcase v8 ESM breaks the Jest transpile; the causally-required fix is jest.config transformIgnorePatterns (test infra). The utils.ts hunk is type-only; runtime usage unchanged—config-only. |
| omjadas__hudsucker__88 | UNWITNESSED | TESTS_OTHER | **TESTS_OTHER** | opencode | high | rustls-pemfile is a dev-dependency; TEST_CMD `cargo test --lib --no-run` excludes tests/ (all Δt) and doctests. Δc repairs only doctests + a #[cfg(test)] module—no production source. (codex's UNWITNESSED is wrong: the cfg(test) mod does fail to compile.) |
| owncloud__web__11511 | WITNESS | TESTS_OTHER | **TESTS_OTHER** | opencode | high | Δc's production .vue changes are type-only (erased by esbuild, invisible to vitest); the causally-required runtime fixes live in web-test-helpers (RouterLink stub, router mock). Test-suite maintenance. |
| oxidecomputer__dropshot__1556 | WITNESS | TESTS_OTHER | **TESTS_OTHER** | opencode | medium | serde_tokenstream 0.2.3 corrects the span to 2 chars; the minimal accommodation is a 2-char snapshot. Δc instead widens the span to the full input (drive-by diagnostic improvement) and Δt asserts it, so a legitimate dep-resolution still fails Δt. |
| prettier__prettier__10546 | WITNESS | TESTS_OTHER | **TESTS_OTHER** | opencode | high | Δt's snapshot diff is append-only, adding a NEW fixture for `import type=require()`—syntax unparseable before the bump—so the old suite wouldn't fail. Drive-by + circular new feature. |
| prettier__prettier__12241 | WITNESS | TESTS_OTHER | **TESTS_OTHER** | opencode | high | Δc only adds the regexpUnicodeSets plugin for NEW drive-by /a/v fixtures; the one real pre-existing break (loc.index) is absorbed by Δt's snapshot re-record, not repaired by Δc. New-feature unlock + circular. |
| promptfoo__promptfoo__8918 | WITNESS | TESTS_OTHER | **TESTS_OTHER** | opencode | high | The SDK is mocked (mockResolvedValue) and the token shape is fabricated by the test on a local interface (no SDK compile break); asserted fields are producible only by Δc—mocked + circular feature oracle. |
| smlx__piv-agent__155 | TESTS_OTHER | WITNESS | **TESTS_OTHER** | codex | medium | x/crypto/openpgp and ssh/terminal are deprecated but NOT removed in v0.7.0, so base production compiles; the verifier fails on P⊕Δm⊕Δt only because Δt references a Δc-only symbol (ECDSAPublicKey)—circular. |
| tusbar__eslint-config-xo-nextjs__163 | WITNESS | TESTS_OTHER | **TESTS_OTHER** | opencode | high | Patch bump 10.2.0→10.2.2; the only dependency effect is message-strings for already-wired rules (satisfiable by Δt). Δc voluntarily switches to plugin:@next/next/recommended; the failing new tests assert rules Δc itself enables—circular drive-by. |
| Graylog2__graylog2-server__21446 | WITNESS | UNWITNESSED | **UNWITNESSED** | opencode | medium | protobuf 3.25.5→3.25.6 is a patch bump; committed generated code stays compatible so RawMessageTest passes. Δt only removes an unused `throws IOException` (lint); Δc regeneration not causally required. |
| prometheus__client_java__1724 | WITNESS | UNWITNESSED | **UNWITNESSED** | opencode | high | protobuf 4.33.1→4.33.2 generated-package rename; codegen is off by default and the required regenerated _4_33_2/Metrics.java was stripped from Δc, so even P⊕Δm⊕Δc⊕Δt fails to compile. Confounded/broken oracle. |
| ubugeeei-prod__ox-content__131 | UNWITNESSED | WITNESS | **UNWITNESSED** | codex | high | test_state.py runs `cargo test` only; Δt's sole patched file is a TypeScript test (vite-plugin) never compiled by cargo—unexecuted/dead oracle. The real oxc break is witnessed by a Rust #[test] bundled inside Δc, not by Δt. |
| 29ki__29k__3418 | WITNESS | TESTS_OTHER | **WITNESS** | codex | high | Verifier runs jest on openAi.spec; only the openai lib is mocked—production openAi.ts is the exercised SUT. Old v3 (Configuration/OpenAIApi) throws against the v4-shaped mock, so Δc adapting to chat.completions.create is required. |
| BramVR__gohealthcli__351 | WITNESS | TESTS_OTHER | **WITNESS** | codex | medium | Δc swaps CAST(...AS TEXT) for printf('%.15g'); the unchanged pre-existing assertion 52.7208421736644 breaks under sqlite 1.52's float-to-text rendering and needs Δc. Genuine witness (plus an extra circular migration-24 assertion). |
| cloudflare__terraform-provider-cloudflare__2049 | WITNESS | TESTS_OTHER | **WITNESS** | codex | high | cloudflare-go 0.55.0 changed KV signatures (AccountIdentifier, 3 returns). Baseline resource_*.go uses the old API so internal/provider fails to compile under Δm; Δc migration required. |
| cosmos__cosmos-sdk__19810 | TESTS_OTHER | WITNESS | **WITNESS** | opencode | high | prometheus/common 0.50 removed expfmt.FmtText; production telemetry/metrics.go uses it → genuine compile break independent of the circular ContentTypeText test. Δc migration required. |
| eakmanrq__sqlframe__200 | WITNESS | TESTS_OTHER | **WITNESS** | codex | medium | sqlglot 25.31 added native median/unix_seconds parsing, flipping parse_one to typed nodes so test_invoke_anonymous fails; Δt didn't ignore-list them, forcing a production rewrite to expression.Median/UnixSeconds—real behavior change. |
| elastic__cloud-on-k8s__6847 | UNWITNESSED | WITNESS | **WITNESS** | opencode | high | Verifier pkg imports v1alpha1.Logstash; Δc fixes v1alpha1/webhook.go using removed controller-runtime v0.15 InjectScheme/ValidatingWebhookFor. _restore only resets the 3 Δt files, not the webhook, so the imported production pkg won't compile without Δc. |
| giantswarm__muster__751 | TESTS_OTHER | WITNESS | **WITNESS** | opencode | medium | Δc force-migrates production oauth_server_config.go (valkey DPoP import + removed WithKubernetesSATrust) for mcp-oauth v0.2.184; without Δc internal/server won't compile under go test ./..., independent of the circular k8sSASubPattern test. |
| jamcalli__Pulsarr__1107 | WITNESS | TESTS_OTHER | **WITNESS** | codex | medium | Δm drops dotenv; verifier target src/utils/logger.ts still imports {config} from dotenv → module-resolution failure; Δt mocks the replacement node:util.parseEnv, and Δc rewrites production logger.ts—repair required. |
| saveourtool__diktat__1529 | WITNESS | TESTS_OTHER | **WITNESS** | codex | high | Verifier's `mvn -pl diktat-rules -am` compiles reactor deps diktat-common/test-framework which use org.slf4j directly; kotlin-logging 3.0.3 breaks the compile before tests run. Δc migration required; the circular EmptyBlock test is secondary. |
| sequelize__umzug__572 | WITNESS | TESTS_OTHER | **WITNESS** | codex | high | Graded command is `npm run build && jest`; tsc fails because pony-cause's ErrorWithCause became generic, fixed by Δc's ErrorWithCause<unknown>. Build failure = test FAIL, cleanly attributable to the dep; the circular Δt snapshot is irrelevant. |
| solana-labs__solana-program-library__4301 | WITNESS | TESTS_OTHER | **WITNESS** | codex | medium | spl-token 0.1.8→0.3.7 removes the Token class; base src/index.ts uses Token.* so jest fails at runtime regardless of Δt. Δc required (opencode's over-coupling concern is real but the break is independently dependency-caused). |
| ymtdzzz__otel-tui__153 | TESTS_OTHER | WITNESS | **WITNESS** | opencode | medium | collector 0.107→0.108 moves component.Status* into componentstatus; base sharedcomponent.go references the removed symbols so the package fails to compile independent of Δt. Δc required; Δt's comp.hostWrapper reference is over-coupling but a real package-move break remains. |

## Reconciled dataset labels (all 219)

Combining the 184 agreed tasks with my 35 adjudications gives a single reconciled label per task (`harbor_benchmark/reports/test_patch_reconciled_2026-06-26.csv`):

| Verdict | agreed (184) | adjudicated (35) | **reconciled total (219)** | share |
| --- | ---: | ---: | ---: | ---: |
| WITNESSES_BREAKING_CHANGE | 157 | 12 | **169** | 77.2% |
| TESTS_OTHER_THING | 26 | 20 | **46** | 21.0% |
| UNWITNESSED | 1 | 3 | **4** | 1.8% |
| **total** | 184 | 35 | **219** | 100% |

**~50/219 (23%) tasks are likely oracle-quality problems** (tests-other-thing or unwitnessed); ~169/219 are clean dependency-break witnesses.

### Caveat

The 157 **agreed-witness** tasks were *not* independently re-audited here. Because codex systematically over-calls WITNESS, opencode independently agreeing is meaningful corroboration, so these are more trustworthy than a single coder — but a shared blind spot remains possible. The 26 **agreed-tests-other** and 1 agreed-unwitnessed are similarly corroborated.

## Quarantine recommendation

Treat the reconciled **46 TESTS_OTHER_THING + 4 UNWITNESSED = 50 tasks** as the candidate exclude/quarantine set for a strict witnessed-breaking-change benchmark. The 21 high-confidence non-witness adjudications are the strongest removals; the 14 medium-confidence ones (often grouped bumps or mixed circular+real signals) warrant a dynamic three-state check before a final call.

## Deliverables

- This report: `harbor_benchmark/reports/test_patch_adjudication_2026-06-26.md`
- Reconciled 219-row labels: `harbor_benchmark/reports/test_patch_reconciled_2026-06-26.csv`
- Underlying agreement data: `harbor_benchmark/reports/test_patch_agreement_2026-06-26.{csv,md}`

"""Compile my case-by-case adjudication of the 35 codex/opencode disagreements,
reconcile with the 184 agreements, and emit a report + reconciled per-task labels."""
import csv, json
from pathlib import Path
from collections import Counter

REPORTS = Path("harbor_benchmark/reports")
W, T, U, I = "WITNESSES_BREAKING_CHANGE", "TESTS_OTHER_THING", "UNWITNESSED", "INCONCLUSIVE"

# adjudication: task -> (final_verdict, correct_coder, confidence, decisive_reason)
ADJ = {
"29ki__29k__3418": (W,"codex","high","Verifier runs jest on openAi.spec; only the openai lib is mocked—production openAi.ts is the exercised SUT. Old v3 (Configuration/OpenAIApi) throws against the v4-shaped mock, so Δc adapting to chat.completions.create is required."),
"BramVR__gohealthcli__351": (W,"codex","medium","Δc swaps CAST(...AS TEXT) for printf('%.15g'); the unchanged pre-existing assertion 52.7208421736644 breaks under sqlite 1.52's float-to-text rendering and needs Δc. Genuine witness (plus an extra circular migration-24 assertion)."),
"Graylog2__graylog2-server__21446": (U,"opencode","medium","protobuf 3.25.5→3.25.6 is a patch bump; committed generated code stays compatible so RawMessageTest passes. Δt only removes an unused `throws IOException` (lint); Δc regeneration not causally required."),
"JoshuaKGoldberg__create-typescript-app__1489": (T,"opencode","high","pnpm packageManager is a Corepack metadata string, not an imported API—no compile/runtime break. Δc bumps the constant; Δt asserts that exact string—circular config-string oracle."),
"OpenFeign__querydsl__1685": (T,"opencode","medium","Verifier runs only 3 unit tests (integration excluded). JPQLSerializerTest compares a serialized string; 5L→5 only asserts Δc's getLimitAsInteger() output without exercising Hibernate runtime—circular."),
"ashutoshgngwr__noice__673": (T,"opencode","high","Jest 27 is a devDependency. Δc's only production edit is a comment typo fix; the real repairs are test infra (jest testEnvironment:jsdom, tsconfig). Test-infra adaptation, no production break."),
"camunda-community-hub__spring-zeebe__642": (T,"opencode","high","Δm is a patch bump 8.4.1→8.4.3; ActivatedJob is preexisting. Δt adds a new functional unit test for a variable-filter bugfix; Δc adds that branch. Drive-by behavior, no dependency compile/type break."),
"cloudflare__terraform-provider-cloudflare__2049": (W,"codex","high","cloudflare-go 0.55.0 changed KV signatures (AccountIdentifier, 3 returns). Baseline resource_*.go uses the old API so internal/provider fails to compile under Δm; Δc migration required."),
"cosmos__cosmos-sdk__19810": (W,"opencode","high","prometheus/common 0.50 removed expfmt.FmtText; production telemetry/metrics.go uses it → genuine compile break independent of the circular ContentTypeText test. Δc migration required."),
"eakmanrq__sqlframe__137": (T,"opencode","high","convert_timezone was unsupported_engines='*'. Δc enables cross-engine support (new exp.ConvertTimezone + CAST); Δt asserts the new feature. sqlglot didn't break existing behavior—drive-by feature."),
"eakmanrq__sqlframe__200": (W,"codex","medium","sqlglot 25.31 added native median/unix_seconds parsing, flipping parse_one to typed nodes so test_invoke_anonymous fails; Δt didn't ignore-list them, forcing a production rewrite to expression.Median/UnixSeconds—real behavior change."),
"eakmanrq__sqlframe__216": (T,"opencode","medium","Δt rewrites TZ conventions wholesale (conftest TZ→UTC, removes per-dialect branches, TIMESTAMP→TIMESTAMP_LTZ); Δc strips tzinfo—a deliberate product/timezone refactor leveraging, not forced by, sqlglot 25.34."),
"eakmanrq__sqlframe__492": (T,"opencode","high","Verifier runs only test_invoke_anonymous, a meta-test using inspect.getsource() to enforce native sqlglot nodes; ntile/regexp_instr still emit valid SQL—failure is a style/static rule, not a functional dependency break."),
"elastic__cloud-on-k8s__6847": (W,"opencode","high","Verifier pkg imports v1alpha1.Logstash; Δc fixes v1alpha1/webhook.go using removed controller-runtime v0.15 InjectScheme/ValidatingWebhookFor. _restore only resets the 3 Δt files, not the webhook, so the imported production pkg won't compile without Δc."),
"giantswarm__muster__751": (W,"opencode","medium","Δc force-migrates production oauth_server_config.go (valkey DPoP import + removed WithKubernetesSATrust) for mcp-oauth v0.2.184; without Δc internal/server won't compile under go test ./..., independent of the circular k8sSASubPattern test."),
"golangci__golangci-lint__4718": (T,"opencode","high","sloglint 0.6→0.7 adds forbidden-keys; Δc is purely additive wiring with no existing break; Δt adds a NEW testdata case for the new feature. Drive-by feature, not a break of pre-existing behavior."),
"jamcalli__Pulsarr__1107": (W,"codex","medium","Δm drops dotenv; verifier target src/utils/logger.ts still imports {config} from dotenv → module-resolution failure; Δt mocks the replacement node:util.parseEnv, and Δc rewrites production logger.ts—repair required."),
"ledgersmb__LedgerSMB__8904": (T,"opencode","medium","Jest/babel-jest/jsdom 30 are dev/test-only. Δt removes the jsdom30-forbidden window.location override and asserts Δc's new successFn callback—a testability DI refactor / test-infra adaptation."),
"mightyiam__eslint-config-love__2178": (T,"opencode","medium","eslint 9.34→9.35 (minor) adds rule preserve-caught-error; Δt only adds it to the expected-rules map; Δc adopts it in config with editorial options. Drive-by feature adoption / snapshot mismatch."),
"mozilla__addons-frontend__9637": (T,"opencode","high","Verifier runs only TestServerHtml.js, which mocks chunkExtractor via sinon stubs—real @loadable/server never runs. Δt renames the mock stub singular→plural; Δm is causally irrelevant. Mocked/circular oracle."),
"nextcloud__server__39964": (T,"opencode","medium","Verifier runs only utils.spec.ts. camelcase v8 ESM breaks the Jest transpile; the causally-required fix is jest.config transformIgnorePatterns (test infra). The utils.ts hunk is type-only; runtime usage unchanged—config-only."),
"omjadas__hudsucker__88": (T,"opencode","high","rustls-pemfile is a dev-dependency; TEST_CMD `cargo test --lib --no-run` excludes tests/ (all Δt) and doctests. Δc repairs only doctests + a #[cfg(test)] module—no production source. (codex's UNWITNESSED is wrong: the cfg(test) mod does fail to compile.)"),
"owncloud__web__11511": (T,"opencode","high","Δc's production .vue changes are type-only (erased by esbuild, invisible to vitest); the causally-required runtime fixes live in web-test-helpers (RouterLink stub, router mock). Test-suite maintenance."),
"oxidecomputer__dropshot__1556": (T,"opencode","medium","serde_tokenstream 0.2.3 corrects the span to 2 chars; the minimal accommodation is a 2-char snapshot. Δc instead widens the span to the full input (drive-by diagnostic improvement) and Δt asserts it, so a legitimate dep-resolution still fails Δt."),
"prettier__prettier__10546": (T,"opencode","high","Δt's snapshot diff is append-only, adding a NEW fixture for `import type=require()`—syntax unparseable before the bump—so the old suite wouldn't fail. Drive-by + circular new feature."),
"prettier__prettier__12241": (T,"opencode","high","Δc only adds the regexpUnicodeSets plugin for NEW drive-by /a/v fixtures; the one real pre-existing break (loc.index) is absorbed by Δt's snapshot re-record, not repaired by Δc. New-feature unlock + circular."),
"prometheus__client_java__1724": (U,"opencode","high","protobuf 4.33.1→4.33.2 generated-package rename; codegen is off by default and the required regenerated _4_33_2/Metrics.java was stripped from Δc, so even P⊕Δm⊕Δc⊕Δt fails to compile. Confounded/broken oracle."),
"promptfoo__promptfoo__8918": (T,"opencode","high","The SDK is mocked (mockResolvedValue) and the token shape is fabricated by the test on a local interface (no SDK compile break); asserted fields are producible only by Δc—mocked + circular feature oracle."),
"saveourtool__diktat__1529": (W,"codex","high","Verifier's `mvn -pl diktat-rules -am` compiles reactor deps diktat-common/test-framework which use org.slf4j directly; kotlin-logging 3.0.3 breaks the compile before tests run. Δc migration required; the circular EmptyBlock test is secondary."),
"sequelize__umzug__572": (W,"codex","high","Graded command is `npm run build && jest`; tsc fails because pony-cause's ErrorWithCause became generic, fixed by Δc's ErrorWithCause<unknown>. Build failure = test FAIL, cleanly attributable to the dep; the circular Δt snapshot is irrelevant."),
"smlx__piv-agent__155": (T,"codex","medium","x/crypto/openpgp and ssh/terminal are deprecated but NOT removed in v0.7.0, so base production compiles; the verifier fails on P⊕Δm⊕Δt only because Δt references a Δc-only symbol (ECDSAPublicKey)—circular."),
"solana-labs__solana-program-library__4301": (W,"codex","medium","spl-token 0.1.8→0.3.7 removes the Token class; base src/index.ts uses Token.* so jest fails at runtime regardless of Δt. Δc required (opencode's over-coupling concern is real but the break is independently dependency-caused)."),
"tusbar__eslint-config-xo-nextjs__163": (T,"opencode","high","Patch bump 10.2.0→10.2.2; the only dependency effect is message-strings for already-wired rules (satisfiable by Δt). Δc voluntarily switches to plugin:@next/next/recommended; the failing new tests assert rules Δc itself enables—circular drive-by."),
"ubugeeei-prod__ox-content__131": (U,"codex","high","test_state.py runs `cargo test` only; Δt's sole patched file is a TypeScript test (vite-plugin) never compiled by cargo—unexecuted/dead oracle. The real oxc break is witnessed by a Rust #[test] bundled inside Δc, not by Δt."),
"ymtdzzz__otel-tui__153": (W,"opencode","medium","collector 0.107→0.108 moves component.Status* into componentstatus; base sharedcomponent.go references the removed symbols so the package fails to compile independent of Δt. Δc required; Δt's comp.hostWrapper reference is over-coupling but a real package-move break remains."),
}

rows = list(csv.DictReader(open(REPORTS/"test_patch_agreement_2026-06-26.csv")))
assert set(ADJ) <= {r["task"] for r in rows}

# ---- reconciled 219-row labeling
recon = []
for r in rows:
    cv, ov = r["codex_verdict"], r["opencode_verdict"]
    if r["task"] in ADJ:
        fv, coder, conf, reason = ADJ[r["task"]]
        recon.append({"task": r["task"], "codex": cv, "opencode": ov, "agreed": 0,
                      "final_verdict": fv, "source": "adjudication", "correct_coder": coder,
                      "confidence": conf, "reason": reason})
    elif cv and ov and cv == ov:
        recon.append({"task": r["task"], "codex": cv, "opencode": ov, "agreed": 1,
                      "final_verdict": cv, "source": "agreement", "correct_coder": "both",
                      "confidence": "", "reason": ""})
    else:  # one side empty (shouldn't happen now) -> leave unresolved
        recon.append({"task": r["task"], "codex": cv, "opencode": ov, "agreed": 0,
                      "final_verdict": cv or ov, "source": "single", "correct_coder": "",
                      "confidence": "", "reason": ""})

with open(REPORTS/"test_patch_reconciled_2026-06-26.csv","w",newline="") as fh:
    w=csv.DictWriter(fh, fieldnames=list(recon[0].keys())); w.writeheader(); w.writerows(recon)

# ---- stats
adj_rows=[x for x in recon if x["source"]=="adjudication"]
adj_verdict=Counter(x["final_verdict"] for x in adj_rows)
adj_coder=Counter(x["correct_coder"] for x in adj_rows)
adj_conf=Counter(x["confidence"] for x in adj_rows)
final_dist=Counter(x["final_verdict"] for x in recon)
agreed_dist=Counter(x["final_verdict"] for x in recon if x["source"]=="agreement")

print("=== adjudication of 35 disputes ===")
print("final verdict:", dict(adj_verdict))
print("correct coder:", dict(adj_coder))
print("confidence:", dict(adj_conf))
print("=== reconciled 219 ===")
print("final dist:", dict(final_dist))
print("agreed dist:", dict(agreed_dist))
json.dump({"adj_verdict":dict(adj_verdict),"adj_coder":dict(adj_coder),
           "adj_conf":dict(adj_conf),"final_dist":dict(final_dist),
           "agreed_dist":dict(agreed_dist)}, open("jobs/adj_stats.json","w"), indent=2)
print("\nwrote", REPORTS/"test_patch_reconciled_2026-06-26.csv")

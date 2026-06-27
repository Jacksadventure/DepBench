"""Render the adjudication report markdown from the reconciled CSV."""
import csv
from pathlib import Path
from collections import Counter

REPORTS = Path("harbor_benchmark/reports")
recon = list(csv.DictReader(open(REPORTS/"test_patch_reconciled_2026-06-26.csv")))
adj = [r for r in recon if r["source"] == "adjudication"]
adj.sort(key=lambda r: (r["final_verdict"], r["task"]))

SHORT = {"WITNESSES_BREAKING_CHANGE":"WITNESS","TESTS_OTHER_THING":"TESTS_OTHER","UNWITNESSED":"UNWITNESSED","INCONCLUSIVE":"INCONCLUSIVE"}
def esc(s): return s.replace("|","\\|").replace("\n"," ")

fv = Counter(r["final_verdict"] for r in adj)
coder = Counter(r["correct_coder"] for r in adj)
conf = Counter(r["confidence"] for r in adj)
final_all = Counter(r["final_verdict"] for r in recon)
agreed = Counter(r["final_verdict"] for r in recon if r["source"]=="agreement")

m = []
m.append("# Adjudication of the 35 codex-vs-opencode Disagreements\n")
m.append("Date: 2026-06-26 · Adjudicator: Claude (independent third coder) · Branch `v4-with-test`\n")
m.append("I resolved each of the 35 tasks where **codex** (`gpt-5.3-codex`) and **opencode** "
         "(`github-copilot/gemini-3.1-pro-preview`) disagreed, by reading the real "
         "`solution/manifest.patch` (Δm), `tests/test.patch` (Δt), `solution/code.patch` (Δc) and — "
         "decisively — the verifier (`tests/test.sh` + `tests/test_state.py`) for each task, and "
         "applying the locked Level-1 criterion: a valid witness requires "
         "`TEST(P⊕Δm⊕Δt)=FAIL` for a **dependency-caused** compile/type/runtime reason **and** a "
         "production `Δc` that is causally required to pass.\n")

m.append("## Decisive principle\n")
m.append("> For every \"is this circular?\" dispute: **strip the Δc-coupled lines from Δt and ask "
         "whether `P⊕Δm⊕Δt` still fails for a dependency reason.** If yes → witness (the circular "
         "assertion is incidental); if it then passes → the oracle is circular/other. I also checked, "
         "for every task, whether the verifier actually **runs** the patched test and whether the "
         "upgraded dependency is **mocked** or **dev/test-only**.\n")

m.append("## Headline\n")
m.append(f"- Disputes adjudicated: **{len(adj)}**.")
m.append(f"- Correct coder: **opencode {coder['opencode']}**, **codex {coder['codex']}**.")
m.append(f"- Adjudicated verdicts: **{fv['WITNESSES_BREAKING_CHANGE']} WITNESS**, "
         f"**{fv['TESTS_OTHER_THING']} TESTS_OTHER_THING**, **{fv['UNWITNESSED']} UNWITNESSED** "
         f"→ {fv['TESTS_OTHER_THING']+fv['UNWITNESSED']}/{len(adj)} of the disputed tasks are "
         f"**not** clean witnesses (likely oracle-quality problems).")
m.append(f"- Confidence: {conf['high']} high, {conf['medium']} medium, {conf.get('low',0)} low.\n")

m.append("opencode (gemini-3.1-pro-preview) was right on ~71% of disagreements: codex systematically "
         "**over-calls WITNESS** on circular oracles, drive-by feature tests, dev/test-only-dependency "
         "breaks, mocked dependencies, and tests the verifier doesn't run. codex's 10 correct calls were "
         "the inverse trap — a real production compile/runtime break sitting *behind* a circular-looking "
         "Δt (e.g. `29ki`, `cloudflare`, `saveourtool__diktat`, `sequelize__umzug`, `solana`), which "
         "opencode wrongly dismissed.\n")

m.append("## Recurring failure modes among the 23 non-witness disputes\n")
m.append("| Mode | Example tasks |\n| --- | --- |")
m.append("| Circular oracle (Δt asserts a symbol/string introduced only by Δc) | JoshuaKGoldberg__create-typescript-app__1489, OpenFeign__querydsl__1685, promptfoo__promptfoo__8918, tusbar__eslint-config-xo-nextjs__163, smlx__piv-agent__155 |")
m.append("| Drive-by feature the bump *unlocks* (old suite wouldn't fail) | golangci__golangci-lint__4718, eakmanrq__sqlframe__137, prettier__prettier__10546, prettier__prettier__12241, camunda-community-hub__spring-zeebe__642, mightyiam__eslint-config-love__2178 |")
m.append("| Dev/test-only dependency; Δc repairs only test infra | ashutoshgngwr__noice__673, omjadas__hudsucker__88, ledgersmb__LedgerSMB__8904, owncloud__web__11511 |")
m.append("| Dependency mocked / verifier scope excludes the real path | mozilla__addons-frontend__9637, nextcloud__server__39964 |")
m.append("| Δt not executed by the verifier, or broken oracle | ubugeeei-prod__ox-content__131 (cargo test never runs the TS Δt), prometheus__client_java__1724 (regenerated file stripped from Δc) |")
m.append("| Patch-bump with no real API break | Graylog2__graylog2-server__21446, oxidecomputer__dropshot__1556, eakmanrq__sqlframe__216 |\n")

m.append("## Full case-by-case adjudication (35)\n")
m.append("| task | codex | opencode | **adjudicated** | correct | conf | decisive reason |")
m.append("| --- | --- | --- | --- | --- | --- | --- |")
for r in adj:
    m.append(f"| {r['task']} | {SHORT[r['codex']]} | {SHORT[r['opencode']]} | "
             f"**{SHORT[r['final_verdict']]}** | {r['correct_coder']} | {r['confidence']} | {esc(r['reason'])} |")
m.append("")

m.append("## Reconciled dataset labels (all 219)\n")
m.append("Combining the 184 agreed tasks with my 35 adjudications gives a single reconciled label per task "
         "(`harbor_benchmark/reports/test_patch_reconciled_2026-06-26.csv`):\n")
m.append("| Verdict | agreed (184) | adjudicated (35) | **reconciled total (219)** | share |\n| --- | ---: | ---: | ---: | ---: |")
for v in ("WITNESSES_BREAKING_CHANGE","TESTS_OTHER_THING","UNWITNESSED"):
    m.append(f"| {v} | {agreed.get(v,0)} | {fv.get(v,0)} | **{final_all.get(v,0)}** | {final_all.get(v,0)/len(recon)*100:.1f}% |")
m.append(f"| **total** | 184 | 35 | **{len(recon)}** | 100% |\n")
nonwit = final_all['TESTS_OTHER_THING']+final_all['UNWITNESSED']
m.append(f"**~{nonwit}/219 ({nonwit/len(recon)*100:.0f}%) tasks are likely oracle-quality problems** "
         f"(tests-other-thing or unwitnessed); ~{final_all['WITNESSES_BREAKING_CHANGE']}/219 are clean "
         f"dependency-break witnesses.\n")

m.append("### Caveat\n")
m.append("The 157 **agreed-witness** tasks were *not* independently re-audited here. Because codex "
         "systematically over-calls WITNESS, opencode independently agreeing is meaningful corroboration, "
         "so these are more trustworthy than a single coder — but a shared blind spot remains possible. "
         "The 26 **agreed-tests-other** and 1 agreed-unwitnessed are similarly corroborated.\n")

m.append("## Quarantine recommendation\n")
m.append("Treat the reconciled **46 TESTS_OTHER_THING + 4 UNWITNESSED = 50 tasks** as the candidate "
         "exclude/quarantine set for a strict witnessed-breaking-change benchmark. The "
         f"{conf['high']} high-confidence non-witness adjudications are the strongest removals; the "
         f"{conf['medium']} medium-confidence ones (often grouped bumps or mixed circular+real signals) "
         "warrant a dynamic three-state check before a final call.\n")

m.append("## Deliverables\n")
m.append("- This report: `harbor_benchmark/reports/test_patch_adjudication_2026-06-26.md`\n"
         "- Reconciled 219-row labels: `harbor_benchmark/reports/test_patch_reconciled_2026-06-26.csv`\n"
         "- Underlying agreement data: `harbor_benchmark/reports/test_patch_agreement_2026-06-26.{csv,md}`\n")

(REPORTS/"test_patch_adjudication_2026-06-26.md").write_text("\n".join(m))
print("wrote", REPORTS/"test_patch_adjudication_2026-06-26.md", f"({len(m)} lines)")

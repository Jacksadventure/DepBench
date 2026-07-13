# Case study: OWASP__wrongsecrets__970 (Maven, org.linguafranca.pwdb:KeePassJava2 2.1.4 → 2.2.1)

**Half-pass profile (final pass_matrix):** 5/10 configs pass.
Pass: claude48/opencode, gemini35flash/claude_code, gemini35flash/opencode, gpt55/claude_code, gpt55/copilot_cli.
Fail: claude48/claude_code, claude48/copilot_cli, gemini35flash/copilot_cli, gpt55/codex, gpt55/opencode.

**Headline finding:** This is *not* a capability half-pass and only partially a leakage story. Every guarded rerun agent on this task produced the correct migration; **3 of the 4 guarded-rerun "failures" (1.0→0) are a systematic verifier-environment artifact** — the hidden-test harness's `mvn` died on `JAVA_HOME` before compiling anything — and the 4th is an agent-harness timeout. The one guarded rerun whose verifier environment worked (gpt55/claude_code) passed, revalidating the task as solvable without upstream access.

---

## 1. Ground truth

`solution/manifest.patch` bumps one POM property (`harbor_benchmark/tasks_v4/OWASP__wrongsecrets__970/solution/manifest.patch`):

```
-    <KeePassJava2.version>2.1.4</KeePassJava2.version>
+    <KeePassJava2.version>2.2.1</KeePassJava2.version>
```

`solution/code.patch` makes three changes:

1. **Challenge23.java — the load-bearing fix.** KeePassJava2 2.2.1 dropped its SpongyCastle transitive dependency (the Android fork of BouncyCastle, identical package layout under `org.spongycastle`), so the two production imports must be repointed:
   ```java
   +import org.bouncycastle.util.encoders.Base64;
   +import org.bouncycastle.util.encoders.Hex;
   ...
   -import org.spongycastle.util.encoders.Base64;
   -import org.spongycastle.util.encoders.Hex;
   ```
2. **Challenge14.java** — adds a second-chance fallback that loads `src/test/resources/alibabacreds.kdbx` on local runs ("Fix to prevent local execution issues").
3. **ctf-instructions.md** — a docs link fix (cosmetic).

**Hidden test (`tests/test.patch`)** patches only `Challenge28Test.java`, swapping its `org.spongycastle.util.encoders.Hex` import to `org.bouncycastle.util.encoders.Hex`. The oracle (`tests/test_state.py`) re-applies this patch, then runs `mvn ... -DskipTests test-compile` (INSTALL) and `mvn ... -Dtest=Challenge28Test test` (TEST). So the *only* strictly required production work is: bump the POM + swap Challenge23's two imports so the whole tree compiles against 2.2.1. The Challenge14 fallback is not oracle-relevant.

**Visible-test trap:** the pre-upgrade `Challenge28Test` in the checkout still imports `org.spongycastle`, so after a correct migration the visible test *cannot compile*. The task rewards agents that recognize the stale visible test and leave it alone rather than shimming SpongyCastle back onto the classpath.

**Knowledge availability:** the instruction itself quotes the human repair commit summary — *"Remove all spongycastle items as we only use BC now"* — so the breaking-change "card" is effectively handed to the agent. The swap is also locally derivable: `mvn dependency:tree` shows spongycastle vanishing at 2.2.1, and sibling challenges (Challenge24–35 and Challenge29Test) already import `org.bouncycastle`.

## 2. Guard-verified pass: gpt55/claude_code (trial `OWASP__wrongsecrets__970__WUf56ua`, revalidated 1.0→1)

Audit row (`guarded_leak_claude_segment1_replacement_audit_20260701.csv`): guarded rerun with `blocked_repo=True, agent_proxy=True, git_history_pruned=True` scored **reward=1**. Trajectory: `harbor_benchmark/reports/guarded_leak_claude_segment1_artifacts_20260701/claude_code/gpt_55/OWASP__wrongsecrets__970/agent/claude-code.txt` (extracted to `trials/OWASP__wrongsecrets__970__gpt55__claude_code.json`).

How it found the breaking change **without the upstream repo**:

- Immediate hypothesis from local inspection alone (2nd assistant message): *"The likely compile break is that KeePassJava2 2.2.1 no longer brings the SpongyCastle encoder package that `Challenge23` was using transitively."*
- Attempted **jar/POM metadata inspection**, not the repo: two WebFetch calls to `https://repo1.maven.org/maven2/org/linguafranca/pwdb/KeePassJava2/2.2.1/KeePassJava2-2.2.1.pom` and `.../KeePassJava2-kdbx/2.2.1/...pom` ("Summarize ... especially any BouncyCastle or SpongyCastle dependencies"). Both returned 403 through the guard proxy, so it fell back on parametric knowledge: *"Maven Central's web fetch path returned 403 for the POM metadata, so I'm relying on the local dependency usage and the known package-level replacement from SpongyCastle encoders to BouncyCastle encoders."*
- **Trial against the resolver/compiler:** installed JDK17 + Node in the container, then *"The dependency tree now confirms KeePassJava2 and its modules resolve at `2.2.1`, and SpongyCastle is no longer present in the filtered tree."* Maven compile succeeded.
- **Refused the visible-test shim:** when `-Dtest=Challenge14Test,Challenge23Test` failed at test-compile on the stale `Challenge28Test` spongycastle import, it reasoned: *"Production code already uses BouncyCastle for `Challenge28`, so adding SpongyCastle back just to satisfy a stale visible test would contradict the upgrade repair. I'm going to keep tests untouched, run a compile/package verification that skips test compilation, and report the visible-test compile blocker clearly."* — exactly the behavior the hidden oracle rewards.

## 3. "Failing" strong configs: verifier artifact, not knowledge gap

**gpt55/codex** (guarded rerun `4QwpYCX`, log 1.2 MB at `guarded_leak_exact_artifacts_20260630/codex/gpt_55/.../agent/codex.txt`): made **zero web searches** (vs. the leaky original), derived everything locally, and delivered the correct fix. Final message: *"Bumped `KeePassJava2` to `2.2.1` ... Switched the remaining production Spongy Castle usage to Bouncy Castle in Challenge23.java ... Dependency tree resolves `org.linguafranca.pwdb:KeePassJava2:2.2.1` and no production Spongy Castle dependency ... I did not modify tests. The current local test compile still fails because an existing test imports `org.spongycastle.util.encoders`, which is outside the allowed edit scope."* It even ran `./mvnw dependency:tree -Dincludes=org.linguafranca.pwdb,org.bouncycastle,com.madgag.spongycastle` (bouncycastle 1.73 present, no spongycastle) and jshell round-trip checks. **Not** a knowledge gap, incomplete migration, or overfit shim.

Its verifier then failed *before compiling anything*:
```
E   The JAVA_HOME environment variable is not defined correctly,
E   this environment variable is needed to run this program.
FAILED tests/test_state.py::test_dependency_upgrade_fix
```
`test_state.py` runs INSTALL via `bash -lc '... && mvn -B -q -U ... test-compile'`; in the guarded-rerun container the login-shell `JAVA_HOME` was broken (the agent itself hit `Error: JAVA_HOME is not defined correctly` at its first `./mvnw` call and worked around it with `JAVA_HOME=/opt/java/openjdk`). The defect is **systematic**: 18 of 50 tasks in `guarded_leak_exact_artifacts_20260630/codex/gpt_55/` show the identical JAVA_HOME verifier failure.

**claude48/copilot_cli** (rerun `oo64nr3`) and **claude48/claude_code** (rerun `gsK8kbW`) failed with the *byte-identical* verifier error — yet both produced correct fixes:
- copilot_cli/claude48 final message: *"exactly 3 production files changed, no test files modified, all 61 docker challenge tests pass ... swapped `org.spongycastle.util.encoders.{Base64,Hex}` → `org.bouncycastle` ... validated by temporarily simulating the hidden `Challenge28Test` spongycastle→bouncycastle patch, then reverting — test files are unmodified, SHA256-verified."*
- claude_code/claude48 final message: *"Repointed its two encoder imports to the BouncyCastle package (which the rest of the codebase — Challenge24/25/26/27/28/32/33/35 — already uses) ... `Challenge23Test` + `Challenge28Test` — 6/6 passed."* (Note the **sibling exemplar** reasoning.)

**gpt55/opencode** (rerun `frwmXvJ`): `AgentTimeoutError: Agent execution timed out after 3600.0 seconds`; the opencode log is 5 KB — the harness stalled after the very first reasoning step. Infrastructure, not capability.

**gemini35flash/copilot_cli** (rerun `kT9Y3Z9`, original already 0.0): the rerun agent *also* produced the right migration ("Replaced Spongy Castle with Bouncy Castle ... migrating Challenge23.java ... imports") and *also* died on the JAVA_HOME verifier defect. (It did touch `Challenge28Test.java`, which the oracle restores anyway.)

## 4. What the leaky originals fetched

- **codex/gpt55 original** (`harbor_jobs/codex_cloudgpt_gpt55_clean205_resume204_clean_conc5_2026-06-21__04-12-00/OWASP__wrongsecrets__970__RJYPmZ8/agent/codex.txt`): fetched **the ground-truth PR itself** — web_search on `https://github.com/OWASP/wrongsecrets/pull/970/files`, then `curl -L https://github.com/OWASP/wrongsecrets/pull/970.patch`, dumping the full 4-commit human patch into context, then stated: *"I pulled the PR patch to avoid guessing."* This is why it was replaced with a guarded rerun (leak_annotation_key `v4_withtest219__codex__gpt55__full219_20260627__...RJYPmZ8`; consensus annotation `own-project-fix`).
- **gpt55/copilot_cli original pass** (`SME4Ec4`, never guard-rerun — annotators split `own-project-fix`/`none`): mid-run it called the GitHub MCP tool `github-mcp-server-pull_request_read {"owner": "OWASP", "repo": "wrongsecrets", "pullNumber": 970, "method": "get_diff"}` — the ground-truth PR diff. Mitigating detail: it had already committed the oracle-relevant fix (pom bump + Challenge23 bouncycastle swap, "The new KeePass version drops Spongy Castle transitive usage in favor of Bouncy Castle") *before* the PR read; the PR was consulted only for the oracle-irrelevant Challenge14 detail. Tainted pass, but the taint was not load-bearing.
- **Clean never-flagged passes:** gemini35flash/claude_code (`kL9GSoC`, 24 k chars) used zero web access — `git grep -i spongy`, read Challenge14/23, compile. claude48/opencode (`9UgQBF9`) explicitly wanted the PR, found itself blocked, and fell back on the instruction: *"Since I can't reach GitHub via git ... WebFetch is not available ... The repair summary lists exactly 3 items: Remove all spongycastle items (done: Challenge23, about.html; tests via oracle) - fix link - Fix to prevent local execution issues."* gemini35flash/opencode (`XeQtTme`) shows no upstream fetches either.

## 5. Verdict

**(a) Solvable without leakage — proven — AND (c) the fail side of the half-pass is an artifact.**

- Proof of (a): gpt55/claude_code passed its fully guarded rerun (blocked repo, pruned git history, proxy) end-to-end. Differentiator: none in capability — the differentiators were (i) a working verifier environment and (ii) an agent harness that didn't stall.
- Proof of (c): all three guarded 1.0→0 replacements (gpt55/codex, claude48/copilot_cli, claude48/claude_code) submitted the ground-truth-equivalent fix and were zeroed by the identical `JAVA_HOME` verifier defect (systematic: 18/50 trials in the 20260630 exact-rerun batch); the fourth (gpt55/opencode) was a 5 KB-log agent timeout.
- The task itself is near-trivial by design leak-in-instruction: the commit summary "Remove all spongycastle items as we only use BC now" plus the compiler error plus in-repo bouncycastle sibling usage make the fix locally derivable; even gemini-3.5-flash solved it clean in 24 k chars.

**Intervention to flip the failers:** no breaking-change card, exemplar, policy prior, or extra time is needed — the agents already succeeded. Fix the guarded-rerun verifier environment (export a valid `JAVA_HOME`/`PATH` for `bash -lc` in the verifier container, or make `test_state.py` use `./mvnw` with an explicit JDK home) and re-score; this task's four guarded failures would very likely flip to pass (the three JAVA_HOME ones near-certainly; opencode needs its harness stall fixed). For benchmark hygiene: (i) recheck all 18 JAVA_HOME-failed guarded reruns across tasks, (ii) mark the gpt55/copilot_cli original pass as tainted-but-not-load-bearing (GitHub MCP PR read post-fix), and (iii) consider redacting the Human Repair Commit Summary from instructions if the benchmark intends to test breaking-change *discovery* rather than *execution*.

### Key artifacts
- Task: `harbor_benchmark/tasks_v4/OWASP__wrongsecrets__970/{instruction.md,solution/code.patch,tests/test.patch,tests/test_state.py}`
- Verified pass log: `harbor_benchmark/reports/guarded_leak_claude_segment1_artifacts_20260701/claude_code/gpt_55/OWASP__wrongsecrets__970/agent/claude-code.txt`
- Artifact-failure logs + verifier stdout: `harbor_benchmark/reports/guarded_leak_exact_artifacts_20260630/codex/gpt_55/OWASP__wrongsecrets__970/`, `guarded_leak_copilot_claude48_artifacts_20260701/copilot_cli/claude48/...`, `guarded_leak_remaining_claude_artifacts_20260702/claude_code/claude48/...`
- Leaky original: `harbor_jobs/codex_cloudgpt_gpt55_clean205_resume204_clean_conc5_2026-06-21__04-12-00/OWASP__wrongsecrets__970__RJYPmZ8/agent/codex.txt`
- Tainted original pass: `harbor_jobs/copilot_cli_gpt55_clean205_reuse_host_auth_nopreapply_conc5_retry1_2026-06-20__00-15-00/OWASP__wrongsecrets__970__SME4Ec4/agent/copilot-cli.jsonl`

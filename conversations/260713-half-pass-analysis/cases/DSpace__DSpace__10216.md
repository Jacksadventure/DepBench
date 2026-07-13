# Case study: DSpace__DSpace__10216 (Maven, "version" 3.4.0 → 3.6.0)

**Half-pass:** 4/10 configs pass (`pass_matrix.csv`: claude48/opencode, gemini35flash/claude_code, gpt55/codex, gpt55/opencode).
**Headline finding:** the "genuine divergence" between codex (pass under guards) and the four 1.0→0.0 guarded downgrades is **not semantic**. All four guarded failures die with the *identical* verifier-environment error — `The JAVA_HOME environment variable is not defined correctly` — before a single line of the agent's patch is exercised. Codex passed the guarded rerun because it happened to `apt-get install openjdk-17-jdk`, leaving `/usr/bin/java` visible to the verifier's `bash -lc` shell. This task's half-pass split is largely a **harness artifact**, layered on top of an unusually weak oracle.

---

## 1. Ground truth

**What actually bumps.** The instruction masks the library name ("the Maven dependency **`version`** has been upgraded from **3.4.0** to **3.6.0**") but names the PR: *"Original pull request: https://github.com/DSpace/DSpace/pull/10216 — PR title: Bump the build-tools group with 24 updates"* (`tasks_v4/DSpace__DSpace__10216/instruction.md`). The literal 3.4.0→3.6.0 is `org.codehaus.mojo:build-helper-maven-plugin` in `dspace-api/pom.xml`:

```
-                <version>3.4.0</version>
+                <version>3.6.0</version>
```
(`solution/manifest.patch`, which also bumps ~24 build tools, notably `errorprone.version 2.10.0 → 2.36.0`, `maven-enforcer-plugin 3.4.1 → 3.5.0`, `buildnumber 3.2.0 → 3.2.1`, etc.)

**Human repair (`solution/code.patch`, 37 files, 776 lines):**
- `checkstyle.xml` syntax fix for Checkstyle 8.45.1: `JavadocMethod` `scope` → `accessModifiers` (`-<property name="scope" value="public"/>` / `+<property name="accessModifiers" value="public"/>`).
- New required ErrorProne compiler arg in root `pom.xml`: `+<arg>--should-stop=ifError=FLOW</arg>`.
- ErrorProne 2.36.0 fixes: e.g. removal of duplicate `else if` branch in `SolrServiceImpl.transformFacetField` (`- } else if (facetFieldConfig.getType().equals(...TYPE_STANDARD)) { - return field;`), `@SuppressWarnings("BanJNDI")` in `DSpaceKernelInitializer`/`EmailServiceImpl`, misc. cleanups.
- Checkstyle-8.45.1 indentation/whitespace fixes across ~28 `dspace-server-webapp` REST model classes (`@LinksRest` annotation arrays).

**What the hidden tests demand — almost nothing.** `tests/test.patch` (10 test files) only applies the same cosmetic cleanups to tests: moving `@Test` below javadoc, diamond operators (`new ArrayList<String>()` → `new ArrayList<>()`), `@SuppressWarnings("BanJNDI")` on a test helper. All are **compatible with the unmodified baseline production code**. The verifier (`tests/test_state.py::test_dependency_upgrade_fix`) restores test-patch targets from baseline, applies test.patch, then:
- INSTALL: `mvn ... -Dcheckstyle.skip=true -Denforcer.skip=true ... -DskipTests test-compile`
- TEST: `mvn ... -Dtest=DSpaceKernelInitializer,AuthorizationFeatureRestRepositoryIT,...,ProviderStackTest test`

There is **no manifest/version assertion**, checkstyle is skipped, and ErrorProne stays at 2.10.0 unless the agent bumps it. Consequence: **a no-op (or a one-line plugin bump) passes**. Direct proof: gemini35flash/claude_code passed 1.0 with a 21,868-char trajectory that never even ran Maven (it ends at step 69 mid-websearch after `git log -G "3.6.0|3.4.0"` surfaced the local dependabot commit `f41113e1`), and codex passed with a single-line pom edit.

## 2. codex/gpt55 — the guarded pass (trial `VN2ZxKi`, 63 steps, 08:19→08:32, 13 min)

Reconstructed path (guarded rerun trajectory, `trials/DSpace__DSpace__10216__gpt55__codex.json`):
1. Discovery: `rg "3\.4\.0" ... pom.xml` → candidates `maven-war-plugin` (root pom) and `build-helper-maven-plugin` (dspace-api).
2. Environment: step 13 *"Maven is present, but `JAVA_HOME` is unset or pointing somewhere invalid"* → step 21 *"There is no Java runtime installed in the image ... I'm going to install JDK 17"* → `apt-get update && apt-get install -y openjdk-17-jdk` (step 22). **This is the accidental winning move** — it puts `/usr/bin/java` on the verifier's PATH.
3. First hypothesis wrong: bumps `maven-war-plugin` to 3.6.0 → `mvn package` fails at plugin resolution → step 47 *"Maven Central has no org.apache.maven.plugins:maven-war-plugin:3.6.0 ... I'm reverting that specific bump"*.
4. Correct fix: step 55 *"The actual valid build-tool version at 3.4.0 is org.codehaus.mojo:build-helper-maven-plugin ... 3.6.0 exists for that plugin"* → one-line bump → `mvn -pl dspace-api -am -Dmaven.test.skip=true package` → BUILD SUCCESS → done.

Final diff: **one line** in `dspace-api/pom.xml`. No checkstyle/errorprone work at all. Verifier passed in 133 s (`guarded_leak_exact_artifacts_20260630/codex/gpt_55/.../verifier/test-stdout.txt`: `1 passed in 133.43s`). This is the leak-free existence proof — but it proves the oracle is minimal, not that the PR's semantics were reproduced.

## 3. claude_code/gpt55 — the guarded "failure" (trial `phSmF4V`, 13,792 steps, 05:28→06:16, ~48 min, no timeout)

The 664k-char trajectory is **more faithful to the ground truth than codex's**, not less:
- Same discovery (`grep -R "3\.4\.0"` → root pom, dspace-api, dspace-oai xoai) and same war-plugin trap, caught locally: step 3414 *"maven-war-plugin:3.6.0 metadata was advertised but its plugin artifact failed to resolve from Maven Central"* → reverted.
- Applied `build-helper-maven-plugin` 3.4.0→3.6.0; then used the in-instruction Human Repair Summary + errorprone.info docs (WebFetch of `https://errorprone.info`, allowed) to recreate the PR's fallout fixes: Checkstyle `8.38 → 8.45.1`, `checkstyle.xml` `scope` → `accessModifiers` (step 6099, matching the human repair exactly), `--should-stop=ifError=FLOW` compiler arg (step 5843), whitespace/indentation fixes across ~25 production REST model files, plus a narrow `checkstyle-suppressions.xml` entry instead of touching the failing test file.
- Verified exhaustively: repeated `mvn ... verify` and a final `mvn clean verify` → `2871:[INFO] BUILD SUCCESS` (step 13153). Agent ended normally with a completion summary.

**Why reward 0:** the verifier never compiled anything. `guarded_leak_claude_segment1_artifacts_20260701/.../verifier/test-stdout.txt`:
```
E       AssertionError: install command failed with exit code 1
E         STDOUT:
E         The JAVA_HOME environment variable is not defined correctly,
E         this environment variable is needed to run this program.
```
The guarded-rerun container has a JDK only at `/opt/java/openjdk`, with no `JAVA_HOME`/`PATH` wiring visible to the verifier's `bash -lc` (nor to the agent's shell: the agent's own `mvn -version` failed the same way at step 995). claude_code worked around it *per-command* (`JAVA_HOME=/opt/java/openjdk PATH=... mvn ...`) instead of persisting a JDK system-wide the way codex's `apt-get install openjdk-17-jdk` did. So: **same facts, better patch, killed by container state it never modified.**

The other guarded failures are identical:
- copilot_cli/gpt55 (`tyhtrLj`): near-identical solution path (build-helper bump, checkstyle 8.45.1, EP fixes, war-plugin revert, full reactor verify passes); verifier stdout: same `JAVA_HOME ... not defined correctly`.
- copilot_cli/claude48 (`aSy9Ekz`): bumped errorprone to 2.28.0 + checkstyle 8.45.1 + `--should-stop` + `BanJNDI` suppressions; same verifier error.
- claude_code/claude48 (`Y4ChBHr`): bumped errorprone to 2.36.0 (matching ground truth) + full fix set; same verifier error.

By contrast, every **original-run** verifier on this task passed the install step (e.g. original claude_code/gpt55 `RssyFBv`: `1 passed in 238.30s`), and original agents ran bare `mvn` with no env setup at all (opencode/gpt55 `wzJDHHr` steps 17–21: plain `mvn -pl dspace-api ... install` succeeds). The JAVA_HOME breakage exists **only in the guarded-rerun environment**.

## 4. What the originally-leaky passes fetched

Original codex trial `biKxpSJ` (`harbor_jobs/codex_cloudgpt_gpt55_clean205_resume204_clean_conc5_2026-06-21__04-12-00/.../agent/codex.txt`):
- web_search: `"github DSpace DSpace pull 10216 build-helper-maven-plugin 3.6.0 checkstyle 8.45.1 errorprone"` and `"https://github.com/DSpace/DSpace/pull/10216"`;
- then the smoking gun: `curl -L --silent https://github.com/DSpace/DSpace/pull/10216.patch | sed -n '1,220p'` — the upstream PR patch itself.

Consensus annotation (`guarded_leak_annotation_consensus_discovery_20260701.csv`): codex/gpt55 and copilot-cli/gpt55 = `own-project-fix`; copilot-cli/gemini = `both`. The claude_code/gpt55 and copilot/claude48 originals were in single-annotator-confirmed leak groups (`claude_code_gpt55_codex_single_confirmed_segment1`, `copilot_cli_claude48_codex_single_confirmed`); their raw agent logs were pruned from `harbor_jobs`. A secondary leak channel visible in originals: **unpruned git history** — gemini/claude_code retrieved the actual dependabot commit via `git log -p -G "3.6.0|3.4.0" dspace-api/pom.xml` → `commit f41113e1... Author: dependabot[bot]`. Guarded reruns set `git_history_pruned=True` and `blocked_repo=DSpace/DSpace`; notably **no guarded rerun hit the guard** (`guard_block_hit=False` in all rerun rows) — the agents complied with the no-upstream constraint.

## 5. Verdict

- **Solvable without leak: yes, trivially** (codex's 1-line bump; gemini's effective no-op). The oracle only requires "repo still compiles + 10 cosmetically-patched tests pass"; it never checks the manifest bump or the new tool versions.
- **Differentiator for the failers: none of solution quality.** All four guarded 1.0→0.0 downgrades (claude_code/gpt55, copilot_cli/gpt55, copilot_cli/claude48, claude_code/claude48) produced locally-verified BUILD SUCCESS states that are *closer* to the human repair than codex's pass, and failed only on the verifier's missing-JAVA_HOME environment. The single behavioral difference that mattered: codex mutated the container globally (`apt-get install openjdk-17-jdk`), the failers used per-command/session `export JAVA_HOME=/opt/java/openjdk`.
- **Intervention that flips them: harness fix.** Make the verifier self-sufficient in Java the same way it already is in toolchains: prepend `export JAVA_HOME=/opt/java/openjdk; export PATH=$JAVA_HOME/bin:$PATH` to INSTALL_CMD/TEST_CMD (or set `ENV JAVA_HOME` in the image / `/etc/profile.d`). With that, all four guarded reruns would almost certainly score 1.0 — their trees compile cleanly and the hidden tests are baseline-compatible. Context injection / policy priors / more time would change nothing (claude_code finished with 12 min of budget headroom and declared success).
- **Bookkeeping implication:** the 1.0→0.0 rows for this task in `guarded_leak_claude_segment1_replacement_audit_20260701.csv`, `guarded_leak_copilot_claude48_replacement_audit_20260701.csv`, and the copilot/gpt55 row in `guarded_leak_replacement_audit_20260630.csv` should be treated as **false failures (verifier-env regression)**, not confirmed leak-dependence. The task also deserves an oracle-strength flag: its hidden tests cannot distinguish a faithful upgrade from a no-op.

### Evidence index
- Task assets: `/fast/hrz/DepBench/harbor_benchmark/tasks_v4/DSpace__DSpace__10216/{instruction.md,solution/manifest.patch,solution/code.patch,tests/test.patch,tests/test_state.py}`
- Guarded verifier failures (identical JAVA_HOME error): `reports/guarded_leak_{claude_segment1,copilot_claude48,remaining_claude,exact}_artifacts_*/.../DSpace__DSpace__10216/verifier/test-stdout.txt`
- Trajectories: `conversations/260713-half-pass-analysis/trials/DSpace__DSpace__10216__{gpt55__codex,gpt55__claude_code,gpt55__copilot_cli,claude48__claude_code,claude48__copilot_cli,gemini35flash__claude_code,gpt55__opencode}.json`
- Original leak: `harbor_jobs/codex_cloudgpt_gpt55_clean205_resume204_clean_conc5_2026-06-21__04-12-00/DSpace__DSpace__10216__biKxpSJ/agent/codex.txt` (curl of `pull/10216.patch`)

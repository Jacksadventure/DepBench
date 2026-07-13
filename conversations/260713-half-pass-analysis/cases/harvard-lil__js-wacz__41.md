# Case study: harvard-lil__js-wacz__41 (npm, glob 8.1.0 → 10.3.3)

**Rewards** (pass_matrix.csv): claude48 = 3/3 PASS (claude_code, copilot_cli, opencode); gemini35flash = 2/3; gpt55 = 1/4 — codex FAIL (135k chars), claude_code FAIL (113k), opencode FAIL (92k), **copilot_cli PASS**.

> **Premise correction.** The split is *not* perfectly clean by model: `gpt55__copilot_cli` (trial `4a2fFtJ`, 126 steps, reward=1.0, model `gpt-5.5` confirmed in trial header) is a genuine full run that passed. The behavior CSV records it as `chars=1166`, which likely caused it to be miscounted as a non-full run. Its existence is analytically valuable: the same model passes when it makes the opposite decision at the critical fork (see §4).

## 1. Ground truth: what the repair changes and what the hidden tests demand

**Human repair** (`harbor_benchmark/tasks_v4/harvard-lil__js-wacz__41/solution/code.patch`) is a two-line migration to the canonical glob v9+ named-export idiom in `index.js`:

```diff
-import glob from 'glob'
+import { globSync } from 'glob'
...
-        for (const file of glob.sync(path)) {
+        for (const file of globSync(path)) {
```

`solution/manifest.patch` bumps `package.json`/`package-lock.json` from `"glob": "^8.1.0"` to `"glob": "^10.3.3"`. Under `v3-no-manifest-preapply` the checkout still has glob 8.1.0 declared *and installed* — the agent must land the bump itself.

**Hidden test** (`tests/test.patch`) applies the *same* idiom to `index.test.js`:

```diff
-import glob from 'glob'
+import { globSync } from 'glob'
...
-  assert.equal(warcCount, glob.sync(FIXTURE_INPUT).length)
+  assert.equal(warcCount, globSync(FIXTURE_INPUT).length)
```

**Verifier mechanics** (`tests/test_state.py`): applies test.patch to `/app` and runs `node --test` **against whatever `node_modules` the agent left behind** — it performs no install of its own. Two empirically verified hard constraints follow:

- Under glob **10.3.3** ESM there is **no default export**: `import glob from 'glob'` → `SyntaxError: The requested module 'glob' does not provide an export named 'default'` (reproduced in claude48/claude_code step 47 and in scratchpad).
- Under glob **8.1.0** (CJS), the hidden test's own import fails: `SyntaxError: Named export 'globSync' not found. The requested module 'glob' is a CommonJS module...` (reproduced locally).

So the hidden test demands **both** (a) glob ≥ v9 actually installed in `node_modules` at grading time, and (b) an `index.js` that loads under it. Crucially, the *visible* pre-upgrade `index.test.js` itself does `import glob from 'glob'` + `glob.sync(...)`, which **cannot pass under glob 10** without a shim/loader and cannot be edited ("Do not modify any test files"). This impossibility is the fork where the two model families diverge.

## 2. Where the runs diverge

Every run — pass and fail — correctly diagnosed the breaking change. The divergence is a single *decision*, not knowledge.

### claude48 / claude_code (PASS, 147 steps) — upgrade-forward, shim the legacy test import

- Step 33: "**glob 10.3.3 has NO default export.** So `import glob from 'glob'` will give ... `SyntaxError` ... The **named export `glob`** is a function with a `.sync` property".
- Step 34: `npm install glob@10.3.3` — **saved to package.json** ("package.json now has `glob: ^10.3.3`", step 38).
- Steps 87–107: builds `/app/shims/glob` (a local `file:` package wired as `"glob": "file:./shims/glob"` + `"glob-real": "npm:glob@10.3.3"`), designed explicitly for both idioms (step 89): "1. Provide `default` = the `glob` function ... satisfies `import glob from 'glob'` → `glob.sync(...)`. 2. **Re-export all named exports of real glob (`glob`, `globSync`, `sync`, ...) — satisfies any `import { globSync } from 'glob'`**."
- Steps 109–111: migrates `index.js` to the ground-truth idiom (`import { globSync } from 'glob'`, `globSync(path)`).
- Steps 125–142: 32/32 visible tests pass under glob 10; `npm ci` verified clean because "the grader may use a clean install" (step 129).
- Final state: glob 10.3.3 in node_modules (via shim re-export) + globSync in index.js → hidden test's `import { globSync }` resolves → **PASS**. (claude48/opencode and claude48/copilot_cli independently built the same vendor-shim, e.g. opencode final: "Bumped `glob` from 8.1.0 to 10.3.3 with all 32 tests passing"; copilot_cli modified `/app/vendor/glob/*` + `package.json`.)

### gpt55 / codex (FAIL, 47 steps) — wrote the ground-truth patch, then reverted the upgrade

- Step 14: **authors the exact ground-truth diff** — `-import glob from 'glob'` / `+import { globSync } from 'glob'`, `+for (const file of globSync(path))`.
- Step 16: `npm test` — fails, because glob **8** is still installed (v8 has no `globSync`).
- Step 18 (the fork): "The v10-style named import fails under the current v8 install ... **I'm making the import bridge tolerate both shapes so the same source works before and after the dependency bump.**" → replaces the correct patch with a `createRequire` bridge (`glob.globSync || glob.sync`).
- Step 23: "I'm installing `glob@10.3.3` into `node_modules` **without updating manifests or lockfiles**" — treats v10 as a temporary verification target only.
- Step 32: correctly sees the trap: "`index.test.js` itself imports `glob` as a default export, which v10 no longer provides. Since tests cannot be edited..." — but instead of shimming, retreats.
- Step 40 (the fatal act): "I'm **restoring `node_modules` from the lockfile** so the workspace is not left in a temporary invalid dependency state" → `npm ci` reinstalls glob **8.1.0**.
- Final message (step 46): "use `glob.globSync || glob.sync`, so the source path works with **both glob v8 and v10 API shapes**."
- Grading: glob 8 in node_modules → hidden test's `import { globSync }` throws `SyntaxError` before any test runs → **FAIL**.

### gpt55 / opencode (FAIL, 19 steps) — identical arc, compressed

- Step 4: authors the exact ground-truth diff (`import { globSync } from 'glob'` + `globSync(path)`).
- Step 6: `npm test` under installed glob 8 fails → step 7 **reverts** to `import * as glob from 'glob'` + `const globSync = glob.globSync ?? glob.sync ?? glob.default?.globSync ?? glob.default?.sync`.
- Step 10: `npm install --no-save --package-lock=false glob@10.3.3` (temporary); sees the test-file default-import failure; step 14: `npm install --package-lock=false` — "**Restores installed dependencies from package files**" (i.e., glob 8).
- Final message: "Temporarily tested with `glob@10.3.3`; source/CLI loading works, but **the full suite is blocked by `index.test.js` importing `glob` as a default**" — it *names the blocker* and ships glob 8 anyway. **FAIL** (same SyntaxError).

### gpt55 / claude_code (FAIL, 2406 steps) — never even keeps globSync

- Step 1059: "replace the ESM default import with a `createRequire` load of `glob`, which **preserves the existing `glob.sync(...)` call** and works with both glob 8's CommonJS shape and glob 10.3.3's CommonJS entrypoint."
- Step 1256: under temp glob 10, "`npm test` ... fails only before `index.test.js` executes because that unchanged test file still uses `import glob from 'glob'` ... Since tests are off-limits, I'm running lint and a source-level smoke check" — verifies only `index.js` in isolation.
- Step 1956 (the fatal act): `npm install --no-save --package-lock=false glob@8.1.0 && npm test` — deliberately reinstalls v8 as the final state.
- Step 2228: "with the repository's current glob 8 install, the full `npm test` suite passes 32/32. The only tracked change remains `index.js`; **no test, package, or lock files were modified**." — states the losing condition as a virtue. **FAIL**.

### gpt55 / copilot_cli (PASS, 126 steps) — the intra-model control

- Step 96: "`glob@10` exposes named exports instead of the old default export, so I'm updating the runtime import and call site to use the named synchronous API" → lands the exact ground-truth `globSync` diff in `index.js`.
- Step 104/110: **modifies `package.json` (+299-line lockfile diff)** — the bump is persisted; step 102: adds an ESM loader (`scripts/glob-default-loader.mjs`, registered in the npm `test` script) so the unchanged visible tests also run under v10.
- Final (step 124): "Updated `glob` to `^10.3.3` and migrated runtime usage in `index.js` from the removed default export to the named `globSync` API. No test files were modified." → glob 10 installed at grading; hidden test's `globSync` import works → **PASS** (the verifier calls `node --test` directly, so its loader isn't even needed).

## 3. Differentiator: knowledge, evidence weighting, or luck?

**Not knowledge.** All four gpt55 runs independently articulated the v10 breaking change ("v10 no longer provides [a default export]", codex step 32; "The v10 module exports `glob`, `globSync`, and `sync` as named ESM exports, with no `default` export", claude_code step 725), and **codex and opencode literally authored the ground-truth patch before deleting it**. Behavior flags (`v4_withtest219_trajectory_behavior_unified_20260627.csv`) show `api=True, tests=True, bc_hyp=True` for all three failures.

**Evidence weighting + constraint interpretation.** The failing gpt55 runs resolved the "visible tests can't pass under v10" dilemma by *demoting the upgrade*: they read "Restrict your changes to the project's source code" hyper-literally as forbidding manifest/lock/node_modules persistence ("without updating manifests or lockfiles" — codex step 23; "no test, package, or lock files were modified" — claude_code step 2228), and treated in-session `npm test` green (under glob 8!) as the success criterion. All three claude48 runs — and gpt55's own copilot_cli run — resolved the same dilemma by *keeping the upgrade non-negotiable* and engineering the legacy test import around it (shim / vendor package / loader). This is visible-test overfitting in its purest form: the failing runs shipped a working tree in which the *bump itself was reverted*.

**Luck: minor, and mostly benchmark-side.** claude48's shim passing the hidden test was not luck — step 89 explicitly designs for "any `import { globSync } from 'glob'`". The luck-adjacent element is a task-design coupling: the verifier reuses the agent's `node_modules`, so "leave v8 installed" is silently fatal, and the visible suite is *unsatisfiable* under a plain canonical upgrade (the test file's own import crashes). Note gpt55/copilot_cli would have passed even with a plain bump + globSync and red visible tests — the hidden suite only needs v10 installed + migrated `index.js`.

## 4. Would a sibling-PR exemplar have flipped the gpt55 runs?

**Plausibly yes, for all three.** The canonical community migration (~73 human-repaired sibling PRs) is exactly: bump manifest to `^10.x` **in the same commit** as `glob.sync → globSync` in both source *and* test files. An exemplar makes two things unmistakable: (1) the named-import failure under v8 means *upgrade the install*, not *revert the code*; (2) the manifest bump is part of the fix, not out of scope.

Specific decision moments an exemplar would flip:

- **codex, step 16→18**: `npm test` fails under the still-installed v8 immediately after it wrote the correct patch. Its inference was "make the source tolerate both shapes." With a sibling diff in context showing `package.json: -"glob": "^8" / +"glob": "^10"` alongside `globSync`, the natural inference becomes "install the bumped version and keep my patch." Likewise step 40, where it runs `npm ci` to restore v8 — an exemplar showing the lockfile is *supposed* to change removes the rationale entirely.
- **opencode, step 7**: reverts `import { globSync }` to the `?? `-chain shim one step after the v8 test failure — same flip.
- **claude_code, step 1955–1956**: chooses "the repository's current manifest version" (v8) as the final verification target. A sibling exemplar redefines "current" as post-bump; the run had already proven `index.js` works under v10 (step 1258 smoke test), so it only needed to *leave v10 installed*.

The strongest evidence the exemplar suffices is gpt55/copilot_cli: the identical model, shown nothing extra, passed the moment it committed to the exemplar-shaped plan (bump + globSync + leave tests unmodified).

## 5. Verdict

**VERDICT: EVIDENCE-WEIGHTING FAILURE (visible-test overfitting + over-literal "source-only" constraint reading) — NOT a knowledge gap.** gpt55 knew the glob v10 idiom (two runs wrote the ground-truth patch verbatim), but three of four runs optimized "visible tests green in-session with minimal footprint," which under this task's mechanics requires *reverting the dependency bump* — the one thing the hidden suite cannot forgive. claude48 uniformly (3/3) treated the bump as the immovable objective and engineered compatibility around the legacy test import; gpt55 did the same in exactly the one run where it passed.

**Intervention classification:**
- **Sibling-PR exemplar: HIGH expected flip** — directly targets the decision at codex step 18/40, opencode step 7/14, claude_code step 1956.
- **Instruction clarification: HIGH** — one sentence ("the manifest/lockfile bump must be applied and the upgraded version left installed; hidden tests run post-upgrade") removes the misreading of "Restrict your changes to the project's source code."
- **Benchmark hardening (alternative): the verifier could install the bumped dependency itself** before `node --test`, which would decouple grading from the agent's `node_modules` hygiene — under that change, codex's and claude_code's `createRequire` bridges would both have passed.
- Secondary observation: the visible suite is unsatisfiable under a plain canonical upgrade (test file's own default import), which actively pushes minimal-footprint agents toward the losing branch; tasks where visible tests can't pass under the target version deserve a flag in the mining pipeline.

**Artifacts:** trial digests at `/tmp/.../scratchpad/digests.txt`; extracted trials in `/fast/hrz/DepBench/conversations/260713-half-pass-analysis/trials/harvard-lil__js-wacz__41__*.json`; task assets under `/fast/hrz/DepBench/harbor_benchmark/tasks_v4/harvard-lil__js-wacz__41/`.

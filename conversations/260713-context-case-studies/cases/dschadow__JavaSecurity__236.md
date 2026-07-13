# Case study: dschadow/JavaSecurity #236 — org.apache.shiro:shiro-core 1.13.0 → 2.0.1 (Maven)

**RQ:** Could an agent have obtained enough context to fix this breaking update correctly *before the PR was created* (2024-05-31T04:29:48Z), from (a) the upstream apache/shiro repository and (b) sibling repos that upgraded earlier?

| | |
|---|---|
| Task PR | https://github.com/dschadow/JavaSecurity/pull/236, created 2024-05-31T04:29:48Z (CUTOFF), merged 2024-06-08 |
| Upstream releases | shiro-root-2.0.0 published **2024-02-28T16:59:01Z**; shiro-root-2.0.1 published **2024-05-31T03:30:56Z** — **59 minutes before the task PR was opened** |
| Harness results | **0/10** harness×model configs solved (Maven is DepBench's easiest ecosystem) |
| Human repair | 2 files: `crypto-shiro/.../hash/SHA512.java`, `crypto-shiro/.../symmetric/AES.java` ("Fixed api usage for major update") |
| Task dir | `/Users/hrz/Documents/GitHub/DependAgent/DepBench/dataset/tasks/dschadow__JavaSecurity__236/` |

**Headline finding:** This task was NOT lost on missing API knowledge. 9/10 agents fixed every compile-breaking change; **8/10 failed on a single hidden *behavioral* assertion** (`expected: <50000> but was: <1000000>` hash iterations). Two frontier agents literally decompiled the new default (`DEFAULT_ITERATIONS = 50_000`) into their context — and then deliberately preserved the old 1,000,000 iterations because **the visible test file in the repo asserted 1,000,000**. The hidden oracle instead encodes the human's choice to *drop* the iteration config and adopt Shiro 2's new default. No upstream doc, upstream test, or sibling PR can disambiguate that choice; only the (forbidden) ground-truth PR does.

---

## Step 1 — Repair facts (from local task files)

Ground truth: `solution/code.patch` (2 files), hidden oracle: `tests/test.patch` (2 test files).

| # | Fact | Kind | Exercised by hidden tests? |
|---|------|------|-----------------------------|
| F1 | `org.apache.shiro.util.ByteSource` → `org.apache.shiro.lang.util.ByteSource` (shiro-lang split, SHIRO-679) | compile-breaking | indirectly (must compile) |
| F2 | `org.apache.shiro.crypto.AesCipherService` → `org.apache.shiro.crypto.cipher.AesCipherService` (crypto split) | compile-breaking | indirectly |
| F3 | `org.apache.shiro.codec.CodecSupport` → `org.apache.shiro.lang.codec.CodecSupport` (appears only in the hidden test file `AESTest.java`) | compile-breaking (test-side) | yes (test imports it) |
| F4 | `DefaultHashService` lost `setPrivateSalt` / `setGeneratePublicSalt` / `setHashIterations`; salt now goes on `HashRequest.Builder.setSalt(...)` (SHIRO-290 redesign) | compile-breaking | yes (`hash.getSalt()` non-null; round-trip verify) |
| F5 | `DefaultHashService` default algorithm is now **argon2**; to stay on SHA-512 the request must call `builder.setAlgorithmName("SHA-512")` | **behavioral** | yes: `assertEquals("SHA-512", hash.getAlgorithmName())` |
| F6 | With algorithm SHA-512 and no explicit iterations, `SimpleHashProvider` applies **DEFAULT_ITERATIONS = 50 000** — and the hidden test flips its assertion from `1000000` to `50000`; the human repair *deletes* `ITERATIONS = 1000000` entirely | **behavioral + oracle-encoded human choice** | yes: `assertEquals(50000, hash.getIterations())` — the killer assertion |
| F7 | `CipherService.decrypt(...)` now returns `ByteSourceBroker` (SHIRO-349); the old `ByteSource.getBytes()` call is replaced by `.getClonedBytes()` | compile-breaking (return type changed) | indirectly (AES round-trip test) |

Hidden test hunks (the oracle):

```diff
-                () -> assertEquals(1000000, hash.getIterations()),
+                () -> assertEquals(50000, hash.getIterations()),
```
(twice in `SHA512Test.java`), plus in `AESTest.java`:
```diff
-import org.apache.shiro.codec.CodecSupport;
+import org.apache.shiro.lang.codec.CodecSupport;
```

Note the trap topology: the *visible* `SHA512Test.java` in the checkout still asserts `1000000`. The hidden "post-upgrade" test asserts `50000`. F6 is therefore not merely behavioral — the repo's own visible state actively points agents to the wrong answer.

## Step 2 — What agents actually did (trajectories + verify logs)

Failure modes across all 10 configs (`verify_logs/*.jsonl.gz`, task `dschadow__JavaSecurity__236`):

| Config | Failure |
|---|---|
| claude48__copilot_cli, claude48__opencode, gemini35flash__copilot_cli, gemini35flash__opencode, gpt55__claude_code, gpt55__codex, gpt55__copilot_cli, gpt55__opencode | **8/10: tests ran; failed `org.opentest4j.AssertionFailedError: expected: <50000> but was: <1000000>`** in `SHA512Test` |
| claude48__claude_code | verifier `install` step died with "The JAVA_HOME environment variable is not defined correctly" (env flake at verify time) — but its in-session code also kept 1,000,000 iterations, so it would have failed F6 anyway |
| gemini35flash__claude_code | never fixed the compile errors (old imports, `setHashIterations` still present) |

**claude48__claude_code** (trajectory steps 44–110): systematically `javap`-decompiled the 2.0.1 jars; found `AesCipherService` in `crypto.cipher` (step 45), noticed "DefaultHashService's API changed drastically — no more `setPrivateSalt`, `setGeneratePublicSalt`, `setHashIterations`" (step 51), decompiled `SimpleHashProvider$Parameters` and printed `DEFAULT_ALGORITHM = "SHA-512"; DEFAULT_ITERATIONS = 50000` (step 68), found `ByteSourceBroker.getClonedBytes()` (step 82). Then at step 59 it anchored: *"The test requires `getIterations()==1000000`"* — and engineered `SimpleHash.iterations = 1000000` via request parameters. Its standalone verification proudly printed `iters=1000000 algo=SHA-512` "exactly as the hidden tests expect" (steps 109–110). Wrong bet.

**gpt55__copilot_cli**: identical arc — decompiled `SimpleHashProvider`, had the constants `PARAMETER_ITERATIONS = "SimpleHash.iterations"` and `Integer 50000` in context, then wrote:

```java
private static final String ITERATIONS_PARAMETER = "SimpleHash.iterations";
private static final int ITERATIONS = 1000000;   // kept, to match the visible test
```

**Gap statement:** agents recovered every API fact (F1–F5, F7) from the jars alone. The loss is F6: a two-valued behavioral decision — *preserve old semantics (1M) vs adopt new library default (50k)* — where the visible repo evidence and the hidden oracle point in opposite directions. All 8 test-reaching agents chose fidelity to the visible test; the oracle encodes the human's simplification.

## Step 3 — Upstream mining at cutoff (pre 2024-05-31)

**Correction to the case brief:** there was **no** official migration guide or "What's New in Shiro 2.0" page at cutoff.

- shiro.apache.org **migration-guide.html**: first Wayback capture **2026-02-11** (`http://web.archive.org/cdx/search/cdx?url=shiro.apache.org/migration-guide.html` → single row `20260211213250`). No `whats-new`-for-2.0 page exists in pre-cutoff CDX either (only the 2012 "whats-new-in-apache-shiro-12" post).
- apache/shiro issue **#1589** "Migration 1.13 -> 2.0.x guide?" opened **2024-07-11** (6 weeks *after* cutoff): "Updating from 1.13 to 2.x on an existing project yields compiler errors. … Is there a guide available?" Maintainer @lprimak, same day: **"Unfortunately, there is no migration guide currently. You can refer to individual issues in the Release Notes"** (https://github.com/apache/shiro/issues/1589).

So the only upstream prose at cutoff was the GitHub release notes; everything deeper lives in upstream code/tests.

Per-fact coverage (all URLs verified, all evidence timestamped pre-cutoff):

| Fact | Upstream docs (prose) | Upstream code/tests |
|---|---|---|
| F1–F3 relocations | 2.0.0 release notes (2024-02-28), one-liner: "**[SHIRO-679] Shiro modules have split packages** by @fpapon in https://github.com/apache/shiro/pull/236" (coincidentally also PR #236) — no new package names given | New coordinates trivially visible in tag `shiro-root-2.0.0` source tree / published jars |
| F4 HashService redesign | Release notes one-liner: "**[SHIRO-290] Implement BCrypt and Argon2** by @bmarwell in https://github.com/apache/shiro/pull/280" | Commit `c6e6ca7c` (2020-12-31) removes the setters; upstream test `crypto/hash/src/test/groovy/.../DefaultHashServiceTest.groovy` @ `shiro-root-2.0.0` line 114 demonstrates the exact target idiom: `hashService.computeHash(new HashRequest.Builder().setSource(source).setSalt(salt).build())` — precisely the shape of the human repair |
| F5 argon2 default | Release notes **headline**: "**Stronger default password hashing algorithms (Argon2 and BCrypt)**" | `DefaultHashService.java` @ `shiro-root-2.0.0` line 62: `this.defaultAlgorithmName = "argon2";` |
| F6 50 000 iterations | **Nowhere in prose.** Not in release notes, not on the site | `SimpleHashProvider.java` @ `shiro-root-2.0.0` lines 214–216: `DEFAULT_ALGORITHM = "SHA-512"; DEFAULT_ITERATIONS = 50_000;` (introduced by SHIRO-290, 2020-12-31) — also recoverable by decompiling the jar (both agents did) |
| F7 ByteSourceBroker | Release notes one-liner: "SHIRO-349 Security: Byte arrays (and other memory) holding sensitive … by @bmarwell in https://github.com/apache/shiro/pull/254" — the return-type change is not spelled out | `ByteSourceBroker.java` introduced by commit `8590adce` (2020-08-20, SHIRO-349); interface has exactly `useBytes(...)` and `getClonedBytes()` |

2.0.1 release notes (published 2024-05-31T03:30:56Z, 59 min pre-cutoff) contain no crypto-related changes — nothing repair-relevant beyond 2.0.0.

**Upstream verdict:** F1–F5, F7 fully knowable pre-cutoff (mostly from code, thinly from release notes). F6's *value* (50000) is knowable from upstream code; F6's *decision* (that the post-upgrade tests would assert the new default instead of the preserved old behavior) is knowable from nothing upstream.

## Step 4 — Sibling mining at cutoff (GHArchive via ClickHouse)

Query (play.clickhouse.com, table `github_events`):

```sql
SELECT repo_name, number, title, min(created_at) AS opened,
       max(merged_at) AS merged_time, max(additions) AS adds, max(deletions) AS dels,
       max(changed_files) AS files, max(commits) AS n_commits
FROM github_events
WHERE event_type = 'PullRequestEvent'
  AND created_at < '2024-05-31 04:29:48'
  AND created_at > '2024-01-01 00:00:00'
  AND (title ILIKE '%shiro-core from 1%to 2%'
    OR title ILIKE '%shiro%from 1.1%to 2.0%'
    OR (title ILIKE '%shiro%' AND title ILIKE '%2.0.0%' AND title ILIKE '%bump%')
    OR (title ILIKE '%shiro%' AND title ILIKE '%2.0.1%'))
GROUP BY repo_name, number, title
ORDER BY opened
```

**Stratum size:** 27 PR rows; after removing forks/dupes and the task repo itself, ~20 distinct repos attempted a 1.x/alpha → 2.0.0 bump in the 93-day window (2.0.0 → cutoff). For **2.0.1** the window was **59 minutes → zero siblings** (query returned none). Merged: ~8. Repair-signal subset (files > 2 or commits > 1, merged): **4** — Graylog2/graylog2-server #18430 (7 files, merged 2024-03-05), apache/jena #2302 (4 files, merged 2024-03-01), flowlogix/flowlogix #692 (4 files, merged 2024-02-29), Waffle/waffle #2278 (2 files, merged 2024-03-16). Same-repo prehistory: Dependabot's earlier `dschadow/JavaSecurity #222` "Bump … 1.13.0 to 2.0.0" (2024-02-29) was closed **unmerged** — the owner sat on the major bump for 3 months.

Sibling diffs vs repair facts (`gh pr diff`, all merged pre-cutoff):

- **flowlogix/flowlogix #692** (merged 2024-02-29, shiro-adjacent maintainer repo) — exact match for **F1 + F2**:
  ```diff
  -import org.apache.shiro.crypto.AesCipherService;
  +import org.apache.shiro.crypto.cipher.AesCipherService;
  ...
  -import org.apache.shiro.util.ByteSource;
  +import org.apache.shiro.lang.util.ByteSource;
  ```
- **Waffle/waffle #2278** (merged 2024-03-16) — exact match for **F1**:
  ```diff
  -import org.apache.shiro.util.ByteSource;
  +import org.apache.shiro.lang.util.ByteSource;
  ```
- **Graylog2/graylog2-server #18430** (merged 2024-03-05) — `org.apache.shiro.util.LifecycleUtils` → `org.apache.shiro.lang.util.LifecycleUtils` (F1-family `shiro-lang` pattern); dodged the codec relocation by migrating `org.apache.shiro.codec.Hex` to commons-codec (F3-adjacent evidence that `org.apache.shiro.codec` died).
- **apache/jena #2302** (merged 2024-03-01) — `org.apache.shiro.io.ResourceUtils` → `org.apache.shiro.lang.io.ResourceUtils` (same relocation family).

**Coverage gap:** no pre-cutoff sibling touches `DefaultHashService`, hash iterations, `setAlgorithmName`, or `ByteSourceBroker`/`getClonedBytes`. `gh search commits "getClonedBytes" --committer-date="<2024-05-31"` returns nothing outside apache/shiro. The crypto-hash surface of this breaking change had **zero crowd coverage**: siblings were all using Shiro for authn/authz, not as a crypto library. F4–F7 are sibling-invisible.

## Step 5 — Verdict

**Knowability matrix (pre-PR):**

| Fact | Upstream prose | Upstream code/tests | Siblings | Nowhere |
|---|---|---|---|---|
| F1 ByteSource → lang.util | hint (SHIRO-679 line) | yes | **yes (exact hunks, 2–4 repos)** | |
| F2 AesCipherService → crypto.cipher | hint | yes | **yes (flowlogix #692 exact)** | |
| F3 CodecSupport → lang.codec | hint | yes | pattern-level (Graylog) | |
| F4 HashService setters gone, salt on builder | hint (SHIRO-290 line) | **yes — upstream test shows exact target idiom** | no | |
| F5 argon2 default / setAlgorithmName("SHA-512") | **yes (release-notes headline)** | yes | no | |
| F6 value 50 000 | no | yes (`DEFAULT_ITERATIONS = 50_000`) | no | |
| F6 **decision** — oracle asserts the new default, not preserved 1M | no | no | no | **yes** |
| F7 ByteSourceBroker.getClonedBytes | hint (SHIRO-349 line) | yes | no | |

**Sibling stratum:** genuinely early-adopter territory — ~20 repos attempted in 93 days, ~8 merged, 4 with code repairs, 0 for the exact 2.0.1 version (released 59 minutes before the PR). Yet the thin crowd still nails the *relocation* facts, because relocations are universal. What it cannot supply is the crypto-hash API surface (this project is a security-examples repo — an outlier consumer of Shiro's crypto API) and, categorically, the downstream maintainer's behavioral preference.

**Contrast upstream vs siblings:** unusually, upstream-side mining dominates here — and even *runtime* mining dominates docs: everything mineable from docs/siblings was also recovered by the agents themselves from the jars in-container. This case is evidence that for API-surface facts, mined context adds little over a competent agent with `javap`; the binding constraint is elsewhere.

**Minimal context artifact that would plausibly have flipped the task:** a *behavioral-defaults delta* note tied to the observed gap, e.g.:

> "Shiro 2.0 `DefaultHashService`: iterations are no longer configurable on the service (SHIRO-290). Upstream's own tests migrate by building requests with only source/salt (+algorithm) and accepting library defaults — SHA-512 ⇒ 50 000 iterations. **Post-upgrade test suites typically re-baseline assertions to the new defaults rather than re-pinning old values via `SimpleHash.iterations`.**"

The first two sentences are mineable (upstream commit + `DefaultHashServiceTest.groovy`). The bolded prior is a *policy heuristic*, not a minable fact for this dependency (zero siblings exercised it) — though it could be learned cross-corpus from other majors where humans re-baseline tests to new defaults. Both failing frontier agents already possessed every factual ingredient; only the prior was missing. An agent that shipped the 3-line human repair (drop `ITERATIONS`, `setSalt(privateSalt)`, `setAlgorithmName("SHA-512")`) — the *simplest* migration — would have passed; both agents did strictly more work to lose.

**Surprises:**
1. The case brief's premise was wrong: no official Shiro 2.0 migration guide existed at cutoff (maintainer-confirmed, issue #1589, 2024-07-11); the guide page first archived 2026-02.
2. shiro-core 2.0.1 was released **59 minutes** before Dependabot opened the task PR — the exact-version sibling window is effectively zero by construction of Dependabot's own latency.
3. Both frontier agents decompiled `DEFAULT_ITERATIONS = 50000` into context and still lost — a pure evidence-weighting failure (visible-test anchoring), not a retrieval failure.
4. The verifier flake (claude48__claude_code's `JAVA_HOME` install failure) masks that config's true failure mode; it too had 1M iterations staged.
5. The repo owner had already rejected (closed unmerged) Dependabot's 2.0.0 bump (#222) three months earlier — same-repo PR history was a mineable hint that this major needed manual code work.

**Facts even perfect mining wouldn't surface:** F6-decision. The hidden oracle encodes an arbitrary post-upgrade human choice (adopt new default rather than preserve documented old behavior — arguably a *semantic regression* the human accepted: 1M → 50k iterations weakens the hash). When an upgrade forces a choice between behavior preservation and default adoption, and the oracle is the human's test edit, no pre-PR context artifact short of the PR itself is guaranteed to disambiguate. For DepBench, this is the signature of its hardest class: **oracle-encoded behavioral preference**, strictly harder than "behavioral change" per se.

---
*Evidence gathered 2026-07-13. Key sources: apache/shiro releases API (`gh api repos/apache/shiro/releases`), tags `shiro-root-2.0.0`/`2.0.1`, issue #1589, Wayback CDX, GHArchive `github_events` on play.clickhouse.com, `gh pr diff` on Graylog2/graylog2-server#18430, apache/jena#2302, flowlogix/flowlogix#692, Waffle/waffle#2278; DepBench trajectories `claude48__claude_code`, `gpt55__copilot_cli` and all 10 verify logs.*

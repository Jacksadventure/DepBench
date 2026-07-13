# Case study: actix/actix #554 — syn 1 → 2 (cargo, proc-macro)

**Task:** DepBench `actix__actix__554` — bump `syn` from 1 to 2 in `actix_derive` (workspace member of actix/actix).
**Task PR created:** 2023-07-23T21:57:15Z (= CUTOFF). Merged 2023-07-24. Author: robjtede (actix maintainer).
**Upstream:** dtolnay/syn 2.0.0, released 2023-03-18T00:00:31Z (https://github.com/dtolnay/syn/releases/tag/2.0.0).
**Benchmark outcome:** solved by **0 / 10** harness×model configurations.
**Local artifacts:** `/Users/hrz/Documents/GitHub/DependAgent/DepBench/dataset/tasks/actix__actix__554/` (instruction.md, solution/code.patch, solution/manifest.patch, tests/test.patch).

---

## Step 1 — The breaking change: repair facts

Ground truth touches 9 files (code.patch) + 2 manifests (manifest.patch). Hidden tests (test.patch) add a `trybuild` compile-test harness (`actix-derive/tests/trybuild.rs` + 5 fixture files) and patch `actix/tests/test_arbiter.rs` (`do_send` → `send(..).await`, a flakiness fix unrelated to syn).

Distinct repair facts:

| # | Fact | Where in ground truth | Exercised by hidden tests? |
|---|------|----------------------|---------------------------|
| F1 | Manifest bump `syn = { version = "2", features = ["full"] }` | actix-derive/Cargo.toml | Yes (everything) |
| F2 | `Attribute::parse_meta()` removed → use `attr.parse_args()` / `parse_args_with` on the attribute's tokens | message.rs `get_attribute_type_multiple` | Yes (`message.rs` fixtures: `#[rtype(result = "Added")]`, `#[rtype(Added)]`) |
| F3 | `syn::AttributeArgs` and `syn::NestedMeta` removed; `MetaList.nested: Punctuated<NestedMeta,_>` → `MetaList.tokens: TokenStream`; re-parse with `Punctuated::<Meta, Token![,]>::parse_terminated` via `syn::parse::Parser` | message.rs — ground truth literally defines `type AttributeArgs = syn::punctuated::Punctuated<syn::Meta, syn::Token![,]>;` | Yes |
| F4 | `MetaNameValue.lit: Lit` → `MetaNameValue.value: Expr`; match `Expr::Lit(ExprLit { lit: Lit::Str(..), .. })` | message.rs (both top-level and nested `result = "TYPE"` arms) | Yes (`#[rtype(result = "Added")]` pass, `#[rtype(result = Added)]` compile-fail) |
| F5 | `Attribute.path` field → `attr.path()` method | message.rs, lib.rs (test macro) | Yes |
| F6 | Compile-fail diagnostics must match `message-fail-bare-rtype.stderr` byte-for-byte: `error: Expect type` spanned on `Added` in `#[rtype(result = Added)]` | error strings preserved from syn-1 code, spans moved to `&nv.value` | Nominally yes, **but moot**: the harness is gated `#[rustversion::stable(1.65)]` and the verify container runs rustc 1.96, so the trybuild cases never execute |
| F7 | Rewrite of `#[actix::main]` / `#[actix::test]`: instead of re-porting the `ItemFn` surgery, delegate to `actix-macros = "0.2"` via a new `actix::__private` re-export module + `macros = ["actix-macros", "actix_derive"]` feature | actix-derive/src/lib.rs, actix/src/lib.rs, actix/Cargo.toml | `rt-main.rs` / `message.rs` fixtures use `#[actix::main]`, but a minimally-fixed syn-1-style port also passes; delegation is stylistic |
| F8 | **Dev-deps `trybuild = "1"` and `rustversion = "1"`** (plus `actix = "0.13"` with default features) in actix-derive/Cargo.toml — required for the *hidden* test target `tests/trybuild.rs` to even compile | solution/manifest.patch only | **Yes — this is the make-or-break fact.** `cargo test -p actix_derive` compiles all test targets; without these two dev-deps the hidden test file fails with E0433 |
| F9 | CI/docs/vscode tweaks | workflows, .vscode | No |

Note the oracle shape: verification runs `cargo test -p actix_derive && cargo test -p actix --test test_arbiter` after re-applying test.patch. Because rustc is 1.96, the only bite the trybuild harness has is *compiling* `tests/trybuild.rs` — i.e. F8. The semantic facts F2–F5 are exercised through the pre-existing `tests/test_macro.rs` and through compilation of the derive crate itself.

## Step 2 — What agents actually did wrong

Verify logs: `/Users/hrz/Documents/GitHub/DependAgent/DepBench/verify_logs/*.jsonl.gz` (grep `actix__actix__554`).

**9 of 10 configs failed with the identical error** — and it is *not* a syn-2 knowledge failure:

```
error[E0433]: cannot find module or crate `rustversion` in this scope
 --> actix-derive/tests/trybuild.rs:4:3
error[E0433]: cannot find module or crate `trybuild` in this scope
 --> actix-derive/tests/trybuild.rs:7:13
error: could not compile `actix_derive` (test "trybuild") due to 2 previous errors
```

The 10th (gpt55__codex) failed earlier: ``no method named `path` found for `&Attribute` ``, ``no field `meta` on type `&Attribute` `` — it wrote syn-2 idioms but never actually bumped the manifest to syn 2 (procedural miss, not knowledge miss).

Trajectory inspection (`trajectories/gpt55__copilot_cli.jsonl.gz`, `claude48__claude_code.jsonl.gz`):

- **gpt55__copilot_cli** produced a *semantically correct* migration: bumped syn to 2, replaced `parse_meta()`/`NestedMeta` with a custom `enum MessageAttr` + `Parse` impl + `attr.parse_args_with(Punctuated::<MessageAttr, Token![,]>::parse_terminated)`, handled `result = "TYPE"`, bare types, and bare string literals, kept the `"Expect type"` error strings. All visible tests passed in-container before submission.
- **claude48__claude_code** likewise: full workspace `cargo test` green in-container ("Every test binary reports 0 failed"), syn bumped to 2, attribute parsing rewritten.

**Gap statement:** agents solved the migration the task ostensibly tests, then were failed by two dev-dependency lines (`trybuild = "1"`, `rustversion = "1"`) that exist only in `solution/manifest.patch` and are needed only by the *hidden* test harness. Under the `v3-no-manifest-preapply` protocol, nothing in the visible repo compels those lines: the build and all visible tests pass without them. This is an oracle/scaffolding gap, not an API-knowledge gap.

## Step 3 — Upstream mining at cutoff (all pre-2023-07-23)

### 3a. syn 2.0.0 release notes (2023-03-18)

https://github.com/dtolnay/syn/releases/tag/2.0.0 — the "Breaking changes → Attributes" section covers F2/F3 explicitly:

> "The syntax tree for `Attribute` has been redesigned. The new API better accommodates attributes which mix structured and unstructured content at different levels of nesting."

> "`AttributeArgs` has been removed. Use `Punctuated<Meta, Token![,]>`."

> "For parsing attribute contents, `parse_meta()` is superseded by a new parsing library called `syn::meta`, and the `parse_nested_meta` method on `Attribute`."

The ground truth's `type AttributeArgs = syn::punctuated::Punctuated<syn::Meta, syn::Token![,]>;` is the release-note sentence transcribed into code.

**Documented:** F1 (trivially), F2, F3.
**NOT spelled out in the release notes:** F4 (`MetaNameValue.lit: Lit` → `value: Expr`), F5 (`attr.path` field → `path()` method), and the `MetaList.nested` → `MetaList.tokens` field change. These fall under the vague "syntax tree … redesigned" sentence and must be recovered from API docs, compiler errors, or exemplar diffs.

### 3b. Upstream-authored exemplar migrations (dtolnay, same day as the release)

All merged 2023-03-18, within an hour of the 2.0.0 release — effectively upstream-blessed migration guides:

- **serde-rs/serde #2405** "Update to syn 2" (merged 2023-03-18T00:23:20Z) — https://github.com/serde-rs/serde/pull/2405. Contains every undocumented fact in one hunk (`serde_derive/src/internals/attr.rs`):

  ```diff
  -pub fn get_serde_meta_items(cx: &Ctxt, attr: &syn::Attribute) -> Result<Vec<syn::NestedMeta>, ()> {
  -    if attr.path != SERDE {
  +pub fn get_serde_meta_items(cx: &Ctxt, attr: &syn::Attribute) -> Result<Vec<Meta>, ()> {
  +    if attr.path() != SERDE {
  ...
  -    match attr.parse_meta() {
  -        Ok(List(meta)) => Ok(meta.nested.into_iter().collect()),
  +    let nested = attr.parse_args_with(Punctuated::<Meta, Token![,]>::parse_terminated);
  ...
  -    if let syn::Lit::Str(lit) = lit {
  +    expr: &syn::Expr,
  +    if let Expr::Lit(expr) = expr {
  +        if let syn::Lit::Str(lit) = &expr.lit {
  ```
  → F2, F3, F4, F5 all present, in the same `NestedMeta`-list-of-metas shape actix uses.

- **dtolnay/thiserror #227** "Update to syn 2" (merged 2023-03-18T00:53:15Z) — `attr.path().is_ident("error")` etc. (F5).
- **dtolnay/async-trait #241** "Update to syn 2" (merged 2023-03-18T01:00:30Z).

### 3c. Fact-by-fact upstream verdict

| Fact | Release notes | dtolnay exemplar PRs |
|------|--------------|---------------------|
| F1 manifest bump | implied | yes |
| F2 parse_meta removal | **quoted verbatim** | yes (serde #2405) |
| F3 AttributeArgs/NestedMeta → Punctuated<Meta, Token![,]> | **quoted verbatim** | yes (serde #2405, exact idiom) |
| F4 MetaNameValue.value: Expr | no | **yes** (serde #2405 `get_lit_str2`) |
| F5 attr.path() method | no | **yes** (serde #2405, thiserror #227) |
| F6 exact stderr | no | no (task-specific; moot under rustc 1.96) |
| F7 delegate to actix-macros | no | no (ecosystem-specific; see siblings) |
| F8 trybuild/rustversion dev-deps | no | no (see siblings) |

## Step 4 — Sibling mining at cutoff (GHArchive via play.clickhouse.com)

`github_events` DESCRIBEd first (PullRequestEvent rows carry `title, merged, merged_at, commits, changed_files, additions, deletions`).

### Stratum size (merged PRs, created 2023-01-01 → cutoff 2023-07-23T21:57:15Z)

Strict "syn … 1 … to … 2" titles:

```sql
SELECT uniqExact(repo_name, number) AS uniq_prs
FROM github_events
WHERE event_type = 'PullRequestEvent' AND action = 'closed' AND merged = 1
  AND created_at < '2023-07-23 21:57:15' AND created_at >= '2023-01-01'
  AND match(title, '(?i)\\bsyn\\b.{0,40}\\b(1|1\\.0(\\.[0-9]+)?)\\b.{0,15}(to|->).{0,3}\\b(2|2\\.0(\\.[0-9]+)?)\\b')
-- → 107 unique PRs / 106 repos, 45 with repair signal
```

Union with verb-based titles ("update/upgrade/migrate/bump/port/switch … syn … 2", excluding syntax/synapse/sync noise):

```sql
SELECT uniqExact(repo_name, number) AS uniq_prs, uniqExact(repo_name) AS uniq_repos,
       uniqExactIf((repo_name, number), commits > 1 OR changed_files > 2) AS repair_signal_prs
FROM github_events
WHERE event_type = 'PullRequestEvent' AND action = 'closed' AND merged = 1
  AND created_at < '2023-07-23 21:57:15' AND created_at >= '2023-01-01'
  AND ( match(title, '(?i)\\bsyn\\b.{0,40}\\b1(\\.0)?(\\.[0-9]+)?\\b.{0,15}(to|->).{0,3}\\b2(\\.0)?(\\.[0-9]+)?\\b')
     OR match(title, '(?i)(upgrade|update|migrate|bump|port|move|switch)[^,;]{0,25}\\bsyn\\b[^,;]{0,15}\\bv?2(\\.0)?(\\.[0-9]+)?\\b') )
  AND NOT match(title, '(?i)syntax|synapse|synchron|rsync')
-- → 717 unique PRs across 323 repos; 266 repair-signal (commits>1 OR changed_files>2)
```

Looser ILIKE families reach ~1,400 PR candidates (with noise). Defensible headline: **~700 merged sibling PRs across ~320 repos in the 4 months before cutoff, ~270 of which contain real code repair beyond the version bump.** Well-known repos in the stratum include solana-labs/solana, libp2p/rust-libp2p, JelteF/derive_more, oxidecomputer/omicron & progenitor, rusterlium/rustler, cucumber-rs/cucumber, sfackler/rust-postgres.

### The killer siblings: same org, same maintainer

```sql
SELECT repo_name, number, title, merged_at FROM github_events
WHERE event_type='PullRequestEvent' AND action='closed' AND merged=1
  AND created_at < '2023-07-23 21:57:15'
  AND repo_name IN ('actix/actix-web','actix/actix-net','actix/actix-extras')
  AND title ILIKE '%syn%2%'
-- actix/actix-net   #481  "update syn to v2"                 merged 2023-04-01 21:21:15
-- actix/actix-web  #3081  "update syn to 2 in web codegen"   merged 2023-07-20 09:49:02
```

Both authored by **robjtede — the same person who authored actix/actix#554 three days after #3081 merged.**

**actix/actix-net #481** (2023-04-01, `actix-macros` crate) contains, verbatim, the idioms that later appear in actix#554's ground truth:

```diff
+use syn::parse::Parser as _;
+type AttributeArgs = syn::punctuated::Punctuated<syn::Meta, syn::Token![,]>;
...
-    let args = syn::parse_macro_input!(args as syn::AttributeArgs);
+    let parser = AttributeArgs::parse_terminated;
+    let args = match parser.parse(args.clone()) {
...
-            syn::NestedMeta::Meta(syn::Meta::NameValue(syn::MetaNameValue {
-                lit: syn::Lit::Str(lit),
+            syn::Meta::NameValue(syn::MetaNameValue {
+                    syn::Expr::Lit(syn::ExprLit {
+                        lit: syn::Lit::Str(lit),
...
+        if attr.path().is_ident("test") {
```

(F2, F3 — including the *exact* `type AttributeArgs = …` alias line — F4, F5.) The PR also touches `actix-macros/tests/trybuild.rs`, and the `actix-macros` manifest (tag `macros-v0.2.4`, commit dated **2023-07-19**, four days pre-cutoff) carries:

```toml
[dev-dependencies]
actix-rt = "2"
futures-util = { version = "0.3.17", default-features = false }
rustversion = "1"
trybuild = "1"
```

— i.e. **F8, the exact two dev-deps whose absence failed 9/10 agent runs**, plus the `#[rustversion::stable(...)]`-gated trybuild convention that the hidden test file follows. actix#554 is, to a first approximation, robjtede transplanting his actix-net/actix-web migration recipe (including the trybuild test convention) into actix/actix.

**actix/actix-web #3081** (2023-07-20) additionally shows F1 (`syn = "2"`), the removal of `use syn::{… AttributeArgs, … NestedMeta …}` in favor of `Punctuated`, and a custom `Parse` impl for route args — plus dev-dep `actix-macros = "0.2.4"` (F7's enabling release).

**Non-actix sibling spot-check — sfackler/rust-postgres #1005** (merged 2023-03-21, dependabot PR fixed up by maintainer commits; `postgres-derive/src/overrides.rs`):

```diff
-use syn::{Attribute, Error, Lit, Meta, NestedMeta};
+use syn::punctuated::Punctuated;
-            let attr = attr.parse_meta()?;
+            let nested = list.parse_args_with(Punctuated::<Meta, Token![,]>::parse_terminated)?;
-                        let value = match &meta.lit {
-                            Lit::Str(s) => s.value(),
+                        let value = match &meta.value {
+                            Expr::Lit(ExprLit { … }) => lit.value(),
```

Same facts (F2/F3/F4), independently converged — the migration recipe was ecosystem-wide months before cutoff.

## Step 5 — Verdict

**Knowability of each repair fact pre-PR:**

- **From upstream release notes alone:** F1, F2, F3 (F3 quoted verbatim, including the replacement type).
- **From upstream-authored migrations (serde #2405, thiserror #227, async-trait #241, all 2023-03-18):** adds F4, F5 — every semantic fact the compiler would otherwise reveal.
- **From siblings (esp. same-maintainer actix-net #481, 2023-04-01; actix-web #3081, 2023-07-20):** all of the above **plus F7 (actix-macros delegation) and F8 (trybuild + rustversion dev-deps and the trybuild test convention)** — the only facts the release notes cannot give.
- **From nowhere:** F6, the byte-exact `.stderr` of the hidden compile-fail test — but it is dead code under the verify toolchain (rustc 1.96 vs the `rustversion::stable(1.65)` gate), so nothing unknowable was actually load-bearing.

**Sibling stratum at cutoff:** ~717 merged PRs / 323 repos (strict-ish title union; 107 with explicit "1→2" titles; ~266 with repair signal). One of the largest sibling strata any Cargo task could hope for, including two same-org, same-author PRs, one merged 3 days before the task PR.

**Minimal context artifact that plausibly flips the task:** the diff of **actix/actix-net #481** (~150 lines) — or even just its `actix-macros/Cargo.toml` + `src/lib.rs` hunks. It supplies the exact code idioms (down to the `type AttributeArgs = Punctuated<Meta, Token![,]>` alias the human reused) *and* the maintainer's proc-macro testing convention (`trybuild = "1"`, `rustversion = "1"` dev-deps + gated `tests/trybuild.rs`), which is precisely the observed 9/10 failure. An agent told "mirror the sibling migration's manifest changes, including dev-dependencies" adds the two lines and passes; the syn 2.0.0 release notes alone do not close that gap because no visible build step exercises it.

**Surprises:**

1. **The hard part was not syn-2 knowledge.** 9/10 agents (mid-2026 models) executed the canonical AttributeArgs/parse_meta migration correctly from priors + compiler errors; all visible tests were green pre-submission. The entire 0/10 outcome reduces to two hidden-oracle dev-dependency lines — a benchmark-protocol artifact (`v3-no-manifest-preapply` withholds solution/manifest.patch, but the hidden tests depend on it) as much as a context-mining problem.
2. Still, mining *would* have fixed it — uniquely via the **same-maintainer sibling**, not upstream docs. This case cleanly separates the three context strata: release notes cover the documented API surface, upstream-authored migrations cover the undocumented field/method renames, and only siblings cover project-convention facts (test scaffolding, actix-macros delegation).
3. The scariest-looking oracle (byte-exact trybuild `.stderr`) is silently disabled by a toolchain-version gate — worth checking in any DepBench Cargo task before declaring a fact "unknowable."
4. The 10th failure (gpt55__codex) is a reminder that under no-manifest-preapply, "bump the manifest" itself is a repair fact; the agent wrote syn-2 code against syn 1.

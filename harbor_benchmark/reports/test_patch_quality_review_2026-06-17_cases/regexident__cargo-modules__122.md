# Test-patch audit — regexident__cargo-modules__122

## 1. Task summary
- Folder: regexident__cargo-modules__122
- Ecosystem: cargo
- Upgrade: rust-analyzer crates `ra_ap_*` 0.0.122 -> 0.0.132 (Cargo.toml pins); chalk 0.83.0 -> 0.84.0 and notify/lsp-types/serde bumps as transitive consequences (bundle header labels it "version 0.83.0 -> 0.84.0")
- Flagged in problematic_prs_review_2026-06-10.md: NO (random control)
- test_cmd: `cargo test --no-fail-fast`

## 2. What is the breaking change?
rust-analyzer 0.0.132 restructured the `ra_ap_project_model::CargoConfig` API: the `no_default_features: bool` / `all_features: bool` / `features: Vec` fields were collapsed into a single `features: CargoFeatures` enum (`All` | `Selected { features, no_default_features }`); `no_sysroot: bool` became `sysroot: Option<RustcSource>`; a new `extra_env` field was added; and `load_workspace` gained an `&extra_env` parameter. Old call sites in `src/generate.rs` no longer compile. Separately, the upgraded crate also changed the order in which graph "uses" edges are emitted.

## 3. What does Δt (test.patch) actually do?
Touches exactly one file: `tests/snapshots/generate_graph__github_issue_79__github_issue_79.snap` (an `insta` snapshot). It (a) drops a blank line in the insta front-matter header (format churn from a newer insta), and (b) reorders two `uses` edges in the expected digraph output — `...::a::d` and `...::a::b::c` `uses` edges swap positions. No new assertions, no new test cases, no fixtures — purely a snapshot update to match the new edge-emission order.

## 4. Does Δt directly exercise the breaking change?
Partially. The snapshot is the expected output of `generate_graph__github_issue_79`, which invokes `src/generate.rs` (the code Δc repairs) through the upgraded `ra_ap_*` stack. On P⊕Δm⊕Δc (Δc applied, Δt NOT applied) the build succeeds but the snapshot test FAILS because the new rust-analyzer emits the `uses` edges in the reordered sequence that the old snapshot does not match — so Δt is necessary and reflects a genuine behavioral consequence of the dependency upgrade. Representative failing diff: the `...::a::d` vs `...::a::b::c` `uses`-edge ordering in `generate_graph__github_issue_79__github_issue_79.snap`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — without Δc the crate does not compile (API break), and even with Δc the test fails without Δt (snapshot reorder from the dep's behavioral change), so both FAIL-without-Δc and PASS-with-Δc⊕Δt hold.

## 6. Δc nature
REAL_SOURCE_REPAIR — `src/generate.rs` adapts to the new `ra_ap_*` 0.0.132 API: `CargoFeatures::All`/`Selected`, `RustcSource::Discover`, `extra_env: FxHashMap`, and the new `load_workspace(workspace, &cargo_config.extra_env, load_config)` signature.

## 7. Soundness concerns / notes
- Δt is snapshot-only. Snapshot updates are a weaker form of witnessing (the oracle is "whatever the new output is" rather than a behavioral assertion), so an agent could in principle satisfy it by producing any code that emits edges in the new order; here that still requires correct use of the new API, so it remains a real (if coarse) witness.
- The insta header blank-line removal is incidental insta-version churn, not a dep-break consequence.
- The primary witness is the compile break (fixed by Δc); the snapshot (Δt) captures a secondary behavioral reorder. Legitimate witnessed task.

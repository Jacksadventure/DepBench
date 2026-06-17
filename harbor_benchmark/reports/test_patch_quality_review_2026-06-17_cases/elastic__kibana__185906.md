# Test-patch audit — elastic__kibana__185906

## 1. Task summary
- Folder: elastic__kibana__185906
- Ecosystem: npm_and_yarn
- Upgrade: @elastic/charts 65.2.0 -> 66.0.3
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `node scripts/jest --runInBand --no-cache src/plugins/chart_expressions/expression_gauge/public/components/gauge_component.test.tsx && node scripts/jest --runInBand --no-cache src/plugins/chart_expressions/expression_partition_vis/public/components/partition_vis_component.test.tsx && node scripts/jest --runInBand --no-cache src/plugins/chart_expressions/expression_xy/public/components/xy_chart.test.tsx`

## 2. What is the breaking change?
@elastic/charts v66 restructured the theme config: the `text: { darkColor, lightColor }` object was flattened to `textDarkColor` / `textLightColor`, and new fields were added (`iconAlign`, `minValueFontSize`, `titlesTextAlign`, `valueFontSize`, `valuesTextAlign`). This changes the serialized chart-theme object captured in jest snapshots, and also changes metric rendering (a `%` suffix appears on goal/gauge values; visible-text extraction differs).

## 3. What does Δt (test.patch) actually do?
Touches 2 files, both **functional** tests (not the unit tests in `test_cmd`):
- `x-pack/test/functional/apps/lens/open_in_lens/agg_based/goal.ts` — appends `%` to five expected `value` strings (e.g. `'65,047,486.03'` -> `'65,047,486.03%'`).
- `x-pack/test/functional/page_objects/lens_page.ts` — switches `getMetricDatum` from `getVisibleText()` to `getAttribute('innerText')` for title/subtitle/extraText/value, with a comment about metric-panel text overflow.

No new test cases; just updated expectations/page-object logic for functional (Selenium) tests that are not executed by the verifier.

## 4. Does Δt directly exercise the breaking change?
No. The `test_cmd` runs three **jest unit tests** (`gauge_component`, `partition_vis_component`, `xy_chart`) whose pass/fail is governed by `__snapshots__/*.snap` files. Δt edits two `x-pack/test/functional/**` files that are not compiled or run by that jest command. So Δt contributes nothing to the verifier outcome. The actual witness is the pre-existing snapshot mismatch under v66, "repaired" by Δc's snapshot regeneration.

## 5. Coverage verdict
TESTS_OTHER_THING — Δt modifies functional/page-object tests that are not executed by `test_cmd`; the real fail/pass is the pre-existing snapshot mismatch in the three jest unit tests, fixed by Δc's snapshot-only updates (no source repair at all).

## 6. Δc nature
SNAPSHOT_ONLY — all 4 changed files are `__snapshots__/*.snap` (`expression_gauge/.../gauge_component.test.tsx.snap`, `expression_partition_vis/.../partition_vis_component.test.tsx.snap`, `expression_xy/.../xy_chart.test.tsx.snap`, `x-pack/.../legacy_uptime/.../donut_chart.test.tsx.snap`). Each hunk replaces the `text: {darkColor, lightColor}` block with the flattened `textDarkColor`/`textLightColor` + new fields. Zero source-code changes.

## 7. Soundness concerns / notes
- Δc is purely snapshot regeneration, which the problematic review correctly flags as "oracle/testdata artifacts, not source repair." The agent is instructed not to touch tests, yet the only "repair" is editing snapshot fixtures — an impossible/ill-posed task for an agent following the rules.
- Δt is dead weight: its files aren't run by `test_cmd`, so it provides no witness and no coverage of the source (there is no source to cover).
- The snapshot mismatch is a real test failure (so formal FAIL/PASS holds), but it witnesses a test-data drift, not a functional source repair — exclude from witnessed main set.
- The functional-test changes in Δt (the `%` suffix and `innerText` switch) describe a genuine v66 metric-rendering change, but because those tests aren't run, that signal is wasted.

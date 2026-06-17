# Test-patch audit — mui__mui-x__18276

## 1. Task summary
- Folder: mui__mui-x__18276
- Ecosystem: npm_and_yarn
- Upgrade: `@mui/monorepo` github:mui/material-ui#8cd3aa58 -> #9b3d36ed (a digest bump of the internal mui/material-ui dep). The material-ui bump renamed/replaced the `stylis-plugin-rtl` package with `@mui/stylis-plugin-rtl`.
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `BROWSERSLIST_IGNORE_OLD_DATA=1 pnpm --dir /app/test/regressions run build`

## 2. What is the breaking change?
The material-ui monorepo bump removes the standalone `stylis-plugin-rtl` package from the workspace and ships `@mui/stylis-plugin-rtl` instead (Δm drops `stylis-plugin-rtl` and adds `@mui/stylis-plugin-rtl` in `docs/package.json`, `test/package.json`, `pnpm-workspace.yaml`, `pnpm-lock.yaml`). Any `import rtlPlugin from 'stylis-plugin-rtl'` no longer resolves.

## 3. What does Δt (test.patch) actually do?
Touches 2 files in `test/regressions/data-grid/` (`DataGridRTLPinnedColumns.js`, `DataGridRTLVirtualization.js`): single-line import rewrite `from 'stylis-plugin-rtl'` -> `from '@mui/stylis-plugin-rtl'`. No new assertions, no new test cases — just retargeting the import so the regression build can resolve the module.

## 4. Does Δt directly exercise the breaking change?
It exercises the *module-resolution* facet of the breaking change for the `test/regressions` workspace: without Δt, `pnpm --dir /app/test/regressions run build` would fail to resolve `stylis-plugin-rtl`. But Δt fully repairs that resolution by itself, so it does not create a failing-without-Δc / passing-with-Δc dynamic. The `test_cmd` builds only `/app/test/regressions`; Δc's edits live in `/app/docs/data/**`, a different workspace that the regression build does not compile.

## 5. Coverage verdict
UNWITNESSED — `test_cmd` builds `/app/test/regressions`, whose only broken imports (`stylis-plugin-rtl`) are entirely fixed by Δt's 2 file edits; Δc's 10 `docs/data/**` example files are in a separate workspace not built by the test, so `TEST(P⊕Δm⊕Δt)` already passes without Δc (no_code_pass).

## 6. Δc nature
DOCS_EXAMPLE_ONLY — all 10 changed files are documentation demos under `docs/data/data-grid/localization/` and `docs/data/date-pickers/{adapters-locale,calendar-systems}/` (`DataGridRTL.{js,tsx}`, `PickersRTL.{js,tsx}`, `AdapterHijri.{js,tsx}`, `AdapterJalali.{js,tsx}`, `AdapterMomentJalali.{js,tsx}`). Each is the identical `stylis-plugin-rtl` -> `@mui/stylis-plugin-rtl` import rewrite. No product source, no test logic.

## 7. Soundness concerns / notes
- Clear no_code_pass: the graded build (test/regressions) is fully repaired by Δt alone; Δc is docs-only and out of the test_cmd's scope, so removing Δc leaves the test passing.
- The breaking change is real (package rename) but trivially fixable by import rewrite, and Δt does that fix in the only files the verifier builds — making Δc redundant for grading.
- Per the problematic review: "Exclude from main benchmark unless docs examples are intentionally in scope." Confirmed unwitnessed for the chosen test_cmd; if the intent were to grade docs-example repair, the test_cmd would need to build `/app/docs` instead.
- Note the manifest also bumps `babel-plugin-transform-import-meta` 2.3.2->2.3.3 and `@mui/monorepo` 7.1.0->7.1.1 transitively, but these are not exercised by either Δc or Δt.

# Test-patch audit — plotly__react-chart-editor__1025

## 1. Task summary
- Folder: plotly__react-chart-editor__1025
- Ecosystem: npm_and_yarn
- Upgrade: prettier 1.19.1 -> 2.0.2
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `npx jest src/__tests__/syntax-test.js --runInBand`

## 2. What is the breaking change?
None behavioral. prettier 2.0 changes formatting defaults (`arrowParens: "always"` -> `(d) =>`; `trailingComma` default "all"; more aggressive method-chain collapsing). The "repair" is reformatting source/tests to the new prettier 2.0 style; no runtime/API behavior changes.

## 3. What does Δt (test.patch) actually do?
Reformats 12 test files to prettier 2.0 style: `src/__tests__/syntax-test.js`, `AnnotationAccordion-test.js`, `TraceAccordion-test.js`, `UnconnectedContainersVisibility-test.js`, `Layout-test.js`, `connectLayoutToPlot-test.js`, `connectTraceToPlot-test.js`, `dereference-test.js`, `maybeAdjustSrc-test.js`, `transpose-test.js`, `unpackPlotProps-test.js`, `walkObject-test.js`. Changes are exclusively cosmetic: arrow-paren insertion (`token =>` -> `(token) =>`), and collapsing multi-line `.find().at(0).simulate('click')` chains onto one line. No assertion is added or changed.

## 4. Does Δt directly exercise the breaking change?
No. The test_cmd runs ONLY `src/__tests__/syntax-test.js`, which scans test files for blacklisted tokens (`fdescribe`, `fit`, `it.only`, etc.). That scan is behavioral, not formatting-dependent: no reformatted test introduces a blacklisted token, so it passes regardless of prettier version or Δc. The other 11 Δt-modified test files are not executed by the test_cmd at all.

## 5. Coverage verdict
UNWITNESSED — TEST(P⊕Δm⊕Δt) already PASS: the only executed test is a blacklist-token scanner that is indifferent to prettier formatting; Δt is pure formatter churn and Δc is source reformatting, neither of which the hidden test can distinguish from P⊕Δm.

## 6. Δc nature
FORMATTER_LINT_CHURN — 81 files reformat (`x =>` -> `(x) =>`, method-chain collapsing) plus `.prettierrc` drops `trailingComma: "es5"` (prettier 2.0 default is "all"). No semantic source change.

## 7. Soundness concerns / notes
Confirmed unwitnessed (matches the problematic-review flag). prettier is a formatter; there is no runtime breaking change to witness. The test_cmd narrows to a single syntax/blacklist test that passes independent of the upgrade, and 11 of the 12 Δt files are not even run. Exclude from the witnessed main set.

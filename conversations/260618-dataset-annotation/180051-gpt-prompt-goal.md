Create a goal: fully validate DepBench `tasks_v4` test-patch quality across all 297 dataset cases, produce per-case analyses and aggregate statistics, then commit and push the report.

You are in `/fast/hrz/DepBench`. First read:
- `AGENTS.md`
- `harbor_benchmark/HARNESS.md`
- `conversations/260618-dataset-annotation/180039-deepseek-complete-audit.md`
- `conversations/2026-06-06-breaking-change-definition/061710-claude-drafted.md`
- `conversations/260610-problematic-pr-review/101101-gpt-complete-pr-review.md`
- `harbor_benchmark/reports/test_patch_quality_review_2026-06-17.md`
- several existing examples under `harbor_benchmark/reports/test_patch_quality_review_2026-06-17_cases/`

Task context:
- 65 cases have already been statically audited.
- Remaining work is the other 232 tasks, then a full 297-case consolidated report.
- Main benchmark eligibility is witnessed Level 1 only:
  `TEST(P⊕Δm⊕Δt)=FAIL` and `TEST(P⊕Δm⊕Δc⊕Δt)=PASS`.
- Latent/no-code-pass, lint-only, test-other, snapshot/docs/test-only/config-only, and inconclusive cases must be reported separately, not included in the main witnessed headline.
- Do not commit `screenlog.0`, `jobs/`, `jobs-fix/`, `trials-fix/`, or other run outputs.

Execution plan:
1. Inspect current branch and git status. Preserve unrelated changes.
2. Generate bundle files for all 297 tasks from:
   - `instruction.md`
   - `environment/patches/manifest.patch`
   - `solution/code.patch`
   - `tests/test.patch`
   - `tests/test_state.py`
   - extracted `test_cmd`
   - `task_summary.json` metadata
3. Reuse the 65 existing case audits as fixed prior work unless clear format normalization is needed.
4. Identify the 232 unaudited folders.
5. Bin-pack them into roughly 30-35 batches of 6-8 tasks, with very large bundles assigned alone.
6. Spawn worker subagents with `multi_agent_v1.spawn_agent`, using `agent_type="worker"`.
   - Each worker owns one disjoint batch.
   - Each worker must write markdown case reports directly to:
     `harbor_benchmark/reports/test_patch_quality_review_2026-06-18_cases/<folder>.md`
   - Workers must not edit task files or shared summary files.
   - Workers must not revert or overwrite other workers' outputs.
7. While workers run, prepare scripts/helpers for parsing finished case reports and producing aggregate statistics.
8. Wait for workers, review outputs, fix missing/invalid reports yourself, and normalize all enum values.

Per-case report format must match:

```markdown
# Test-patch audit — <folder>

## 1. Task summary
- Folder:
- Ecosystem:
- Upgrade:
- Flagged in problematic_prs_review_2026-06-10.md: YES/NO
- test_cmd:

## 2. What is the breaking change?
Concrete 1-3 sentence explanation.

## 3. What does Δt (test.patch) actually do?
Files touched and kind of test change.

## 4. Does Δt directly exercise the breaking change?
Representative assertion/test/import/build failure, or why not.

## 5. Coverage verdict
One of exactly:
- WITNESSES_BREAKING_CHANGE
- UNWITNESSED
- TESTS_OTHER_THING
- INCONCLUSIVE

Include one-sentence justification.

## 6. Δc nature
One of exactly:
- REAL_SOURCE_REPAIR
- FORMATTER_LINT_CHURN
- CONFIG_INFRA_ONLY
- TEST_ONLY
- SNAPSHOT_ONLY
- DOCS_EXAMPLE_ONLY
- MIXED

Include one-sentence justification with key paths.

## 7. Soundness concerns / notes
Case-specific concerns.
```

Classification rules:
- Lint/format-only `test_cmd` is always `TESTS_OTHER_THING`.
- If Δt likely passes on P⊕Δm without Δc, mark `UNWITNESSED`.
- If Δt tests unrelated behavior, drive-by feature work, snapshots, docs, formatter churn, or a misattributed dependency bump, mark `TESTS_OTHER_THING`.
- Compile/build/type/import/runtime errors caused by missing Δc can count as `WITNESSES_BREAKING_CHANGE`.
- Dependency resolution, network, OOM, flaky behavior, timeout, and lint are not valid witnessed breaking-change evidence.
- If static evidence is genuinely insufficient, use `INCONCLUSIVE` and explain exactly what dynamic check would resolve it.

Final deliverables:
- Full case directory: `harbor_benchmark/reports/test_patch_quality_review_2026-06-18_cases/` with 297 markdown files.
- Machine-readable table: `harbor_benchmark/reports/test_patch_quality_review_2026-06-18_cases.csv`.
- Comprehensive report: `harbor_benchmark/reports/test_patch_quality_review_2026-06-18_full297.md`.

The final report must include:
- Executive summary.
- Full 297 verdict counts and percentages.
- Counts by ecosystem.
- Counts by Δc nature.
- Flagged vs non-flagged comparison.
- Main witnessed benchmark size after excluding latent/test-other/inconclusive cases.
- List of cases to quarantine.
- List of high-priority manual/dynamic revalidation cases.
- Methodology and limitations.
- Comparison against the earlier 65-case smoke audit.
- Implications for paper numbers and benchmark reporting.

Before committing:
- Run a parser/check script to verify exactly 297 case files exist and every file has valid enum values.
- Run `git status --short`.
- Confirm no run outputs are staged.
- Stage only reports, helper scripts if created, and a new handoff note under `conversations/260618-dataset-annotation/`.
- Commit with a clear message, e.g. `Audit full DepBench test-patch quality`.
- Push to the current branch.
- Final response should include commit hash, pushed branch, headline statistics, and any unresolved risks.

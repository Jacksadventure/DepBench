# Analysis tables

This directory contains aggregate analysis tables derived from the release artifacts.

- `ecosystem_results.csv`: pass/fail/no-reward counts and rates by configuration and ecosystem.
- `coverage.csv`: trajectory and verifier-log coverage by configuration.
- `trajectory_scan_summary.csv`: aggregate trajectory-scan counts by configuration.
- `trajectory_scan_by_source.csv`: the same scan split by original and rerun
  outcome source.
- `trajectory_scan_detail.csv`: per-trial trajectory-scan features.
- `original_full_run_trajectory_scan_summary.csv`: frozen original full-run
  behavior counts retained as rerun provenance.
- `trajectory_recovery_failure_classification_203.jsonl`: root-cause labels
  for all 142 non-pass trajectory-recovery reruns.
- `trajectory_recovery_failure_category_counts_203.csv`: recovery non-pass
  category counts by configuration.
- `trajectory_recovery_failure_summary_203.json`: category, confidence, and
  visible-then-hidden summary for the recovery annotations.
- `repository_metadata.{csv,json}`: metadata for the 159 unique GitHub
  repositories represented by the release, including canonical URLs, licenses,
  primary languages, archive status, and task mappings.
- `task_repository_metadata.csv`: the same repository metadata expanded to the
  203 task rows.
- `runtime_exception_rerun_summary_203.json`: numeric summary after applying
  the final runtime and trajectory-recovery reruns.
- `paper_numbers_203.json`: result-derived numbers used to synchronize the two
  paper worktrees.
- `test_contract_repair_decisions_2026-07-14.{md,csv}`: decisions and rationale
  for the 37 reviewed semantic/mixed test contracts.

All aggregate tables are generated from the 203-task filtered
`trajectories/`, `verify_logs/`, and `results/` files in this branch. The
37-row contract decision report is retained as audit provenance for both kept
and removed tasks.

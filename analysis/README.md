# Analysis tables

This directory contains aggregate analysis tables derived from the release artifacts.

- `ecosystem_results.csv`: pass/fail/no-reward counts and rates by configuration and ecosystem.
- `coverage.csv`: trajectory and verifier-log coverage by configuration.
- `trajectory_scan_summary.csv`: aggregate trajectory-scan counts by configuration.
- `trajectory_scan_detail.csv`: per-trial trajectory-scan features.
- `repository_metadata.{csv,json}`: metadata for the 159 unique GitHub
  repositories represented by the release, including canonical URLs, licenses,
  primary languages, archive status, and task mappings.
- `task_repository_metadata.csv`: the same repository metadata expanded to the
  203 task rows.
- `runtime_exception_rerun_summary_203.json`: numeric summary after applying the
  targeted runtime-exception reruns.
- `test_contract_repair_decisions_2026-07-14.{md,csv}`: decisions and rationale
  for the 37 reviewed semantic/mixed test contracts.

All aggregate tables are generated from the 203-task filtered
`trajectories/`, `verify_logs/`, and `results/` files in this branch. The
37-row contract decision report is retained as audit provenance for both kept
and removed tasks.

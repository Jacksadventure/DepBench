# Analysis tables

This directory contains aggregate analysis tables derived from the release artifacts.

- `ecosystem_results.csv`: pass/fail/no-reward counts and rates by configuration and ecosystem.
- `coverage.csv`: trajectory and verifier-log coverage by configuration.
- `trajectory_scan_summary.csv`: aggregate trajectory-scan counts by configuration.
- `trajectory_scan_detail.csv`: per-trial trajectory-scan features.
- `test_contract_repair_decisions_2026-07-14.{md,csv}`: decisions and rationale
  for the 37 reviewed semantic/mixed test contracts.

All tables are generated from the `trajectories/`, `verify_logs/`, and `results/` files in this branch.

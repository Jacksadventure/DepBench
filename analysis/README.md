# Benchmark audits

This directory contains task-level metadata and static audits for the
201-task benchmark distributed from `main`.

- `repository_metadata.{csv,json}`: canonical URLs, licenses, primary
  languages, archive status, and task mappings for the 157 source repositories.
- `task_repository_metadata.csv`: repository metadata expanded to all 201 task
  rows.
- `dependency_metadata_corrections_2026-07-26.{md,csv}`: audited dependency
  identity and version corrections.
- `bot_pr_dependency_audit_2026-07-26.{md,csv}`: cross-checks against the
  associated Dependabot or Renovate pull requests.
- `instruction_bump_audit_201.{md,csv,json}`: per-task verification of the Bump
  instruction against the packaged manifest and upstream pull request.
- `task_change_mechanism_*`: direct and indirect dependency-upgrade mechanism
  classifications and taxonomy.
- `test_patch_behavior_classification_201.csv`: static held-out test-patch
  behavior labels and size metrics.
- `test_contract_repair_decisions_2026-07-14.{md,csv}`: decisions and rationale
  for the 36 reviewed test contracts retained in main metadata.
- `secret_scan_review_2026-07-23.csv`: reviewed private-key fixture headers in
  the downloadable benchmark tasks.

Run results, trajectories, verifier logs, failure annotations, and Harbor job
archives are intentionally not distributed from the `main` branch.

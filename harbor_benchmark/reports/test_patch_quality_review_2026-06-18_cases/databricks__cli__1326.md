# Test-patch audit - databricks__cli__1326

## 1. Task summary
- Folder: databricks__cli__1326
- Ecosystem: go_modules
- Upgrade: github.com/databricks/databricks-sdk-go 0.36.0 -> 0.37.0
- test_cmd: `go test -count=1 -short ./bundle/deploy/metadata/... ./bundle/python/... ./bundle/config/mutator/... ./bundle/deploy/terraform/... ./bundle/deploy/terraform/tfdyn/... ./cmd/bundle/generate/...`

## 2. What is the breaking change?
The SDK update changes generated Databricks Go API types. Examples visible in the repair are `jobs.JobSettingsEditModeUiLocked` becoming `jobs.JobEditModeUiLocked`, and `JobCluster.NewCluster` changing from pointer-style test/source usage to value-style `compute.ClusterSpec` usage.

## 3. What does Delta t (test.patch) actually do?
The hidden test patch updates Go tests in bundle metadata, Terraform conversion, Python warning, merge-job-cluster, and bundle generation packages to use the new SDK enum/type shapes. Representative changes replace `&compute.ClusterSpec{...}` with `compute.ClusterSpec{...}` and update assertions from `jobs.JobSettingsEditModeUiLocked` to `jobs.JobEditModeUiLocked`.

## 4. Does Delta t directly exercise the breaking change?
Yes. The patched tests compile and run the same packages where the oracle source repair updates old SDK symbols and struct-field assumptions. Without Delta c, the upgraded SDK leaves production code and test fixtures referring to removed/changed API shapes; with Delta c, those compile and the targeted Go tests can run.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the evidence is a compile/API witness against the upgraded SDK, not dependency resolution, lint, network, OOM, timeout, or flakiness.

## 6. Delta c nature
MIXED - real Go source repair plus generated command/schema/doc metadata and a `.codegen/_openapi_sha` update.

## 7. Soundness concerns / notes
- The witness is primarily an SDK compile-surface witness, which is acceptable for compiled languages.
- Non-source generated/doc churn is present in Delta c, so the task is not a pure source-only repair.

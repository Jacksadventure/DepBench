# Test-patch audit — hashicorp__aws-sdk-go-base__796

## 1. Task summary
- Folder: hashicorp__aws-sdk-go-base__796
- Ecosystem: go_modules
- Upgrade: github.com/aws/aws-sdk-go-v2 1.22.2 -> 1.23.0 (plus config/credentials/imds/dynamodb/iam/s3/sqs/sso/sts/smithy-go minors)
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test ./...`

## 2. What is the breaking change?
aws-sdk-go-v2 1.23.0 changed the S3 input struct field types `s3types.Delete.Quiet` from `bool` → `*bool` and `s3.UploadPartInput.PartNumber` from `int32` → `*int32`, so `int(v.PartNumber)` and `fmt.Fprintf("…%t", d.Quiet)` no longer compile/produce correct output, and `awsmiddleware.GetSigningRegion` became deprecated (staticcheck).

## 3. What does Δt (test.patch) actually do?
- `aws_config_test.go`: refactors `TestAssumeRoleWithWebIdentity` to replace the `ValidateDiags test.DiagsValidator` field with `ExpectedDiags diag.Diagnostics` and compares via `cmp.Diff(diags, testCase.ExpectedDiags)`; drops the `ExpectWarningDiagValidator(...)` wrappers in favor of literal `diag.Diagnostics` slices.
- `s3attributes_test.go`: updates fixtures for the new pointer-typed fields — `Quiet: false`→`aws.Bool(false)`, `Quiet: true`→`aws.Bool(true)`, `PartNumber: 1234`→`aws.Int32(1234)` in `TestS3AttributesDeleteObjectsInput`, `TestS3AttributesUploadPartInput`, and `TestS3AttributesSerializeDeleteShorthand`.

## 4. Does Δt directly exercise the breaking change?
Yes. `TestS3AttributesUploadPartInput` builds `UploadPartInput{ PartNumber: aws.Int32(1234) }` and exercises `s3AttributeSetter`, which on P⊕Δm calls `int(v.PartNumber)` where `v.PartNumber` is now `*int32` — that does not compile (`cannot convert *int32 to int`), so `go test ./...` FAILS at build time; with Δc (`aws.ToInt32(v.PartNumber)`) it compiles and passes. `TestS3AttributesSerializeDeleteShorthand` uses `Quiet: aws.Bool(true/false)` fixtures and asserts `expected: "…,Quiet=true"`/`"…,Quiet=false"`; on P⊕Δm `fmt.Fprintf("Quiet=%t", d.Quiet)` with `*bool` yields `%!t(*bool=0x…)`, mismatching the snapshot → FAIL; with Δc (`aws.ToBool(d.Quiet)`) it prints `true`/`false` → PASS.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — `TestS3AttributesUploadPartInput` (compile-level: `int(*int32)`) and `TestS3AttributesSerializeDeleteShorthand` (behavior: `%t` on `*bool`) fail on P⊕Δm and pass on P⊕Δm⊕Δc via Δc's `aws.ToInt32`/`aws.ToBool` dereferences.

## 6. Δc nature
MIXED — real source repairs in `logger.go` (`semconv.AWSS3PartNumber(int(aws.ToInt32(v.PartNumber)))`, `aws.ToBool(d.Quiet)`, `//nolint:staticcheck` on the deprecated `GetSigningRegion`) and `credentials.go` (`awsConfig.Credentials = nil` before `stsClient` to drop IMDS creds), plus a minor `GNUmakefile` build-infra change introducing a `TIMEOUT ?= 30s` variable.

## 7. Soundness concerns / notes
- The `aws_config_test.go` Δt is largely a test-infra refactoring (validator function → `cmp.Diff` against `ExpectedDiags`), only loosely coupled to the `credentials.go` `awsConfig.Credentials = nil` change; the load-bearing witnesses are the two `s3attributes_test.go` cases.
- The `GNUmakefile` `TIMEOUT` edit is unrelated infra churn, not a dependency repair.
- Solid witness overall: the S3 pointer-typed field changes are a genuine compile + behavior break from aws-sdk-go-v2 1.23.0.

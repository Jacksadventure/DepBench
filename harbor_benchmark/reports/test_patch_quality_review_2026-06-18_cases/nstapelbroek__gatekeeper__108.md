# Test-patch audit - nstapelbroek__gatekeeper__108

## 1. Task summary
- Folder: nstapelbroek__gatekeeper__108
- Ecosystem: go_modules
- Upgrade: github.com/aws/aws-sdk-go-v2 0.24.0 -> 0.29.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test ./...`

## 2. What is the breaking change?
The AWS SDK v2 Go API changed package structure and EC2 operation shapes. Static credentials/config loading moved from `aws/external` and `aws.NewStaticCredentialsProvider` to `config` and `credentials`; EC2 model types moved under `service/ec2/types`; operations changed from request builders plus `Send` to direct client methods; several numeric fields became `int32` pointers and slices became pointer slices.

## 3. What does test.patch actually do?
The hidden tests update AWS test fixtures and type assertions: `client_test.go` no longer inspects the old credentials provider directly and asserts an `*ec2.Client`; `dto_test.go` migrates ACL fixtures from `ec2.NetworkAclEntry` / `ec2.PortRange` to `types.NetworkAclEntry` / `types.PortRange`, pointer slices, and `int32` rule numbers.

## 4. Does test.patch directly exercise the breaking change?
Yes. The patched tests compile against the AWS SDK 0.29 type layout. Without Delta_c, production code still imports removed packages and uses old request/type APIs, causing Go compile failures.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the test patch directly witnesses the AWS SDK API migration required by the dependency bump.

## 6. Delta_c nature
REAL_SOURCE_REPAIR - production AWS adapters are migrated to the new SDK config, operation, and EC2 type APIs.

## 7. Soundness concerns / notes
The client credential assertion was weakened, but the broader `go test ./...` compile surface still directly exercises the SDK migration in production code.

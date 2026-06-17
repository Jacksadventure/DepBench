# Test-patch audit — spiffe__spire__4184

## 1. Task summary
- Folder: spiffe__spire__4184
- Ecosystem: go_modules
- Upgrade: github.com/hashicorp/go-plugin 1.4.6 -> 1.4.8 (manifest actually moves to 1.4.10 and also bumps hashicorp/hcl to `v1.0.1-vault-5`)
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test -count=1 ./pkg/common/catalog/... ./pkg/agent/plugin/workloadattestor/docker/...`

## 2. What is the breaking change?
The witnessed source repair is primarily the HashiCorp HCL change from `,unusedKeys` into `,unusedKeyPositions`, requiring map-based unknown-key handling and deterministic sorting before reporting. The test patch also accounts for a changed go-plugin bad-plugin error message.

## 3. What does Δt (test.patch) actually do?
- `docker_test.go`: fixes the test case name typo from "unknow configuration" to "unknown configuration".
- `catalog_test.go`: updates the expected bad external-plugin error from the old short go-plugin message to the newer multi-line diagnostic, and relaxes the assertion from exact equality to `ErrorContains`.
- `catalog_test.go`: minor gofmt collapse of `coreConfig`.

## 4. Does Δt directly exercise the breaking change?
Partially. The catalog test change directly tracks the go-plugin diagnostic change. The docker package still relies on existing unknown-config assertions, which fail unless Δc migrates the production HCL structs to `UnusedKeyPositions` and reports sorted unknown keys.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — under the upgraded HashiCorp dependency set, P⊕Δm⊕Δt fails in the executed packages without the HCL unknown-key migration and passes with Δc; Δt also updates the go-plugin error oracle.

## 6. Δc nature
REAL_SOURCE_REPAIR — source structs and validation in agent/server config, telemetry, health, GCP secret manager, and Docker workload attestor migrate from `UnusedKeys []string` to `UnusedKeyPositions map[string][]token.Pos`, with sorted error reporting.

## 7. Soundness concerns / notes
- The named library in the batch is go-plugin, but much of Δc repairs the simultaneously bumped HCL fork.
- Δt is mostly expected-error maintenance; the strongest witness comes from existing tests run after the dependency bump.

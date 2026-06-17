# Test-patch audit — hetznercloud__cli__940

## 1. Task summary
- Folder: hetznercloud__cli__940
- Ecosystem: go_modules
- Upgrade: github.com/hetznercloud/hcloud-go/v2 2.17.0 -> 2.17.1
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `export PATH=/usr/local/go/bin:$PATH && go test ./... -count=1 -timeout=300s`

## 2. What is the breaking change?
hcloud-go v2.17.1 added a `LoadBalancers []*hcloud.LoadBalancer` field to the `hcloud.Network` struct. Because the CLI serializes `Network` to JSON, the new field now appears in command output (e.g. `hcloud network create -o=json`) as `"load_balancers": [...]`.

## 3. What does Δt (test.patch) actually do?
A single one-line addition to `test/e2e/network_test.go`: inserts `"load_balancers": []` into the expected JSON for the `TestNetwork` e2e test (between the `subnets` and `routes` keys).

## 4. Does Δt directly exercise the breaking change?
It targets the right field, but not in a way that requires Δc. The e2e test expects `"load_balancers": []` in the network JSON output. That field is emitted automatically once the upgraded hcloud-go struct (with the new `LoadBalancers` field) is serialized — i.e. it appears on P⊕Δm with no source change at all. Δc does not touch any production CLI code, so it cannot be the cause of a fail→pass transition for this e2e test.

## 5. Coverage verdict
UNWITNESSED — Δc contains no production source change (only a unit test and a testdata fixture), so it cannot turn an e2e failure into a pass; the e2e `load_balancers: []` expectation is satisfied by the manifest upgrade alone (TEST(P⊕Δm⊕Δt)=PASS).

## 6. Δc nature
TEST_ONLY — Δc modifies `internal/cmd/network/create_test.go` (a Go unit test, adding a `LoadBalancers` field to a mocked `hcloud.Network`) and `internal/cmd/network/testdata/create_response.json` (the fixture, adding `load_balancers:[4,5,6]`). No production CLI source files are touched — and the task constraints explicitly forbid the agent from modifying test files, so Δc is not even reproducible by an agent.

## 7. Soundness concerns / notes
Doubly unsound. (1) Δc is entirely in test code/testdata, which the agent is instructed not to edit, so the oracle is unreachable by construction. (2) The verifier applies only Δt (the e2e `network_test.go` change), not Δc's unit-test/fixture changes, and the e2e expectation passes purely from the struct-field addition brought by the dependency bump. Matches the 2026-06-10 review: "The patch is test code/testdata, not production CLI behavior."

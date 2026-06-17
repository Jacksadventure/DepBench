# Test-patch audit — cloudflare__terraform-provider-cloudflare__1563

## 1. Task summary
- Folder: cloudflare__terraform-provider-cloudflare__1563
- Ecosystem: go_modules
- Upgrade: `github.com/cloudflare/cloudflare-go` 0.36.0 -> 0.37.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test ./cloudflare/...`

## 2. What is the breaking change?
`cloudflare-go` 0.37.0 changed several account-scoped APIs to take `accountID` explicitly instead of relying on `client.AccountID`. Provider resources for BYO IP prefixes, IP lists, magic firewall rulesets, static routes, and worker cron triggers still called the old method signatures or set `client.AccountID`.

## 3. What does Δt (test.patch) actually do?
It updates acceptance-test helper calls to pass `CLOUDFLARE_ACCOUNT_ID` into the new cloudflare-go API signatures, renames several acceptance tests to the provider’s underscore naming convention, and adds `account_id` to the worker cron trigger test config.

## 4. Does Δt directly exercise the breaking change?
Mostly at compile time. The acceptance tests are normally skipped without Cloudflare credentials, but Go still compiles the package and test files. With the upgraded dependency, old source/test calls to `GetIPList`, `GetMagicFirewallRuleset`, `GetMagicTransitStaticRoute`, worker cron methods, and related APIs no longer match the new signatures. Δc fixes production resources by reading `account_id` from Terraform schema and passing it explicitly.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the cloudflare-go signature change is a deterministic compile break under `go test ./cloudflare/...`, and Δc repairs the provider’s source calls.

## 6. Δc nature
MIXED — real provider source repairs across multiple resources and schemas, plus an incidental `.changelog/1563.txt` release-note file.

## 7. Soundness concerns / notes
- Runtime acceptance behavior is not exercised in the verifier without external credentials; the witness is compile/type checking.
- The hidden tests still use real upgraded API signatures, so the compile witness is legitimate.

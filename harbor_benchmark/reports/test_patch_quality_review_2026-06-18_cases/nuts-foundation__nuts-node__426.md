# Test-patch audit — nuts-foundation__nuts-node__426

## 1. Task summary
- Folder: nuts-foundation__nuts-node__426
- Ecosystem: go_modules
- Upgrade: github.com/lestrrat-go/jwx 1.1.2 -> 1.2.6
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test -count=1 ./crypto/... ./vcr/... ./network/p2p/... ./vdr/types/...`

## 2. What is the breaking change?
jwx 1.2.x changed JWS/JWT signing and detached-payload handling. The repair switches JWT signing headers from `jws.WithHeaders` to `jwt.WithHeaders`, changes detached JWS challenge construction to use the raw payload segment, and base64url-encodes the generated credential/revocation challenge bytes before signing.

## 3. What does Δt (test.patch) actually do?
- Replaces VCR test keys, DID identifiers, public JWK, credential JSON, and revocation JSON with fixtures signed using the new challenge construction.
- Updates trust tests to expect the new DID.
- Includes minor formatting/no-newline churn in unrelated Go tests.

## 4. Does Δt directly exercise the breaking change?
Yes. The VCR tests parse and verify the updated credential/revocation fixtures. On P⊕Δm, the verifier still constructs verification challenges with the old double/base64 encoding behavior, so signatures generated for the new jwx-compatible challenge fail verification. With Δc, verification uses the raw payload segment and the updated challenge generation, so the fixtures pass.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden VCR fixture updates exercise the JWS signing/verification compatibility change introduced by the jwx upgrade.

## 6. Δc nature
REAL_SOURCE_REPAIR — production code in `crypto/jwx.go` and `vcr/vcr.go` adapts to the new jwx APIs and detached JWS signing semantics. The patch also updates a test helper key ID in `vcr/test.go`.

## 7. Soundness concerns / notes
- Δt includes some formatter/no-newline churn, but the decisive evidence is the regenerated signed VC/revocation fixtures.
- The verifier also runs packages unrelated to jwx (`network/p2p`, `vdr/types`), but those do not drive the verdict.

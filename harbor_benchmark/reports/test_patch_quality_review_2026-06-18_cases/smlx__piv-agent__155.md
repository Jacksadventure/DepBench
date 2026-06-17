# Test-patch audit — smlx__piv-agent__155

## 1. Task summary
- Folder: smlx__piv-agent__155
- Ecosystem: go_modules
- Upgrade: golang.org/x/crypto 0.0.0-20200820211705-5c72a883971a -> 0.7.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test ./...`

## 2. What is the breaking change?
The x/crypto upgrade removes/moves APIs used by the project (`ssh/terminal` -> `x/term`) and the OpenPGP/ECDSA path is migrated to the ProtonMail go-crypto fork with different ECDSA key wrapper types.

## 3. What does Δt (test.patch) actually do?
It updates tests to import ProtonMail `openpgp`, `armor`, `ecdsa`, and `packet`; adjusts mock signer key types; adds a `gpg.ECDSAPublicKey` test export helper; and converts keygrip tests from ProtonMail ECDSA public keys into stdlib ECDSA keys before calling `KeygripECDSA`.

## 4. Does Δt directly exercise the breaking change?
Yes. Without Δc, the source still imports old x/crypto OpenPGP/terminal packages and lacks the `ecdsaPublicKey` conversion helper exported for tests, so the upgraded package fails at compile time. With Δc, the source uses `x/term`, ProtonMail OpenPGP packages, and conversion helpers that the hidden tests call.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the Go test suite fails to compile/run on P⊕Δm⊕Δt and passes after Δc's x/crypto/OpenPGP migration.

## 6. Δc nature
REAL_SOURCE_REPAIR — migrates command and internal packages from removed/moved x/crypto APIs to `x/term` and ProtonMail go-crypto, including ECDSA public/private key conversion helpers.

## 7. Soundness concerns / notes
- Δt adds a test-only export shim for an unexported helper, so one witness is existence of that helper.
- The broad `go test ./...` command also catches compile breaks in command packages not directly asserted by the changed test hunks.

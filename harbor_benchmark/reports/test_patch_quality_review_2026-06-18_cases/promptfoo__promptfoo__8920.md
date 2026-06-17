# Test-patch audit — promptfoo__promptfoo__8920

## 1. Task summary
- Folder: promptfoo__promptfoo__8920
- Ecosystem: npm_and_yarn
- Upgrade: @fal-ai/client 1.9.6 -> 1.10.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx vitest run test/providers/fal.test.ts`

## 2. What is the breaking change?
The repair introduces support for passing SDK client options, especially `client.proxyUrl`, to `@fal-ai/client` while keeping those values out of the model endpoint input. The bundle does not show a removed API or compile-time incompatibility from `@fal-ai/client` itself; the change is framed as a new provider behavior for proxy routing.

## 3. What does Δt (test.patch) actually do?
Adds one Vitest case to `test/providers/fal.test.ts` that constructs a Fal provider with `config.client.proxyUrl`, calls `callApi`, and asserts:
- `fal.config` receives `credentials` plus the provider-level `proxyUrl`.
- `fal.subscribe` receives model input containing `prompt`, `seed`, and `guidance_scale`, but not the `client` block.

## 4. Does Δt directly exercise the breaking change?
Not convincingly. The test uses mocks and checks newly introduced promptfoo provider semantics. It would fail on the old source because old promptfoo sent all config except `apiKey` as model input and never forwarded `client` options to `fal.config`, but the failure is a new feature/behavior assertion rather than direct evidence of an upstream API break.

## 5. Coverage verdict
TESTS_OTHER_THING — Δt tests promptfoo's new `client.proxyUrl` handling and config filtering, not a demonstrated break caused by the dependency bump.

## 6. Δc nature
MIXED — Δc contains real source changes in `src/providers/fal.ts`, plus documentation/example updates describing the new client option.

## 7. Soundness concerns / notes
- If external PR context proves `@fal-ai/client` 1.10 made this option mandatory for an existing supported workflow, the verdict could be revisited. The bundled evidence alone reads as an added provider capability.
- The test is deterministic and useful, but it does not establish the locked `TEST(P⊕Δm⊕Δt)=FAIL` as a dependency-breaking-change witness.

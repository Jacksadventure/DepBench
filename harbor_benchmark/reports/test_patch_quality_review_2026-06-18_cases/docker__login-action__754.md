# Test-patch audit — docker__login-action__754

## 1. Task summary
- Folder: docker__login-action__754
- Ecosystem: npm_and_yarn
- Upgrade: @docker/actions-toolkit 0.24.0 -> 0.35.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `yarn test`

## 2. What is the breaking change?
`@docker/actions-toolkit` moved Docker command execution behind `@docker/actions-toolkit/lib/docker/docker`'s `Docker.getExecOutput(args, opts)` helper, replacing the prior `Exec.getExecOutput('docker', args, opts)` usage from `@docker/actions-toolkit/lib/exec`. The project source must update both the import and the call signature for `loginStandard`, `logout`, and ECR login.

## 3. What does Δt (test.patch) actually do?
Touches `__tests__/docker.test.ts` only. The test import changes from `Exec` to `Docker`, the spies target `Docker.getExecOutput`, and the expected calls drop the leading `'docker'` executable argument. The patch also checks `toHaveBeenCalledTimes(1)` and clears the injected `env` option before asserting the remaining options.

## 4. Does Δt directly exercise the breaking change?
Yes. The patched tests spy on `Docker.getExecOutput` and expect calls like `Docker.getExecOutput(['login', '--password-stdin', '--username', username, registry], {...})`; P⊕Δm source still imports/calls `Exec.getExecOutput('docker', ...)`, so the spy is not called with the new API (or the old import may fail under the upgraded package). Δc updates `src/docker.ts` and regenerated `dist/` to use `Docker.getExecOutput(args, opts)`, making the hidden tests pass.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — `yarn test` runs the Docker login/logout Jest tests, and Δt directly checks the new toolkit API that P⊕Δm does not use but P⊕Δm⊕Δc does.

## 6. Δc nature
REAL_SOURCE_REPAIR — `src/docker.ts` is adapted to the new `@docker/actions-toolkit` Docker helper and call signature; `dist/index.js`, `dist/index.js.map`, and `dist/licenses.txt` are regenerated bundled action artifacts for the same source repair.

## 7. Soundness concerns / notes
- The verifier runs the whole `yarn test` suite, but the hidden Δt witness is concentrated in `__tests__/docker.test.ts`.
- The large bundle size is almost entirely generated `dist/index.js.map`; the semantic repair is the small `src/docker.ts` API migration plus generated distribution output.

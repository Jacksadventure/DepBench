# Test-patch audit — cryostatio__cryostat-legacy__1880

## 1. Task summary
- Folder: cryostatio__cryostat-legacy__1880
- Ecosystem: maven
- Upgrade: io.cryostat:cryostat-core 2.28.0 -> 2.29.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `<could not extract>`; `test_state.py` runs Maven `test-compile` first, then a selected Surefire test list.

## 2. What is the breaking change?
`cryostat-core` 2.29.0 removes or stops exposing the old `io.cryostat.core.log.Logger` singleton API used throughout `cryostat-legacy`. The production repair replaces imports of `io.cryostat.core.log.Logger` / `Logger.INSTANCE` with SLF4J `Logger` + `LoggerFactory`, removes logger injection from many Dagger providers and constructors, and adjusts exception logging calls to SLF4J's message-plus-throwable style.

## 3. What does Δt (test.patch) actually do?
- Updates 114 test files to match the no-`core.log.Logger` production API: removes `io.cryostat.core.log.Logger` imports and `@Mock Logger logger` fields, changes `MainModule.provideGson(logger)` to `provideGson()`, and calls constructors such as `CredentialsManager(...)`, `MessagingServer(...)`, `BasicAuthManager(...)`, `SslConfiguration(...)`, `TargetConnectionManager(...)`, `WebServer(...)`, and many HTTP handler constructors without a logger argument.
- Removes several assertions whose only purpose was verifying calls to the injected logger, e.g. warning/error checks in `BasicAuthManagerTest` and `OpenShiftAuthManagerTest`.
- Does not add new functional cases; it is a broad test-suite migration to the post-upgrade compile/API surface.

## 4. Does Δt directly exercise the breaking change?
Yes, at compile level. With only Δm and Δt, the project source still imports and injects the old `io.cryostat.core.log.Logger` type and still exposes logger-taking constructors/providers, while the hidden tests have been migrated to the new no-logger signatures. Maven `test-compile` should fail on the removed dependency type and/or signature mismatches. With Δc, production no longer depends on `core.log.Logger`, constructs per-class SLF4J loggers, and the migrated tests compile and run.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt is mostly mechanical, but it is aligned with the real `cryostat-core` logger API removal and makes the verifier exercise the required compile-time migration away from `io.cryostat.core.log.Logger`.

## 6. Δc nature
REAL_SOURCE_REPAIR — the solution changes 154 production files, replacing the removed core logger API with SLF4J and updating constructor/provider signatures and logging call sites across configuration, discovery, messaging, network, web, reporting, recording, and rule components.

## 7. Soundness concerns / notes
- The witness is primarily compile-level rather than behavioral; many Δt hunks simply mirror Δc constructor-signature changes.
- Δt drops some log-observation assertions, so a few original behavioral checks are weakened. This does not make it lint/format or infrastructure-only, but it reduces semantic test strength.
- The metadata says the test command was unextractable; the embedded verifier still contains a concrete Maven `test-compile` plus selected test invocation.

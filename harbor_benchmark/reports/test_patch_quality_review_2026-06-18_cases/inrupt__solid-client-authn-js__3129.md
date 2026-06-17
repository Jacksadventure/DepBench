# Test-patch audit — inrupt__solid-client-authn-js__3129

## 1. Task summary
- Folder: inrupt__solid-client-authn-js__3129
- Ecosystem: npm_and_yarn
- Upgrade: @typescript-eslint/eslint-plugin 5.6.0 -> 6.6.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest --selectProjects node --no-coverage --runInBand`

## 2. What is the breaking change?
The repair is driven by a lint/tooling migration, not by runtime library behavior: Δc removes TypeScript constructor parameter properties across many source classes and simplifies unused constructor parameters in node OIDC helpers. The upgraded dependency is an ESLint plugin/parser pair; Jest is then used to compile/run the node tests after those source/test signatures have been changed.

## 3. What does Δt (test.patch) actually do?
Δt adds a few eslint-disable comments in e2e tests, adds a drive-by e2e `getSolidDataset` snippet, and updates node unit tests to match Δc's constructor refactors: `new TokenRequester()` replaces helper construction with three dependencies, and many `new ClientCredentialsOidcHandler(mockDefaultTokenRefresher(), mockStorageUtility({}))` calls drop the second argument.

## 4. Does Δt directly exercise the breaking change?
Not as a dependency breaking change. The relevant Jest-visible checks are circular API/signature expectations introduced by Δt itself, e.g. `const TokenRefresher = new TokenRequester()` and one-argument `new ClientCredentialsOidcHandler(...)`; those fail against the pre-Δc source because the hidden tests now expect the refactor, not because @typescript-eslint changes runtime behavior.

## 5. Coverage verdict
TESTS_OTHER_THING — Δt primarily tests a lint-driven source refactor and test-side constructor call changes; the @typescript-eslint upgrade's actual failure mode is lint/tooling policy, not a functional dependency break witnessed by Jest.

## 6. Δc nature
MIXED — Δc touches many production TypeScript files to remove parameter properties and unused constructor parameters, and also adds `audit.json`; the change is source-visible but dominated by lint/tooling compliance rather than runtime repair.

## 7. Soundness concerns / notes
This is a circular-oracle risk: the hidden tests assert the exact constructor shape that Δc creates. A dynamic run may show FAIL/PASS, but that would not establish a witnessed dependency-update breaking change under the locked definition.

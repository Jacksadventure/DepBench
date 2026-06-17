# Test-patch audit - jo-sm__stylelint_d__709

## 1. Task summary
- Folder: jo-sm__stylelint_d__709
- Ecosystem: npm_and_yarn
- Upgrade: glob 8.0.1 -> 10.2.6
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest --colors=false`

## 2. What is the breaking change?
`glob` 10 changes the package API. The old code imports `glob` as a default-like object and constructs `new glob.Glob(...)` to inspect minimatch internals; the repair uses the new named `globIterate(...)` API and changes behavior to resolve the first matching file or fall back to `clientCwd`.

## 3. What does test.patch actually do?
`Server.spec.ts` imports `globSync`, changes the "given glob" test to compute the expected base directory from an actual match for `**/*.css`, and adds a no-match glob case that expects the stylelint basedir to fall back to `/the/cwd`.

## 4. Does test.patch directly exercise the breaking change?
Yes. The patched Jest tests drive `Server.setup` with glob inputs and assert the new matching/fallback behavior. Old source still uses the removed/changed `glob.Glob` style and old minimatch introspection, so it cannot satisfy the patched tests after the dependency bump.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - Delta_t directly targets the glob-handling branch repaired by Delta_c.

## 6. Delta_c nature
REAL_SOURCE_REPAIR - `src/Server.ts` migrates from the old `glob` object/`Glob` internals to `globIterate` and updates the basedir resolution logic.

## 7. Soundness concerns / notes
This is a focused and clean witness. The tests assert a slightly changed behavior for no-match globs, but it is part of the new glob API migration.

# Test-patch audit — scinos__yarn-deduplicate__89

## 1. Task summary
- Folder: scinos__yarn-deduplicate__89
- Ecosystem: npm_and_yarn
- Upgrade: commander 5.1.0 -> 6.1.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest __tests__/cli.js --no-coverage --passWithNoTests`

## 2. What is the breaking change?
commander 6's variadic-option support motivated migrating `--scopes`/`--packages`/`--exclude` from comma-separated single-value options (`<scopes>` + `(val) => val.split(',')`) to variadic options (`<scopes...>` with a `collectValues` reducer), and requiring `--` to separate the yarn.lock positional argument.

## 3. What does Δt (test.patch) actually do?
- `__tests__/cli.js`: a large rewrite that restructures tests into `describe` blocks and adds a `testWithFlags` helper (passes `--print ...flags -- yarnLockFilePath`). New cases assert variadic behavior: multiple values in one flag (`--packages lodash @scope/lib`), repeated flags (`--packages lodash --packages @scope/lib`), multiple scopes (`--scopes @scope @another-scope`), and exclude variants, plus assertions against new `@another-scope/lib` fixture entries.
- `__fixtures__/yarn.lock` (in Δm): adds `@another-scope/lib@>=1.0.0` and `@another-scope/lib@>=2.0.0` entries to support the new multi-scope tests.

## 4. Does Δt directly exercise the breaking change?
Yes. New assertions like `it accepts a multiple packages in one flag` (`--packages lodash @scope/lib`) and `it accepts a multiple flags` directly require the variadic `<packages...>` implementation in Δc. With the old `cli.js` (`--packages <packages>` + comma-split), commander 6 captures only `lodash` and treats `@scope/lib` as a positional arg (wrong yarn.lock path), so `expect(stdout).not.toContain('@scope/lib@>=1.0.0:')` fails → FAIL; with Δc's variadic `collectValues` both packages are processed → PASS.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt's new variadic-flag assertions fail against the old comma-split `cli.js` and pass against Δc's variadic migration; the FAIL/PASS criterion holds.

## 6. Δc nature
REAL_SOURCE_REPAIR — `cli.js` migrates `--scopes`/`--packages`/`--exclude` to variadic `<...>` options with `collectValues`; `CHANGELOG.md` is a docs drive-by.

## 7. Soundness concerns / notes
- Soft / feature-migration witness: commander 6 does not strictly force the change — the old comma-split `cli.js` still runs under commander 6 for comma-separated input. The witness is created by Δt demanding the new variadic behavior rather than by a hard API break in commander 6. Still legitimately witnessed under the benchmark's FAIL/PASS definition (and not flagged).
- Δt also rewrites/renames many pre-existing tests, so it is more of a test-suite overhaul than a minimal oracle addition.

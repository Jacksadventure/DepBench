# Test-patch audit — cloudant__nodejs-cloudant__400

## 1. Task summary
- Folder: cloudant__nodejs-cloudant__400
- Ecosystem: npm_and_yarn
- Upgrade: the mined "library" field is a bogus transitive `resolved` URL change (acorn 3.3.0 tarball `http://` -> `https://`); the real semantic change in `package.json` is `eslint ^3.19.0 -> ^4.18.2` (plus `eslint-config-*` stays). So the effective upgrade is **eslint 3 -> 4**.
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx eslint --ignore-path .eslintignore .`

## 2. What is the breaking change?
eslint 4 enforces stricter `indent` / no-multi-space / comment-spacing rules than eslint 3, so the existing source and test files (formatted to eslint 3 tolerances) now fail `npx eslint .`. There is no functional/runtime breaking change — it is a lint-rule tightening on a dev-only config dependency.

## 3. What does Δt (test.patch) actually do?
Touches 8 test files (`test/client.js`, `test/clientutils.js`, `test/issues/292.js`, `test/partitioned_databases.js`, `test/plugins/cookieauth.js`, `test/plugins/retry.js`, `test/readmeexamples.js`, `test/stream.js`). Every hunk is pure **indentation/whitespace normalization** — e.g. reducing chained `.put()/.reply()` indentation from 8 to 6 spaces, trimming double spaces before `//` comments. No new assertions, no new test cases, no fixtures, no behavior changes.

## 4. Does Δt directly exercise the breaking change?
No. Δt contains no behavioral assertions at all — it only re-indents test files so they satisfy eslint 4's `indent` rule. The "failure" it helps produce is `npx eslint .` exiting non-zero on the still-misindented `lib/` source (which Δc fixes), not any assertion about Cloudant behavior.

## 5. Coverage verdict
TESTS_OTHER_THING — the verifier "test" is `npx eslint .` (a style/lint check), which the locked breaking-change definition explicitly excludes ("not ... lint"); Δt is pure indentation churn with zero functional assertions.

## 6. Δc nature
FORMATTER_LINT_CHURN — `cloudant.js`, `lib/client.js`, `plugins/retry.js`, `soak_tests/soak.js` changes are all whitespace (trim double spaces before `//`, fix one comment indent, fix one closing-paren indent); no logic change.

## 7. Soundness concerns / notes
- This is a lint-only task whose test_cmd is `npx eslint .`; per the locked definition, lint failures are excluded from Level 1, so it should not be in the witnessed main set — yet it is NOT flagged in `problematic_prs_review_2026-06-10.md` (a gap in that review).
- The mined `library` field (acorn tarball http->https) is misleading and unrelated to the actual eslint bump; the mining pipeline mis-attributed the upgrade.
- Δc and Δt are symmetric whitespace churn; an agent could trivially reproduce by running `eslint --fix`, which tests formatting compliance rather than dependency-repair skill.

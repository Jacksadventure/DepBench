# Test-patch audit — dkhmelenko__autoapproval__343

## 1. Task summary
- Folder: dkhmelenko__autoapproval__343
- Ecosystem: npm_and_yarn
- Upgrade: mime-db 1.40.0 -> 1.47.0 (labeled; Δm also upgrades Probot/Octokit and parser dependencies)
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest --colors=false`

## 2. What is the breaking change?
The visible dependency label is misleading: the consequential manifest change upgrades Probot from 7.5.3 to 11.3.0 and moves the GitHub API surface to `context.octokit`, `context.pullRequest()`, and `context.config()`. The old source still imports `probot-config`, uses `context.github.pullRequests.*`, and relies on old config response encoding, so the post-upgrade tests fail until the app is migrated to the new Probot API.

## 3. What does Δt (test.patch) actually do?
Δt updates `test/index.test.ts` from `import myProbotApp`/`probot.load()` to `require('../src')`, constructs Probot with `ProbotOctokit.defaults`, calls `myProbotApp(probot)`, switches nock config responses from base64 content objects to raw YAML at `.github%2Fautoapproval.yml`, and expects Octokit v18 request bodies such as `body.labels.includes('done')`. It also edits `test/fixtures/pull_request_review.dismissed.json` to remove one label.

## 4. Does Δt directly exercise the breaking change?
Yes. The updated tests drive Probot 11 webhook handling and expect `context.config('autoapproval.yml')`, `context.pullRequest({ event: 'APPROVE' })`, and `context.octokit.pulls.createReview(...)`; the old source still calls `getConfig`, `context.issue({ event: ... })`, and `context.github.pullRequests.createReview(...)`, so it fails under P⊕Δm⊕Δt and passes after Δc.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the Jest suite fails on the old Probot/Octokit API usage after the manifest upgrade and passes once Δc migrates the source and generated `lib/` output.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc updates `src/index.ts` plus generated `lib/index.js`/`.d.ts`/`.map` from Probot 7 APIs to Probot 11 APIs; `.gitignore` churn is incidental.

## 7. Soundness concerns / notes
The mined library field (`mime-db`) does not describe the actual repair; the witness is a Probot/Octokit migration bundled in the same manifest patch.

# Test-patch audit — renovatebot__renovate__36455

## 1. Task summary
- Folder: renovatebot__renovate__36455
- Ecosystem: npm_and_yarn
- Upgrade: remark 13.0.0 -> 15.0.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `pnpm generate && npx vitest run lib/util/markdown.spec.ts lib/workers/repository/update/pr/changelog/release-notes.spec.ts && pnpm build:docs && node --test tools/docs/test/index.test.mjs`

## 2. What is the breaking change?
remark/unified moved to the newer ESM/named-export and mdast type surface: `remark` is imported as a named export, `remark-github` exposes its options type differently, and mdast types changed from `Content` to `RootContent`. The new remark-stringify also changes markdown list formatting from `-   item` to `- item`.

## 3. What does Δt (test.patch) actually do?
It updates `lib/util/markdown.spec.ts` expected markdown list indentation, regenerates a large `release-notes.spec.ts.snap` snapshot with the new list formatting, and changes `tools/docs/test/index.test.mjs` from `import remark from 'remark'` to `import { remark } from 'remark'`.

## 4. Does Δt directly exercise the breaking change?
Yes. The docs test import `import { remark } from 'remark'` matches the new remark 15 export shape, and the vitest/snapshot expectations assert the new markdown stringifier output such as `- Commit:` instead of `-   Commit:`. Old source still default-imports `remark` and expects the old output/types, while Δc migrates those call sites.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — P⊕Δm⊕Δt should fail on the old default import/type usage and changed remark formatting, and pass once Δc updates production markdown code to the new remark/unified APIs.

## 6. Δc nature
REAL_SOURCE_REPAIR — `lib/modules/platform/github/massage-markdown-links.ts` and `lib/util/markdown.ts` migrate production code to named `remark` imports, `RootContent`, and `RemarkGithubOptions`.

## 7. Soundness concerns / notes
The snapshot portion is large, but it is expected output churn from the upgraded markdown stringifier and is causally tied to the remark upgrade.


# Test-patch audit — KnpLabs__server-side-renderer__209

## 1. Task summary
- Folder: KnpLabs__server-side-renderer__209
- Ecosystem: npm_and_yarn
- Upgrade: bull 3.29.3 -> 4.1.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `yarn test-ci --testPathPattern=queue`

## 2. What is the breaking change?
Bull 4 / its ioredis usage requires explicit queue options for this environment: `maxRetriesPerRequest: null` and `enableReadyCheck: false`. The old `DEFAULT_QUEUE_OPTIONS = {}` no longer represents the required post-upgrade behavior.

## 3. What does Δt (test.patch) actually do?
Δt updates `src/queue.test.js` expectations so `createQueue('redis://redis:6379')` must call `Bull('request-queue', ..., { maxRetriesPerRequest: null, enableReadyCheck: false })`, and custom options must be merged after those defaults.

## 4. Does Δt directly exercise the breaking change?
Yes. The verifier runs the queue tests. Without Δc, `createQueue()` still passes `{}` or only the caller's options to Bull, so the updated constructor-call assertions fail. With Δc, `DEFAULT_QUEUE_OPTIONS` contains the Bull 4-compatible ioredis options and the expectations pass.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden tests directly pin the Bull 4 queue option migration implemented by Δc.

## 6. Δc nature
REAL_SOURCE_REPAIR — `src/queue.js` changes production default queue options for the upgraded Bull dependency.

## 7. Soundness concerns / notes
Clean, focused witness. The test is a mock-level constructor assertion rather than an integration Redis run, but it targets the exact source-level migration.

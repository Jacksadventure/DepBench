# Claude Code DeepSeek v4-with-test219 results - 2026-06-29

| Model | Agent | Snapshot | Rewards | Accuracy | Mean reward | Source |
|---|---|---|---:|---:|---:|---|
| DeepSeek | Claude Code | v4-with-test219 | 36/219 | 16.4% | 0.164 | fresh + resume6 jobs |

Notes:
- Result combines the fresh DeepSeek run with a resume6 run for unfinished tasks.
- Final aggregation uses each trial's `verifier/reward.txt`, keyed by `config.json` task path, to avoid double-counting retried tasks.
- The fresh base job's top-level `result.json` is stale because Docker stopped after 208 completed trials; the final report uses per-task verifier rewards across fresh base and resume6.
- Per-task exception files record `NonZeroAgentExitCodeError` for all 219 Claude Code trials, but all 219 tasks have verifier rewards in the final aggregate.

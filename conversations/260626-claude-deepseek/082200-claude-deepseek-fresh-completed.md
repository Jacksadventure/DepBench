# Claude Code + DeepSeek fresh run completed

## Result

| Model | Agent | Rewards | Accuracy |
|---|---|---:|---:|
| DeepSeek | Claude Code | 36/219 | 16.4% |

## Jobs

- Fresh base job: `harbor_jobs/claude_code_claudegpt_deepseek_v4_with_test219_fresh_conc5_2026-06-26__18-16-00`
  - Top-level `result.json` stalled after 208 completed trials.
  - Per-task verifier rewards covered 213 tasks.
- Resume6 job: `harbor_jobs/claude_code_claudegpt_deepseek_v4_with_test219_fresh_resume6_conc3_2026-06-29__08-02-00`
  - Finished at `2026-06-29T08:20:01.299983`.
  - Covered the remaining 6 tasks.

## Aggregation

- Final aggregation used each trial's `config.json` task path plus `verifier/reward.txt`.
- Source counts:
  - fresh: 213 tasks
  - resume6: 6 tasks
- Final rewards:
  - pass: 36
  - fail: 183
  - reward-bearing tasks: 219
  - mean reward: 0.1643835616438356
- Per-task exception files record `NonZeroAgentExitCodeError` for all 219 trials.

## Next

- Push compact metadata to `origin/v4-with-test`.
- After the push, launch Copilot DeepSeek using `_run_configs/copilot_deepseek_20260626/copilot_cli_deepseek_v4_withtest_219_conc6_2026-06-26__after-claude.json`.

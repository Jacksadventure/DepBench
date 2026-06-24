# Claude Code Maestro v4-with-test219 results - 2026-06-24

| Model | Agent | Snapshot | Rewards | Accuracy | Mean reward | Source |
|---|---|---|---:|---:|---:|---|
| GPT-5.5 | Claude Code | v4-with-test219 | 38/219 | 17.4% | 0.174 | clean205 + hard14 Maestro jobs |
| Gemini 3.5 Flash | Claude Code | v4-with-test219 | 38/219 | 17.4% | 0.174 | clean205 + hard14 Maestro jobs |

Notes:
- Corrected total is 219 tasks: clean205 + hard14.
- GPT-5.5 has 217 reward-bearing trials and 2 no-reward trials; reward-bearing accuracy is 38/217 = 17.5%.
- Gemini 3.5 Flash has 219 reward-bearing trials; reward-bearing accuracy equals mean reward.
- Harbor recorded `NonZeroAgentExitCodeError` for every Claude Code trial in these runs, but verifier rewards were still produced for reward-bearing tasks.

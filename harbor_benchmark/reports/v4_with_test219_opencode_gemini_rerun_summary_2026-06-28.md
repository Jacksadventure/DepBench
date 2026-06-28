# OpenCode + Gemini 3.5 Flash rerun summary — v4-with-test219

Generated: 2026-06-28T12:17:57.101868+00:00

Jobs: `opencode_gemini35flash_v4_withtest_219_fixed_conc5_setup1200_2026-06-27__1025-00` + `opencode_gemini35flash_v4_withtest_219_fixed_conc5_setup1200_resume14_2026-06-28__1005-00`

| Metric | Value |
|---|---:|
| Tasks | 219 / 219 |
| Pass | 54 |
| Fail | 164 |
| No reward | 1 |
| Reward-bearing pass rate | 0.248 |
| Total pass rate | 0.247 |
| Trajectory files | 78 |
| Non-empty OpenCode logs | 79 |

## Exceptions

| Exception | Count |
|---|---:|
| `AgentTimeoutError` | 148 |
| `NonZeroAgentExitCodeError` | 10 |

## Notes

- Base setup1200 job was interrupted after 205 valid results; resume14 supplies the 14 missing or empty-result tasks.
- No systematic auth/login/model/disk/wrapper/setup-timeout failure path was found in exception/trial logs; most exceptions are agent timeouts.

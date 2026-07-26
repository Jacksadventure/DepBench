# Selected rerun trajectories

This directory contains standalone exports for all rerun trajectories selected
into the final 203-task results:

- `targeted_runtime_exception/`: 111 targeted runtime-exception reruns across
  four configurations.
- `trajectory_recovery/`: 177 trajectory-recovery reruns across two
  configurations.

Each `*.jsonl.gz` file contains complete serialized trajectories. Rows preserve
the task, trial, reward, source job, exception metadata, and `outcome_source`
from the final release. A `configuration` field derived from the parent final
trajectory filename is included so each standalone row is self-identifying.

The two `*_reruns_203.csv` files map every selected configuration-task cell to
its exact job and trial. `index.csv` and `index.json` provide row counts,
outcome counts, file sizes, and SHA-256 digests.

| Rerun type | Configuration | Rows | Pass | Fail |
|---|---|---:|---:|---:|
| Targeted runtime exception | Gemini 3.5 Flash + Copilot CLI | 17 | 2 | 15 |
| Targeted runtime exception | GPT-5.5 + Codex | 28 | 11 | 17 |
| Targeted runtime exception | GPT-5.5 + Copilot CLI | 21 | 6 | 15 |
| Targeted runtime exception | GPT-5.5 + OpenCode | 45 | 13 | 32 |
| **Targeted total** |  | **111** | **32** | **79** |
| Trajectory recovery | Claude Opus 4.8 + OpenCode | 47 | 13 | 34 |
| Trajectory recovery | Gemini 3.5 Flash + OpenCode | 130 | 22 | 108 |
| **Recovery total** |  | **177** | **35** | **142** |


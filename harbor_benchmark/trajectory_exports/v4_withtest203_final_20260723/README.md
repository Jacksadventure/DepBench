# Final 203-task trajectory exports

Generated: 2026-07-24

These are the complete final trajectories used for the 203-task paper results
and trajectory-behavior analysis. They were copied from release commit
`0db6c37ccb7226145e92b5d17b9f574f1560765f`.

Each `*.jsonl.gz` file contains one JSON object per task. Every configuration
has exactly 203 rows and every row has a non-empty `trajectory`. Records include
the configuration metadata, task and trial identifiers, reward,
`outcome_source`, and serialized agent trajectory.

The exports merge the selected original full-run trials with targeted runtime
exception reruns and trajectory-recovery reruns. `index.csv` and `index.json`
record the source distribution and SHA-256 digest for each file.

## Analysis outputs

The `analysis/` directory contains the final annotation-based trajectory
analysis used for Table 7:

- `trajectory_behavior_annotations_203.jsonl`: one annotation for each of the
  2,030 final trajectories, including provenance and evidence rationale.
- `trajectory_behavior_summary_203.csv`: the four behavior counts for each of
  the 10 configurations.
- `trajectory_behavior_by_source_203.csv`: the same counts split by original,
  targeted-rerun, and trajectory-recovery source.
- `trajectory_behavior_summary_203.json`: machine-readable summary with
  annotation provenance.
- `trajectory_behavior_annotation_protocol.md`: definitions for Docs, API,
  Tests, and breaking-change hypothesis labels.

These files are the final analysis artifacts. The earlier rule-based keyword
scan is exploratory and is not included here.

| Configuration | Rows | Pass | Fail | No reward | Original | Targeted rerun | Recovery rerun |
|---|---:|---:|---:|---:|---:|---:|---:|
| Claude Opus 4.8 + Claude Code | 203 | 71 | 130 | 2 | 203 | 0 | 0 |
| Claude Opus 4.8 + Copilot CLI | 203 | 76 | 125 | 2 | 203 | 0 | 0 |
| Claude Opus 4.8 + OpenCode | 203 | 84 | 119 | 0 | 156 | 0 | 47 |
| Gemini 3.5 Flash + Claude Code | 203 | 41 | 159 | 3 | 203 | 0 | 0 |
| Gemini 3.5 Flash + Copilot CLI | 203 | 47 | 156 | 0 | 186 | 17 | 0 |
| Gemini 3.5 Flash + OpenCode | 203 | 44 | 159 | 0 | 73 | 0 | 130 |
| GPT-5.5 + Claude Code | 203 | 61 | 142 | 0 | 203 | 0 | 0 |
| GPT-5.5 + Codex | 203 | 95 | 108 | 0 | 175 | 28 | 0 |
| GPT-5.5 + Copilot CLI | 203 | 93 | 110 | 0 | 182 | 21 | 0 |
| GPT-5.5 + OpenCode | 203 | 80 | 123 | 0 | 158 | 45 | 0 |

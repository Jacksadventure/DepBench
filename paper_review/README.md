# DepBench paper-review artifact

This directory contains **203 tasks and 2,030 matching final selected
trajectories**, covering 10 model-harness configurations. All trajectory,
outcome, and verifier-log files use the same 203-task cohort.

The branch is based on `main` at
`c320122f1f76645cd348150a2839e973f36764fa`. The latest main implementation,
source-build helpers, and 201-task distribution metadata remain unchanged;
this directory is a separate artifact for reviewing the paper's experiments.

## Contents

| Path | Contents |
|---|---|
| `dataset/task_summary.json` | Index of the 203 review tasks |
| `dataset/tasks/` | Instructions, task metadata, hidden patches, and verifiers |
| `trajectories/` | Ten gzip JSONL files, each with 203 final selected trajectories |
| `results/final_per_task_outcomes.csv` | 2,030 final configuration-task outcomes |
| `results/summary.csv` | Per-configuration results with the 203-task denominator |
| `results/*reruns_203.csv` | Historical rerun records and replacement provenance |
| `verify_logs/` | Ten gzip JSONL files aligned with the selected trajectories |
| `analysis/release_redactions_2026-07-23.csv` | Historical trajectory redaction record |
| `analysis/README.md` (when available) | Optional historical supplementary analyses |
| `skills/depupgrader/SKILL.md` | DepUpgrader five-step skill for follow-up dependency-upgrade experiments |
| `MANIFEST.json` | Source commits, pinned dataset revision, and cohort boundaries |

## Execution budget for new runs

All 203 packaged tasks set `[agent].timeout_sec = 3600` (60 minutes).
Verifier limits are unchanged. This override applies to new executions of
these task packages; it does not change the historical runs or their measured
durations. The frozen runtime-audit inputs retain the task limits captured
when that audit was collected, including the earlier 30-minute agent limits.

## DepUpgrader skill

[DepUpgrader](skills/depupgrader/SKILL.md) contains the five-step skill described
in the paper. Frozen follow-up experiment records use the identifier
`deprepair-basic`; this published copy changes only the skill name and heading,
not the five instructions. This addition does not change the 2,030 historical
outcomes above or include results from the follow-up skill experiments.

## Provenance and interpretation

The experiment artifacts come from
`5db2628a0f43fc81b67e4eb0ca289241748c1cc7` (2026-08-02), immediately before
experimental artifacts were removed from main. The task snapshot comes from
`9750bc95f5d0830059346fb1b3f6c947e40cb7d9`, with its archive and Hugging Face
revision pinned in this directory's manifest.

These are **historical runs, not new agent executions**. Original and rerun
trials are distinguished by `outcome_source`, `source_job`, `trajectory_source`,
and the per-task outcome table. The final selected trial, task, and reward must
match across trajectory, result, and verifier-log records.

Task instructions in the packaged review snapshot use the normalized template.
Historical trajectories retain the instructions actually shown during each run;
some earlier runs predate prompt normalization. Do not infer that every stored
trajectory was generated with the latest prompt or the main source-build
environment. Matching task IDs establishes cohort alignment, not identical
execution environments or proof of a complete normalized-prompt rerun.

## Review

Run these commands from the repository root:

```bash
python3 repro/validate_paper_review.py

python3 repro/read_trial.py \
  --artifact-root paper_review \
  --configuration gpt55__codex \
  --task harvard-lil__js-wacz__41
```

Add `--show-trajectory` or `--show-verifier` to inspect the corresponding record.
The files are ordinary gzip-compressed JSONL and can also be read with Python's
`gzip` and `json` modules.

The paper-review dataset is committed in this directory; it does not require
downloading the separate 201-task main dataset. The normal
`repro/download_benchmark.py` and `repro/validate_release.py` commands continue
to refer to that main distribution, not to this historical review cohort.

## Failure-root-cause annotation

New annotation defaults to **all 10 model-harness configurations**, not only
Gemini + OpenCode. The current selected-run table contains **1,262 non-passes**
across the 2,030 runs; rows without a reward are included.

| Model | Harness | Non-passes |
|---|---|---:|
| Claude 4.8 | Claude Code | 119 |
| Claude 4.8 | Copilot CLI | 115 |
| Claude 4.8 | OpenCode | 124 |
| Gemini 3.5 Flash | Claude Code | 146 |
| Gemini 3.5 Flash | Copilot CLI | 146 |
| Gemini 3.5 Flash | OpenCode | 150 |
| GPT-5.5 | Claude Code | 133 |
| GPT-5.5 | Codex | 104 |
| GPT-5.5 | Copilot CLI | 103 |
| GPT-5.5 | OpenCode | 122 |

These are the evaluated configurations, not the models performing annotation.
`repro/run_multilabel_annotation.py` uses Grok 4.7 through the signed-in Copilot
CLI and GPT-6.1 Sol through CloudGPT as independent, blinded annotators.
After both finish, GPT-6 Astra adjudicates unequal label sets. Each case can
have multiple supported causes, with a rationale and checked evidence quotations
for each label. The taxonomy merges `wrong-root-cause` and
`wrong-semantic-output` into `code-adaptation-error`; `execution-timeout`
replaces `gave-up-or-budget` and requires explicit execution-timeout evidence.
Unsupported cases abstain rather than receive invented causes.

Prepare frozen evidence from all configurations without making model calls:

```bash
python3 repro/run_multilabel_annotation.py \
  --output results/failure_multilabel \
  --prepare-only
```

To start annotation, sign in with `copilot login`, and supply
`CLOUDGPT_BASE_URL` and `CLOUDGPT_API_KEY` through approved runtime secret
injection. No credentials are stored in the repository or generated protocol.

```bash
python3 repro/run_multilabel_annotation.py \
  --output results/failure_multilabel \
  --resume --concurrency 15 --cloudgpt-interval 20
```

Use the same command to resume interrupted work; validated labels are reused.
The concurrency is an upper bound: provider request spacing and HTTP 429
cooldowns may reduce the effective rate. Logs with explicit omission markers
are bounded evidence excerpts; the original archives remain unchanged.

The ignored output directory contains `manifest.json`, `protocol.json`,
`packets/`, independent `labels/A/` and `labels/B/`, Astra `labels/judge/`,
`agreement.json`, and `status.json`. Only after all required adjudications
finish are `final.jsonl`, `category_counts.csv`, and `summary.json` written.
Multi-label category counts can exceed the number of cases. Independent
agreement is measured before adjudication: exact label-set agreement, mean
Jaccard, and per-label binary Cohen's kappa on cases where both annotators
did not abstain. A macro-average kappa is the arithmetic mean of those
defined per-label kappas.

## Historical supplementary analyses (optional)

The following describes the earlier, single-label Gemini + OpenCode supplement,
not the default scope or results of the new all-configuration annotation.
Some snapshots do not include `paper_review/analysis/`; the trajectories,
verifier logs, outcomes and task contracts above remain sufficient for new
annotation. When the historical supplement is present, validate it with
`python3 repro/validate_paper_review_supplements.py`.

The historical supplementary evidence adds statistical sensitivity and
runtime-budget audits plus an independent two-model annotation of the 150
OpenCode + Gemini non-passes. The models agree on 80 cases (53.3%, kappa 0.450);
69 concrete-category disagreements and one insufficient-evidence case are
preserved in the pre-adjudication records. A subsequent GPT-6 Astra stage
adjudicated all 69 disagreements: 62 received concrete categories and seven
received insufficient-evidence labels. The final table retains eight
insufficient-evidence cases, including the original one.

The final Table 5 column combines original consensus and third-model adjudication;
the other four columns retain their historical final categories. Annotation
protocols and paired coverage still differ. Original independent agreement is not
recomputed after adjudication. Frozen inputs, raw decisions and an offline verifier
are provided; no human review is claimed. These supplements do not change tasks,
benchmark rewards or selected trajectories, and are not new coding-agent executions.

## Task membership and licensing

The 203-task paper cohort includes `databricks__cli__1326` and
`nearform__brokeneck__820`. Main's later 201-task distribution excluded these
because the former has a custom repository license and the latter has no
declared repository-level license. They and their run records are retained here
to preserve the paper's original denominator and exact task-trajectory alignment.

This review branch does not grant new redistribution rights or change upstream
terms. Review and sharing must comply with the original repositories' terms;
this is not a replacement for the 201-task redistributable release.

Keep `solution/` and `tests/` hidden from agents in any new evaluation. Published
trajectories may expose repairs and must never be supplied as agent input.

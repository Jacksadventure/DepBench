# Statistical supplements

These tables use the existing 203-task, ten-configuration result snapshot in
`paper_review/results/final_per_task_outcomes.csv`. Frozen reduced inputs and
source provenance are under `inputs/`. No benchmark rewards are changed.

| Output | Contents |
|---|---|
| `rates.csv`, `results-table.md` | Configuration rates and 95% Wilson/repository-bootstrap intervals |
| `paired_comparisons.csv` | All 45 exact McNemar comparisons, Holm adjustment and paired cluster-bootstrap intervals |
| `ecosystem_rates.csv` | Ecosystem-specific counts and rates |
| `task_overlap.csv` | Cross-configuration task overlap |
| `sensitivity.csv` | Direct-behavior and unchanged-test-patch subsets |
| `annotation_reliability.csv`, `.json` | Historical matched annotation coverage and agreement |
| `behavior_shares.csv` | Non-exclusive trajectory behavior frequencies |
| `exceptions.csv` | Exception/reward cross-tabulations |
| `date_sensitivity.csv` | Descriptive fix-year strata |
| `summary.json` | Aggregated results and limitations |

Copilot CLI + GPT-5.5 has 100/203 passes (49.3%): Wilson 95% interval 42.5-56.1%;
repository-bootstrap interval 41.9-56.4%. Bootstrap intervals use 10,000
whole-repository resamples across 159 repositories, seed 20260924, with
task-weighted rates. Copilot versus Codex with GPT-5.5 has 21 versus 20 discordant
wins (exact McNemar p=1.0). These results do not establish run-to-run model variance
or population representativeness.

The original four-configuration failure cohort has 475 non-passes and 213 usable
independent label pairs (62.4% agreement, kappa 0.504). The other 262 cases are not
counted as agreements. These files preserve that analysis, not the later
[150-pair independent study](../opencode_gemini_dual_annotation/README.md).
The [subsequent GPT-6 adjudication](../opencode_gemini_adjudication/README.md)
supplies final categories for the 69 disagreements without changing that study's
pre-adjudication statistics.
RQ4 field-specific agreement uses its own paired subsets, not all 2,030 records.
Do not pool agreement statistics from different annotation studies.

Historical test-quality labels are matched to current patch bytes. The 138-task
unchanged-patch direct-behavior subset and its 103-task no-deletion subset provide
more conservative sensitivities; label freshness does not prove oracle validity.

The 440 normalized-instruction follow-up executions cover 42 distinct tasks;
420 cells enter the final table and 1,610 other cells retain earlier runs. These
batches also changed environments/contracts and are not a prompt-only ablation.
Missing intermediate construction attrition, person-hours and complete historical
settings are not inferred. Fix-year strata do not establish post-training-cutoff
status.

Use `python3 repro/validate_paper_review_supplements.py` from the repository root
to check frozen-file integrity and score alignment. This offline check does not
recompute the bootstrap or repeat the historical label-collection process.

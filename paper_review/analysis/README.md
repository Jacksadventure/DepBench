# Paper-review supplementary analyses

These supplements analyze the existing **203 tasks and 2,030 selected runs**.
They do not replace benchmark tasks, rewards or trajectories, and are not a new
coding-agent evaluation. Rebuttal prose is maintained separately.

| Directory | Evidence |
|---|---|
| [opencode_gemini_dual_annotation](opencode_gemini_dual_annotation/README.md) | 150 independent two-model label pairs, frozen evidence, protocol, raw outputs, confusion matrix and restored Table 5 |
| [rebuttal_supplements](rebuttal_supplements/README.md) | Rates, intervals, paired comparisons, sensitivity subsets and historical annotation coverage |
| [budget_audit](budget_audit/README.md) | Task budgets, measured runtimes, timeout/resource evidence and historical-setting coverage |

Run from the repository root, with Python's standard library only:

```bash
python3 repro/validate_paper_review_supplements.py
```

This checks publication checksums and selected-run identities, frozen packet and
rubric hashes, raw-versus-accepted annotation categories, confidence and rationale,
literal citations, both kappa calculations, confusion counts, scores and budget
coverage. It does not call models, adjudicate disagreements or rerun agents.
It does not independently reproduce every historical data-collection step or
bootstrap interval.

## Publication provenance

`supplement_manifest.json` records source and published checksums and any
publication-only transformations. Host-local path prefixes in budget provenance
are replaced with `local_sources/`; these are source locators, not downloadable
paths. Unneeded raw-response `reasoning_content` fields are omitted. Original
category, confidence, rationale, response IDs, usage and citation-repair records
are retained.

The compressed evidence packets are lossless exports of the actual frozen
two-model inputs: their decoded canonical-JSON hashes match the original manifest.
They include reference patches and must not be used as coding-agent evaluation
input. The upstream licensing limitations in the [review README](../README.md)
continue to apply.
Two key-header strings in the `slowli__jwt-compact__138` trajectory excerpt match
the already-reviewed public test fixture in the original selected trajectory.
Their copied artifact fingerprint is recorded in
`analysis/secret_scan_review_2026-07-23.csv` at the repository root.

No reviewer comments, credentials, host caches, images or superseded single-model
completion/adjudication data are included in this supplement. Historical errors
under the independent study describe earlier attempts, not final missing labels.

The packaging helper accepts local source and packet directories explicitly:
`repro/package_paper_review_supplements.py --help`. It only copies saved analyses;
it is not an experiment runner. Existing benchmark artifacts remain authoritative.

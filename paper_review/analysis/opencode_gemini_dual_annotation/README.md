# Independent two-model failure annotation

All **150 selected OpenCode + Gemini non-passes** were independently labeled by
`gpt-5.5-20260424` (Responses API, medium reasoning) and `DeepSeek-V4-Pro`
(Chat Completions API, temperature 0). Both received the same frozen evidence
in separate stateless requests, without prior annotations or the other model's
labels. This is automated annotation, not human review.

| Measure | Result |
|---|---:|
| Valid model outputs | 150 + 150 |
| Identical primary labels | 80/150 (53.3%) |
| Different concrete categories | 69/150 (46.0%) |
| Insufficient evidence assigned by either annotator | 1/150 (0.7%) |
| Missing pairs | 0 |
| Cohen's kappa, all pairs | 0.44965669060223284 |
| Kappa excluding the insufficient-evidence pair | 0.453225549114503 |

These are **pre-adjudication** statistics, preserving the original disagreements.
GPT-5.5 requests more evidence in 34 cases, including its one insufficient-evidence
label; DeepSeek requests none. Tentative concrete categories remain in the primary
calculation. Agreement is limited and does not establish label accuracy or prove
that the shared evidence/rubric is sufficient.

A subsequent [GPT-6 adjudication](../opencode_gemini_adjudication/README.md)
processed all 69 concrete disagreements, assigning concrete categories to 62 and
insufficient evidence to seven. Including the original abstention, the final table
has eight insufficient-evidence cases. Original labels, pre-adjudication tables and
kappa values in this directory remain unchanged.

## Files

`protocol.json` contains the exact rubric, taxonomy and model settings.
`manifest.json` pins task/trial identities and canonical-JSON evidence hashes.
`evidence_packets.jsonl.gz` contains 150 rows with `id` and `packet`; the latter is
the actual model input, including metadata, trajectory, verifier, candidate patch
and reference patch sections. Empty versus unavailable patches and truncated
excerpts are explicitly distinguished. No evidence text is changed for publication.

`labels/A/` and `labels/B/` contain accepted outputs; `attempts/` preserves model
responses and mechanical format/quotation retries. Retries do not reveal another
annotator's answer or whether the categories agree. Same-model citation repairs
and 11 final deterministic citation recoveries preserve category, rationale and
confidence; original/replacement citations and response IDs are recorded.
Deterministic recovery retains literal fragments or corrects the cited section.
It is not category adjudication. Historical `last_*errors.json` files describe
prior invocation errors; use `summary.json` and accepted labels for final coverage.

`paired_labels.json` and `.csv` include uncertainty flags; `confusion_matrix.csv`
contains the full category matrix. `table5.md` and `table5_counts.csv` preserve the
pre-adjudication column using consensus categories plus separate disagreement and
insufficient-evidence rows.

**The other four columns retain historical final/adjudicated labels.** Their
frequencies are not directly comparable to this column's pre-adjudication consensus.
Dashes mean not remeasured, not zero. Do not pool this study with the older
four-configuration agreement analysis or reinterpret agreement as human validation.

From the repository root, `python3 repro/validate_paper_review_supplements.py`
checks the evidence hashes/citations and independently recomputes both kappas
using exact fractions. It requires no API credentials or third-party packages.

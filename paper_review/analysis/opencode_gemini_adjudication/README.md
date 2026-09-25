# GPT-6 adjudication of the 69 concrete disagreements

This is a subsequent adjudication stage, not a replacement independent annotation
study. Exactly the 69 different-concrete-category cases from the original
150-pair study are selected. The 80 original consensus cases and the one original
insufficient-evidence case are retained without reannotation.

## Completed results

All **69/69** selected disagreements have a validated GPT-6 decision. The judge
selected A's category in 33 cases, B's in 22, a different concrete category in
seven, and insufficient evidence in seven. Thus 62 cases receive concrete
categories, while the complete 150-case table retains **eight insufficient-evidence
cases (5.3%)**, including the one untouched original case.

The judge reports 25 high-confidence and 44 medium-confidence decisions, requesting
more evidence for the seven abstentions. These self-reported confidence levels
are not measured accuracy. The other 80 original consensus categories are unchanged.

## Protocol

The third automated adjudicator is **GPT-6 Astra (`gpt-6-astra`)**, invoked through
Copilot CLI custom task agents in three disjoint 23-case batches. Context may
persist within each batch; these are not claimed to be stateless API requests.
The requested model is explicit; reasoning/context settings use harness defaults.

Each judge receives the original frozen evidence and both prior annotations,
but not the annotator model identities, previous adjudications or desired category
frequencies. The original taxonomy and precedence are retained. The judge can
choose either proposed category, another existing category, or insufficient
evidence. An unavailable patch, incomplete trace or verifier-contract ambiguity
must not be converted into a forced concrete attribution.

This stage is not blind to the two primary labels and does not provide a third
independent label for estimating agreement. The original **80/150 agreement and
Cohen's kappa 0.44965669060223284** remain unchanged. No post-adjudication kappa
is substituted, and neither agreement nor adjudication establishes label accuracy.
No human review, new coding-agent run or changed benchmark reward is claimed.

## Records

| File | Meaning |
|---|---|
| `protocol.json` | Exact rubric, model/transport, and hashes of the unchanged original study |
| `manifest.json`, `inputs/` | Exactly 69 selected identities, original label hashes, blinded prior annotations and complete judge-input hashes |
| `assignments.json`, `executions.json` | Disjoint batch assignments and actual CLI invocation IDs |
| `raw/` | Agent-authored decision JSON, not fabricated provider API envelopes |
| `decisions/` | Validated decisions with input, execution and raw-output provenance |
| `final_labels.json`, `.csv` | All 150 cases, preserving the distinction between original consensus, original insufficient evidence and third-model adjudication |
| `summary.json`, `table5.md`, `table5_counts.csv` | Final category counts and the corresponding Table 5 |

`summary.json` is generated only after all 69 decisions pass identity and literal
citation checks. Mechanical citation recovery cannot change category, rationale
or confidence; any such recovery is recorded and the raw decision is retained.
Insufficient-evidence outcomes remain explicit, including any new judge abstentions.

The original evidence is in
`../opencode_gemini_dual_annotation/evidence_packets.jsonl.gz` in the published
artifact. A judge-input hash covers that unchanged packet and the two visible
annotations together. The original pre-adjudication tables remain available in
the independent-study directory.

The final Table 5 uses adjudicated categories for this column and historical final
categories for the other four columns. Their annotation coverage and model
protocols still differ. Removing a disagreement row after adjudication does not
mean that primary-annotator agreement became 100%.

From the published repository root:
`python3 repro/validate_paper_review_supplements.py` checks original-study hashes,
exact 69-case selection, raw-to-accepted decision integrity, citations, final
counts and preservation of the original kappa. It calls no models.

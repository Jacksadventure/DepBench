# Trajectory Annotation — Interim Report

Generated: 2026-06-30 12:16 UTC  ·  eligible trials (have trajectory): **1170**

## 1. Coverage

| annotator | annotated | of eligible |
| --- | --- | --- |
| codex | 1170 | 100.0% |
| opencode | 1170 | 100.0% |

Trials annotated by **all 2**: 1170 (100.0%)


### Per harness × LLM (annotated by codex)

| group | eligible | annotated |
| --- | --- | --- |
| ? / gemini-3.5-flash | 78 | 78 |
| codex / gemini-3.5-flash | 219 | 219 |
| codex / gpt-5.5 | 219 | 219 |
| copilot-cli / gemini-3.5-flash | 219 | 219 |
| copilot-cli / gpt-5.5 | 216 | 216 |
| opencode / gpt-5.5 | 219 | 219 |

## 2.1 codex (1170 trials) — label distributions

**Leakage** (L)

| label | n | % |
| --- | --- | --- |
| none | 911 | 77.9% |
| suspect | 68 | 5.8% |
| confirmed | 190 | 16.2% |
| none | suspect | confirmed | 1 | 0.1% |

→ **confirmed leakage: 190 (16.2%)**, incl. suspect: 258 (22.1%)


**RQ4 evidence-gathering mode** (D)

| mode | n | % |
| --- | --- | --- |
| evidence-first | 404 | 34.5% |
| reactive-test-driven | 607 | 51.9% |
| none | 158 | 13.5% |
| evidence-first | reactive-test-driven | none | 1 | 0.1% |

Visible-then-hidden overfit: 484 (of 733 failed = 66.0%)


**Pass alignment** (P) — 436 passing trials

| label | n | % |
| --- | --- | --- |
| oracle-equivalent | 1 | 0.2% |
| oracle-aligned-minor | 201 | 46.1% |
| plausible-different | 91 | 20.9% |
| suspicious-pass | 142 | 32.6% |
| oracle-equivalent | oracle-aligned-minor | plausible-different | suspicious-pass | 1 | 0.2% |

**Failure category** (F) — 733 failing trials

| category | n | % |
| --- | --- | --- |
| incomplete-migration | 221 | 30.2% |
| wrong-semantic-output | 76 | 10.4% |
| compile-namespace-inconsistency | 27 | 3.7% |
| fixture-generated-state-inconsistent | 2 | 0.3% |
| wrong-root-cause | 148 | 20.2% |
| no-upgrade-attempted | 28 | 3.8% |
| install-build-failure | 18 | 2.5% |
| test-tampering | 4 | 0.5% |
| gave-up-or-budget | 76 | 10.4% |
| infra-exception | 133 | 18.1% |

## 2.2 opencode (1170 trials) — label distributions

**Leakage** (L)

| label | n | % |
| --- | --- | --- |
| none | 954 | 81.5% |
| suspect | 35 | 3.0% |
| confirmed | 180 | 15.4% |
| none | suspect | confirmed | 1 | 0.1% |

→ **confirmed leakage: 180 (15.4%)**, incl. suspect: 215 (18.4%)


**RQ4 evidence-gathering mode** (D)

| mode | n | % |
| --- | --- | --- |
| evidence-first | 279 | 23.8% |
| reactive-test-driven | 576 | 49.2% |
| none | 314 | 26.8% |
| evidence-first | reactive-test-driven | none | 1 | 0.1% |

Visible-then-hidden overfit: 461 (of 733 failed = 62.9%)


**Pass alignment** (P) — 436 passing trials

| label | n | % |
| --- | --- | --- |
| oracle-equivalent | 57 | 13.2% |
| oracle-aligned-minor | 120 | 27.7% |
| plausible-different | 119 | 27.5% |
| suspicious-pass | 136 | 31.4% |
| oracle-equivalent | oracle-aligned-minor | plausible-different | suspicious-pass | 1 | 0.2% |

**Failure category** (F) — 733 failing trials

| category | n | % |
| --- | --- | --- |
| incomplete-migration | 209 | 28.6% |
| wrong-semantic-output | 114 | 15.6% |
| compile-namespace-inconsistency | 9 | 1.2% |
| fixture-generated-state-inconsistent | 7 | 1.0% |
| wrong-root-cause | 74 | 10.1% |
| no-upgrade-attempted | 42 | 5.7% |
| install-build-failure | 4 | 0.5% |
| test-tampering | 10 | 1.4% |
| gave-up-or-budget | 108 | 14.8% |
| infra-exception | 155 | 21.2% |

## 3. Inter-annotator agreement (codex vs opencode, n=1170 co-annotated)

| dimension | n | % agree | Cohen κ | weighted κ | Gwet AC1 |
| --- | --- | --- | --- | --- | --- |
| L leakage | 1170 | 0.950 | 0.851 | 0.922 | 0.943 |
| D evidence-mode | 1170 | 0.744 | 0.592 | — | 0.678 |
| P alignment | 433 | 0.688 | 0.562 | — | 0.622 |
| F failure-cat | 732 | 0.635 | 0.556 | — | 0.599 |

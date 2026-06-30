# Trajectory Annotation — Interim Report

Generated: 2026-06-30 06:48 UTC  ·  eligible trials (have trajectory): **1170**

## 1. Coverage

| annotator | annotated | of eligible |
| --- | --- | --- |
| codex | 854 | 73.0% |
| opencode | 797 | 68.1% |

Trials annotated by **all 2**: 797 (68.1%)


### Per harness × LLM (annotated by codex)

| group | eligible | annotated |
| --- | --- | --- |
| ? / gemini-3.5-flash | 78 | 0 |
| codex / gemini-3.5-flash | 219 | 219 |
| codex / gpt-5.5 | 219 | 219 |
| copilot-cli / gemini-3.5-flash | 219 | 219 |
| copilot-cli / gpt-5.5 | 216 | 197 |
| opencode / gpt-5.5 | 219 | 0 |

## 2.1 codex (854 trials) — label distributions

**Leakage** (L)

| label | n | % |
| --- | --- | --- |
| none | 671 | 78.6% |
| suspect | 53 | 6.2% |
| confirmed | 130 | 15.2% |

→ **confirmed leakage: 130 (15.2%)**, incl. suspect: 183 (21.4%)


**RQ4 evidence-gathering mode** (D)

| mode | n | % |
| --- | --- | --- |
| evidence-first | 275 | 32.2% |
| reactive-test-driven | 433 | 50.7% |
| none | 146 | 17.1% |

Visible-then-hidden overfit: 326 (of 546 failed = 59.7%)


**Pass alignment** (P) — 307 passing trials

| label | n | % |
| --- | --- | --- |
| oracle-equivalent | 1 | 0.3% |
| oracle-aligned-minor | 140 | 45.6% |
| plausible-different | 65 | 21.2% |
| suspicious-pass | 101 | 32.9% |

**Failure category** (F) — 546 failing trials

| category | n | % |
| --- | --- | --- |
| incomplete-migration | 150 | 27.5% |
| wrong-semantic-output | 51 | 9.3% |
| compile-namespace-inconsistency | 17 | 3.1% |
| fixture-generated-state-inconsistent | 2 | 0.4% |
| wrong-root-cause | 108 | 19.8% |
| no-upgrade-attempted | 20 | 3.7% |
| install-build-failure | 11 | 2.0% |
| test-tampering | 2 | 0.4% |
| gave-up-or-budget | 70 | 12.8% |
| infra-exception | 115 | 21.1% |

## 2.2 opencode (797 trials) — label distributions

**Leakage** (L)

| label | n | % |
| --- | --- | --- |
| none | 653 | 81.9% |
| suspect | 32 | 4.0% |
| confirmed | 112 | 14.1% |

→ **confirmed leakage: 112 (14.1%)**, incl. suspect: 144 (18.1%)


**RQ4 evidence-gathering mode** (D)

| mode | n | % |
| --- | --- | --- |
| evidence-first | 175 | 22.0% |
| reactive-test-driven | 380 | 47.7% |
| none | 242 | 30.4% |

Visible-then-hidden overfit: 283 (of 517 failed = 54.7%)


**Pass alignment** (P) — 279 passing trials

| label | n | % |
| --- | --- | --- |
| oracle-equivalent | 35 | 12.7% |
| oracle-aligned-minor | 74 | 26.8% |
| plausible-different | 80 | 29.0% |
| suspicious-pass | 87 | 31.5% |

**Failure category** (F) — 517 failing trials

| category | n | % |
| --- | --- | --- |
| incomplete-migration | 140 | 27.1% |
| wrong-semantic-output | 73 | 14.1% |
| compile-namespace-inconsistency | 7 | 1.4% |
| fixture-generated-state-inconsistent | 5 | 1.0% |
| wrong-root-cause | 50 | 9.7% |
| no-upgrade-attempted | 27 | 5.2% |
| install-build-failure | 3 | 0.6% |
| test-tampering | 8 | 1.6% |
| gave-up-or-budget | 87 | 16.9% |
| infra-exception | 116 | 22.5% |

## 3. Inter-annotator agreement (codex vs opencode, n=797 co-annotated)

| dimension | n | % agree | Cohen κ | weighted κ | Gwet AC1 |
| --- | --- | --- | --- | --- | --- |
| L leakage | 797 | 0.952 | 0.857 | 0.917 | 0.943 |
| D evidence-mode | 797 | 0.763 | 0.626 | — | 0.654 |
| P alignment | 276 | 0.674 | 0.542 | — | 0.575 |
| F failure-cat | 516 | 0.665 | 0.592 | — | 0.631 |

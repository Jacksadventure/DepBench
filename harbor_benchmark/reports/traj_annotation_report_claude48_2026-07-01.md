# Trajectory Annotation — Interim Report

Generated: 2026-07-01 11:05 UTC  ·  eligible trials (have trajectory): **873**

## 1. Coverage

| annotator | annotated | of eligible |
| --- | --- | --- |
| codex | 873 | 100.0% |
| opencode | 873 | 100.0% |

Trials annotated by **all 2**: 873 (100.0%)


### Per harness × LLM (annotated by codex)

| group | eligible | annotated |
| --- | --- | --- |
| claude-code / claude-opus-4-8 | 218 | 218 |
| codex / claude-opus-4-8 | 217 | 217 |
| copilot-cli / claude-opus-4-8 | 219 | 219 |
| opencode / claude-opus-4-8 | 219 | 219 |

## 2.1 codex (873 trials) — label distributions

**Leakage** (L)

| label | n | % |
| --- | --- | --- |
| none | 193 | 22.1% |
| suspect | 480 | 55.0% |
| confirmed | 200 | 22.9% |

→ **confirmed leakage: 200 (22.9%)**, incl. suspect: 680 (77.9%)


**RQ4 evidence-gathering mode** (D)

| mode | n | % |
| --- | --- | --- |
| evidence-first | 591 | 67.7% |
| reactive-test-driven | 236 | 27.0% |
| none | 46 | 5.3% |

Visible-then-hidden overfit: 390 (of 493 failed = 79.1%)


**Pass alignment** (P) — 376 passing trials

| label | n | % |
| --- | --- | --- |
| oracle-equivalent | 3 | 0.8% |
| oracle-aligned-minor | 170 | 45.2% |
| plausible-different | 79 | 21.0% |
| suspicious-pass | 124 | 33.0% |

**Failure category** (F) — 493 failing trials

| category | n | % |
| --- | --- | --- |
| incomplete-migration | 148 | 30.0% |
| wrong-semantic-output | 57 | 11.6% |
| compile-namespace-inconsistency | 12 | 2.4% |
| fixture-generated-state-inconsistent | 3 | 0.6% |
| wrong-root-cause | 147 | 29.8% |
| no-upgrade-attempted | 3 | 0.6% |
| install-build-failure | 5 | 1.0% |
| test-tampering | 3 | 0.6% |
| gave-up-or-budget | 49 | 9.9% |
| infra-exception | 66 | 13.4% |

## 2.2 opencode (873 trials) — label distributions

**Leakage** (L)

| label | n | % |
| --- | --- | --- |
| none | 484 | 55.4% |
| suspect | 191 | 21.9% |
| confirmed | 198 | 22.7% |

→ **confirmed leakage: 198 (22.7%)**, incl. suspect: 389 (44.6%)


**RQ4 evidence-gathering mode** (D)

| mode | n | % |
| --- | --- | --- |
| evidence-first | 453 | 51.9% |
| reactive-test-driven | 263 | 30.1% |
| none | 157 | 18.0% |

Visible-then-hidden overfit: 371 (of 493 failed = 75.3%)


**Pass alignment** (P) — 376 passing trials

| label | n | % |
| --- | --- | --- |
| oracle-equivalent | 58 | 15.5% |
| oracle-aligned-minor | 84 | 22.4% |
| plausible-different | 114 | 30.4% |
| suspicious-pass | 119 | 31.7% |

**Failure category** (F) — 493 failing trials

| category | n | % |
| --- | --- | --- |
| incomplete-migration | 187 | 37.9% |
| wrong-semantic-output | 93 | 18.9% |
| compile-namespace-inconsistency | 4 | 0.8% |
| fixture-generated-state-inconsistent | 4 | 0.8% |
| wrong-root-cause | 43 | 8.7% |
| no-upgrade-attempted | 7 | 1.4% |
| install-build-failure | 4 | 0.8% |
| test-tampering | 3 | 0.6% |
| gave-up-or-budget | 52 | 10.5% |
| infra-exception | 94 | 19.1% |
| wrong-area | 2 | 0.4% |

## 3. Inter-annotator agreement (codex vs opencode, n=873 co-annotated)

| dimension | n | % agree | Cohen κ | weighted κ | Gwet AC1 |
| --- | --- | --- | --- | --- | --- |
| L leakage | 873 | 0.645 | 0.496 | 0.699 | 0.474 |
| D evidence-mode | 873 | 0.701 | 0.464 | — | 0.588 |
| P alignment | 375 | 0.707 | 0.598 | — | 0.616 |
| F failure-cat | 493 | 0.535 | 0.421 | — | 0.496 |

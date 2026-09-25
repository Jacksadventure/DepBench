# Runtime and resource audit

The audit covers exactly the **2,030 final selected runs** (203 tasks, ten
configurations), not every replaced or intermediate trial. No agents were rerun.
All cases are joined by configuration, task, trial and recorded reward.

Packaged agent/verifier limits, in minutes:

| Agent | Verifier | Tasks |
|---:|---:|---:|
| 30 | 5 | 102 |
| 30 | 15 | 4 |
| 30 | 20 | 16 |
| 30 | 25 | 3 |
| 30 | 30 | 13 |
| 60 | 70 | 65 |

Thus 101/203 packaged tasks have verifier budgets above five minutes. Packaged
settings are not proof of every historical run's effective settings: only 876
selected runs have sufficient frozen configuration evidence for reconstruction.

| Observation | Runs | Interpretation |
|---|---:|---|
| Agent timeout | 233 | 93 distinct tasks; 53 runs still pass |
| Nonzero agent exit | 20 | 15 tasks; five still pass; not an OOM proxy |
| Verifier subprocess timeout | 26 | Seven tasks; all reward 0 |
| Tool-level Node/JavaScript heap exhaustion | 16 | Five tasks; seven still pass; not confirmed container OOM |
| Verifier return code -9 | 5 | SIGKILL with unresolved cause |

Events overlap and must not be added as distinct failures. There are zero
top-level `VerifierTimeoutError` records, but that does not negate the 26 inner
timeouts. No positive cgroup-OOM/disk-exhaustion signatures were located;
incomplete telemetry prevents asserting these events never happened.

| Timing evidence | Coverage | Median | P95 | Maximum | Over 300s | Passing over 300s |
|---|---:|---:|---:|---:|---:|---:|
| CTRF verification workload, excluding outer bootstrap | 2,010 | 16.97s | 275.51s | 1,800.25s | 93 | 26 |
| Complete verifier phase in matched raw results | 1,187 | 31.40s | 403.59s | 1,304.32s | 75 | 23 |

These timing columns cover different subsets: do not add their counts, compare
their maxima as paired phases, or treat missing times as zero. Long successful
CTRF workloads span 14 tasks. These observations are not a fixed-five-minute
counterfactual rerun.

Raw results match 1,443 selected runs after excluding four reward-mismatched
candidates. All 1,443 captured memory overrides are 8,192 MB; this is not a claim
about all runs. Local raw-result locators are retained as relative
`local_sources/` references; raw host caches/configuration trees are not published.

`inputs/runs.json` and `inputs/packaged_task_settings.csv` are frozen reduced
inputs. `inputs/provenance.json` records collection coverage and exclusions.
`signal_evidence.csv` provides observed signatures and trial/phase identities;
the remaining CSVs and `summary.json` provide per-configuration, timeout and timing
breakdowns. Events were distinguished from agent speculation and source-code
mentions of resource limits.

From the repository root, `python3 repro/validate_paper_review_supplements.py`
checks publication hashes, exact trial coverage and key timeout counts. It does
not reconstruct unavailable host telemetry or rerun historical containers.

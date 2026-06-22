# Test-patch behavior classification — current clean205

Generated: 2026-06-22T08:18:06.476013+00:00

Scope: current `harbor_benchmark/tasks_v4` / `task_summary.json` (205 tasks).

Definitions:
- **Corrects existing behavior**: modifies existing tests, assertions, snapshots, expected outputs, fixtures, or mocks to align with the dependency-upgraded behavior.
- **Adds new tests**: adds a new test file or new test case/function/block.
- **Deletes/removes tests**: deletes a test file or removes a test case/function/block.
- **Infra/fixture only**: touches test setup/helpers/fixtures without an obvious added/deleted test case or expectation correction.

## Multi-label counts

| Label | Tasks | Percent |
|---|---:|---:|
| `corrects_existing_behavior` | 145 | 70.7% |
| `adds_new_tests` | 65 | 31.7% |
| `deletes_or_removes_tests` | 37 | 18.0% |
| `fixture_or_infra_only` | 45 | 22.0% |

## Combination counts

| Combination | Tasks | Percent |
|---|---:|---:|
| `corrects_only` | 88 | 42.9% |
| `infra_fixture_only` | 45 | 22.0% |
| `adds+corrects+deletes` | 30 | 14.6% |
| `adds+corrects` | 20 | 9.8% |
| `adds_only` | 15 | 7.3% |
| `corrects+deletes` | 7 | 3.4% |

## Primary classification counts

| Primary classification | Tasks | Percent |
|---|---:|---:|
| `CORRECTS_EXISTING_BEHAVIOR` | 88 | 42.9% |
| `MIXED` | 57 | 27.8% |
| `TEST_INFRA_OR_FIXTURE_ONLY` | 45 | 22.0% |
| `ADDS_NEW_TESTS` | 15 | 7.3% |

## Combination by ecosystem

| Ecosystem | Total | `corrects_only` | `infra_fixture_only` | `adds+corrects+deletes` | `adds+corrects` | `adds_only` | `corrects+deletes` |
|---|---:|---:|---:|---:|---:|---:|---:|
| cargo | 20 | 8 | 9 | 1 | 2 | 0 | 0 |
| go_modules | 28 | 14 | 3 | 3 | 3 | 3 | 2 |
| maven | 66 | 21 | 25 | 8 | 3 | 6 | 3 |
| npm_and_yarn | 79 | 38 | 6 | 15 | 12 | 6 | 2 |
| pip | 12 | 7 | 2 | 3 | 0 | 0 | 0 |

## Interpretation

The current clean205 set is dominated by patches that **both add new coverage and correct/update existing tests**. Pure deletion/removal is rare and usually appears as part of a mixed update rather than as a standalone deletion-only patch.

Per-task classification CSV: `harbor_benchmark/reports/test_patch_behavior_classification_2026-06-22.csv`

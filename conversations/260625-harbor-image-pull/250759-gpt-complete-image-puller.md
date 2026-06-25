# Handoff Note — 250759 · gpt · complete-image-puller

## Inherited context

- Read the handoff skill instructions and relevant prior notes:
  - `conversations/2026-06-05-dataset-failure-analysis/070008-codex-fixed-harbor.md`
  - `conversations/260619-benchmark-runs/040530-codex-opencode-resume.md`
  - `conversations/260623-claude-code-maestro/162305-claude-gpt55-launched.md`
- Relevant locked-in project constraints: `harbor_benchmark/tasks_v4` is the task source of truth for current local runs; run outputs should not be committed; Harbor task images are referenced by `[environment].docker_image` in each `task.toml`.
- The user asked for a script similar to `~/msr4agent/src/pull_swebench_images.py`, but that file was not found under `/home` on this machine.

## Work done this session

- [x] Added `scripts/pull_harbor_images.py`.
- [x] Implemented concurrent registry manifest querying to estimate compressed layer/config sizes before pulling.
- [x] Implemented concurrent `docker pull` with retry/backoff, optional `--skip-present`, `--dry-run`, `--yes`, `--platform`, and JSON reporting.
- [x] Verified syntax and ran a full dry-run estimate against the current local `harbor_benchmark/tasks_v4`.

## Current state

| File | Change |
| ---- | ------ |
| `scripts/pull_harbor_images.py` | New executable Python utility for estimating and pulling Harbor task Docker images. |
| `conversations/260625-harbor-image-pull/250759-gpt-complete-image-puller.md` | This handoff note. |

Verification commands run:

```bash
python3 -m py_compile scripts/pull_harbor_images.py
python3 scripts/pull_harbor_images.py --help
python3 scripts/pull_harbor_images.py --dry-run --metadata-concurrency 32 --retries 3
```

Dry-run result on this checkout:

- 219 unique images discovered from `harbor_benchmark/tasks_v4`.
- 219 manifests estimated successfully.
- 1 image already present locally.
- Estimated unique compressed total: 103.3 GiB across 922 unique configs/layers.
- Estimate excluding already-present image refs: 100.6 GiB across 919 unique configs/layers.

Note: local `task.toml` count is 219, despite project notes mentioning the clean205 baseline. The script intentionally follows whatever task root it is pointed at, so it can also be used with a frozen clean205 copy via `--tasks-root`.

## Open tasks for the next agent

1. If desired, run the actual pull:
   `python3 scripts/pull_harbor_images.py --yes --pull-concurrency 12 --retries 4`
2. For frozen clean205 runs, point `--tasks-root` at the immutable snapshot path rather than mutable `harbor_benchmark/tasks_v4`.
3. If committing, include `scripts/pull_harbor_images.py` and this handoff note; leave pre-existing untracked `.agents/` and `skills-lock.json` alone unless the user explicitly wants them.

## Key decisions

| Decision | Rationale |
| -------- | --------- |
| Query registry manifests before pulling | Satisfies the user requirement to estimate size before any pull begins. |
| Count unique compressed layer/config descriptors | Avoids double-counting shared base layers across many task images. |
| Prompt before pulling unless `--yes` is passed | Makes the estimate-before-pull phase explicit and safe for interactive use. |
| Use `task.toml` `[environment].docker_image` | This is the current Harbor runtime image source of truth. |

## Blockers

- None.

## Suggested next step

Run the script with `--dry-run` on the exact frozen dataset path intended for evaluation, then run it with `--yes` if the reported size is acceptable.

## Handoff: corrected Codex model name

User corrected an important assumption: the GPT/Codex model name is
`gpt-5.3-codex`; we are not using CloudGPT model ids/catalogs.

Changes made:

- Updated `configs/custom_agents_smoke.yaml`:
  - `model_name: gpt-5.3-codex`
  - left `wire_api: responses`, `provider_name: depbench-openai`, and
    `settings_path: ~/.claude/settings.json` as-is.
- Updated the example in `custom_agents/codex.py` to use
  `gpt-5.3-codex`.
- Deleted `custom_agents/cloudgpt_models.json` because it was misleading and
  not used by the runtime path.
- Earlier in this checkpoint, redundant artifact file entries were changed to
  `artifacts: []` in `configs/custom_agents_smoke.yaml` and
  `configs/custom_copilot_smoke.yaml`; Harbor convention collection of
  `/logs/artifacts` still captures `solution_patch.diff`, `git_status.txt`,
  and `worktree_status.txt`.
- Added `configs/custom_claude_v4_smoke.yaml` for a two-task Claude-only v4
  smoke pass, but it has not been run because the user interrupted before that.

Validation run after the correction:

- `uv run python -m py_compile custom_agents/codex.py custom_agents/claude_code.py custom_agents/copilot_cli.py custom_agents/hooks.py`
- YAML validation with `harbor.models.job.config.JobConfig` for:
  - `configs/custom_agents_smoke.yaml`
  - `configs/custom_copilot_smoke.yaml`
  - `configs/custom_claude_v4_smoke.yaml`
- `rg` found no remaining references to `cloudgpt`,
  `gpt-5.3-codex-20260224`, or `gpt-5.5-20260424` under `configs`,
  `custom_agents`, or `pyproject.toml`.

Previous smoke result to keep in mind:

- Job `harbor_jobs/2026-06-25__10-46-37` completed.
- Codex trial failed before editing because it used the wrong model id
  `gpt-5.3-codex-20260224` and the gateway rejected it for Responses.
- Claude Code trial ran end-to-end without agent exception; verifier ran but
  reward was `0.0`.
- Artifact collection worked: Claude trial collected
  `artifacts/logs/artifacts/solution_patch.diff`, `git_status.txt`, and
  `worktree_status.txt`.

Recommended next step:

- Run a Codex-only smoke using the corrected `gpt-5.3-codex` model name, or
  run `configs/custom_agents_smoke.yaml` if testing both Codex and Claude is
  desired despite the longer Claude trial.

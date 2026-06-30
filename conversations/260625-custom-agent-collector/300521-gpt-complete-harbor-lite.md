# Handoff Note — 300521 · gpt · complete-harbor-lite

## Inherited context

- Continued from `conversations/260625-custom-agent-collector/`.
- Prior notes established `custom_agents/` as the local Harbor custom-agent package and moved active smoke configs to YAML under `configs/`.
- Prior notes also warned not to commit run outputs, `.env`, stale JSON prototypes, or unrelated analysis artifacts.

## Work done this session

- [x] Read the handoff skill and the relevant custom-agent collector handoff thread.
- [x] Reviewed the dirty tree and scoped the commit to custom-agent run configs plus `harbor_lite`.
- [x] Committed and pushed `harbor_lite` upstream.
- [x] Registered `harbor_lite` in DepBench as a Git submodule.
- [x] Committed and pushed the DepBench parent branch.
- [x] Ran lightweight validation for staged custom-agent code/configs.

## Current state

| File | Change |
| ---- | ------ |
| `harbor_lite/agents/base.py` | In the `harbor_lite` repo, exposes the prepared task workdir on `LocalAgent` before building agent commands. |
| `harbor_lite/agents/opencode.py` | In the `harbor_lite` repo, passes `--dir=<workdir>` to OpenCode so it stays in the prepared task repo. |
| `.gitmodules` | Added `harbor_lite` submodule pointing to `https://github.com/osslab-pku/harbor_lite`. |
| `harbor_lite` | Added parent gitlink to `8b7464f4912b740fc7eb4f13d357bc431539850d`. |
| `configs/custom_codex_smoke.yaml` | Added Codex-only one-task smoke config using `custom_agents.codex:CustomCodex`. |
| `configs/custom_opencode_smoke.yaml` | Added OpenCode-only one-task smoke config using `custom_agents.opencode:CustomOpenCode`. |
| `configs/deepseek_v4_pro_cloudgpt_codex_opencode.yaml` | Added CloudGPT DeepSeek Codex+OpenCode smoke config. |

Commits pushed:

- `harbor_lite` `main`: `8b7464f` (`Pin OpenCode runs to prepared workdir`)
- DepBench `v4-with-test`: `897b2e2d` (`Add harbor lite and custom agent configs`)

Validation commands run:

```bash
python -m py_compile __init__.py artifacts.py runs.py runtime.py trajectory.py workspace.py agents/*.py
git diff --check
uv run python -m py_compile custom_agents/__init__.py custom_agents/claude_code.py custom_agents/codex.py custom_agents/copilot_cli.py custom_agents/hooks.py custom_agents/opencode.py
uv run python - <<'PY'
from pathlib import Path
import yaml
from harbor.models.job.config import JobConfig
for name in [
    'configs/custom_codex_smoke.yaml',
    'configs/custom_opencode_smoke.yaml',
    'configs/deepseek_v4_pro_cloudgpt_codex_opencode.yaml',
]:
    cfg = JobConfig.model_validate(yaml.safe_load(Path(name).read_text()))
    print(name, 'ok', len(cfg.agents), [a.import_path for a in cfg.agents])
PY
git diff --check --cached
```

## Open tasks for the next agent

1. Decide whether `.agents/` should be committed. It remains untracked because the user requested custom agents and `harbor_lite`, and `.agents/` is repository-local skill/tooling state.
2. Decide whether to remove or ignore stale `_run_configs/custom_openai_20260625/*.json`; they remain untracked and include superseded dated Codex model ids from earlier experiments.
3. Leave unrelated dirty files alone unless the user explicitly asks to include them: `scripts/traj_analysis/run_annotation.py`, `VERDICT.json` files, trajectory parsing scratch files, `paper/`, and other analysis artifacts remain uncommitted.

## Key decisions

| Decision | Rationale |
| -------- | --------- |
| Committed `harbor_lite` as a submodule | It already has its own Git repo and remote, and the user asked to push it; a gitlink records the exact pushed commit without vendoring the nested repository. |
| Included only active YAML configs | Prior handoffs described JSON configs under `_run_configs/custom_openai_20260625/` as superseded, and two still contain rejected dated model ids. |
| Left `.agents/` untracked | The request said custom agents and `harbor_lite`; `.agents/` is local agent skill infrastructure rather than runtime custom-agent code. |

## Blockers

- None for the requested commit/push.

## Suggested next step

Run a one-task smoke with `configs/custom_codex_smoke.yaml` or `configs/custom_opencode_smoke.yaml` after confirming the desired Docker socket and credentials are available.

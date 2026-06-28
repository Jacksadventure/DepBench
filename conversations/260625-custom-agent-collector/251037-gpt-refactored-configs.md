# Handoff Note — 251037 · gpt · refactored-configs

## Inherited context

- Continued from `conversations/260625-custom-agent-collector/251012-gpt-complete-custom-agents.md`.
- User requested config conversion to YAML and design/implementation guidance for disabling Copilot CLI web tools.
- Earlier interrupted smoke runs left untracked Harbor job outputs under `harbor_jobs/2026-06-25__10-*`; these were not modified or cleaned.

## Work done this session

- [x] Converted root custom-agent smoke configs from JSON to YAML.
- [x] Deleted the root JSON smoke configs.
- [x] Added `disable_web_tools` support to `custom_agents/copilot_cli.py`.
- [x] Validated syntax and Harbor config schema parsing.

## Current state

| File | Change |
| ---- | ------ |
| `configs/custom_agents_smoke.yaml` | YAML smoke config for `CustomCodex` + `CustomClaudeCode`. |
| `configs/custom_copilot_smoke.yaml` | YAML smoke config for `CustomCopilotCli`, with `disable_web_tools: true`. |
| `configs/custom_agents_smoke.json` | Deleted. |
| `configs/custom_copilot_smoke.json` | Deleted. |
| `custom_agents/copilot_cli.py` | Added `disable_web_tools` and `web_tool_names`; `build_cli_flags()` appends Copilot CLI denial flags. |

Validation commands run:

```bash
uv run python -m py_compile custom_agents/copilot_cli.py custom_agents/codex.py custom_agents/claude_code.py custom_agents/hooks.py
uv run python - <<'PY'
import yaml
from pathlib import Path
from harbor.models.job.config import JobConfig
for p in sorted(Path('configs').glob('custom*_smoke.yaml')):
    cfg = JobConfig.model_validate(yaml.safe_load(p.read_text()))
    print(p, len(cfg.agents), [a.import_path for a in cfg.agents])
PY
```

## Open tasks for the next agent

1. If the user wants another smoke run, use:
   `uv run harbor run -c configs/custom_agents_smoke.yaml -y`
2. For Copilot CLI, set a real token/API key before running:
   `COPILOT_API_KEY` in `configs/custom_copilot_smoke.yaml` or `api_key` in agent kwargs.
3. Do not commit `harbor_jobs/2026-06-25__10-*` unless explicitly asked; they are run outputs.

## Key decisions

| Decision | Rationale |
| -------- | --------- |
| Used YAML under `configs/` | Matches user request and keeps reusable configs out of `_run_configs/`. |
| Implemented Copilot web disable via CLI flags | Copilot CLI exposes tool and URL controls, not a single native `--disable-web-tools` flag. |
| Used `--deny-url='*'`, `--disable-builtin-mcps`, and `--excluded-tools=...` together | URL denial blocks web access even when `--yolo` implies allowed URLs; MCP/tool exclusions reduce the model's available web/search surface. |

## Blockers

- No new Harbor smoke run was completed after this YAML conversion; the previous launch was user-interrupted.

## Suggested next step

Run `uv run harbor run -c configs/custom_agents_smoke.yaml -y` after confirming the desired Codex model supports the Responses API.

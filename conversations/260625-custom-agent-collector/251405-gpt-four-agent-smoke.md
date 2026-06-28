# Four-Agent Smoke Config

Date: 2026-06-25

## Request

Update the smoke config to test Codex, Claude Code, OpenCode, and Copilot CLI, then run the smoke tests.

## Config

Updated `configs/custom_agents_smoke.yaml` to include four agents on `actix__actix__554` from `harbor_benchmark/tasks_v4`:

- `custom_agents.codex:CustomCodex`, model `gpt-5.3-codex`, Codex CLI `0.130.0`, OpenAI-compatible gateway from `~/.claude/settings.json`
- `custom_agents.claude_code:CustomClaudeCode`, model `claude-opus-4-8`
- `custom_agents.opencode:CustomOpenCode`, model `gpt-5.3-codex`, OpenAI-compatible gateway from `~/.claude/settings.json`, web tools disabled
- `custom_agents.copilot_cli:CustomCopilotCli`, model `auto`, Copilot CLI `1.0.63`, web tools disabled

Important correction: the first combined run tried OpenCode as `github-copilot/gpt-5.3-codex`; GitHub Copilot's Responses endpoint rejected that model with `model_not_supported`. The combined smoke config now routes OpenCode through the OpenAI-compatible gateway instead, while Copilot CLI remains the Copilot-auth smoke leg.

## Validation

Commands run:

```bash
uv run python -m py_compile custom_agents/opencode.py custom_agents/copilot_cli.py custom_agents/codex.py custom_agents/claude_code.py custom_agents/hooks.py
uv run python - <<'PY'
from pathlib import Path
import yaml
from harbor.models.job.config import JobConfig
for name in ['configs/custom_agents_smoke.yaml', 'configs/custom_opencode_smoke.yaml']:
    JobConfig.model_validate(yaml.safe_load(Path(name).read_text()))
    print(name, 'ok')
PY
```

Both passed.

## Harbor Runs

Combined four-agent run:

```bash
set -a; . ./.env; set +a; uv run harbor run -c configs/custom_agents_smoke.yaml -y
```

Job: `harbor_jobs/2026-06-25__13-35-41`

- Codex: 1 trial, 0 exceptions, reward 0, artifacts collected
- Claude Code: 1 trial, 0 exceptions, reward 0, artifacts collected
- OpenCode via `github-copilot/gpt-5.3-codex`: 1 trial, 1 `NonZeroAgentExitCodeError`; `opencode.txt` reported `model_not_supported` from `https://api.githubcopilot.com/responses`
- Copilot CLI: 1 trial, 0 exceptions, reward 0, artifacts collected

Focused OpenCode rerun after config correction:

```bash
set -a; . ./.env; set +a; uv run harbor run -c configs/custom_opencode_smoke.yaml -y
```

Job: `harbor_jobs/2026-06-25__13-51-04`

- OpenCode via `openai/gpt-5.3-codex`: 1 trial, 0 exceptions, reward 0, artifacts collected

## Notes

- `.env` was sourced for token aliases but not printed.
- Harbor's `/logs/artifacts` convention collected `solution_patch.diff`, `git_status.txt`, and `worktree_status.txt` for all non-exception agent runs.
- `custom_opencode_copilot_smoke.yaml` still exists as a Copilot-provider experiment, but `github-copilot/gpt-5.3-codex` was proven unsupported by the Copilot Responses endpoint in this run.

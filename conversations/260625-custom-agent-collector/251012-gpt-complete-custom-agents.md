# Handoff Note — 251012 · gpt · complete-custom-agents

## Inherited context

- Read the handoff skill and created a new thread because the latest prior thread, `conversations/260625-harbor-image-pull/`, was about image pulling rather than custom agent trajectory collection.
- Read `/home/v-runzhihe/msr4agent/custom_agents/` and reused its relevant pattern: Harbor custom agents loaded by `import_path`, hook-based pre/post run behavior, raw session/trajectory files under `agent/`, and final patch artifacts under `artifacts/`.
- Confirmed this repo already had `_run_configs/codex_maestro_agent.py`, but it was an ad hoc provider shim rather than a reusable local package.

## Work done this session

- [x] Added a local `custom_agents/` package for DepBench.
- [x] Added `GitArtifactMixin` and `HookedAgent` to capture final repository deltas into Harbor artifacts.
- [x] Added `CustomOpenAICodex` for OpenAI-compatible Codex runs.
- [x] Added `CustomAnthropicClaudeCode` for Anthropic-compatible Claude Code runs.
- [x] Stored the user-provided CloudGPT model roster in `custom_agents/cloudgpt_models.json`.
- [x] Added smoke Harbor configs for Codex, Claude Code, and a two-agent run.
- [x] Validated Python syntax and Harbor `JobConfig` schema parsing.

## Current state

| File | Change |
| ---- | ------ |
| `custom_agents/__init__.py` | New package marker. |
| `custom_agents/hooks.py` | Hook wrapper plus `solution_patch.diff`, `git_status.txt`, and `worktree_status.txt` capture. |
| `custom_agents/codex_openai.py` | Codex wrapper for OpenAI-compatible endpoints; can derive `/openai/v1` URL and API key from `~/.claude/settings.json`. |
| `custom_agents/claude_anthropic.py` | Claude Code wrapper for Anthropic-compatible endpoints; reads `~/.claude/settings.json` if explicit env is not provided. |
| `custom_agents/cloudgpt_models.json` | 68 model entries grouped by provider/category with supported API surfaces. |
| `_run_configs/custom_openai_20260625/codex_custom_openai_smoke.json` | One-task Codex smoke config. |
| `_run_configs/custom_openai_20260625/claude_custom_anthropic_smoke.json` | One-task Claude Code smoke config. |
| `_run_configs/custom_openai_20260625/custom_endpoint_multi_agent_smoke.json` | One-task, two-agent smoke config. |

Verification commands run:

```bash
uv run python -m py_compile custom_agents/__init__.py custom_agents/hooks.py custom_agents/codex_openai.py custom_agents/claude_anthropic.py
uv run python - <<'PY'
import json
from pathlib import Path
from harbor.models.job.config import JobConfig
for p in sorted(Path('_run_configs/custom_openai_20260625').glob('*.json')):
    cfg = JobConfig.model_validate(json.loads(p.read_text()))
    print(p.name, len(cfg.agents), [a.model_name for a in cfg.agents])
PY
```

Also checked `$HOME/.claude/settings.json`; it contains `ANTHROPIC_BASE_URL=http://10.12.1.193:40441`, `ANTHROPIC_MODEL=claude-opus-4-8`, and an auth token. The token was not copied into checked-in configs.

## Open tasks for the next agent

1. Run an actual Harbor smoke trial once Docker/socket state is ready, for example:
   `uv run harbor run -c _run_configs/custom_openai_20260625/custom_endpoint_multi_agent_smoke.json -y`
2. Inspect the resulting trial dirs and confirm:
   `agent/codex.txt`, `agent/trajectory.json`, `agent/sessions/`, `agent/claude-code.txt`, `agent/sessions/projects/...`, `artifacts/solution_patch.diff`, and `artifacts/git_status.txt` are present as expected.
3. If the OpenAI route uses a different path than `/openai/v1`, pass explicit `OPENAI_BASE_URL` in the Codex agent `env` or `base_url` in kwargs.
4. If committing, include only the new custom-agent/config/model files plus this handoff note; leave unrelated untracked files such as `.agents/`, `main.py`, `pyproject.toml`, `uv.lock`, and `skills-lock.json` alone unless the user explicitly wants them.

## Key decisions

| Decision | Rationale |
| -------- | --------- |
| Added `custom_agents/` instead of extending `_run_configs/codex_maestro_agent.py` | Package import paths are easier to reuse across configs and agents. |
| Read `~/.claude/settings.json` at runtime | Avoids committing endpoint tokens while matching the user's existing local setup. |
| Capture patch artifacts via `git add -A` + diff from saved `HEAD` | Preserves staged, unstaged, and untracked agent changes without requiring an agent commit. |
| Stored model roster as JSON with API metadata | Easier to consume from scripts than a Python `Literal` copied into agent code. |

## Blockers

- No real Harbor trial was launched in this session. The implementation was validated by import, syntax, settings derivation, model JSON parsing, and Harbor config schema parsing only.

## Suggested next step

Run the two-agent smoke config on one low-cost task and verify the trial artifact layout before launching a larger clean205 evaluation.

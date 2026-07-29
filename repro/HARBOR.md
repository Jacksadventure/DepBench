# Running the release with Harbor

This release can be consumed directly by Harbor after downloading the task
directories from Hugging Face. The downloaded `dataset/tasks/` directory follows
Harbor's task layout and each `task.toml` points to a prebuilt Docker image.

## Install

From the release root:

```bash
python3 -m pip install .
python3 repro/download_benchmark.py
```

This installs the release helper package and dependencies, then downloads the
pinned 203-task benchmark snapshot.

## Generate a Harbor config

Template configs for the reported configurations are already under `repro/examples/`.

Create a config for one task:

```bash
python3 repro/make_harbor_config.py \
  --agent codex \
  --model gpt-5.5 \
  --task 29ki__29k__3418 \
  --output repro/examples/codex_gpt55_one_task.json
```

Create a config for all 203 tasks:

```bash
python3 repro/make_harbor_config.py \
  --agent copilot_cli \
  --model gpt-5.5 \
  --all-tasks \
  --concurrency 10 \
  --output repro/examples/copilot_gpt55_all_tasks.json
```

The generated config uses:

- `dataset/tasks` as the task source
- Docker environments with `force_build=false`
- the task image named in each `task.toml`
- the custom agent adapters in `custom_agents/`

## Run Harbor

After editing the generated config with your own endpoint/auth settings, run:

```bash
harbor run -c repro/examples/codex_gpt55_one_task.json -y
```

The run output is written to the `jobs_dir` configured in the JSON file. Keep
raw outputs outside the release branch. The release publishes only sanitized
job archives that exclude authentication, installation, session, cache, and
SQLite state.

## Agent adapters

The release includes these Harbor adapters:

| Agent option | Import path |
|---|---|
| `codex` | `custom_agents.codex:CustomCodex` |
| `copilot_cli` | `custom_agents.copilot_cli:CustomCopilotCli` |
| `opencode` | `custom_agents.opencode:CustomOpenCode` |
| `claude_code` | `custom_agents.claude_code:CustomClaudeCode` |

The adapters collect agent logs and final repository diffs into Harbor
artifacts. Supply credentials and model-provider endpoints at runtime through
environment variables or another approved secret-injection mechanism. The
generator and checked-in templates intentionally never copy local environment
values into JSON configs.

## Included templates

| Template | Configuration |
|---|---|
| `repro/examples/claude_code__claude48.json` | Claude Code + Claude Opus 4.8 |
| `repro/examples/copilot_cli__claude48.json` | Copilot CLI + Claude Opus 4.8 |
| `repro/examples/opencode__claude48.json` | OpenCode + Claude Opus 4.8 |
| `repro/examples/claude_code__gemini35flash.json` | Claude Code + Gemini 3.5 Flash |
| `repro/examples/copilot_cli__gemini35flash.json` | Copilot CLI + Gemini 3.5 Flash |
| `repro/examples/opencode__gemini35flash.json` | OpenCode + Gemini 3.5 Flash |
| `repro/examples/claude_code__gpt55.json` | Claude Code + GPT-5.5 |
| `repro/examples/codex__gpt55.json` | Codex + GPT-5.5 |
| `repro/examples/copilot_cli__gpt55.json` | Copilot CLI + GPT-5.5 |
| `repro/examples/opencode__gpt55.json` | OpenCode + GPT-5.5 |

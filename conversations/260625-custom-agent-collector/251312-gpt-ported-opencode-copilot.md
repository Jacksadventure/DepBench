## Handoff: custom OpenCode with Copilot support

User clarified that `../msr4agent/` was the intended original implementation
source. I ported `../msr4agent/custom_agents/opencode.py` into this repo as
`custom_agents/opencode.py` and adapted it to the local custom-agent harness.

Implemented:

- Added `custom_agents/opencode.py`.
  - Subclasses Harbor's installed `OpenCode`.
  - Mixes in `Artifacts`/`Hooked` behavior so `/logs/artifacts` captures
    `solution_patch.diff`, `git_status.txt`, and `worktree_status.txt`.
  - Uses system Node/npm install path from msr4agent instead of the stock nvm
    path.
  - Installs `opencode-ai` with `@latest` unless a config explicitly supplies
    `version`.
  - Preserves OpenCode's JSON stream/ATIF trajectory behavior through the
    parent class parser.
  - Supports `disable_web_tools` via OpenCode permission config:
    `webfetch`, `websearch`, and `question` set to `deny`.

- OpenAI-compatible mode:
  - Bare model names normalize to `openai/<model>`, e.g.
    `gpt-5.3-codex` -> `openai/gpt-5.3-codex`.
  - Resolves endpoint/API key from kwargs, `agent.env`, process env, or
    `~/.claude/settings.json`.
  - Writes OpenCode provider config with
    `provider.openai.options.baseURL`.

- GitHub Copilot subscription mode:
  - Use `model_name: github-copilot/<model>`, e.g.
    `github-copilot/gpt-5.3-codex`, or set
    `default_provider: github-copilot` for bare names.
  - Does **not** require `OPENAI_BASE_URL`.
  - Resolves token from `api_key`, `COPILOT_GITHUB_TOKEN`,
    `COPILOT_API_KEY`, `GH_TOKEN`, or `GITHUB_TOKEN`.
  - Exports the token as `GITHUB_TOKEN`, `GH_TOKEN`,
    `COPILOT_GITHUB_TOKEN`, and `COPILOT_API_KEY` for the OpenCode process.

- Added configs:
  - `configs/custom_opencode_smoke.yaml` for OpenAI-compatible OpenCode mode.
  - `configs/custom_opencode_copilot_smoke.yaml` for Copilot subscription mode.

Validation:

- `uv run python -m py_compile custom_agents/opencode.py custom_agents/copilot_cli.py custom_agents/codex.py custom_agents/claude_code.py custom_agents/hooks.py`
- Harbor `JobConfig` YAML validation for:
  - `configs/custom_opencode_smoke.yaml`
  - `configs/custom_opencode_copilot_smoke.yaml`
  - `configs/custom_agents_smoke.yaml`
  - `configs/custom_copilot_smoke.yaml`
- Import-level checks:
  - OpenAI mode normalizes `gpt-5.3-codex` to `openai/gpt-5.3-codex`.
  - OpenAI mode generated config includes `baseURL`.
  - Copilot mode keeps `github-copilot/gpt-5.3-codex`, resolves the token,
    and generates no OpenAI provider config.

Smoke status:

- Earlier corrected Codex/Claude smoke `harbor_jobs/2026-06-25__13-01-46`
  completed with no agent exceptions; verifier and artifact collection worked,
  reward remained `0.0`.
- A first OpenCode smoke `harbor_jobs/2026-06-25__13-08-34` failed during setup
  because the inherited msr4agent pin `opencode-ai@0.16.7` was not available
  in the observed npm registry. The wrapper now defaults to latest instead.
- I did **not** run the Copilot OpenCode smoke because this shell has no
  `COPILOT_GITHUB_TOKEN`, `COPILOT_API_KEY`, `GH_TOKEN`, or `GITHUB_TOKEN`
  exported.

Recommended next step:

- Run `uv run harbor run -c configs/custom_opencode_copilot_smoke.yaml -y`
  after providing a Copilot token in the config or host environment.

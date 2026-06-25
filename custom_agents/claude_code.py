"""Claude Code agent for Anthropic-compatible DepBench endpoints."""

from __future__ import annotations

import json
from pathlib import Path

from harbor.agents.installed.claude_code import ClaudeCode as HarborClaudeCode

from custom_agents.hooks import Artifacts, Hooked


DEFAULT_SETTINGS_PATH = Path.home() / ".claude" / "settings.json"


class CustomClaudeCode(Artifacts, Hooked, HarborClaudeCode):
    """Claude Code routed to a custom Anthropic-compatible endpoint.

    The wrapper accepts explicit Harbor ``agent.env`` values, but also falls
    back to ``~/.claude/settings.json`` so local runs can reuse the same
    endpoint settings as interactive Claude Code.
    """

    def __init__(
        self,
        *args,
        base_url: str | None = None,
        auth_token: str | None = None,
        settings_path: str | None = None,
        disable_nonessential_traffic: bool = True,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._base_url_arg = base_url
        self._auth_token_arg = auth_token
        self._settings_path = Path(settings_path).expanduser() if settings_path else DEFAULT_SETTINGS_PATH
        self._disable_nonessential_traffic = disable_nonessential_traffic

    @staticmethod
    def name() -> str:
        return "custom-claude-code"

    def _settings(self) -> dict[str, str]:
        try:
            data = json.loads(self._settings_path.read_text())
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid Claude settings JSON: {self._settings_path}") from exc

        env = data.get("env", {})
        if not isinstance(env, dict):
            return {}
        return {str(k): str(v) for k, v in env.items() if v is not None}

    def _env(self, key: str, settings: dict[str, str]) -> str | None:
        return self._get_env(key) or settings.get(key)

    def _model(self, settings: dict[str, str]) -> str | None:
        if self.model_name:
            return self.model_name.split("/", 1)[-1] if "/" in self.model_name else self.model_name
        return settings.get("ANTHROPIC_MODEL")

    async def run(self, instruction, environment, context) -> None:
        settings = self._settings()
        base_url = self._base_url_arg or self._env("ANTHROPIC_BASE_URL", settings)
        auth_token = (
            self._auth_token_arg
            or self._env("ANTHROPIC_AUTH_TOKEN", settings)
            or self._env("ANTHROPIC_API_KEY", settings)
        )
        model = self._model(settings)

        if not base_url:
            raise ValueError(
                "CustomClaudeCode requires base_url, ANTHROPIC_BASE_URL, "
                f"or {self._settings_path}"
            )
        if not auth_token:
            raise ValueError(
                "CustomClaudeCode requires auth_token, ANTHROPIC_AUTH_TOKEN, "
                "or ANTHROPIC_API_KEY"
            )
        if not model:
            raise ValueError(
                "CustomClaudeCode requires model_name or ANTHROPIC_MODEL"
            )

        self._extra_env["ANTHROPIC_BASE_URL"] = base_url.rstrip("/")
        self._extra_env["ANTHROPIC_AUTH_TOKEN"] = auth_token
        self._extra_env["ANTHROPIC_API_KEY"] = auth_token
        self._extra_env["ANTHROPIC_MODEL"] = model
        self._extra_env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = model
        self._extra_env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = model
        self._extra_env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = model
        self._extra_env["CLAUDE_CODE_SUBAGENT_MODEL"] = model
        self._extra_env["CLAUDE_CODE_ATTRIBUTION_HEADER"] = "0"
        self._extra_env["CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION"] = "false"
        self._extra_env["CLAUDE_CODE_DISABLE_TERMINAL_TITLE"] = "true"
        self._extra_env["CLAUDE_CODE_ENABLE_AWAY_SUMMARY"] = "0"
        if self._disable_nonessential_traffic:
            self._extra_env["DISABLE_NON_ESSENTIAL_MODEL_CALLS"] = "1"
            self._extra_env["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"

        original_model_name = self.model_name
        self.model_name = model
        try:
            return await super().run(instruction, environment, context)
        finally:
            self.model_name = original_model_name


ClaudeCode = CustomClaudeCode
CustomAnthropicClaudeCode = CustomClaudeCode

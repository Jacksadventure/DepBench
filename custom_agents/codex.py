"""Codex agents for OpenAI-compatible DepBench endpoints.

The classes here are loaded by Harbor through ``agent.import_path``. They keep
Harbor's stock Codex behavior, including raw ``codex.txt``, ATIF
``trajectory.json``, and copied ``CODEX_HOME/sessions`` files, while adding:

* explicit OpenAI-compatible provider configuration;
* final repository patch/status capture in ``artifacts/``.
"""

from __future__ import annotations

import json
import shlex
from pathlib import Path

from harbor.agents.installed.codex import Codex as HarborCodex

from custom_agents.hooks import Artifacts, Hooked


DEFAULT_CLAUDE_SETTINGS_PATH = Path.home() / ".claude" / "settings.json"


class CustomCodex(Artifacts, Hooked, HarborCodex):
    """Codex routed to a custom OpenAI-compatible endpoint.

    Harbor config example:

    .. code-block:: json

        {
          "import_path": "custom_agents.codex:CustomCodex",
          "model_name": "gpt-5.3-codex",
          "kwargs": {
            "version": "0.130.0",
            "reasoning_effort": "high",
            "provider_name": "depbench-openai",
            "wire_api": "responses",
            "requires_openai_auth": false
          },
          "env": {
            "OPENAI_BASE_URL": "http://127.0.0.1:23333",
            "OPENAI_API_KEY": "dummy"
          }
        }
    """

    def __init__(
        self,
        *args,
        provider_name: str = "depbench-openai",
        base_url: str | None = None,
        api_key: str | None = None,
        wire_api: str = "responses",
        requires_openai_auth: bool = False,
        supports_websockets: bool | None = False,
        request_max_retries: int = 3,
        stream_max_retries: int = 1,
        disable_web_tools: bool = False,
        settings_path: str | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._provider_name = provider_name
        self._base_url_arg = base_url
        self._api_key_arg = api_key
        self._wire_api = wire_api
        self._requires_openai_auth = requires_openai_auth
        self._supports_websockets = supports_websockets
        self._request_max_retries = request_max_retries
        self._stream_max_retries = stream_max_retries
        self._disable_web_tools = disable_web_tools
        self._settings_path = (
            Path(settings_path).expanduser()
            if settings_path
            else DEFAULT_CLAUDE_SETTINGS_PATH
        )

    @staticmethod
    def name() -> str:
        return "custom-codex"

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

    def _base_url(self) -> str:
        settings = self._settings()
        anthropic_base_url = settings.get("ANTHROPIC_BASE_URL")
        base_url = (
            self._base_url_arg
            or self._get_env("OPENAI_BASE_URL")
            or self._get_env("CODEX_BASE_URL")
            or self._get_env("CODEX_MAESTRO_BASE_URL")
        )
        if not base_url and anthropic_base_url:
            base_url = anthropic_base_url
        if not base_url:
            raise ValueError(
                "CustomCodex requires base_url, OPENAI_BASE_URL, "
                "CODEX_BASE_URL, CODEX_MAESTRO_BASE_URL, or an "
                f"ANTHROPIC_BASE_URL in {self._settings_path}"
            )
        return base_url.rstrip("/")

    def _api_key(self) -> str:
        settings = self._settings()
        return (
            self._api_key_arg
            or self._get_env("OPENAI_API_KEY")
            or self._get_env("CODEX_API_KEY")
            or settings.get("OPENAI_API_KEY")
            or settings.get("ANTHROPIC_AUTH_TOKEN")
            or settings.get("ANTHROPIC_API_KEY")
            or "dummy"
        )

    @staticmethod
    def _toml_bool(value: bool) -> str:
        return "true" if value else "false"

    def _provider_config(self) -> list[str]:
        if not self.model_name:
            raise ValueError("CustomCodex requires model_name")

        model = self.model_name.split("/")[-1]
        lines = [
            f'model = "{model}"',
            f'model_provider = "{self._provider_name}"',
            "",
            f"[model_providers.{self._provider_name}]",
            f'name = "{self._provider_name}"',
            f'base_url = "{self._base_url()}"',
            f'wire_api = "{self._wire_api}"',
            f"requires_openai_auth = {self._toml_bool(self._requires_openai_auth)}",
            'env_key = "OPENAI_API_KEY"',
            f"request_max_retries = {self._request_max_retries}",
            "retry_429 = true",
            f"stream_max_retries = {self._stream_max_retries}",
        ]
        if self._supports_websockets is not None:
            lines.append(
                f"supports_websockets = {self._toml_bool(self._supports_websockets)}"
            )
        lines.extend(
            [
                "",
                "[features]",
                "unified_exec = true",
                "",
            ]
        )
        return lines

    def _build_register_mcp_servers_command(self) -> str | None:
        lines = self._provider_config()

        for server in self.mcp_servers or []:
            lines.append(f"[mcp_servers.{server.name}]")
            if server.transport == "stdio":
                cmd_parts = [server.command] + server.args if server.command else []
                lines.append(f'command = "{shlex.join(cmd_parts)}"')
            else:
                lines.append(f'url = "{server.url}"')
            lines.append("")

        config = "\n".join(lines)
        return f"cat > \"$CODEX_HOME/config.toml\" <<'EOF'\n{config}\nEOF"

    def build_cli_flags(self) -> str:
        cli_flags = super().build_cli_flags()
        parts: list[str] = []
        if self._disable_web_tools:
            parts.append("-c web_search=disabled")
        if cli_flags:
            parts.append(cli_flags)
        return " ".join(parts)

    async def run(self, instruction, environment, context) -> None:
        self._extra_env["OPENAI_BASE_URL"] = self._base_url()
        self._extra_env["OPENAI_API_KEY"] = self._api_key()
        self._extra_env["CODEX_FORCE_API_KEY"] = "1"
        return await super().run(instruction, environment, context)


class CustomMaestro(CustomCodex):
    """Compatibility alias for the current Maestro OpenAI-compatible proxy."""

    @staticmethod
    def name() -> str:
        return "custom-maestro-codex"

    def _base_url(self) -> str:
        base_url = self._base_url_arg or self._get_env("CODEX_MAESTRO_BASE_URL")
        if base_url:
            return base_url.rstrip("/")
        return super()._base_url()


Codex = CustomCodex
Maestro = CustomMaestro
CustomOpenAICodex = CustomCodex
MaestroCodex = CustomMaestro

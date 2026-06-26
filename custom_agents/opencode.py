"""OpenCode agent for OpenAI-compatible and Copilot-backed DepBench runs."""

from __future__ import annotations

import copy
import json
import shlex
from pathlib import Path
from typing import Any

from harbor.agents.installed.base import with_prompt_template
from harbor.agents.installed.opencode import OpenCode as HarborOpenCode
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

from custom_agents.hooks import Artifacts, Hooked


DEFAULT_SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
NO_WEB_CONFIG = {
    "permission": {
        "webfetch": "deny",
        "websearch": "deny",
        "question": "deny",
    }
}
COPILOT_TOKEN_KEYS = (
    "COPILOT_GITHUB_TOKEN",
    "COPILOT_API_KEY",
    "GH_TOKEN",
    "GITHUB_TOKEN",
)


class CustomOpenCode(Artifacts, Hooked, HarborOpenCode):
    """OpenCode routed through OpenAI-compatible or GitHub Copilot auth.

    This ports the OpenCode wrapper from ``../msr4agent/custom_agents`` while
    adding the DepBench artifact hook used by the other custom agents here.
    Bare model names are normalized to ``openai/<model>`` by default because
    OpenCode expects ``provider/model``. Use ``github-copilot/<model>`` or set
    ``default_provider: github-copilot`` to run through a Copilot subscription.
    """

    def __init__(
        self,
        *args,
        api_key: str | None = None,
        base_url: str | None = None,
        settings_path: str | None = None,
        default_provider: str = "openai",
        disable_web_tools: bool = False,
        version: str | None = None,
        opencode_config: dict[str, Any] | None = None,
        **kwargs,
    ):
        config = copy.deepcopy(opencode_config or {})
        if disable_web_tools:
            config = self._deep_merge(copy.deepcopy(NO_WEB_CONFIG), config)

        super().__init__(
            *args,
            version=version,
            opencode_config=config,
            **kwargs,
        )
        self._api_key_arg = api_key
        self._base_url_arg = base_url
        self._settings_path = (
            Path(settings_path).expanduser() if settings_path else DEFAULT_SETTINGS_PATH
        )
        self._default_provider = default_provider
        self._disable_web_tools = disable_web_tools

    @staticmethod
    def name() -> str:
        return "custom-opencode"

    def get_version_command(self) -> str | None:
        return '. ~/.nvm/nvm.sh; nvm use 22 >/dev/null; opencode --version'

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

    def _base_url(self, settings: dict[str, str]) -> str:
        base_url = (
            self._base_url_arg
            or self._get_env("OPENAI_BASE_URL")
            or self._get_env("CODEX_BASE_URL")
            or self._get_env("CODEX_MAESTRO_BASE_URL")
            or settings.get("OPENAI_BASE_URL")
            or settings.get("ANTHROPIC_BASE_URL")
        )
        if not base_url:
            raise ValueError(
                "CustomOpenCode requires base_url, OPENAI_BASE_URL, "
                "CODEX_BASE_URL, CODEX_MAESTRO_BASE_URL, or endpoint settings"
            )
        return base_url.rstrip("/")

    def _api_key(self, settings: dict[str, str]) -> str:
        return (
            self._api_key_arg
            or self._get_env("OPENAI_API_KEY")
            or self._get_env("CODEX_API_KEY")
            or settings.get("OPENAI_API_KEY")
            or settings.get("ANTHROPIC_AUTH_TOKEN")
            or settings.get("ANTHROPIC_API_KEY")
            or "dummy"
        )

    def _copilot_token(self, settings: dict[str, str]) -> str | None:
        if self._api_key_arg:
            return self._api_key_arg
        for key in COPILOT_TOKEN_KEYS:
            value = self._get_env(key) or settings.get(key)
            if value:
                return value
        return None

    def _model_name(self) -> str:
        if not self.model_name:
            raise ValueError("CustomOpenCode requires model_name")
        if "/" in self.model_name:
            return self.model_name
        return f"{self._default_provider}/{self.model_name}"

    @staticmethod
    def _provider_model(model_name: str) -> tuple[str, str]:
        if "/" not in model_name:
            raise ValueError("OpenCode model name must be in provider/model format")
        return model_name.split("/", 1)

    def _opencode_config_with_endpoint(
        self, model_name: str, base_url: str | None
    ) -> dict[str, Any]:
        config = copy.deepcopy(self._opencode_config)
        provider, model_id = self._provider_model(model_name)
        if provider == "openai" and base_url:
            provider_config: dict[str, Any] = {"models": {model_id: {}}}
            provider_config.setdefault("options", {})["baseURL"] = base_url
            generated = {"provider": {"openai": provider_config}}
            config = self._deep_merge(generated, config)
        return config

    def _build_register_config_command_for(
        self, model_name: str, base_url: str | None = None
    ) -> str | None:
        config: dict[str, Any] = {}

        if self.mcp_servers:
            mcp: dict[str, dict[str, Any]] = {}
            for server in self.mcp_servers:
                if server.transport == "stdio":
                    cmd_list = [server.command] + server.args if server.command else []
                    mcp[server.name] = {"type": "local", "command": cmd_list}
                else:
                    mcp[server.name] = {"type": "remote", "url": server.url}
            config["mcp"] = mcp

        config = self._deep_merge(
            config, self._opencode_config_with_endpoint(model_name, base_url)
        )
        if not config:
            return None

        config_json = json.dumps(config, indent=2)
        return (
            "mkdir -p ~/.config/opencode && "
            f"echo {shlex.quote(config_json)} > ~/.config/opencode/opencode.json"
        )

    async def install(self, environment: BaseEnvironment) -> None:
        await self.exec_as_root(
            environment,
            command=(
                "apt-get update && apt-get install -y curl ca-certificates"
            ),
            env={"DEBIAN_FRONTEND": "noninteractive"},
        )
        version_spec = f"@{self._version}" if self._version else "@latest"
        await self.exec_as_agent(
            environment,
            command=(
                "set -euo pipefail; "
                "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash && "
                'export NVM_DIR="$HOME/.nvm" && '
                '\\. "$NVM_DIR/nvm.sh" || true && '
                "command -v nvm >/dev/null 2>&1 || { echo 'Error: NVM failed to load' >&2; exit 1; } && "
                "nvm install 22 && nvm use 22 >/dev/null && npm -v && "
                f"npm install -g opencode-ai{version_spec} && "
                "opencode --version"
            ),
        )

    def _error_messages(self) -> list[str]:
        output_path = self.logs_dir / self._OUTPUT_FILENAME
        if not output_path.exists():
            return []

        messages: list[str] = []
        for line in output_path.read_text(errors="ignore").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") != "error":
                continue
            error = event.get("error") or event.get("data") or event
            if isinstance(error, dict):
                message = (
                    error.get("message")
                    or error.get("error")
                    or error.get("text")
                    or json.dumps(error, sort_keys=True)
                )
            else:
                message = str(error)
            messages.append(message)
        return messages

    async def _run_opencode(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        self._instruction = instruction
        escaped_instruction = shlex.quote(instruction)
        settings = self._settings()
        model_name = self._model_name()
        provider, _ = self._provider_model(model_name)

        env = {"OPENCODE_FAKE_VCS": "git"}
        base_url: str | None = None

        if provider == "openai":
            base_url = self._base_url(settings)
            env["OPENAI_API_KEY"] = self._api_key(settings)
            env["OPENAI_BASE_URL"] = base_url
        elif provider == "github-copilot":
            token = self._copilot_token(settings)
            if not token:
                raise ValueError(
                    "CustomOpenCode with github-copilot requires api_key or one of "
                    "COPILOT_GITHUB_TOKEN, COPILOT_API_KEY, GH_TOKEN, GITHUB_TOKEN"
                )
            env["GITHUB_TOKEN"] = token
            env["GH_TOKEN"] = token
            env["COPILOT_GITHUB_TOKEN"] = token
            env["COPILOT_API_KEY"] = token

        for key in (
            "OPENAI_API_KEY",
            "OPENAI_BASE_URL",
            "ANTHROPIC_API_KEY",
            "ANTHROPIC_BASE_URL",
            "GEMINI_API_KEY",
            "GOOGLE_GENERATIVE_AI_API_KEY",
            "GOOGLE_API_KEY",
            "OPENROUTER_API_KEY",
        ):
            value = self._get_env(key) or settings.get(key)
            if value and key not in env:
                env[key] = value

        skills_command = self._build_register_skills_command()
        if skills_command:
            await self.exec_as_agent(environment, command=skills_command, env=env)

        config_command = self._build_register_config_command_for(model_name, base_url)
        if config_command:
            await self.exec_as_agent(environment, command=config_command, env=env)

        cli_flags = self.build_cli_flags()
        cli_flags_arg = (cli_flags + " ") if cli_flags else ""
        await self.exec_as_agent(
            environment,
            command=(
                ". ~/.nvm/nvm.sh; nvm use 22 >/dev/null; "
                f"opencode --model={model_name} run --format=json "
                f"{cli_flags_arg}--thinking --dangerously-skip-permissions "
                f"-- {escaped_instruction} "
                "2>&1 </dev/null | stdbuf -oL tee /logs/agent/opencode.txt"
            ),
            env=env,
        )

        if messages := self._error_messages():
            from harbor.agents.installed.base import NonZeroAgentExitCodeError

            raise NonZeroAgentExitCodeError(
                "OpenCode emitted error event(s): " + "; ".join(messages[:3])
            )

    @with_prompt_template
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        await self.pre_run(environment, context)
        exc: BaseException | None = None
        try:
            await self._run_opencode(instruction, environment, context)
        except BaseException as err:
            exc = err
            raise
        finally:
            await self.post_run(environment, context, error=exc)


OpenCode = CustomOpenCode
PatchedOpenCode = CustomOpenCode

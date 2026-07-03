"""Copilot CLI agent with API-key based authentication for DepBench."""

from __future__ import annotations

import shlex

from harbor.agents.installed.copilot_cli import CopilotCli as HarborCopilotCli

from custom_agents.hooks import Artifacts, Hooked


DEFAULT_WEB_TOOLS = (
    "web_search",
    "web_fetch",
    "web_fetch_url",
    "browser",
    "fetch",
    "url_fetch",
    "github_search",
    "github_search_code",
    "github_search_issues",
)


class CustomCopilotCli(Artifacts, Hooked, HarborCopilotCli):
    """Copilot CLI routed through an explicit API key/token.

    Harbor's stock Copilot agent reads GitHub auth only from the host process
    environment. This wrapper also accepts ``api_key`` in kwargs or any of
    ``COPILOT_GITHUB_TOKEN``, ``COPILOT_API_KEY``, ``GH_TOKEN``, or
    ``GITHUB_TOKEN`` in ``agent.env``.
    """

    def __init__(
        self,
        *args,
        api_key: str | None = None,
        disable_web_tools: bool = False,
        web_tool_names: list[str] | tuple[str, ...] | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._api_key_arg = api_key
        self._disable_web_tools = disable_web_tools
        self._web_tool_names = tuple(web_tool_names or DEFAULT_WEB_TOOLS)

    @staticmethod
    def name() -> str:
        return "custom-copilot-cli"

    def _api_key(self) -> str | None:
        return (
            self._api_key_arg
            or self._get_env("COPILOT_GITHUB_TOKEN")
            or self._get_env("COPILOT_API_KEY")
            or self._get_env("GH_TOKEN")
            or self._get_env("GITHUB_TOKEN")
        )

    def build_cli_flags(self) -> str:
        flags = [super().build_cli_flags()]
        if self._disable_web_tools:
            flags.extend(
                [
                    "--disable-builtin-mcps",
                    f"--deny-url={shlex.quote('*')}",
                    "--excluded-tools=" + ",".join(self._web_tool_names),
                ]
            )
        return " ".join(flag for flag in flags if flag)

    async def run(self, instruction, environment, context) -> None:
        token = self._api_key()
        if not token:
            raise ValueError(
                "CustomCopilotCli requires api_key or one of "
                "COPILOT_GITHUB_TOKEN, COPILOT_API_KEY, GH_TOKEN, GITHUB_TOKEN"
            )

        self._extra_env["COPILOT_GITHUB_TOKEN"] = token
        self._extra_env["COPILOT_API_KEY"] = token
        self._extra_env["GH_TOKEN"] = token
        self._extra_env["GITHUB_TOKEN"] = token
        return await super().run(instruction, environment, context)


CopilotCli = CustomCopilotCli

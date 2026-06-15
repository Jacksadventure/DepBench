"""Custom Codex agents that inject Codex provider config for Harbor runs.

Maestro usage via Harbor agent config:
  {
    "name": "codex",
    "import_path": "_run_configs.codex_maestro_agent:CodexMaestro",
    "model_name": "gpt-5.5",
    "env": {
      "CODEX_MAESTRO_BASE_URL": "http://172.100.216.1:23333/api/openai/v1",
      "CODEX_FORCE_API_KEY": "1",
      "OPENAI_API_KEY": "dummy"
    }
  }

Azure usage via Harbor agent config:
  {
    "name": "codex",
    "import_path": "_run_configs.codex_maestro_agent:CodexAzure",
    "model_name": "gpt-5-codex",
    "env": {
      "AZURE_OPENAI_BASE_URL": "https://YOUR_RESOURCE_NAME.openai.azure.com/openai/v1",
      "AZURE_OPENAI_API_KEY": "<injected by launcher, do not commit>",
      "AZURE_OPENAI_MODEL": "gpt-5-codex"
    }
  }

Both classes subclass Harbor's stock Codex and write `config.toml` into the
per-trial CODEX_HOME before `codex exec` runs. The implementation is surgical:
it overrides `_build_register_mcp_servers_command` to emit BOTH provider config
and any MCP blocks, so Harbor's existing setup_command path picks it up.
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess

from harbor.agents.installed.codex import Codex


PROVIDER_NAME = "agent-maestro"
AZURE_PROVIDER_NAME = "azure"
CLOUDGPT_PROVIDER_NAME = "cloudgpt"
CLOUDGPT_DEFAULT_BASE_URL = "https://cloudgpt-openai.azure-api.net/openai/v1"
CLOUDGPT_DEFAULT_MODEL = "gpt-5.5-20260424"
CLOUDGPT_DEFAULT_TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"
CLOUDGPT_DEFAULT_RESOURCE = "api://feb7b661-cac7-44a8-8dc1-163b63c23df2"


class CodexMaestro(Codex):
    """Codex variant that routes all calls to a local Agent Maestro proxy."""

    def _maestro_base_url(self) -> str | None:
        return self._get_env("CODEX_MAESTRO_BASE_URL")

    def _build_register_mcp_servers_command(self) -> str | None:
        """Write a config.toml that selects + defines the maestro provider.

        Combines: top-level `model_provider = "agent-maestro"` default, the
        provider block, and any MCP server blocks the parent class would emit.
        Single shell command so we don't race the parent's setup pipeline.
        """
        base_url = self._maestro_base_url()
        lines: list[str] = []
        if base_url:
            lines.extend([
                f'model_provider = "{PROVIDER_NAME}"',
                "",
                f"[model_providers.{PROVIDER_NAME}]",
                f'name = "{PROVIDER_NAME}"',
                f'base_url = "{base_url}"',
                'wire_api = "responses"',
                "requires_openai_auth = false",
                "",
            ])

        # Append MCP server entries (mirrors parent's logic)
        for server in self.mcp_servers or []:
            lines.append(f"[mcp_servers.{server.name}]")
            if server.transport == "stdio":
                cmd_parts = [server.command] + server.args if server.command else []
                lines.append(f'command = "{shlex.join(cmd_parts)}"')
            else:
                lines.append(f'url = "{server.url}"')
            lines.append("")

        if not lines:
            return None
        escaped = shlex.quote("\n".join(lines))
        return f'echo {escaped} > "$CODEX_HOME/config.toml"'


class CodexAzure(Codex):
    """Codex variant that routes calls to Azure OpenAI Responses API.

    This follows Microsoft's Codex-on-Azure guidance:

      model_provider = "azure"
      [model_providers.azure]
      base_url = "https://<resource>.openai.azure.com/openai/v1"
      env_key = "AZURE_OPENAI_API_KEY"
      wire_api = "responses"

    Required env:
      - AZURE_OPENAI_API_KEY
      - AZURE_OPENAI_BASE_URL or AZURE_OPENAI_ENDPOINT

    Optional env:
      - AZURE_OPENAI_MODEL / AZURE_OPENAI_DEPLOYMENT
    """

    def _azure_base_url(self) -> str | None:
        base_url = self._get_env("AZURE_OPENAI_BASE_URL") or self._get_env(
            "AZURE_OPENAI_ENDPOINT"
        )
        if not base_url:
            return None

        base_url = base_url.rstrip("/")
        if base_url.endswith("/openai/v1"):
            return base_url
        if base_url.endswith("/openai"):
            return f"{base_url}/v1"
        return f"{base_url}/openai/v1"

    def _azure_model_name(self) -> str:
        return (
            self._get_env("AZURE_OPENAI_MODEL")
            or self._get_env("AZURE_OPENAI_DEPLOYMENT")
            or self.model_name
            or "gpt-5-codex"
        ).split("/")[-1]

    async def run(self, instruction, environment, context) -> None:
        """Run Codex with Azure env vars available inside the trial container."""
        base_url = self._azure_base_url()
        if not base_url:
            raise ValueError(
                "CodexAzure requires AZURE_OPENAI_BASE_URL or "
                "AZURE_OPENAI_ENDPOINT, e.g. "
                "https://<resource>.openai.azure.com/openai/v1"
            )
        api_key = self._get_env("AZURE_OPENAI_API_KEY")
        if not api_key:
            raise ValueError("CodexAzure requires AZURE_OPENAI_API_KEY")

        # BaseInstalledAgent merges _extra_env into every exec_as_agent call.
        # This is required because Codex reads env_key=AZURE_OPENAI_API_KEY from
        # the container process environment, not from Harbor's host environment.
        self._extra_env["AZURE_OPENAI_BASE_URL"] = base_url
        self._extra_env["AZURE_OPENAI_API_KEY"] = api_key
        self._extra_env["AZURE_OPENAI_MODEL"] = self._azure_model_name()

        original_model_name = self.model_name
        self.model_name = self._azure_model_name()
        try:
            return await super().run(instruction, environment, context)
        finally:
            self.model_name = original_model_name

    def _build_register_mcp_servers_command(self) -> str | None:
        base_url = self._azure_base_url()
        if not base_url:
            raise ValueError(
                "CodexAzure requires AZURE_OPENAI_BASE_URL or "
                "AZURE_OPENAI_ENDPOINT, e.g. "
                "https://<resource>.openai.azure.com/openai/v1"
            )

        lines: list[str] = [
            f'model = "{self._azure_model_name()}"',
            f'model_provider = "{AZURE_PROVIDER_NAME}"',
            'model_reasoning_effort = "medium"',
            "",
            f"[model_providers.{AZURE_PROVIDER_NAME}]",
            'name = "Azure OpenAI"',
            f'base_url = "{base_url}"',
            'env_key = "AZURE_OPENAI_API_KEY"',
            'wire_api = "responses"',
            "",
        ]

        # Append MCP server entries (mirrors parent's logic)
        for server in self.mcp_servers or []:
            lines.append(f"[mcp_servers.{server.name}]")
            if server.transport == "stdio":
                cmd_parts = [server.command] + server.args if server.command else []
                lines.append(f'command = "{shlex.join(cmd_parts)}"')
            else:
                lines.append(f'url = "{server.url}"')
            lines.append("")

        escaped = shlex.quote("\n".join(lines))
        return f'echo {escaped} > "$CODEX_HOME/config.toml"'


class CodexCloudGPT(Codex):
    """Codex variant for CloudGPT OpenAI via Azure APIM + AAD bearer token.

    This follows the pasted CloudGPT helper:

      base_url = "https://cloudgpt-openai.azure-api.net/openai/v1"
      tenant_id = "72f988bf-86f1-41af-91ab-2d7cd011db47"
      resource/scope = "api://feb7b661-cac7-44a8-8dc1-163b63c23df2"
      model = "gpt-5.5-20260424"

    Required auth, in priority order:
      1. CLOUDGPT_OPENAI_TOKEN (pre-acquired AAD bearer token), or
      2. AZURE_OPENAI_API_KEY (treated as bearer token for compatibility), or
      3. `az account get-access-token` on the Harbor host.

    Optional env:
      - CLOUDGPT_OPENAI_BASE_URL (defaults to CloudGPT /openai/v1 endpoint)
      - CLOUDGPT_OPENAI_MODEL (defaults to gpt-5.5-20260424)
      - CLOUDGPT_AAD_TENANT_ID
      - CLOUDGPT_AAD_RESOURCE
    """

    def _cloudgpt_base_url(self) -> str:
        base_url = (
            self._get_env("CLOUDGPT_OPENAI_BASE_URL")
            or self._get_env("AZURE_OPENAI_BASE_URL")
            or self._get_env("AZURE_OPENAI_ENDPOINT")
            or CLOUDGPT_DEFAULT_BASE_URL
        ).rstrip("/")
        if base_url.endswith("/openai/v1"):
            return base_url
        if base_url.endswith("/openai"):
            return f"{base_url}/v1"
        return f"{base_url}/openai/v1"

    def _cloudgpt_model_name(self) -> str:
        return (
            self._get_env("CLOUDGPT_OPENAI_MODEL")
            or self._get_env("AZURE_OPENAI_MODEL")
            or self._get_env("AZURE_OPENAI_DEPLOYMENT")
            or self.model_name
            or CLOUDGPT_DEFAULT_MODEL
        ).split("/")[-1]

    def _cloudgpt_resource(self) -> str:
        return self._get_env("CLOUDGPT_AAD_RESOURCE") or CLOUDGPT_DEFAULT_RESOURCE

    def _cloudgpt_tenant_id(self) -> str:
        return self._get_env("CLOUDGPT_AAD_TENANT_ID") or CLOUDGPT_DEFAULT_TENANT_ID

    def _get_cloudgpt_token_from_az(self) -> str:
        resource = self._cloudgpt_resource()
        tenant_id = self._cloudgpt_tenant_id()
        common_args = [
            "az",
            "account",
            "get-access-token",
            "--tenant",
            tenant_id,
            "--output",
            "json",
        ]

        attempts = [
            common_args + ["--resource", resource],
            common_args + ["--scope", f"{resource}/.default"],
        ]
        last_error = ""
        for cmd in attempts:
            try:
                completed = subprocess.run(
                    cmd,
                    capture_output=True,
                    check=True,
                    text=True,
                    timeout=60,
                )
                token = json.loads(completed.stdout).get("accessToken")
                if token:
                    return token
            except Exception as exc:
                stderr = getattr(exc, "stderr", "") or ""
                last_error = f"{type(exc).__name__}: {stderr[:300]}"

        raise ValueError(
            "CodexCloudGPT could not acquire an AAD token. Set "
            "CLOUDGPT_OPENAI_TOKEN, or run `az login` on the Harbor host. "
            f"Last az error: {last_error}"
        )

    def _cloudgpt_token(self) -> str:
        return (
            self._get_env("CLOUDGPT_OPENAI_TOKEN")
            or self._get_env("AZURE_OPENAI_API_KEY")
            or self._get_cloudgpt_token_from_az()
        )

    async def run(self, instruction, environment, context) -> None:
        """Run Codex with a fresh CloudGPT bearer token in the trial container."""
        token = self._cloudgpt_token()
        self._extra_env["CLOUDGPT_OPENAI_TOKEN"] = token
        self._extra_env["CLOUDGPT_OPENAI_BASE_URL"] = self._cloudgpt_base_url()
        self._extra_env["CLOUDGPT_OPENAI_MODEL"] = self._cloudgpt_model_name()

        original_model_name = self.model_name
        self.model_name = self._cloudgpt_model_name()
        try:
            return await super().run(instruction, environment, context)
        finally:
            self.model_name = original_model_name

    def _build_register_mcp_servers_command(self) -> str | None:
        lines: list[str] = [
            f'model = "{self._cloudgpt_model_name()}"',
            f'model_provider = "{CLOUDGPT_PROVIDER_NAME}"',
            'model_reasoning_effort = "medium"',
            "",
            f"[model_providers.{CLOUDGPT_PROVIDER_NAME}]",
            'name = "CloudGPT OpenAI"',
            f'base_url = "{self._cloudgpt_base_url()}"',
            'env_key = "CLOUDGPT_OPENAI_TOKEN"',
            'wire_api = "responses"',
            "",
        ]

        # Append MCP server entries (mirrors parent's logic)
        for server in self.mcp_servers or []:
            lines.append(f"[mcp_servers.{server.name}]")
            if server.transport == "stdio":
                cmd_parts = [server.command] + server.args if server.command else []
                lines.append(f'command = "{shlex.join(cmd_parts)}"')
            else:
                lines.append(f'url = "{server.url}"')
            lines.append("")

        escaped = shlex.quote("\n".join(lines))
        return f'echo {escaped} > "$CODEX_HOME/config.toml"'

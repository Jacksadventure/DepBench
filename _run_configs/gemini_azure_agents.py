"""Gemini agent adapters for Harbor benchmark runs.

These wrappers intentionally do not hard-code secrets or endpoints. Launchers
may provide:

  AZURE_GEMINI_BASE_URL    OpenAI/Anthropic-compatible endpoint
  AZURE_GEMINI_API_KEY     API key or AAD bearer token for that endpoint
  AZURE_GEMINI_MODEL       optional, defaults to gemini-3.1-pro-preview

They also support the CloudGPT env names used by the existing GPT-5.5 Codex
adapter:

  CLOUDGPT_OPENAI_BASE_URL
  CLOUDGPT_OPENAI_TOKEN
  CLOUDGPT_AAD_TENANT_ID
  CLOUDGPT_AAD_RESOURCE

If no token env is set, the wrappers attempt `az account get-access-token` with
the same CloudGPT tenant/resource defaults as `_run_configs.codex_maestro_agent`.

For GitHub Copilot-hosted Gemini, OpenCode can use its native
`github-copilot` provider via `OpenCodeCopilotGemini`; Copilot CLI uses its
stock Harbor adapter with `--model=gemini-3.1-pro-preview`.

Codex and Claude Code do not natively support GitHub Copilot's private endpoint;
use the Azure/OpenAI-compatible wrappers below, or run a separate OpenAI/Anthropic
compatible proxy backed by GitHub Copilot.
"""

from __future__ import annotations

import json
import os
import subprocess

from harbor.agents.installed.claude_code import ClaudeCode

from _run_configs.codex_maestro_agent import (
    CLOUDGPT_DEFAULT_BASE_URL,
    CLOUDGPT_DEFAULT_RESOURCE,
    CLOUDGPT_DEFAULT_TENANT_ID,
    CodexCloudGPT,
)
from _run_configs.opencode_nvm22_agent import OpenCodeNvm22


DEFAULT_GEMINI_MODEL = "gemini-3.1-pro-preview"


def _strip_slash(value: str) -> str:
    return value.rstrip("/")


class _AzureGeminiMixin:
    def _gemini_base_url(self) -> str:
        base_url = (
            self._get_env("AZURE_GEMINI_BASE_URL")
            or self._get_env("CLOUDGPT_OPENAI_BASE_URL")
            or self._get_env("AZURE_OPENAI_BASE_URL")
            or self._get_env("AZURE_OPENAI_ENDPOINT")
            or CLOUDGPT_DEFAULT_BASE_URL
        )
        return _strip_slash(base_url)

    def _gemini_resource(self) -> str:
        return (
            self._get_env("AZURE_GEMINI_AAD_RESOURCE")
            or self._get_env("CLOUDGPT_AAD_RESOURCE")
            or CLOUDGPT_DEFAULT_RESOURCE
        )

    def _gemini_tenant_id(self) -> str:
        return (
            self._get_env("AZURE_GEMINI_AAD_TENANT_ID")
            or self._get_env("CLOUDGPT_AAD_TENANT_ID")
            or CLOUDGPT_DEFAULT_TENANT_ID
        )

    def _get_gemini_token_from_az(self) -> str:
        resource = self._gemini_resource()
        tenant_id = self._gemini_tenant_id()
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
            "Azure Gemini wrapper could not acquire an AAD token. Set "
            "AZURE_GEMINI_API_KEY or CLOUDGPT_OPENAI_TOKEN, or run `az login` "
            f"on the Harbor host. Last az error: {last_error}"
        )

    def _gemini_token(self) -> str:
        return (
            self._get_env("AZURE_GEMINI_API_KEY")
            or self._get_env("CLOUDGPT_OPENAI_TOKEN")
            or self._get_env("AZURE_OPENAI_API_KEY")
            or self._get_gemini_token_from_az()
        )

    def _gemini_model(self) -> str:
        return (
            self._get_env("AZURE_GEMINI_MODEL")
            or self._get_env("CLOUDGPT_OPENAI_MODEL")
            or self._get_env("AZURE_OPENAI_MODEL")
            or self._get_env("AZURE_OPENAI_DEPLOYMENT")
            or self.model_name
            or DEFAULT_GEMINI_MODEL
        ).split("/")[-1]


class OpenCodeAzureGemini(_AzureGeminiMixin, OpenCodeNvm22):
    """Run OpenCode against an Azure-hosted OpenAI-compatible Gemini endpoint."""

    async def run(self, instruction, environment, context) -> None:
        self._extra_env["OPENAI_BASE_URL"] = self._gemini_base_url()
        self._extra_env["OPENAI_API_KEY"] = self._gemini_token()
        original_model_name = self.model_name
        self.model_name = f"openai/{self._gemini_model()}"
        try:
            return await super().run(instruction, environment, context)
        finally:
            self.model_name = original_model_name


class OpenCodeCopilotGemini(_AzureGeminiMixin, OpenCodeNvm22):
    """Run OpenCode against GitHub Copilot-hosted Gemini."""

    async def run(self, instruction, environment, context) -> None:
        original_model_name = self.model_name
        self.model_name = f"github-copilot/{self._gemini_model()}"
        try:
            return await super().run(instruction, environment, context)
        finally:
            self.model_name = original_model_name


class ClaudeCodeAzureGemini(_AzureGeminiMixin, ClaudeCode):
    """Run Claude Code against an Anthropic-compatible Azure Gemini endpoint."""

    async def run(self, instruction, environment, context) -> None:
        base_url = self._gemini_base_url()
        token = self._gemini_token()
        model = self._gemini_model()
        self._extra_env["ANTHROPIC_BASE_URL"] = base_url
        self._extra_env["ANTHROPIC_API_KEY"] = token
        self._extra_env["ANTHROPIC_AUTH_TOKEN"] = token
        self._extra_env["ANTHROPIC_MODEL"] = model
        self._extra_env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = model
        self._extra_env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = model
        self._extra_env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = model
        self._extra_env["CLAUDE_CODE_SUBAGENT_MODEL"] = model

        env_keys = ("ANTHROPIC_BASE_URL", "ANTHROPIC_MODEL")
        original_env = {key: os.environ.get(key) for key in env_keys}
        os.environ["ANTHROPIC_BASE_URL"] = base_url
        os.environ["ANTHROPIC_MODEL"] = model
        original_model_name = self.model_name
        self.model_name = model
        try:
            return await super().run(instruction, environment, context)
        finally:
            self.model_name = original_model_name
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


class CodexAzureGemini(_AzureGeminiMixin, CodexCloudGPT):
    """Run Codex through the same CloudGPT/AAD flow used for GPT-5.5."""

    def _cloudgpt_base_url(self) -> str:
        base_url = self._gemini_base_url()
        if base_url.endswith("/openai/v1"):
            return base_url
        if base_url.endswith("/openai"):
            return f"{base_url}/v1"
        return base_url

    def _cloudgpt_model_name(self) -> str:
        return self._gemini_model()

    def _cloudgpt_resource(self) -> str:
        return self._gemini_resource()

    def _cloudgpt_tenant_id(self) -> str:
        return self._gemini_tenant_id()

    def _cloudgpt_token(self) -> str:
        return self._gemini_token()

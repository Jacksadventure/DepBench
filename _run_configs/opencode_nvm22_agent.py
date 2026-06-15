"""OpenCode Harbor agent variant that keeps the nvm-installed Node on PATH.

Harbor's stock OpenCode adapter installs opencode under nvm's Node 22, but its
run command only sources nvm and does not select Node 22. In some containers
that leaves the global npm bin directory off PATH, so `opencode` exits 127.
"""
from __future__ import annotations

import shlex

from harbor.agents.installed.opencode import OpenCode
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext
from harbor.agents.installed.base import with_prompt_template


class OpenCodeNvm22(OpenCode):
    """OpenCode adapter that runs with the Node 22 environment activated."""

    _NVM_USE_22 = '. ~/.nvm/nvm.sh; nvm use 22 >/dev/null; '

    def get_version_command(self) -> str | None:
        return f"{self._NVM_USE_22}opencode --version"

    @with_prompt_template
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        escaped_instruction = shlex.quote(instruction)

        if not self.model_name or "/" not in self.model_name:
            raise ValueError("Model name must be in the format provider/model_name")

        provider, _ = self.model_name.split("/", 1)
        env = {}
        keys = []

        if provider == "amazon-bedrock":
            keys.extend(["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION"])
        elif provider == "anthropic":
            keys.append("ANTHROPIC_API_KEY")
        elif provider == "azure":
            keys.extend(["AZURE_RESOURCE_NAME", "AZURE_API_KEY"])
        elif provider == "deepseek":
            keys.append("DEEPSEEK_API_KEY")
        elif provider == "github-copilot":
            keys.append("GITHUB_TOKEN")
        elif provider == "google":
            keys.extend(
                [
                    "GEMINI_API_KEY",
                    "GOOGLE_GENERATIVE_AI_API_KEY",
                    "GOOGLE_APPLICATION_CREDENTIALS",
                    "GOOGLE_CLOUD_PROJECT",
                    "GOOGLE_CLOUD_LOCATION",
                    "GOOGLE_GENAI_USE_VERTEXAI",
                    "GOOGLE_API_KEY",
                ]
            )
        elif provider == "groq":
            keys.append("GROQ_API_KEY")
        elif provider == "huggingface":
            keys.append("HF_TOKEN")
        elif provider == "llama":
            keys.append("LLAMA_API_KEY")
        elif provider == "mistral":
            keys.append("MISTRAL_API_KEY")
        elif provider == "openai":
            keys.append("OPENAI_API_KEY")
            keys.append("OPENAI_BASE_URL")
        elif provider == "opencode":
            keys.append("OPENCODE_API_KEY")
        elif provider == "xai":
            keys.append("XAI_API_KEY")
        elif provider == "openrouter":
            keys.append("OPENROUTER_API_KEY")
        else:
            raise ValueError(
                f"Unknown provider {provider}. If you believe this provider "
                "should be supported, please contact the maintainers."
            )

        import os

        for key in keys:
            if key in os.environ:
                env[key] = os.environ[key]

        env["OPENCODE_FAKE_VCS"] = "git"

        skills_command = self._build_register_skills_command()
        if skills_command:
            await self.exec_as_agent(environment, command=skills_command, env=env)

        config_command = self._build_register_config_command()
        if config_command:
            await self.exec_as_agent(environment, command=config_command, env=env)

        await self.exec_as_agent(
            environment,
            command=(
                f"{self._NVM_USE_22}"
                f"opencode --model={self.model_name} run --format=json --thinking "
                f"--dangerously-skip-permissions -- {escaped_instruction} "
                "2>&1 </dev/null | stdbuf -oL tee /logs/agent/opencode.txt"
            ),
            env=env,
        )

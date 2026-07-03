"""Reusable Harbor agent hooks for collecting DepBench run artifacts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harbor.agents.installed.base import with_prompt_template
from harbor.models.trial.paths import EnvironmentPaths

if TYPE_CHECKING:
    from harbor.environments.base import BaseEnvironment
    from harbor.models.agent.context import AgentContext


BASE_COMMIT_PATH = "/tmp/depbench_agent_base_commit"


class Hooked:
    """Mixin that wraps an installed Harbor agent with pre/post hooks."""

    async def pre_run(
        self, environment: "BaseEnvironment", context: "AgentContext"
    ) -> None:
        """Hook executed immediately before the parent agent runs."""

    async def post_run(
        self,
        environment: "BaseEnvironment",
        context: "AgentContext",
        *,
        error: BaseException | None = None,
    ) -> None:
        """Hook executed after the parent agent, even when it errors."""

    @with_prompt_template
    async def run(
        self, instruction: str, environment: "BaseEnvironment", context: "AgentContext"
    ) -> None:
        await self.pre_run(environment, context)
        exc: BaseException | None = None
        try:
            parent_run = super().run
            unwrapped = getattr(getattr(parent_run, "__func__", None), "__wrapped__", None)
            if unwrapped is not None:
                await unwrapped(self, instruction, environment, context)
            else:
                await parent_run(instruction, environment, context)
        except BaseException as err:
            exc = err
            raise
        finally:
            await self.post_run(environment, context, error=exc)


class Artifacts:
    """Capture the final repository delta under Harbor's artifacts directory."""

    async def pre_run(
        self, environment: "BaseEnvironment", context: "AgentContext"
    ) -> None:
        await super().pre_run(environment, context)
        workdir = environment.task_env_config.workdir or "/app"
        result = await environment.exec(
            f"git rev-parse HEAD > {BASE_COMMIT_PATH}", cwd=workdir
        )
        if result.return_code != 0:
            raise RuntimeError(
                "Could not record the pre-agent git HEAD: "
                f"{result.stdout or ''}{result.stderr or ''}"
            )

    async def post_run(
        self,
        environment: "BaseEnvironment",
        context: "AgentContext",
        *,
        error: BaseException | None = None,
    ) -> None:
        try:
            await super().post_run(environment, context, error=error)
        finally:
            workdir = environment.task_env_config.workdir or "/app"
            artifacts_dir = EnvironmentPaths.artifacts_dir.as_posix()
            command = (
                f"mkdir -p {artifacts_dir}; "
                f"BASE_COMMIT=$(cat {BASE_COMMIT_PATH} 2>/dev/null || git rev-parse HEAD); "
                "git add -A; "
                f'git diff --cached --no-color "$BASE_COMMIT" > {artifacts_dir}/solution_patch.diff 2>/dev/null || true; '
                f'git diff --cached --stat --summary "$BASE_COMMIT" > {artifacts_dir}/git_status.txt 2>/dev/null || true; '
                f"git status --short > {artifacts_dir}/worktree_status.txt 2>/dev/null || true"
            )
            await environment.exec(command, cwd=workdir)


HookedAgent = Hooked
GitArtifactMixin = Artifacts

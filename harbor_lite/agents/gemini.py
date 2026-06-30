from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from ..runtime import AgentRuntime
from .base import LocalAgent
from .utils import agent_text_step, agent_tool_step, compact, obj, string, stringify


class GeminiAgent(LocalAgent):
    name = "gemini-cli"
    runner = "gemini"
    executable = "gemini"
    output_name = "gemini-cli.txt"
    default_model = "pro"

    def build_command(self, prompt: str, runtime: AgentRuntime) -> list[str]:
        model = (self.model or "").split("/", 1)[-1]
        return [
            self.executable,
            "--yolo",
            f"--model={model}",
            "--output-format=stream-json",
            f"--prompt={prompt}",
            *self.combined_args(runtime),
        ]

    def runtime_env(self, *, workdir: Path, state_dir: Path | None, runtime: AgentRuntime) -> dict[str, str]:
        env = super().runtime_env(workdir=workdir, state_dir=state_dir, runtime=runtime)
        env["GEMINI_CLI_TRUST_WORKSPACE"] = "true"
        return env

    def session_files(self, *, workdir: Path, state_dir: Path | None, started_at: float) -> Sequence[Path]:
        roots = [Path.home() / ".gemini" / "tmp"]
        home = self._state_home(state_dir)
        if home is not None:
            roots.append(home / ".gemini" / "tmp")
        return self._recent_files(roots, ("**/session-*",), started_at)

    def build_trajectory_steps(
        self,
        events: Sequence[dict[str, Any]],
        *,
        fallback_timestamp: str,
    ) -> list[dict[str, Any]]:
        steps: list[dict[str, Any]] = []
        for event in events:
            event_type = string(event.get("type"))
            timestamp = string(event.get("timestamp")) or fallback_timestamp
            if event_type == "message" and event.get("role") == "assistant":
                text = string(event.get("content"))
                if text:
                    steps.append(agent_text_step(self, text, timestamp, {"kind": "runner_message"}))
                continue
            if event_type == "tool_use":
                steps.append(
                    agent_tool_step(
                        self,
                        timestamp=timestamp,
                        message=string(event.get("name")) or "Gemini tool call",
                        call_id=string(event.get("id")) or f"gemini-tool-{len(steps) + 1}",
                        function_name=string(event.get("name")) or "tool_use",
                        arguments=obj(event.get("args")) or obj(event.get("arguments")) or {},
                    )
                )
                continue
            if event_type == "tool_result":
                content = stringify(event.get("result") if "result" in event else event.get("content"))
                if content:
                    steps.append(
                        agent_text_step(
                            self,
                            content,
                            timestamp,
                            compact({"kind": "runner_observation", "tool_name": event.get("name")}),
                        )
                    )
        return steps

    def extract_trajectory_answer(self, events: Sequence[dict[str, Any]], raw_text: str) -> str | None:
        parts = [
            text
            for event in events
            if event.get("type") == "message" and event.get("role") == "assistant"
            for text in [string(event.get("content"))]
            if text
        ]
        return "".join(parts).strip() or super().extract_trajectory_answer(events, raw_text)

    def extract_trajectory_stats(self, events: Sequence[dict[str, Any]]) -> dict[str, Any]:
        for event in reversed(events):
            if event.get("type") == "result" and isinstance(event.get("stats"), dict):
                return event["stats"]
        return {}

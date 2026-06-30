from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from ..runtime import AgentRuntime
from .base import LocalAgent
from .utils import agent_text_step, agent_tool_step, obj, path_value, string


class ClaudeAgent(LocalAgent):
    name = "claude-code"
    runner = "claude"
    executable = "claude"
    output_name = "claude-code.txt"
    default_model = "claude-sonnet-4-5"

    def build_command(self, prompt: str, runtime: AgentRuntime) -> list[str]:
        command = [
            self.executable,
            "--verbose",
            "--output-format=stream-json",
            "--permission-mode=bypassPermissions",
            "--print",
            *self.combined_args(runtime),
            "--",
            prompt,
        ]
        if self.model:
            command[1:1] = ["--model", self.model.split("/", 1)[-1]]
        return command

    def disable_web_args(self) -> Sequence[str]:
        return ("--disallowedTools", "WebSearch,WebFetch")

    def session_files(self, *, workdir: Path, state_dir: Path | None, started_at: float) -> Sequence[Path]:
        encoded = str(workdir.resolve()).replace("/", "-")
        roots = [Path.home() / ".claude" / "projects" / encoded]
        home = self._state_home(state_dir)
        if home is not None:
            roots.append(home / ".claude" / "projects" / encoded)
        return self._recent_files(roots, ("*.jsonl",), started_at)

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
            if event_type == "assistant":
                content = event.get("content") if "content" in event else path_value(event, ("message", "content"))
                text = claude_text(content)
                if text:
                    steps.append(agent_text_step(self, text, timestamp, {"kind": "runner_message"}))
                for call in claude_tool_calls(content, offset=len(steps)):
                    steps.append(agent_tool_step(self, timestamp=timestamp, **call))
                continue
            if event_type == "tool_use":
                steps.append(
                    agent_tool_step(
                        self,
                        timestamp=timestamp,
                        message=string(event.get("name")) or "Claude tool call",
                        call_id=string(event.get("id")) or f"claude-tool-{len(steps) + 1}",
                        function_name=string(event.get("name")) or "tool_use",
                        arguments=obj(event.get("input")) or {},
                    )
                )
                continue
            if event_type == "tool_result":
                text = claude_text(event.get("content") if "content" in event else event.get("result"))
                if text:
                    steps.append(agent_text_step(self, text, timestamp, {"kind": "runner_observation"}))
                continue
            if event_type == "result":
                text = string(event.get("result"))
                if text:
                    steps.append(agent_text_step(self, text, timestamp, {"kind": "runner_result"}))
        return steps

    def extract_trajectory_answer(self, events: Sequence[dict[str, Any]], raw_text: str) -> str | None:
        result_text: str | None = None
        parts: list[str] = []
        for event in events:
            if event.get("type") == "assistant":
                text = claude_text(event.get("content") if "content" in event else path_value(event, ("message", "content")))
                if text:
                    parts.append(text)
            elif event.get("type") == "result":
                result_text = string(event.get("result")) or result_text
        return (result_text or "\n".join(parts)).strip() or super().extract_trajectory_answer(events, raw_text)


def claude_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    texts: list[str] = []
    for part in content:
        if not isinstance(part, dict) or part.get("type") != "text":
            continue
        text = string(part.get("text"))
        if text:
            texts.append(text)
    return "\n\n".join(texts)


def claude_tool_calls(content: object, *, offset: int) -> list[dict[str, Any]]:
    if not isinstance(content, list):
        return []
    calls: list[dict[str, Any]] = []
    for part in content:
        if not isinstance(part, dict) or part.get("type") not in {"tool_use", "server_tool_use"}:
            continue
        function_name = string(part.get("name")) or string(part.get("tool_name")) or "tool_use"
        calls.append(
            {
                "message": function_name,
                "call_id": string(part.get("id")) or f"claude-tool-{offset + len(calls) + 1}",
                "function_name": function_name,
                "arguments": obj(part.get("input")) or {},
            }
        )
    return calls

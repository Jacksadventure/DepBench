from __future__ import annotations

from typing import Any, Sequence

from ..runtime import AgentRuntime
from .base import LocalAgent
from .utils import agent_text_step, agent_tool_step, compact, millis_to_iso, obj, path_value, string, stringify


class OpenCodeAgent(LocalAgent):
    name = "opencode"
    runner = "opencode"
    executable = "opencode"
    output_name = "opencode.txt"
    default_model = "deepseek/deepseek-v4-pro"

    def build_command(self, prompt: str, runtime: AgentRuntime) -> list[str]:
        workdir = getattr(self, "workdir", None)
        dir_args = [f"--dir={workdir}"] if workdir else []
        return [
            self.executable,
            f"--model={self.model}",
            "run",
            *dir_args,
            "--format=json",
            "--print-logs",
            "--log-level",
            "INFO",
            "--dangerously-skip-permissions",
            *self.combined_args(runtime),
            "--",
            prompt,
        ]

    def build_trajectory_steps(
        self,
        events: Sequence[dict[str, Any]],
        *,
        fallback_timestamp: str,
    ) -> list[dict[str, Any]]:
        steps: list[dict[str, Any]] = []
        for event in events:
            event_type = string(event.get("type"))
            part = obj(event.get("part")) or {}
            timestamp = millis_to_iso(event.get("timestamp")) or string(event.get("timestamp")) or fallback_timestamp
            if event_type == "text":
                text = string(part.get("text")) or string(event.get("text"))
                if text:
                    steps.append(agent_text_step(self, text, timestamp, {"kind": "runner_message"}))
                continue
            if event_type == "reasoning":
                text = string(part.get("text"))
                if text:
                    steps.append(
                        agent_text_step(
                            self,
                            "(reasoning)",
                            timestamp,
                            {"kind": "runner_reasoning", "reasoning_content": text},
                        )
                    )
                continue
            if event_type == "tool_use" and part:
                state = obj(part.get("state")) or {}
                call_id = string(part.get("callID")) or string(part.get("id")) or f"opencode-tool-{len(steps) + 1}"
                function_name = string(part.get("tool")) or "tool_use"
                steps.append(
                    agent_tool_step(
                        self,
                        timestamp=timestamp,
                        message=function_name,
                        call_id=call_id,
                        function_name=function_name,
                        arguments=obj(state.get("input")) or {},
                        output=stringify(state.get("output") if "output" in state else path_value(state, ("metadata", "output"))),
                        extra=compact(
                            {
                                "kind": "runner_tool",
                                "status": path_value(state, ("status",)),
                                "title": path_value(state, ("title",)),
                                "exit_code": path_value(state, ("metadata", "exit")),
                            }
                        ),
                    )
                )
        return steps

    def extract_trajectory_answer(self, events: Sequence[dict[str, Any]], raw_text: str) -> str | None:
        parts: list[str] = []
        for event in events:
            part = obj(event.get("part")) or {}
            if event.get("type") == "text":
                text = string(part.get("text")) or string(event.get("text"))
                if text:
                    parts.append(text)
        return "".join(parts).strip() or super().extract_trajectory_answer(events, raw_text)

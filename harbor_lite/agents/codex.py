from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from ..runtime import AgentRuntime
from .base import LocalAgent
from .utils import agent_text_step, agent_tool_step, compact, obj, path_value, string


class CodexAgent(LocalAgent):
    name = "codex"
    runner = "codex"
    executable = "codex"
    output_name = "codex.txt"
    default_model = "gpt-5.4"

    def build_command(self, prompt: str, runtime: AgentRuntime) -> list[str]:
        model = (self.model or "").split("/", 1)[-1]
        return [
            self.executable,
            "exec",
            "--dangerously-bypass-approvals-and-sandbox",
            "--skip-git-repo-check",
            "--model",
            model,
            "--json",
            *self.combined_args(runtime),
            "--",
            prompt,
        ]

    def disable_web_args(self) -> Sequence[str]:
        return ("-c", "web_search=disabled")

    def state_env(self, state_dir: Path) -> dict[str, str]:
        env = super().state_env(state_dir)
        env["CODEX_HOME"] = str(state_dir / "codex")
        return env

    def session_files(self, *, workdir: Path, state_dir: Path | None, started_at: float) -> Sequence[Path]:
        roots = [Path.home() / ".codex" / "sessions"]
        if state_dir is not None:
            roots.extend(
                [
                    state_dir / "codex" / "sessions",
                    state_dir / "home" / ".codex" / "sessions",
                ]
            )
        return self._recent_files(roots, ("**/*.jsonl",), started_at)

    def build_trajectory_steps(
        self,
        events: Sequence[dict[str, Any]],
        *,
        fallback_timestamp: str,
    ) -> list[dict[str, Any]]:
        steps: list[dict[str, Any]] = []
        for event in events:
            item = obj(event.get("item"))
            timestamp = string(event.get("timestamp")) or fallback_timestamp
            if item:
                item_type = item.get("type")
                if item_type == "agent_message":
                    text = string(item.get("text"))
                    if text:
                        steps.append(agent_text_step(self, text, timestamp, {"kind": "runner_message"}))
                    continue
                if item_type == "command_execution":
                    command = string(item.get("command")) or ""
                    call_id = string(item.get("id")) or f"codex-command-{len(steps) + 1}"
                    steps.append(
                        agent_tool_step(
                            self,
                            timestamp=timestamp,
                            message=f"Run command: {command}" if command else "Run command",
                            call_id=call_id,
                            function_name="command_execution",
                            arguments={"command": command} if command else {},
                            output=string(item.get("aggregated_output")),
                            extra=compact(
                                {
                                    "kind": "runner_tool",
                                    "status": item.get("status"),
                                    "exit_code": item.get("exit_code"),
                                }
                            ),
                        )
                    )
                    continue
                if item_type == "mcp_tool_call":
                    call_id = string(item.get("id")) or f"codex-mcp-{len(steps) + 1}"
                    function_name = ".".join(str(v) for v in (item.get("server"), item.get("tool")) if v) or "mcp_tool_call"
                    steps.append(
                        agent_tool_step(
                            self,
                            timestamp=timestamp,
                            message=function_name,
                            call_id=call_id,
                            function_name=function_name,
                            arguments=obj(item.get("arguments")) or {},
                            output=string(item.get("output")),
                            extra=compact({"kind": "runner_tool", "status": item.get("status")}),
                        )
                    )
                    continue

            msg = obj(event.get("msg"))
            if msg and msg.get("type") == "text":
                text = string(msg.get("content"))
                if text:
                    steps.append(agent_text_step(self, text, timestamp, {"kind": "runner_message"}))
                continue

            if event.get("method") == "item/agentMessage/delta":
                text = string(path_value(event, ("params", "delta")))
                if text:
                    steps.append(agent_text_step(self, text, timestamp, {"kind": "runner_delta"}))
        return steps

    def extract_trajectory_answer(self, events: Sequence[dict[str, Any]], raw_text: str) -> str | None:
        parts: list[str] = []
        for event in events:
            item = obj(event.get("item"))
            if item and item.get("type") == "agent_message":
                text = string(item.get("text"))
                if text:
                    parts.append(text)
            msg = obj(event.get("msg"))
            if msg and msg.get("type") == "text":
                text = string(msg.get("content"))
                if text:
                    parts.append(text)
            if event.get("method") == "item/agentMessage/delta":
                text = string(path_value(event, ("params", "delta")))
                if text:
                    parts.append(text)
        return "\n".join(parts).strip() or super().extract_trajectory_answer(events, raw_text)

    def extract_trajectory_stats(self, events: Sequence[dict[str, Any]]) -> dict[str, Any]:
        for event in reversed(events):
            if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
                return event["usage"]
            if event.get("type") != "event_msg":
                continue
            payload = obj(event.get("payload"))
            if not payload or payload.get("type") != "token_count":
                continue
            info = obj(payload.get("info")) or {}
            total = obj(info.get("total_token_usage"))
            if total:
                return {
                    "input_tokens": total.get("input_tokens"),
                    "output_tokens": total.get("output_tokens"),
                    "cached_tokens": total.get("cached_input_tokens"),
                    "cost_usd": info.get("total_cost") or info.get("cost_usd"),
                    "raw_stats": info,
                }
        return {}

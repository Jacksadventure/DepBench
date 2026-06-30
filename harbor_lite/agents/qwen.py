from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from ..runtime import AgentRuntime
from .base import LocalAgent
from .utils import agent_text_step, attach_observation, metrics_from_stats, obj, path_value, string, stringify


class QwenAgent(LocalAgent):
    name = "qwen-coder"
    runner = "qwen"
    executable = "qwen"
    output_name = "qwen-code.txt"
    default_model = "qwen3.6-plus"

    def build_command(self, prompt: str, runtime: AgentRuntime) -> list[str]:
        return [self.executable, "--yolo", f"--prompt={prompt}", *self.combined_args(runtime)]

    def runtime_env(self, *, workdir: Path, state_dir: Path | None, runtime: AgentRuntime) -> dict[str, str]:
        env = super().runtime_env(workdir=workdir, state_dir=state_dir, runtime=runtime)
        if self.model:
            env["OPENAI_MODEL"] = self.model
        return env

    def session_files(self, *, workdir: Path, state_dir: Path | None, started_at: float) -> Sequence[Path]:
        roots = [Path.home() / ".qwen" / "projects"]
        home = self._state_home(state_dir)
        if home is not None:
            roots.append(home / ".qwen" / "projects")
        return self._recent_files(roots, ("**/chats/*.jsonl",), started_at)

    def trajectory_sources(self, *, raw_log_path: Path, sessions_dir: Path) -> Sequence[Path]:
        session_files = sorted(sessions_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime if p.exists() else 0)
        return tuple(session_files) or (raw_log_path,)

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
            message = obj(event.get("message"))
            if event_type == "assistant" and message:
                parts = message.get("parts") if isinstance(message.get("parts"), list) else []
                text_parts: list[str] = []
                tool_calls: list[dict[str, Any]] = []
                for part in parts:
                    if not isinstance(part, dict):
                        continue
                    text = string(part.get("text"))
                    if text:
                        text_parts.append(text)
                    function_call = obj(part.get("functionCall"))
                    if function_call:
                        call_id = string(function_call.get("id")) or f"qwen-tool-{len(steps) + len(tool_calls) + 1}"
                        tool_calls.append(
                            {
                                "tool_call_id": call_id,
                                "function_name": string(function_call.get("name")) or "function_call",
                                "arguments": obj(function_call.get("args")) or {},
                            }
                        )
                step = agent_text_step(self, "\n".join(text_parts) or "(tool use)", timestamp, {"kind": "runner_message"})
                if tool_calls:
                    step["tool_calls"] = tool_calls
                    step["llm_call_count"] = 1
                usage = obj(event.get("usageMetadata")) or {}
                metrics = metrics_from_stats(
                    {
                        "prompt_tokens": usage.get("promptTokenCount"),
                        "completion_tokens": usage.get("candidatesTokenCount"),
                        "cached_tokens": usage.get("cachedContentTokenCount"),
                    }
                )
                if metrics:
                    thoughts = usage.get("thoughtsTokenCount")
                    if thoughts:
                        metrics["extra"] = {"thoughts_tokens": thoughts}
                    step["metrics"] = metrics
                steps.append(step)
                continue

            if event_type == "tool_result" and message:
                parts = message.get("parts") if isinstance(message.get("parts"), list) else []
                for part in parts:
                    if not isinstance(part, dict):
                        continue
                    response = obj(part.get("functionResponse"))
                    if not response:
                        continue
                    call_id = string(response.get("id")) or ""
                    output = stringify(path_value(response, ("response", "output")))
                    attach_observation(steps, call_id=call_id, content=output)
        return steps

    def extract_trajectory_answer(self, events: Sequence[dict[str, Any]], raw_text: str) -> str | None:
        parts: list[str] = []
        for event in events:
            if event.get("type") != "assistant":
                continue
            message = obj(event.get("message"))
            if not message:
                continue
            for part in message.get("parts") if isinstance(message.get("parts"), list) else []:
                if isinstance(part, dict):
                    text = string(part.get("text"))
                    if text:
                        parts.append(text)
        return "\n".join(parts).strip() or super().extract_trajectory_answer(events, raw_text)

    def extract_trajectory_stats(self, events: Sequence[dict[str, Any]]) -> dict[str, Any]:
        totals = {"prompt_tokens": 0, "completion_tokens": 0, "cached_tokens": 0}
        for event in events:
            usage = obj(event.get("usageMetadata"))
            if not usage:
                continue
            totals["prompt_tokens"] += int(usage.get("promptTokenCount") or 0)
            totals["completion_tokens"] += int(usage.get("candidatesTokenCount") or 0)
            totals["cached_tokens"] += int(usage.get("cachedContentTokenCount") or 0)
        return {key: value for key, value in totals.items() if value}

#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Convert supported Harbor agent logs into compact ATIF-like trajectories."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


RAW_LOG_NAMES = {
    "codex": ("codex.txt",),
    "copilot_cli": ("copilot-cli.jsonl", "copilot-cli.txt"),
    "opencode": ("opencode.txt",),
    "claude_code": ("claude-code.txt",),
}


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def content_to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(content_to_text(item) for item in value)
    if isinstance(value, dict):
        if value.get("type") == "text" and "text" in value:
            return str(value["text"])
        if value.get("type") == "tool_use":
            return (
                f"tool_use {value.get('name', '')}: "
                f"{json_dumps(value.get('input', {}))}"
            )
        if value.get("type") == "tool_result":
            return (
                f"tool_result {value.get('tool_use_id', '')}: "
                f"{content_to_text(value.get('content'))}"
            )
        for key in (
            "text",
            "content",
            "message",
            "command",
            "aggregated_output",
            "output",
        ):
            if key in value:
                text = content_to_text(value[key])
                if text:
                    return text
        return json_dumps(value)
    return str(value)


def read_json_lines(path: Path) -> Iterable[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    except OSError:
        return


def step(
    step_id: int,
    source: str,
    message: str,
    *,
    timestamp: str | None = None,
    model_name: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "step_id": step_id,
        "source": source,
        "message": message,
    }
    if timestamp:
        item["timestamp"] = timestamp
    if model_name and source == "agent":
        item["model_name"] = model_name
    if extra:
        item["extra"] = extra
    return item


def trajectory(
    agent: str,
    model: str,
    steps: list[dict[str, Any]],
    session_id: str | None,
) -> dict[str, Any] | None:
    if not steps:
        return None
    return {
        "schema_version": "ATIF-v1.6",
        "session_id": session_id or "unknown",
        "agent": {
            "name": agent,
            "version": "unknown",
            "model_name": model,
        },
        "steps": steps,
        "final_metrics": {"total_steps": len(steps)},
    }


def convert_copilot(path: Path, *, model: str) -> dict[str, Any] | None:
    steps: list[dict[str, Any]] = []
    session_id: str | None = None
    for event in read_json_lines(path):
        event_type = event.get("type", "")
        data = event.get("data") or {}
        timestamp = event.get("timestamp")
        session_id = data.get("sessionId") or event.get("sessionId") or session_id
        if event_type == "user.message":
            text = data.get("content") or data.get("transformedContent") or ""
            source = "user"
        elif event_type == "assistant.message":
            text = content_to_text(data.get("content"))
            source = "agent"
        elif event_type == "tool.execution_started":
            text = (
                f"tool_start {data.get('name', '')}: "
                f"{json_dumps(data.get('arguments', {}))}"
            )
            source = "agent"
        elif event_type == "tool.execution_complete":
            result = data.get("result") or {}
            text = (
                f"tool_result {data.get('toolCallId', '')} "
                f"success={data.get('success')}: "
                f"{content_to_text(result.get('content') or result)}"
            )
            source = "system"
        elif event_type == "result":
            text = json_dumps(data or event)
            source = "system"
        else:
            continue
        if text:
            steps.append(
                step(
                    len(steps) + 1,
                    source,
                    text,
                    timestamp=timestamp,
                    model_name=data.get("model") or model,
                    extra={"event_type": event_type},
                )
            )
    return trajectory("copilot_cli", model, steps, session_id)


def convert_claude(path: Path, *, model: str) -> dict[str, Any] | None:
    steps: list[dict[str, Any]] = []
    session_id: str | None = None
    for event in read_json_lines(path):
        event_type = event.get("type", "")
        timestamp = event.get("timestamp")
        session_id = event.get("session_id") or session_id
        if event_type == "system":
            text = json_dumps(
                {key: value for key, value in event.items() if key != "type"}
            )
            source = "system"
        else:
            message = event.get("message") or {}
            role = message.get("role")
            if role == "assistant":
                source = "agent"
                text = content_to_text(message.get("content"))
            elif role == "user":
                source = "user"
                text = content_to_text(message.get("content"))
            else:
                continue
        if text:
            steps.append(
                step(
                    len(steps) + 1,
                    source,
                    text,
                    timestamp=timestamp,
                    model_name=model,
                    extra={"event_type": event_type},
                )
            )
    return trajectory("claude_code", model, steps, session_id)


def convert_opencode(path: Path, *, model: str) -> dict[str, Any] | None:
    steps: list[dict[str, Any]] = []
    session_id: str | None = None
    for event in read_json_lines(path):
        event_type = event.get("type", "")
        part = event.get("part") or {}
        timestamp = str(event.get("timestamp")) if event.get("timestamp") else None
        session_id = event.get("sessionID") or part.get("sessionID") or session_id
        if event_type == "text":
            text = part.get("text", "")
            source = "agent"
        elif event_type == "tool_use":
            state = part.get("state") or {}
            text = (
                f"tool {part.get('tool', '')}: "
                f"input={json_dumps(state.get('input', {}))}\n"
                f"output={content_to_text(state.get('output'))}"
            )
            source = "agent"
        elif event_type == "error":
            text = json_dumps(event)
            source = "system"
        else:
            continue
        if text:
            steps.append(
                step(
                    len(steps) + 1,
                    source,
                    text,
                    timestamp=timestamp,
                    model_name=model,
                    extra={"event_type": event_type},
                )
            )
    return trajectory("opencode", model, steps, session_id)


def convert_codex(path: Path, *, model: str) -> dict[str, Any] | None:
    steps: list[dict[str, Any]] = []
    session_id: str | None = None
    for event in read_json_lines(path):
        event_type = event.get("type", "")
        item = event.get("item") or {}
        session_id = event.get("thread_id") or session_id
        timestamp = event.get("timestamp")
        if item.get("type") == "agent_message":
            text = item.get("text", "")
            source = "agent"
        elif item.get("type") == "command_execution":
            text = (
                f"command: {item.get('command', '')}\n"
                f"status={item.get('status')}\n"
                f"exit_code={item.get('exit_code')}\n"
                f"{content_to_text(item.get('aggregated_output'))}"
            )
            source = "agent"
        elif event_type.endswith("error"):
            text = json_dumps(event)
            source = "system"
        else:
            continue
        if text:
            steps.append(
                step(
                    len(steps) + 1,
                    source,
                    text,
                    timestamp=timestamp,
                    model_name=model,
                    extra={
                        "event_type": event_type,
                        "item_type": item.get("type"),
                    },
                )
            )
    return trajectory("codex", model, steps, session_id)


CONVERTERS = {
    "codex": convert_codex,
    "copilot_cli": convert_copilot,
    "opencode": convert_opencode,
    "claude_code": convert_claude,
}


def trajectory_from_trial(
    trial_dir: Path,
    *,
    harness: str,
    model: str,
) -> tuple[dict[str, Any] | None, str]:
    existing = trial_dir / "agent/trajectory.json"
    if existing.exists() and existing.stat().st_size:
        try:
            value = json.loads(existing.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            value = None
        if value and value.get("steps"):
            return value, "native"

    for raw_name in RAW_LOG_NAMES[harness]:
        raw_path = trial_dir / "agent" / raw_name
        if not raw_path.exists() or raw_path.stat().st_size == 0:
            continue
        value = CONVERTERS[harness](raw_path, model=model)
        if value and value.get("steps"):
            return value, f"converted:{raw_name}"
    return None, "missing"

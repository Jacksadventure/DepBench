from __future__ import annotations

import json
import time
from typing import Any, Mapping, Sequence


def string(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def obj(value: object) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def path_value(root: object, segments: Sequence[str]) -> object:
    current = root
    for segment in segments:
        if not isinstance(current, dict):
            return None
        current = current.get(segment)
    return current


def compact(record: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if value is not None and value != ""}


def stringify(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def fallback_answer(raw_text: str) -> str | None:
    lines = [line for line in raw_text.splitlines() if line.strip() and not line.startswith("$ ")]
    text = "\n".join(lines).strip()
    return text[-20000:] if text else None


def agent_text_step(
    agent: object,
    message: str,
    timestamp: str,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    clean_extra = dict(extra or {})
    reasoning_content = clean_extra.pop("reasoning_content", None)
    step: dict[str, Any] = {
        "step_id": 1,
        "timestamp": timestamp,
        "source": "agent",
        "model_name": getattr(agent, "model", None),
        "message": message,
        "llm_call_count": 1,
    }
    if reasoning_content:
        step["reasoning_content"] = reasoning_content
    if clean_extra:
        step["extra"] = compact(clean_extra)
    return step


def agent_tool_step(
    agent: object,
    *,
    timestamp: str,
    message: str,
    call_id: str,
    function_name: str,
    arguments: Mapping[str, Any],
    output: str | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    step: dict[str, Any] = {
        "step_id": 1,
        "timestamp": timestamp,
        "source": "agent",
        "model_name": getattr(agent, "model", None),
        "message": message,
        "tool_calls": [
            {
                "tool_call_id": call_id,
                "function_name": function_name,
                "arguments": dict(arguments),
            }
        ],
        "llm_call_count": 0,
    }
    if output:
        step["observation"] = {"results": [{"source_call_id": call_id, "content": output}]}
    if extra:
        step["extra"] = compact(extra)
    return step


def attach_observation(steps: list[dict[str, Any]], *, call_id: str, content: str) -> None:
    for step in reversed(steps):
        calls = step.get("tool_calls")
        if not isinstance(calls, list):
            continue
        if not any(isinstance(call, dict) and call.get("tool_call_id") == call_id for call in calls):
            continue
        observation = step.setdefault("observation", {"results": []})
        if isinstance(observation, dict) and isinstance(observation.get("results"), list):
            observation["results"].append({"source_call_id": call_id, "content": content})
        return


def metrics_from_stats(stats: Mapping[str, Any]) -> dict[str, Any]:
    return compact(
        {
            "prompt_tokens": stats.get("prompt_tokens") or stats.get("input_tokens"),
            "completion_tokens": stats.get("completion_tokens") or stats.get("output_tokens"),
            "cached_tokens": stats.get("cached_tokens") or stats.get("cached_input_tokens"),
            "cost_usd": stats.get("cost_usd") or stats.get("total_cost_usd") or stats.get("cost"),
        }
    )


def millis_to_iso(value: object) -> str | None:
    if not isinstance(value, (int, float)):
        return None
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(value / 1000))

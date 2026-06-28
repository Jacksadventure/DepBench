#!/usr/bin/env python3
"""Export v4-with-test219 LLM x harness trajectories.

The source Harbor jobs already contain the authoritative per-trial results.
This exporter writes a compact, commit-friendly export:

    harbor_benchmark/trajectory_exports/v4_withtest219_YYYYMMDD/
      index.csv
      index.json
      <llm>__<harness>.jsonl.gz

Each JSONL row contains one task/trial with reward metadata, source path, and an
ATIF-like trajectory JSON object.  If a Harbor `agent/trajectory.json` exists, it
is preserved exactly.  Otherwise we convert the raw agent JSONL/log stream into a
lightweight ATIF-compatible shape.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
HARBOR_JOBS = ROOT / "harbor_jobs"
DEFAULT_OUT = ROOT / "harbor_benchmark/trajectory_exports/v4_withtest219_20260627"


GROUPS: list[dict[str, str]] = [
    {
        "llm": "gpt55",
        "harness": "codex",
        "model": "gpt-5.5",
        "job": "v4_withtest219__codex__gpt55__full219_20260627",
    },
    {
        "llm": "gpt55",
        "harness": "copilot_cli",
        "model": "gpt-5.5",
        "job": "v4_withtest219__copilot_cli__gpt55__full219_20260627",
    },
    {
        "llm": "gpt55",
        "harness": "opencode",
        "model": "gpt-5.5",
        "job": "v4_withtest219__opencode__gpt55__full219_20260627",
    },
    {
        "llm": "gpt55",
        "harness": "claude_code",
        "model": "gpt-5.5",
        "job": "claude_code_copilot_api_gpt55_v4_withtest_219_conc10_2026-06-25__0400-00",
    },
    {
        "llm": "gemini35flash",
        "harness": "copilot_cli",
        "model": "gemini-3.5-flash",
        "job": "v4_withtest219__copilot_cli__gemini35flash__full219_20260627",
    },
    {
        "llm": "gemini35flash",
        "harness": "opencode",
        "model": "gemini-3.5-flash",
        "job": "v4_withtest219__opencode__gemini35flash__full219_20260627",
    },
    {
        "llm": "gemini35flash",
        "harness": "claude_code",
        "model": "gemini-3.5-flash",
        "job": "claude_code_copilot_api_gemini35flash_v4_withtest_219_conc10_2026-06-25__0400-00",
    },
    {
        "llm": "claude48",
        "harness": "copilot_cli",
        "model": "claude-opus-4-8",
        "job": "copilot_cli_claude48_byok_v4_withtest_219_conc10_2026-06-26__1248-00",
    },
    {
        "llm": "claude48",
        "harness": "opencode",
        "model": "claude-opus-4-8",
        "job": "opencode_claude48_v4_withtest_219_conc10_2026-06-26__1248-00",
    },
    {
        "llm": "claude48",
        "harness": "claude_code",
        "model": "claude-opus-4-8",
        "job": "claude_code_claude48_v4_withtest_219_conc10_2026-06-26__ready-00",
    },
]


RAW_LOG_NAMES = {
    "codex": ["codex.txt"],
    "copilot_cli": ["copilot-cli.jsonl", "copilot-cli.txt"],
    "opencode": ["opencode.txt"],
    "claude_code": ["claude-code.txt"],
}


def _load_tasks() -> list[str]:
    summary = ROOT / "harbor_benchmark/task_summary.json"
    return [row["folder"] for row in json.loads(summary.read_text())]


TASKS = _load_tasks()
TASK_SET = set(TASKS)


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _content_to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(_content_to_text(item) for item in value)
    if isinstance(value, dict):
        if value.get("type") == "text" and "text" in value:
            return str(value["text"])
        if value.get("type") == "tool_use":
            return f"tool_use {value.get('name', '')}: {_json_dumps(value.get('input', {}))}"
        if value.get("type") == "tool_result":
            return f"tool_result {value.get('tool_use_id', '')}: {_content_to_text(value.get('content'))}"
        for key in ("text", "content", "message", "command", "aggregated_output", "output"):
            if key in value:
                text = _content_to_text(value[key])
                if text:
                    return text
        return _json_dumps(value)
    return str(value)


def _read_json_lines(path: Path) -> Iterable[dict[str, Any]]:
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


def _step(step_id: int, source: str, message: str, *, timestamp: str | None = None,
          model_name: str | None = None, extra: dict[str, Any] | None = None) -> dict[str, Any]:
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


def _trajectory(agent: str, model: str, steps: list[dict[str, Any]], session_id: str | None) -> dict[str, Any] | None:
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
        "final_metrics": {
            "total_steps": len(steps),
        },
    }


def convert_copilot(path: Path, *, model: str) -> dict[str, Any] | None:
    steps: list[dict[str, Any]] = []
    step_id = 1
    session_id: str | None = None
    for event in _read_json_lines(path):
        etype = event.get("type", "")
        data = event.get("data") or {}
        timestamp = event.get("timestamp")
        session_id = data.get("sessionId") or event.get("sessionId") or session_id
        if etype == "user.message":
            text = data.get("content") or data.get("transformedContent") or ""
            source = "user"
        elif etype == "assistant.message":
            text = _content_to_text(data.get("content"))
            source = "agent"
        elif etype == "tool.execution_started":
            text = f"tool_start {data.get('name', '')}: {_json_dumps(data.get('arguments', {}))}"
            source = "agent"
        elif etype == "tool.execution_complete":
            result = data.get("result") or {}
            text = f"tool_result {data.get('toolCallId', '')} success={data.get('success')}: {_content_to_text(result.get('content') or result)}"
            source = "system"
        elif etype == "result":
            text = _json_dumps(data or event)
            source = "system"
        else:
            continue
        if text:
            steps.append(_step(step_id, source, text, timestamp=timestamp, model_name=data.get("model") or model, extra={"event_type": etype}))
            step_id += 1
    return _trajectory("copilot_cli", model, steps, session_id)


def convert_claude(path: Path, *, model: str) -> dict[str, Any] | None:
    steps: list[dict[str, Any]] = []
    step_id = 1
    session_id: str | None = None
    for event in _read_json_lines(path):
        etype = event.get("type", "")
        timestamp = event.get("timestamp")
        session_id = event.get("session_id") or session_id
        if etype == "system":
            text = _json_dumps({k: v for k, v in event.items() if k not in {"type"}})
            source = "system"
        else:
            msg = event.get("message") or {}
            role = msg.get("role")
            if role == "assistant":
                source = "agent"
                text = _content_to_text(msg.get("content"))
            elif role == "user":
                source = "user"
                text = _content_to_text(msg.get("content"))
            else:
                continue
        if text:
            steps.append(_step(step_id, source, text, timestamp=timestamp, model_name=model, extra={"event_type": etype}))
            step_id += 1
    return _trajectory("claude_code", model, steps, session_id)


def convert_opencode(path: Path, *, model: str) -> dict[str, Any] | None:
    steps: list[dict[str, Any]] = []
    step_id = 1
    session_id: str | None = None
    for event in _read_json_lines(path):
        etype = event.get("type", "")
        part = event.get("part") or {}
        timestamp = str(event.get("timestamp")) if event.get("timestamp") else None
        session_id = event.get("sessionID") or part.get("sessionID") or session_id
        if etype == "text":
            text = part.get("text", "")
            source = "agent"
        elif etype == "tool_use":
            state = part.get("state") or {}
            text = f"tool {part.get('tool', '')}: input={_json_dumps(state.get('input', {}))}\noutput={_content_to_text(state.get('output'))}"
            source = "agent"
        elif etype == "error":
            text = _json_dumps(event)
            source = "system"
        else:
            continue
        if text:
            steps.append(_step(step_id, source, text, timestamp=timestamp, model_name=model, extra={"event_type": etype}))
            step_id += 1
    return _trajectory("opencode", model, steps, session_id)


def convert_codex(path: Path, *, model: str) -> dict[str, Any] | None:
    steps: list[dict[str, Any]] = []
    step_id = 1
    session_id: str | None = None
    for event in _read_json_lines(path):
        etype = event.get("type", "")
        item = event.get("item") or {}
        session_id = event.get("thread_id") or session_id
        timestamp = event.get("timestamp")
        if item.get("type") == "agent_message":
            text = item.get("text", "")
            source = "agent"
        elif item.get("type") == "command_execution":
            text = f"command: {item.get('command', '')}\nstatus={item.get('status')}\nexit_code={item.get('exit_code')}\n{_content_to_text(item.get('aggregated_output'))}"
            source = "agent"
        elif etype.endswith("error"):
            text = _json_dumps(event)
            source = "system"
        else:
            continue
        if text:
            steps.append(_step(step_id, source, text, timestamp=timestamp, model_name=model, extra={"event_type": etype, "item_type": item.get("type")}))
            step_id += 1
    return _trajectory("codex", model, steps, session_id)


CONVERTERS = {
    "codex": convert_codex,
    "copilot_cli": convert_copilot,
    "opencode": convert_opencode,
    "claude_code": convert_claude,
}


def reward_from_trial(trial_dir: Path, result: dict[str, Any]) -> float | None:
    rewards = ((result.get("verifier_result") or {}).get("rewards") or {})
    if "reward" in rewards:
        try:
            return float(rewards["reward"])
        except (TypeError, ValueError):
            return None
    reward_file = trial_dir / "verifier/reward.txt"
    if reward_file.exists():
        try:
            return float(reward_file.read_text(errors="ignore").strip())
        except ValueError:
            return None
    return None


def task_from_result(trial_dir: Path, result: dict[str, Any]) -> str:
    task_path = ((result.get("task_id") or {}).get("path") or "")
    if task_path:
        name = Path(task_path).name
        if name in TASK_SET:
            return name
    task_name = result.get("task_name") or ""
    if "/" in task_name:
        task_name = task_name.split("/")[-1]
    if task_name in TASK_SET:
        return task_name
    matches = [task for task in TASKS if trial_dir.name.startswith(task + "__") or trial_dir.name.startswith(task[:24])]
    if len(matches) == 1:
        return matches[0]
    return task_name or trial_dir.name


def existing_or_converted_trajectory(trial_dir: Path, *, harness: str, model: str) -> tuple[dict[str, Any] | None, str | None, str | None]:
    existing = trial_dir / "agent/trajectory.json"
    if existing.exists():
        try:
            return json.loads(existing.read_text()), str(existing), "existing"
        except json.JSONDecodeError:
            pass

    for raw_name in RAW_LOG_NAMES[harness]:
        raw_path = trial_dir / "agent" / raw_name
        if not raw_path.exists() or raw_path.stat().st_size == 0:
            continue
        trajectory = CONVERTERS[harness](raw_path, model=model)
        if trajectory:
            return trajectory, str(raw_path), "converted"
    return None, None, None


def export_group(group: dict[str, str], out_dir: Path) -> dict[str, Any]:
    group_name = f"{group['llm']}__{group['harness']}"
    job_dir = HARBOR_JOBS / group["job"]
    out_file = out_dir / f"{group_name}.jsonl.gz"
    rows: list[dict[str, Any]] = []

    with gzip.open(out_file, "wt", encoding="utf-8") as handle:
        for trial_dir in sorted(p.resolve() for p in job_dir.iterdir() if p.is_dir()):
            result_path = trial_dir / "result.json"
            result: dict[str, Any] = {}
            if result_path.exists():
                try:
                    result = json.loads(result_path.read_text())
                except json.JSONDecodeError:
                    result = {}

            trajectory, raw_path, trajectory_source = existing_or_converted_trajectory(
                trial_dir, harness=group["harness"], model=group["model"]
            )
            reward = reward_from_trial(trial_dir, result)
            exception = result.get("exception_info") or {}
            row = {
                "llm": group["llm"],
                "harness": group["harness"],
                "model": group["model"],
                "task": task_from_result(trial_dir, result),
                "trial": trial_dir.name,
                "source_job": group["job"],
                "source_trial_path": str(trial_dir),
                "raw_log_path": raw_path,
                "trajectory_source": trajectory_source,
                "has_trajectory": trajectory is not None,
                "reward": reward,
                "exception_type": exception.get("type") or exception.get("exception_type") or "",
                "trajectory": trajectory,
            }
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            rows.append(row)

    return {
        "llm": group["llm"],
        "harness": group["harness"],
        "model": group["model"],
        "source_job": group["job"],
        "export_file": str(out_file.resolve().relative_to(ROOT)),
        "rows": len(rows),
        "with_trajectory": sum(1 for row in rows if row["has_trajectory"]),
        "converted": sum(1 for row in rows if row["trajectory_source"] == "converted"),
        "existing": sum(1 for row in rows if row["trajectory_source"] == "existing"),
        "missing": sum(1 for row in rows if not row["has_trajectory"]),
        "pass": sum(1 for row in rows if row["reward"] == 1.0),
        "fail": sum(1 for row in rows if row["reward"] not in (None, 1.0)),
        "no_reward": sum(1 for row in rows if row["reward"] is None),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    args.out_dir = args.out_dir.resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    summaries = [export_group(group, args.out_dir) for group in GROUPS]
    generated_at = datetime.now(timezone.utc).isoformat()

    index_json = {
        "generated_at": generated_at,
        "dataset": "v4-with-test219",
        "format": "gzip JSONL; each row contains one task/trial trajectory",
        "groups": summaries,
    }
    (args.out_dir / "index.json").write_text(json.dumps(index_json, indent=2, sort_keys=True) + "\n")
    with (args.out_dir / "index.csv").open("w", newline="") as handle:
        fieldnames = [
            "llm",
            "harness",
            "model",
            "source_job",
            "export_file",
            "rows",
            "with_trajectory",
            "converted",
            "existing",
            "missing",
            "pass",
            "fail",
            "no_reward",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summaries)
    lines = [
        "# LLM x Harness trajectory exports",
        "",
        f"Generated: {generated_at}",
        "",
        "Each `.jsonl.gz` file contains one JSON object per task/trial with reward metadata and trajectory JSON.",
        "",
        "| LLM | Harness | Rows | With trajectory | Existing | Converted | Missing | Export |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for item in summaries:
        lines.append(
            f"| {item['llm']} | {item['harness']} | {item['rows']} | "
            f"{item['with_trajectory']} | {item['existing']} | {item['converted']} | "
            f"{item['missing']} | `{item['export_file']}` |"
        )
    (args.out_dir / "README.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(index_json, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

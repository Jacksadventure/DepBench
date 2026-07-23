#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Build compact evidence packets for post-hoc non-pass annotation."""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            rows[row["task"]] = row
    return rows


def clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    half = max(1, (limit - 80) // 2)
    return (
        text[:half]
        + f"\n... [{len(text) - 2 * half} characters omitted] ...\n"
        + text[-half:]
    )


def stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def compact_trajectory(trajectory: dict[str, Any], limit: int) -> str:
    chunks: list[str] = []
    for step in trajectory.get("steps", []):
        if step.get("source") != "agent":
            continue
        pieces = [f"STEP {step.get('step_id', '')}"]
        message = stringify(step.get("message"))
        reasoning = stringify(step.get("reasoning_content"))
        if message and message != "(tool use)":
            pieces.append(f"MESSAGE: {clip(message, 1600)}")
        if reasoning:
            pieces.append(f"REASONING: {clip(reasoning, 1600)}")
        for call in step.get("tool_calls") or []:
            pieces.append(
                "TOOL: "
                + stringify(call.get("function_name"))
                + " "
                + clip(stringify(call.get("arguments")), 1600)
            )
        observation = step.get("observation") or {}
        results = (
            observation.get("results", [])
            if isinstance(observation, dict)
            else []
        )
        for result in results:
            if isinstance(result, dict):
                content = stringify(result.get("content"))
            else:
                content = stringify(result)
            if content:
                pieces.append(f"RESULT: {clip(content, 2200)}")
        chunks.append("\n".join(pieces))
    return clip("\n\n".join(chunks), limit)


def compact_diff(path: Path, limit: int) -> str:
    if not path.exists():
        return ""
    kept: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if (
            line.startswith("diff --git ")
            or line.startswith("@@")
            or line.startswith("--- ")
            or line.startswith("+++ ")
            or (
                line.startswith(("+", "-"))
                and not line.startswith(("+++", "---"))
            )
        ):
            kept.append(line)
    return clip("\n".join(kept), limit)


def verifier_evidence(row: dict[str, Any], limit: int) -> str:
    pieces: list[str] = []
    ctrf = row.get("verifier_ctrf") or {}
    tests = (
        ctrf.get("results", {}).get("tests", [])
        if isinstance(ctrf, dict)
        else []
    )
    for test in tests:
        if not isinstance(test, dict):
            continue
        pieces.append(
            "\n".join(
                [
                    f"TEST: {test.get('name', '')}",
                    f"STATUS: {test.get('status', '')}",
                    f"MESSAGE: {test.get('message', '')}",
                    f"TRACE: {clip(stringify(test.get('trace')), 5000)}",
                ]
            )
        )
    stdout = stringify(row.get("verifier_test_stdout"))
    if stdout:
        pieces.append(f"VERIFIER STDOUT TAIL:\n{stdout[-6000:]}")
    return clip("\n\n".join(pieces), limit)


def build_packet(
    requested: dict[str, Any],
    trajectory_row: dict[str, Any],
    verifier_row: dict[str, Any],
    max_agent_chars: int,
) -> dict[str, Any]:
    task = requested["task"]
    task_dir = ROOT / "dataset/tasks" / task
    return {
        "configuration": requested["configuration"],
        "task": task,
        "trial": trajectory_row.get("trial"),
        "reward": trajectory_row.get("reward"),
        "exception_type": trajectory_row.get("exception_type", ""),
        "outcome_source": trajectory_row.get("outcome_source", ""),
        "instruction": clip(
            (task_dir / "instruction.md").read_text(
                encoding="utf-8", errors="replace"
            ),
            2500,
        ),
        "trajectory_evidence": compact_trajectory(
            trajectory_row.get("trajectory") or {}, max_agent_chars
        ),
        "verifier_evidence": verifier_evidence(verifier_row, 9000),
        "oracle_manifest_diff": compact_diff(
            task_dir / "solution/manifest.patch", 7000
        ),
        "oracle_code_diff": compact_diff(
            task_dir / "solution/code.patch", 9000
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-agent-chars", type=int, default=18000)
    args = parser.parse_args()

    requested = json.loads(args.manifest.read_text(encoding="utf-8"))
    configurations = sorted({row["configuration"] for row in requested})
    trajectory_maps = {
        configuration: read_jsonl(
            ROOT / "trajectories" / f"{configuration}.jsonl.gz"
        )
        for configuration in configurations
    }
    verifier_maps = {
        configuration: read_jsonl(
            ROOT / "verify_logs" / f"{configuration}.jsonl.gz"
        )
        for configuration in configurations
    }

    packets = []
    for row in requested:
        configuration = row["configuration"]
        task = row["task"]
        packets.append(
            build_packet(
                row,
                trajectory_maps[configuration][task],
                verifier_maps[configuration][task],
                args.max_agent_chars,
            )
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(packets, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(packets)} annotation packets to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

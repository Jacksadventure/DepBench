#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Build post-hoc non-pass evidence packets across all configurations by default."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def select_requests(
    artifact_root: Path,
    manifest: Path | None = None,
    configurations: list[str] | None = None,
) -> list[dict[str, Any]]:
    if manifest is not None:
        requested = json.loads(manifest.read_text(encoding="utf-8"))
    else:
        with (artifact_root / "results/final_per_task_outcomes.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            requested = [
                {
                    "configuration": row["configuration"],
                    "task": row["task"],
                    "trial": row["final_trial"],
                    "reward": float(row["final_reward"]) if row["final_reward"] else None,
                }
                for row in csv.DictReader(handle)
                if not row["final_reward"] or float(row["final_reward"]) != 1.0
            ]
    if configurations:
        unknown = set(configurations) - {row["configuration"] for row in requested}
        if unknown:
            raise ValueError(f"No requested non-passes for configurations: {sorted(unknown)}")
        requested = [row for row in requested if row["configuration"] in configurations]
    identities = {(row["configuration"], row["task"]) for row in requested}
    if len(identities) != len(requested):
        raise ValueError("Duplicate requested configuration/task")
    return sorted(requested, key=lambda row: (row["configuration"], row["task"]))


def read_jsonl(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row["task"] in rows:
                raise ValueError(f"Duplicate task in {path}: {row['task']}")
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
    *,
    artifact_root: Path = ROOT / "paper_review",
) -> dict[str, Any]:
    task = requested["task"]
    for row in (trajectory_row, verifier_row):
        if row["task"] != task or row.get("trial") != trajectory_row.get("trial"):
            raise ValueError(f"Evidence task/trial mismatch: {task}")
        if row.get("reward") != trajectory_row.get("reward"):
            raise ValueError(f"Evidence reward mismatch: {task}")
    if "trial" in requested and requested["trial"] != trajectory_row.get("trial"):
        raise ValueError(f"Evidence does not match final selected trial: {task}")
    if "reward" in requested and requested["reward"] != trajectory_row.get("reward"):
        raise ValueError(f"Evidence does not match final selected reward: {task}")
    task_dir = artifact_root / "dataset/tasks" / task
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, default=ROOT / "paper_review")
    parser.add_argument("--manifest", type=Path, help="explicit case selection; defaults to all non-passes")
    parser.add_argument("--configuration", action="append",
                        help="restrict to this configuration; repeat for multiple (default: all)")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-agent-chars", type=int, default=18000)
    args = parser.parse_args()

    requested = select_requests(args.artifact_root, args.manifest, args.configuration)
    configurations = sorted({row["configuration"] for row in requested})
    trajectory_maps = {
        configuration: read_jsonl(
            args.artifact_root / "trajectories" / f"{configuration}.jsonl.gz"
        )
        for configuration in configurations
    }
    verifier_maps = {
        configuration: read_jsonl(
            args.artifact_root / "verify_logs" / f"{configuration}.jsonl.gz"
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
                artifact_root=args.artifact_root,
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

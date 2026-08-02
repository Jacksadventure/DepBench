#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Export the 20-task zero-pass contract-repair reruns."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "results/zero_pass_contract_repair_reruns_203.csv"
SUMMARY_PATH = (
    ROOT / "analysis/zero_pass_contract_repair_rerun_summary_203.json"
)

CONFIGURATIONS = {
    "claude_code__claude48": "claude48__claude_code",
    "claude_code__gemini35flash": "gemini35flash__claude_code",
    "claude_code__gpt55": "gpt55__claude_code",
    "codex__gpt55": "gpt55__codex",
    "copilot_cli__claude48": "claude48__copilot_cli",
    "copilot_cli__gemini35flash": "gemini35flash__copilot_cli",
    "copilot_cli__gpt55": "gpt55__copilot_cli",
    "opencode__claude48": "claude48__opencode",
    "opencode__gemini35flash": "gemini35flash__opencode",
    "opencode__gpt55": "gpt55__opencode",
}


def clean_message(value: Any) -> str:
    return "\n".join(
        line.rstrip() for line in str(value or "").splitlines()
    ).strip()


def reward_from_result(result: dict[str, Any]) -> float | None:
    reward = (
        ((result.get("verifier_result") or {}).get("rewards") or {}).get(
            "reward"
        )
    )
    return None if reward is None else float(reward)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rerun-root", type=Path, required=True)
    args = parser.parse_args()

    rerun_root = args.rerun_root.resolve()
    final_trials_path = rerun_root / "analysis/final_trials.csv"
    affected_tasks_path = rerun_root / "manifests/affected_tasks_20.txt"
    rows = list(csv.DictReader(final_trials_path.open(encoding="utf-8")))
    affected_tasks = {
        line.strip()
        for line in affected_tasks_path.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    }
    if len(rows) != 200 or len(affected_tasks) != 20:
        raise SystemExit(
            f"expected 200 final trials and 20 tasks, got "
            f"{len(rows)} and {len(affected_tasks)}"
        )

    output = []
    seen = set()
    for row in rows:
        configuration = CONFIGURATIONS[row["config"]]
        task = row["task"]
        key = (configuration, task)
        if key in seen:
            raise SystemExit(f"duplicate zero-pass repair rerun cell: {key}")
        seen.add(key)
        if task not in affected_tasks:
            raise SystemExit(f"unexpected task outside affected set: {task}")

        result_path = rerun_root / row["path"]
        result = json.loads(result_path.read_text(encoding="utf-8"))
        observed_task = (result.get("task_name") or "").split("/")[-1]
        if observed_task != task:
            raise SystemExit(
                f"{result_path}: expected task {task}, got {observed_task}"
            )
        reward = reward_from_result(result)
        expected_reward = float(row["reward"])
        exception = result.get("exception_info") or {}
        exception_type = (
            exception.get("exception_type") or exception.get("type") or ""
        )
        if (
            reward is None
            and expected_reward == 0.0
            and exception_type == "AgentTimeoutError"
        ):
            reward = 0.0
        if reward != expected_reward:
            raise SystemExit(
                f"{configuration}/{task}: summary reward {expected_reward} "
                f"!= result reward {reward}"
            )
        trial_dir = result_path.parent
        timestamp = trial_dir.parent.name
        output.append(
            {
                "configuration": configuration,
                "task": task,
                "reward": "" if reward is None else reward,
                "exception_type": exception_type,
                "exception_message": clean_message(
                    exception.get("exception_message")
                    or exception.get("message")
                ),
                "rerun_kind": "zero-pass-contract-repair-rerun",
                "job_name": (
                    f"{rerun_root.name}:{row['config']}:{timestamp}"
                ),
                "trial": trial_dir.name,
                "trial_dir": str(trial_dir.relative_to(rerun_root)),
                "started_at": result.get("started_at") or "",
                "finished_at": result.get("finished_at") or "",
            }
        )

    expected = {
        (configuration, task)
        for configuration in CONFIGURATIONS.values()
        for task in affected_tasks
    }
    if seen != expected:
        raise SystemExit(
            f"zero-pass repair rerun coverage mismatch: "
            f"missing={len(expected - seen)} extra={len(seen - expected)}"
        )
    output.sort(key=lambda row: (row["configuration"], row["task"]))

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(output[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(output)

    by_configuration = {}
    for configuration in sorted(CONFIGURATIONS.values()):
        subset = [
            row for row in output if row["configuration"] == configuration
        ]
        exceptions = Counter(
            row["exception_type"] or "none" for row in subset
        )
        passes = sum(float(row["reward"] or 0) == 1.0 for row in subset)
        by_configuration[configuration] = {
            "trials": len(subset),
            "pass": passes,
            "non_pass": len(subset) - passes,
            "exceptions": dict(sorted(exceptions.items())),
        }
    summary = {
        "rerun_root_name": rerun_root.name,
        "affected_tasks": len(affected_tasks),
        "configurations": len(CONFIGURATIONS),
        "trials": len(output),
        "pass": sum(float(row["reward"] or 0) == 1.0 for row in output),
        "non_pass": sum(float(row["reward"] or 0) != 1.0 for row in output),
        "by_configuration": by_configuration,
        "provenance_file": str(OUTPUT_PATH.relative_to(ROOT)),
    }
    SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"exported {len(output)} zero-pass contract-repair rerun cells")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
